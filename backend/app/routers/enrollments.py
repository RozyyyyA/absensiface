from typing import List
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas
from ..database import get_db
from ..security import get_current_lecturer

router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)

@router.post("/", response_model=List[schemas.EnrollmentResponse])
def enroll_students(
    payload: schemas.EnrollmentCreateMultiple,  # pakai model baru untuk multiple student
    db: Session = Depends(get_db),
    lecturer: models.Lecturer = Security(get_current_lecturer)
):
    # cek course milik dosen
    course = db.get(models.Course, payload.course_id)
    if not course or course.lecturer_id != lecturer.id:
        raise HTTPException(status_code=404, detail="Course not found or unauthorized")

    enrollments = []
    for student_id in payload.student_ids:
        # cek student ada
        student = db.get(models.Student, student_id)
        if not student:
            continue  # skip jika student tidak ada, bisa juga raise error

        # cek sudah enrolled belum
        exists = db.query(models.CourseEnrollment).filter_by(
            course_id=payload.course_id, student_id=student_id
        ).first()
        if exists:
            continue  # skip jika sudah enrolled

        # buat enrollment
        enrollment = models.CourseEnrollment(course_id=payload.course_id, student_id=student_id)
        db.add(enrollment)
        enrollments.append(enrollment)

    db.commit()
    for e in enrollments:
        db.refresh(e)
    return enrollments

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
