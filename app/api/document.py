from uuid import UUID

from fastapi import (
    APIRouter, Depends, Request, WebSocket, Form
)
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_document
from app.core.logging import setup_logger
from app.models import User, Document
from app.services.document import (
    __create_document_page__, __create_document__, __join_document_page__,
    __join_document__, __document_page__, __document_ws__, __update_document__, __delete_document__
)

logger = setup_logger(__name__)

router = APIRouter()

DOCUMENT_SAVE_INTERVAL = 2
connected_clients: dict[str, set[WebSocket]] = {}
active_members: dict[str, set[str]] = {}

templates = Jinja2Templates("templates")


@router.get("/create")
def create_document_page(
    request: Request,
    user: User = Depends(get_current_user),
):
    """New document creation page."""
    return __create_document_page__(request, user)


@router.post("/create")
def create_document(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    document_name: str | None = Form(None),
):
    """
    Parameters
    ----------
    request : Request
        FastAPI request object.
    user : User
        Current user dependency.
    db : Session
        Database session dependency.
    document_name : str | None
        Name of the new document.

    Returns
    -------
    RedirectResponse
        Redirect to the newly created document page.
    """
    return __create_document__(
        request,
        user,
        db,
        document_name,
    )


@router.get("/join")
def join_document_page(
    request: Request,
    user: User = Depends(get_current_user),
):
    """Document join page."""
    return __join_document_page__(
        request,
        user,
    )


@router.post("/join")
def join_document(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    document_id: str | None = Form(None),
):
    """
    Parameters
    ----------
    request : Request
        FastAPI request object.
    user : User
        Current user dependency.
    db : Session
        Database session dependency.
    document_id : str | None
        ID of the document to join.

    Returns
    -------
    RedirectResponse
        Redirect the user to the joined document page.
    """
    return __join_document__(
        request,
        user,
        db,
        document_id,
    )


@router.get("/{document_id}")
def document_page(
    document_id: UUID,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Parameters
    ----------
    document_id : UUID
        ID of the document to join.
    request : Request
        FastAPI request object.
    user : User
        Current user dependency.
    db : Session
        Database session dependency.

    Returns
    -------
    TemplateResponse
    """
    return __document_page__(
        document_id,
        request,
        user,
        db,
    )


@router.websocket("/{document_id}/content")
async def document_websocket(
    document_id: UUID,
    ws: WebSocket,
    db: Session = Depends(get_db),
):
    """
    Parameters
    ----------
    document_id : UUID
        ID of the current document.
    ws : WebSocket
        FastAPI websocket object.
    db : Session
        Database session dependency.

    Returns
    -------
    WebsocketResponse
    """
    return await __document_ws__(
        document_id,
        ws,
        db,
    )


@router.post("/{document_id}/update")
async def update_document(
    request: Request,
    user: User = Depends(get_current_user),
    doc: Document = Depends(get_document),
    db: Session = Depends(get_db),
    name: str | None = Form(None),
    access: str | None = Form(None),
):
    """
    Parameters
    ----------
    request : Request
        FastAPI request object.
    user : User
        Current user dependency.
    doc : Document
        Current document dependency.
    db : Session
        Database session dependency.
    name : str | None, optional
        New name of the document.
    access : str | None, optional
        Document access restriction (Creator or Members)

    Returns
    -------
    TemplateResponse
    """
    return await __update_document__(
        request,
        user,
        doc,
        db,
        name,
        access,
    )


@router.delete("/{document_id}")
def delete_document(
    user: User = Depends(get_current_user),
    doc: Document = Depends(get_document),
    db: Session = Depends(get_db),
):
    """Delete the document with the given ID"""
    return __delete_document__(
        user,
        doc,
        db,
    )
