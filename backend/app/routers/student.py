from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/student",
    tags=["Student"]
)

# ✅ Create student
@router.post("/", response_model=schemas.StudentBase, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db, student)

# ✅ Get all students
@router.get("/", response_model=list[schemas.StudentBase])
def get_students(db: Session = Depends(get_db)):
    return crud.get_students(db)

# ✅ Get student by ID
@router.get("/{student_id}", response_model=schemas.StudentBase)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return schemas.StudentBase.from_orm(student)

# ✅ Update student
@router.put("/{student_id}", response_model=schemas.StudentBase)
def update_student(student_id: int, updated: schemas.StudentUpdate, db: Session = Depends(get_db)):
    student = crud.update_student(db, student_id, updated)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# ✅ Delete student
@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.delete_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"detail": "Student deleted successfully"}
