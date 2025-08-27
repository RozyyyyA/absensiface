# app/routers/courses.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from .. import models, schemas
from ..schemas import CourseBase, CourseCreate, CourseUpdate  # import dari app/schemas.py

router = APIRouter(prefix="/courses", tags=["Courses"])

# GET semua courses
@router.get("/", response_model=List[CourseBase])
def get_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()

# GET course by ID
@router.get("/{course_id}", response_model=CourseBase)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # return dict sesuai schema, hindari nested relationship
    return {
        "id": course.id,
        "name": course.name,
        "code": course.code,
        "lecturer_id": course.lecturer_id
    }

# POST create course
@router.post("/", response_model=schemas.CourseBase)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    new_course = models.Course(**dict(course))
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


# PUT update course
@router.put("/{course_id}", response_model=CourseBase)
def update_course(course_id: int, course: CourseUpdate, db: Session = Depends(get_db)):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    for key, value in course.dict(exclude_unset=True).items():
        setattr(db_course, key, value)

    db.commit()
    db.refresh(db_course)
    return db_course

# DELETE course
@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(db_course)
    db.commit()
    return {"detail": "Course deleted"}
