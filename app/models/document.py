import uuid

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, func, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base


class DocumentMember(Base):
    __tablename__ = "document_members"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, primary_key=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, primary_key=True)


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    content = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
    )
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    access_only_me = Column(Boolean, default=True, nullable=False)

    creator = relationship("User", back_populates="created_documents")
    members = relationship("User", secondary=DocumentMember.__table__, back_populates="documents")
