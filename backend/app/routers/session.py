from ast import List
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..security import get_current_lecturer
from datetime import datetime
from typing import List

# session.py
router = APIRouter(tags=["Session"])

@router.post("/", response_model=schemas.SessionResponse)
def create_session(
    session: schemas.SessionCreate,
    db: Session = Depends(database.get_db),
    lecturer: models.Lecturer = Security(get_current_lecturer)
):
    # cek course valid dan milik dosen yang login
    course = db.query(models.Course).filter(models.Course.id == session.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.lecturer_id != lecturer.id:
        raise HTTPException(status_code=403, detail="Not allowed to create session for this course")

    new_session = models.Session(
        course_id=session.course_id,
        meeting_no=session.meeting_no,
        started_at=datetime.utcnow()
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@router.post("/{session_id}/finish")
def finish_session(
    session_id: int,
    db: Session = Depends(database.get_db),
    lecturer: models.Lecturer = Security(get_current_lecturer)
):
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    # pastikan course session ini memang punya dosen yang login
    if db_session.course.lecturer_id != lecturer.id:
        raise HTTPException(status_code=403, detail="Not allowed to finish this session")

    db_session.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(db_session)
    return {
        "message": "Session finished",
        "session_id": db_session.id,
        "finished_at": db_session.finished_at
    }

@router.get("/", response_model=List[schemas.SessionResponse])
def list_sessions(db: Session = Depends(database.get_db)):
    return db.query(models.Session).all()

