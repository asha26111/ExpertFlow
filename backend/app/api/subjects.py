from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.subject import Subject, UserSubject

router = APIRouter(prefix="/subjects", tags=["subjects"])

DEFAULT_SUBJECTS = [
    {"name": "Mathematics",         "description": "Algebra, Calculus, Statistics, Linear Algebra & more",       "icon": "📐", "color": "#6366f1"},
    {"name": "Physics",             "description": "Mechanics, Thermodynamics, Electromagnetism, Quantum",        "icon": "⚛️", "color": "#0ea5e9"},
    {"name": "Computer Science",    "description": "Algorithms, Data Structures, AI/ML, Web Dev, Databases",     "icon": "💻", "color": "#10b981"},
    {"name": "Chemistry",           "description": "Organic, Inorganic, Physical & Analytical Chemistry",        "icon": "🧪", "color": "#f59e0b"},
    {"name": "Biology",             "description": "Genetics, Cell Biology, Ecology, Anatomy & Physiology",      "icon": "🧬", "color": "#ec4899"},
    {"name": "History",             "description": "World History, Civilizations, Wars & Revolutions",           "icon": "📜", "color": "#8b5cf6"},
    {"name": "Geography",           "description": "Physical Geography, Human Geography, Climate & Environment",  "icon": "🌍", "color": "#06b6d4"},
    {"name": "Economics",           "description": "Micro & Macro Economics, Trade, Finance & Development",      "icon": "📊", "color": "#84cc16"},
    {"name": "Literature & English","description": "Literary Analysis, Grammar, Essay Writing, World Literature", "icon": "📚", "color": "#f97316"},
    {"name": "Psychology",          "description": "Cognitive, Developmental, Social & Abnormal Psychology",     "icon": "🧠", "color": "#a855f7"},
    {"name": "Philosophy",          "description": "Ethics, Logic, Epistemology, Metaphysics & Great Thinkers",  "icon": "🤔", "color": "#14b8a6"},
    {"name": "Advanced Mathematics","description": "Real Analysis, Abstract Algebra, Topology & Number Theory",  "icon": "∑",  "color": "#e11d48"},
    {"name": "General Studies",     "description": "Arts, Music, Law, Medicine, Engineering & more",             "icon": "🎓", "color": "#64748b"},
]


class SubjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    enrolled: bool = False


def seed_subjects(db: Session):
    for s in DEFAULT_SUBJECTS:
        if not db.query(Subject).filter(Subject.name == s["name"]).first():
            db.add(Subject(**s))
    db.commit()


@router.get("", response_model=List[SubjectResponse])
def list_subjects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    seed_subjects(db)
    subjects = db.query(Subject).all()
    enrolled_ids = {
        us.subject_id
        for us in db.query(UserSubject).filter(UserSubject.user_id == current_user.id).all()
    }
    return [
        SubjectResponse(
            id=s.id, name=s.name, description=s.description,
            icon=s.icon, color=s.color, enrolled=s.id in enrolled_ids
        )
        for s in subjects
    ]


@router.post("/{subject_id}/enroll")
def enroll(subject_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(UserSubject).filter(
        UserSubject.user_id == current_user.id,
        UserSubject.subject_id == subject_id
    ).first()
    if not existing:
        db.add(UserSubject(user_id=current_user.id, subject_id=subject_id))
        db.commit()
    return {"enrolled": True}


@router.delete("/{subject_id}/enroll")
def unenroll(subject_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(UserSubject).filter(
        UserSubject.user_id == current_user.id,
        UserSubject.subject_id == subject_id
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
    return {"enrolled": False}
