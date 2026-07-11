import asyncio
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, WebSocketException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.logging import setup_logger
from app.models import Document, User
from app.models import Session as AuthSession
from app.utils.db_helpers import save_document_content
from app.utils.url import normalize_params

logger = setup_logger(__name__)

router = APIRouter()

DOCUMENT_SAVE_INTERVAL = 2
connected_clients: dict[str, set[WebSocket]] = {}
active_members: dict[str, set[str]] = {}

templates = Jinja2Templates("templates")


def __create_document_page__(
    request: Request,
    user: User,
):
    return templates.TemplateResponse(
        request,
        "pages/create_or_join_doc.html",
        {
            "user": user,
            "title": "Create a new document",
            "name": "document_name",
            "placeholder": "New Document",
        },
    )


def __create_document__(
    request: Request,
    user: User,
    db: Session,
    document_name: str | None,
):
    if not document_name or (document_name and not document_name.strip()):
        return RedirectResponse(
            f"{request.url}/?error_message=Document+name+cannot+be+empty.",
            status.HTTP_303_SEE_OTHER,
        )

    new_doc = Document(
        name=document_name,
        created_by=user.id,
    )
    new_doc.members.append(user)

    try:
        db.add(new_doc)
        db.commit()
    except Exception as error:
        logger.error(f"Document create failed: {error}")
        raise HTTPException(
            status.HTTP_303_SEE_OTHER,
            "Document create failed, please try again later.",
            headers={
                "Location": "/?error_message=Document+create+failed,+please+try+again+later.",
            },
        )

    return RedirectResponse(
        f"/documents/{new_doc.id}",
        status.HTTP_303_SEE_OTHER,
    )


def __join_document_page__(
    request: Request,
    user: User,
):
    return templates.TemplateResponse(
        request,
        "pages/create_or_join_doc.html",
        {
            "user": user,
            "title": "Join an existing room",
            "name": "document_id",
            "placeholder": "Document ID",
        },
    )


def __join_document__(
    request: Request,
    user: User,
    db: Session,
    document_id: str | None,
):
    try:
        uuid.UUID(document_id)
    except:
        return RedirectResponse(
            f"{request.url}/?error_message=Invalid+document+ID.",
            status.HTTP_303_SEE_OTHER,
        )

    doc = db.get(Document, document_id)
    if not doc:
        return RedirectResponse(
            "/?error_message=Invalid+document+ID.",
            status.HTTP_303_SEE_OTHER,
        )

    if user in doc.members:
        return RedirectResponse(
            "/?error_message=You've+already+joined+this+document.",
            status.HTTP_303_SEE_OTHER,
        )

    if doc.access_only_me:
        return RedirectResponse(
            "/?error_message=Document+can't+be+joined,+contact+the+document+owner.",
            status.HTTP_303_SEE_OTHER,
        )

    try:
        doc.members.append(user)
        db.commit()
    except Exception as error:
        logger.error(f"Document join failed: {error}")
        return RedirectResponse(
            f"{request.url}/?error_message={normalize_params('Document join failed, please try again later.')}",
            status.HTTP_303_SEE_OTHER,
        )

    return RedirectResponse(
        f"/documents/{doc.id}",
        status.HTTP_303_SEE_OTHER,
    )


def __document_page__(
    document_id: uuid.UUID,
    request: Request,
    user: User,
    db: Session,
):
    doc = db.get(Document, document_id)

    if not doc:
        return RedirectResponse(
            "/?error_message=Invalid+document+ID.",
        )

    creator = user.id == doc.created_by
    member = user in doc.members
    access_by_anyone = doc.access_only_me == False

    if not creator and (not member or not access_by_anyone):
        return RedirectResponse(
            "/?error_message=Access+denied,+contact+the+document+owner.",
            status.HTTP_303_SEE_OTHER,
        )

    if document_id not in active_members:
        active_members[doc.id] = set()
    active_members[doc.id].add(user.email)

    return templates.TemplateResponse(
        request,
        "pages/document.html",
        {
            "user": user,
            "can_save": user.id == doc.created_by,
            "doc": doc,
            "members": list(active_members.get(doc.id, set()))
            if document_id in active_members
            else [],
        },
    )


async def __document_ws__(
    document_id: uuid.UUID,
    ws: WebSocket,
    db: Session,
):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(
            status.HTTP_303_SEE_OTHER,
            "Invalid document ID.",
            headers={"Location": "/?error_message=Invalid+document+ID."},
        )

    await ws.accept()

    if doc.id not in connected_clients:
        connected_clients[doc.id] = set()
    connected_clients[doc.id].add(ws)

    if doc.id not in active_members:
        active_members[doc.id] = set()
    user = (
        db.query(User)
        .join(AuthSession)
        .filter(
            AuthSession.id == ws.cookies.get("session-id"),
            AuthSession.expires_at > datetime.now(timezone.utc),
        )
        .first()
    )
    active_members[doc.id].add(user.email)

    for c in list(connected_clients.get(doc.id, set())):
        try:
            await c.send_text(
                json.dumps({"members": list(active_members.get(doc.id, set()))}),
            )
        except (WebSocketDisconnect, WebSocketException, RuntimeError) as error:
            connected_clients[doc.id].discard(c)
            logger.error(f"Failed to send message to <{c}>: {error}")

    try:
        while True:
            payload = await ws.receive_text()
            parsed_payload = json.loads(payload)
            new_content = parsed_payload.get("content")
            typing = parsed_payload.get("typing")

            data = {
                "typing": typing,
                "members": list(active_members.get(doc.id, set())),
            }
            for c in list(connected_clients.get(doc.id, set())):
                try:
                    if c != ws:
                        data.update(parsed_payload)
                    if not doc.access_only_me:
                        await c.send_text(json.dumps(data))
                except (WebSocketDisconnect, WebSocketException, RuntimeError) as error:
                    logger.error(f"Failed to send message to <{c}> : {error}")

            if new_content is not None:
                try:
                    if doc.access_only_me and doc.created_by != user.id:
                        pass
                    else:
                        if doc.content != new_content:
                            asyncio.create_task(save_document_content(doc.id, new_content))
                except Exception as error:
                    logger.error(f"Failed to save content : {error}")

    except (WebSocketDisconnect, WebSocketException, RuntimeError) as error:
        logger.error(f"Unexpected error: {error}")

        if doc.id in connected_clients:
            connected_clients[doc.id].discard(ws)
        if doc.id in active_members:
            active_members[doc.id].discard(user.email)

        for c in list(connected_clients.get(doc.id, set())):
            try:
                await c.send_text(
                    json.dumps({"members": list(active_members.get(doc.id, set()))}),
                )
            except (WebSocketDisconnect, WebSocketException, RuntimeError) as error:
                logger.error(
                    f"Failed to send message to <{c}> : {error}",
                )

        if doc.id in connected_clients and not connected_clients[doc.id]:
            del connected_clients[doc.id]
        if doc.id in active_members and not active_members[doc.id]:
            del active_members[doc.id]


async def __update_document__(
    request: Request,
    user: User,
    document: Document,
    db: Session,
    name: str | None,
    access: str | None,
):
    template_name = "components/doc_name.html"

    if user.id != document.created_by:
        raise HTTPException(
            status.HTTP_303_SEE_OTHER,
            "You are not authorized.",
            headers={"Location": f"{request.url}/?error_message={normalize_params('You are not authorized.')}"},
        )

    if name and name.strip():
        document.name = name
    elif name and not name.strip() and not document.name:
        document.name = f"my_doc_{uuid.uuid4()}"

    if access and access == "any_one":
        document.access_only_me = False
    elif access and access == "only_me":
        document.access_only_me = True
        if document.id in connected_clients:
            for c in list(connected_clients.get(document.id, set())):
                await c.send_text(json.dumps({"refresh_page": True}))

    if access:
        template_name = "components/doc_dropdown.html"

    try:
        db.commit()
        db.refresh(document)
    except Exception as error:
        logger.error(f"Document update failed: {error}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Document update failed, please try again later.",
            headers={
                "Location": "/?error_message=Document+save+failed,+please+try+again+later.",
            },
        )

    return templates.TemplateResponse(
        request,
        template_name,
        {"doc": document, "user": user},
    )


def __delete_document__(
    user: User,
    document: Document,
    db: Session,
):
    if not document.created_by == user.id:
        raise HTTPException(
            status.HTTP_303_SEE_OTHER,
            "You are not authorized",
            headers={"Location": "/?error_message=You+are+not+authorized."},
        )

    try:
        db.delete(document)
        db.commit()
    except Exception as error:
        logger.error(f"Document save failed: {error}")
        raise HTTPException(
            status.HTTP_303_SEE_OTHER,
            "Document delete failed, please try again later.",
            headers={
                "Location": "/?error_message=Document+delete+failed,+please+try+again+later.",
            },
        )
