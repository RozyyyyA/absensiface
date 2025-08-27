from sqlalchemy.orm import Session
from . import models, schemas

def get_students(db: Session):
    return db.query(models.Student).all()

def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(name=student.name, nim=student.nim)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db: Session, student_id: int, updated: schemas.StudentUpdate):
    student = get_student(db, student_id)
    if not student:
        return None
    student.name = updated.name
    student.nim = updated.nim
    db.commit()
    db.refresh(student)
    return student

def delete_student(db: Session, student_id: int):
    student = get_student(db, student_id)
    if not student:
        return None
    db.delete(student)
    db.commit()
    return student

from sqlalchemy.orm import Session
from . import models

# =========================
# Course Enrollment CRUD
# =========================
def enroll_student(db: Session, course_id: int, student_id: int):
    # Cek apakah sudah terdaftar
    existing = db.query(models.CourseEnrollment).filter_by(
        course_id=course_id, student_id=student_id
    ).first()
    if existing:
        return existing

    enrollment = models.CourseEnrollment(course_id=course_id, student_id=student_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment

def get_course_enrollments(db: Session, course_id: int):
    return db.query(models.CourseEnrollment).filter_by(course_id=course_id).all()
