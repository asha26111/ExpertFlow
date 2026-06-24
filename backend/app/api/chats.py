from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.chat import Chat, Message

router = APIRouter(prefix="/chats", tags=["chats"])


class ChatCreate(BaseModel):
    title: Optional[str] = "New Chat"
    subject: Optional[str] = None


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: Optional[list] = None
    expert_used: Optional[str] = None
    created_at: str

    @classmethod
    def from_msg(cls, msg: Message):
        return cls(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            sources=msg.sources or [],
            expert_used=msg.expert_used or "",
            created_at=msg.created_at.isoformat() if msg.created_at else "",
        )


class ChatResponse(BaseModel):
    id: int
    title: str
    subject: Optional[str] = None
    created_at: str
    message_count: int = 0


@router.get("", response_model=List[ChatResponse])
def list_chats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        chats = (
            db.query(Chat)
            .filter(Chat.user_id == current_user.id)
            .order_by(desc(Chat.created_at))
            .all()
        )
        return [
            ChatResponse(
                id=c.id,
                title=c.title or "New Chat",
                subject=c.subject,
                created_at=c.created_at.isoformat() if c.created_at else "",
                message_count=len(c.messages),
            )
            for c in chats
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list chats: {str(e)}")


@router.post("", response_model=ChatResponse)
def create_chat(data: ChatCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        chat = Chat(user_id=current_user.id, title=data.title or "New Chat", subject=data.subject)
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return ChatResponse(
            id=chat.id, title=chat.title, subject=chat.subject,
            created_at=chat.created_at.isoformat() if chat.created_at else "",
            message_count=0,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create chat: {str(e)}")


@router.get("/{chat_id}/messages")
def get_messages(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return [MessageResponse.from_msg(m) for m in chat.messages]


@router.post("/{chat_id}/messages")
async def send_message(
    chat_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not data.content or not data.content.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    content = data.content.strip()

    # 1. Save user message
    try:
        user_msg = Message(chat_id=chat_id, role="user", content=content)
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save message: {str(e)}")

    # 2. Auto-title chat on first message
    try:
        msg_count = db.query(Message).filter(Message.chat_id == chat_id).count()
        if msg_count == 1:
            chat.title = content[:60] + ("..." if len(content) > 60 else "")
            db.commit()
    except Exception:
        pass  # non-critical

    # 3. Build conversation history
    try:
        prev = (
            db.query(Message)
            .filter(Message.chat_id == chat_id, Message.id != user_msg.id)
            .order_by(Message.created_at)
            .all()
        )
        history = [{"role": m.role, "content": m.content} for m in prev[-8:]]
    except Exception:
        history = []

    # 4. RAG + MoE + Gemini — NEVER raises, always returns a result
    try:
        from app.services.rag_service import get_rag_service
        rag = get_rag_service()
        result = await rag.generate_answer(content, history)
    except Exception as e:
        result = {
            "answer": (
                f"⚠️ **RAG/Gemini Error:** `{str(e)}`\n\n"
                "**Checklist:**\n"
                "1. Is `GEMINI_API_KEY` set in `backend/.env`?\n"
                "2. Get a free key at https://aistudio.google.com\n"
                "3. Check the backend terminal for the full error traceback"
            ),
            "expert_used": "🎓 General Expert",
            "expert_id": "general",
            "sources": [],
        }

    # 5. Save assistant message
    try:
        asst_msg = Message(
            chat_id=chat_id,
            role="assistant",
            content=result["answer"],
            sources=result.get("sources", []),
            expert_used=result.get("expert_used", ""),
        )
        db.add(asst_msg)
        if not chat.subject and result.get("expert_id"):
            chat.subject = result["expert_id"]
        db.commit()
        db.refresh(asst_msg)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save response: {str(e)}")

    return {
        "user_message": MessageResponse.from_msg(user_msg),
        "assistant_message": MessageResponse.from_msg(asst_msg),
        "expert_used": result.get("expert_used", ""),
        "sources": result.get("sources", []),
    }


@router.delete("/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    try:
        db.delete(chat)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Chat deleted"}


class ChatUpdate(BaseModel):
    title: Optional[str] = None
    pinned: Optional[bool] = None
    archived: Optional[bool] = None


@router.patch("/{chat_id}", response_model=ChatResponse)
def update_chat(chat_id: int, data: ChatUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    try:
        if data.title is not None:
            chat.title = data.title
        if data.pinned is not None:
            chat.pinned = data.pinned
        if data.archived is not None:
            chat.archived = data.archived
        db.commit()
        db.refresh(chat)
        return ChatResponse(
            id=chat.id, title=chat.title, subject=chat.subject,
            created_at=chat.created_at.isoformat() if chat.created_at else "",
            message_count=len(chat.messages),
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
