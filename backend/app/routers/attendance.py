from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from datetime import datetime
import numpy as np
import cv2

from .. import models, schemas
from ..database import get_db
from ..security import get_current_lecturer
from ..face_recognition import recognize_bgr  # fungsi deteksi wajahmu

# Router dengan dependency global: gembok otomatis di Swagger
router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)

# ---------------------------
# Helper functions
# ---------------------------
def _ensure_course_owned(db: Session, course_id: int, lecturer_id: int) -> models.Course:
    course = db.get(models.Course, course_id)
    if not course or course.lecturer_id != lecturer_id:
        raise HTTPException(status_code=404, detail="Course not found or unauthorized")
    return course

def _upsert_attendance(db: Session, student_id: int, course_id: int, meeting_no: int, status_val: models.AttendanceStatus) -> models.Attendance:
    att = db.query(models.Attendance).filter_by(
        student_id=student_id, course_id=course_id, meeting_no=meeting_no
    ).first()
    now = datetime.utcnow()
    if att:
        att.status = status_val
        att.timestamp = now
    else:
        att = models.Attendance(
            student_id=student_id,
            course_id=course_id,
            meeting_no=meeting_no,
            status=status_val,
            timestamp=now
        )
        db.add(att)
    db.commit()
    db.refresh(att)
    return att

def _recount_report(db: Session, course_id: int, meeting_no: int) -> models.Report:
    report = db.query(models.Report).filter_by(course_id=course_id, meeting_no=meeting_no).first()
    if report is None:
        total_students = db.query(models.CourseEnrollment).filter_by(course_id=course_id).count()
        report = models.Report(
            course_id=course_id,
            meeting_no=meeting_no,
            started_at=datetime.utcnow(),
            total_students=total_students
        )
        db.add(report)
        db.commit()
        db.refresh(report)

    report.hadir_count = db.query(models.Attendance).filter_by(
        course_id=course_id, meeting_no=meeting_no, status=models.AttendanceStatus.hadir
    ).count()
    report.sakit_count = db.query(models.Attendance).filter_by(
        course_id=course_id, meeting_no=meeting_no, status=models.AttendanceStatus.sakit
    ).count()
    report.tanpa_keterangan_count = db.query(models.Attendance).filter_by(
        course_id=course_id, meeting_no=meeting_no, status=models.AttendanceStatus.tanpa_keterangan
    ).count()
    db.commit()
    db.refresh(report)
    return report

# ---------------------------
# 1) Mark attendance by face
# ---------------------------
@router.post("/mark/face", response_model=schemas.AttendanceMarkResponse)
def mark_attendance_by_face(
    course_id: int,
    meeting_no: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    lecturer: models.Lecturer = Security(get_current_lecturer)
):
    _ = _ensure_course_owned(db, course_id, lecturer.id)

    content = file.file.read()
    npimg = np.frombuffer(content, np.uint8)
    img_bgr = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    student_name, confidence = recognize_bgr(img_bgr)
    if student_name is None:
        raise HTTPException(status_code=422, detail="Face not detected / not recognized")

    # Cari student_id dari nama mahasiswa
    student = db.query(models.Student).filter_by(name=student_name).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student '{student_name}' not found")
    student_id = student.id

    # Pastikan mahasiswa terdaftar di mata kuliah
    enrolled = db.query(models.CourseEnrollment).filter_by(
        course_id=course_id, student_id=student_id
    ).first()
    if not enrolled:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this course")

    _upsert_attendance(db, student_id, course_id, meeting_no, models.AttendanceStatus.hadir)
    _recount_report(db, course_id, meeting_no)

    return schemas.AttendanceMarkResponse(
        status="hadir",
        student_id=student_id,
        confidence=confidence
    )

# ---------------------------
# 2) Manual mark attendance
# ---------------------------
@router.post("/mark/manual", response_model=schemas.AttendanceRecord)
def mark_attendance_manual(
    payload: schemas.AttendanceStatusUpdate,
    db: Session = Depends(get_db),
    lecturer: models.Lecturer = Security(get_current_lecturer)
):
    _ = _ensure_course_owned(db, payload.course_id, lecturer.id)

    student = db.get(models.Student, payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    enrolled = db.query(models.CourseEnrollment).filter_by(
        course_id=payload.course_id, student_id=payload.student_id
    ).first()
    if not enrolled:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this course")

    att = _upsert_attendance(
        db,
        payload.student_id,
        payload.course_id,
        payload.meeting_no,
        payload.status
    )
    _recount_report(db, payload.course_id, payload.meeting_no)

    return schemas.AttendanceRecord(
        student_id=att.student_id,
        student_name=student.name,
        status=att.status.value,
        timestamp=att.timestamp
    )
