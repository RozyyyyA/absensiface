from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, database
from datetime import datetime

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"]
)

@router.post("/", response_model=schemas.SessionResponse)
def create_session(session: schemas.SessionCreate, db: Session = Depends(database.get_db)):
    new_session = models.Session(**session.dict())
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.post("/{session_id}/finish")
def finish_session(session_id: int, db: Session = Depends(database.get_db)):
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    db_session.finished_at = datetime.utcnow()
    db.commit()
    return {"message": "Session finished"}
