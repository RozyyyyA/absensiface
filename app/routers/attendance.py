# app/routers/attendance.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import numpy as np
import cv2

from .. import models, schemas, database
from ..database import get_db
from ..security import get_current_lecturer
from ..face_recognition import recognize_bgr  # <- YOLOv5su + HOG + SVM

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# ---------------------------
# Helpers
# ---------------------------
def _ensure_course_owned(db: Session, course_id: int, lecturer_id: int) -> models.Course:
    course = db.get(models.Course, course_id)
    if not course or course.lecturer_id != lecturer_id:
        raise HTTPException(status_code=404, detail="Course not found or unauthorized")
    return course


def _upsert_attendance(
    db: Session,
    student_id: int,
    course_id: int,
    meeting_no: int,
    status_val: models.AttendanceStatus,
) -> models.Attendance:
    """Insert/update attendance row untuk (student, course, meeting)."""
    att = (
        db.query(models.Attendance)
        .filter_by(student_id=student_id, course_id=course_id, meeting_no=meeting_no)
        .first()
    )
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
            timestamp=now,
        )
        db.add(att)
    db.commit()
    db.refresh(att)
    return att


def _recount_report(db: Session, course_id: int, meeting_no: int) -> models.Report:
    """Hitung ulang agregat report (hadir/sakit/tanpa_keterangan) dan simpan."""
    report = (
        db.query(models.Report)
        .filter(models.Report.course_id == course_id, models.Report.meeting_no == meeting_no)
        .first()
    )
    # Jika report belum ada (mis. dosen lupa start session), buat minimal entry
    if report is None:
        total = (
            db.query(models.CourseEnrollment)
            .filter(models.CourseEnrollment.course_id == course_id)
            .count()
        )
        report = models.Report(
            course_id=course_id,
            meeting_no=meeting_no,
            started_at=datetime.utcnow(),
            total_students=total,
        )
        db.add(report)
        db.commit()
        db.refresh(report)

    hadir = (
        db.query(models.Attendance)
        .filter_by(course_id=course_id, meeting_no=meeting_no, status=models.AttendanceStatus.hadir)
        .count()
    )
    sakit = (
        db.query(models.Attendance)
        .filter_by(course_id=course_id, meeting_no=meeting_no, status=models.AttendanceStatus.sakit)
        .count()
    )
    tanpa = (
        db.query(models.Attendance)
        .filter_by(
            course_id=course_id,
            meeting_no=meeting_no,
            status=models.AttendanceStatus.tanpa_keterangan,
        )
        .count()
    )

    report.hadir_count = hadir
    report.sakit_count = sakit
    report.tanpa_keterangan_count = tanpa

    db.commit()
    db.refresh(report)
    return report


# ---------------------------
# 1) Face-based mark (YOLOv5su + HOG + SVM)
# ---------------------------
@router.post("/mark/face", response_model=schemas.AttendanceMarkResponse)
def mark_attendance_by_face(
    course_id: int,
    meeting_no: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    lecturer=Depends(get_current_lecturer),
):
    """
    Dosen upload 1 frame (jpg/png) dari kamera depan kelas.
    Sistem: YOLOv5su -> crop -> HOG -> SVM -> dapat student_id + confidence.
    Lalu upsert attendance = 'hadir' untuk student tsb.
    """
    # Validasi course
    _ = _ensure_course_owned(db, course_id, lecturer.id)

    # Baca gambar
    content = file.file.read()
    npimg = np.frombuffer(content, np.uint8)
    img_bgr = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    # Recognize (pakai pipeline YOLOv5su+HOG+SVM di face_recognition.py)
    student_id, confidence = recognize_bgr(img_bgr)

    if student_id is None:
        # Tidak ada wajah / tidak dikenal
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Face not detected / not recognized",
        )

    # Pastikan student ada & terdaftar di kelas (opsional tapi disarankan)
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    enrolled = (
        db.query(models.CourseEnrollment)
        .filter_by(course_id=course_id, student_id=student_id)
        .first()
    )
    if not enrolled:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this course")

    # Upsert hadir
    att = _upsert_attendance(
        db,
        student_id=student_id,
        course_id=course_id,
        meeting_no=meeting_no,
        status_val=models.AttendanceStatus.hadir,
    )

    # Update agregat report
    _recount_report(db, course_id, meeting_no)

    return schemas.AttendanceMarkResponse(
        status="hadir",
        student_id=att.student_id,
        confidence=confidence,
    )


# ---------------------------
# 2) Manual mark (sakit / tanpa_keterangan / koreksi)
# ---------------------------
@router.post("/mark/manual", response_model=schemas.AttendanceRecord)
def mark_attendance_manual(
    payload: schemas.AttendanceStatusUpdate,
    db: Session = Depends(database.get_db),
    lecturer=Depends(get_current_lecturer),
):
    """
    Dosen menandai status untuk mahasiswa yang belum absen:
    - sakit
    - tanpa_keterangan
    (atau koreksi status bila perlu)
    """
    # Validasi course
    _ = _ensure_course_owned(db, payload.course_id, lecturer.id)

    # Validasi student
    st = db.get(models.Student, payload.student_id)
    if not st:
        raise HTTPException(status_code=404, detail="Student not found")

    # Optional: pastikan terdaftar di mata kuliah
    enrolled = (
        db.query(models.CourseEnrollment)
        .filter_by(course_id=payload.course_id, student_id=payload.student_id)
        .first()
    )
    if not enrolled:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this course")

    # Upsert sesuai status kiriman
    att = _upsert_attendance(
        db,
        student_id=payload.student_id,
        course_id=payload.course_id,
        meeting_no=payload.meeting_no,
        status_val=models.AttendanceStatus(payload.status.value if hasattr(payload.status, "value") else payload.status),  # handle enum/string
    )

    # Update agregat report
    _recount_report(db, payload.course_id, payload.meeting_no)

    # Bentuk response
    return schemas.AttendanceRecord(
        student_id=att.student_id,
        student_name=st.name,
        status=att.status.value if hasattr(att.status, "value") else str(att.status),
        timestamp=att.timestamp,
    )
