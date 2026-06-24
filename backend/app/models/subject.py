from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    color = Column(String(20), nullable=True, default="#6366f1")
    created_at = Column(DateTime, server_default=func.now())

    user_subjects = relationship("UserSubject", back_populates="subject")


class UserSubject(Base):
    __tablename__ = "user_subjects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    is_enrolled = Column(Boolean, default=True)
    enrolled_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="subjects")
    subject = relationship("Subject", back_populates="user_subjects")
