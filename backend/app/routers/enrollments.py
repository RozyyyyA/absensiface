from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..database import get_db
from ..security import get_current_lecturer

router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)

@router.post("/", response_model=schemas.EnrollmentResponse)
def enroll_student_endpoint(
    payload: schemas.EnrollmentCreate,
    db: Session = Depends(get_db),
    lecturer: models.Lecturer = Security(get_current_lecturer)
):
    # cek course milik dosen
    course = db.get(models.Course, payload.course_id)
    if not course or course.lecturer_id != lecturer.id:
        raise HTTPException(status_code=404, detail="Course not found or unauthorized")

    # cek student ada
    student = db.get(models.Student, payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # enroll
    enrollment = crud.enroll_student(db, payload.course_id, payload.student_id)
    return enrollment

@router.get("/{course_id}", response_model=list[schemas.EnrollmentResponse])
def get_course_enrollments_endpoint(
    course_id: int,
    db: Session = Depends(get_db),
    lecturer: models.Lecturer = Security(get_current_lecturer)
):
    course = db.get(models.Course, course_id)
    if not course or course.lecturer_id != lecturer.id:
        raise HTTPException(status_code=404, detail="Course not found or unauthorized")
    return crud.get_course_enrollments(db, course_id)
