from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator, Text as SAText
from app.core.database import Base
import json


# SQLite-safe JSON column (SQLite has no native JSON type before 3.38)
class JSONText(TypeDecorator):
    impl = SAText
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            try:
                return json.loads(value)
            except Exception:
                return None
        return None


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=True, default="New Chat")
    subject = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    pinned = Column(Boolean, default=False, nullable=False, server_default="0")
    archived = Column(Boolean, default=False, nullable=False, server_default="0")

    user = relationship("User", back_populates="chats")
    messages = relationship(
        "Message", back_populates="chat",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(JSONText, nullable=True)   # SQLite-safe JSON
    expert_used = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    chat = relationship("Chat", back_populates="messages")
