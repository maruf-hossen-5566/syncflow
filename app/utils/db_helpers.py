import asyncio
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.logging import setup_logger
from app.db.session import SessionLocal
from app.models import Document

logger = setup_logger(__name__)


async def save_document_content(doc_id: UUID, content: str):
    await asyncio.to_thread(_save_document_content, doc_id, content)


def _save_document_content(doc_id: UUID, content: str):
    db: Session = SessionLocal()

    try:
        document = db.get(Document, doc_id)
        document.content = content
        db.commit()
    except Exception as error:
        db.rollback()
        logger.error(f"Failed to save document content to db: {error}")
    finally:
        db.close()
