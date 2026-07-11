import uuid

from fastapi import Depends, status, HTTPException
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.logging import setup_logger
from app.db.session import SessionLocal
from app.models import Document
from app.models.session import Session as AuthSession

logger = setup_logger(__name__)

templates = Jinja2Templates("templates")


async def get_db():
    """Create and close a database session"""

    db = SessionLocal()

    try:
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    session_id = request.cookies.get("session-id")

    if not session_id:
        raise HTTPException(
            status.HTTP_303_SEE_OTHER,
            "Missing session ID",
            headers={
                "Location": "/auth/login?error_message=Session+ID+is+missing,+please+login+to+continue.",
            },
        )

    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status.HTTP_303_SEE_OTHER,
            "Invalid session ID",
            headers={
                "Location": "/auth/login/?error_message=Invalid+session+ID,+please+login+to+continue.",
            },
        )

    session = db.get(AuthSession, session_id)
    if not session:
        raise HTTPException(
            status.HTTP_303_SEE_OTHER,
            "Session not found",
            headers={
                "Location": "/auth/login/?error_message=Session+not+found,+please+login+to+continue.",
            },
        )

    if session.is_expired():
        db.delete(session)
        db.commit()
        raise HTTPException(
            status.HTTP_303_SEE_OTHER,
            "Session expired",
            headers={
                "Location": "/auth/login/?error_message=Session+expired,+please+login+to+continue.",
            },
        )

    return session.user


async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
) -> Document:

    if not document_id.strip():
        raise HTTPException(
            status.HTTP_303_SEE_OTHER,
            "Document not found",
            headers={
                "Location": "/?error_message=Document+ID+must+be+given.",
            },
        )
    try:
        uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(
            status.HTTP_303_SEE_OTHER,
            "Invalid document ID.",
            headers={
                "Location": "/?error_message=Invalid+document+ID.",
            },
        )

    doc = db.get(Document, document_id)

    if not doc:
        raise HTTPException(
            status.HTTP_303_SEE_OTHER,
            "Document not found.",
            headers={
                "Location": "/?error_message=Document+not+found.",
            },
        )

    return doc
