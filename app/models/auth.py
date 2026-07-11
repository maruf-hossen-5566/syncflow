import uuid

from sqlalchemy import UUID, Column, DateTime, String, text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.document import DocumentMember


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=text("now()"), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )

    sessions = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan",
    )
    created_documents = relationship("Document", back_populates="creator", order_by="Document.last_updated.desc()")
    documents = relationship(
        "Document", secondary=DocumentMember.__table__, back_populates="members",
        order_by="Document.last_updated.desc()",
    )
