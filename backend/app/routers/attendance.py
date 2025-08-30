from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from datetime import datetime
import numpy as np
import cv2

from .. import models, schemas, database
from ..database import get_db
from ..security import get_current_lecturer
from ..face_recognition import recognize_bgr  # fungsi deteksi wajahmu

# Router dengan dependency global: gembok otomatis di Swagger
router = APIRouter(tags=["Attendance"])

# ---------------------------
# Helper functions
# ---------------------------
def _ensure_course_owned(db: Session, course_id: int, lecturer_id: int) -> models.Course:
    course = db.get(models.Course, course_id)
    if not course or course.lecturer_id != lecturer_id:
        raise HTTPException(status_code=404, detail="Course not found or unauthorized")
    return course

def _upsert_attendance(db: Session, student_id: int, session_id: int, status_val: models.AttendanceStatus) -> models.Attendance:
    att = db.query(models.Attendance).filter_by(
        student_id=student_id, session_id=session_id
    ).first()
    now = datetime.utcnow()
    if att:
        att.status = status_val
        att.timestamp = now
    else:
        att = models.Attendance(
            student_id=student_id,
            session_id=session_id,
            status=status_val,
            timestamp=now
        )
        db.add(att)
    db.commit()
    db.refresh(att)
    return att

def _recount_report(db: Session, session_id: int) -> models.Report:
    report = db.query(models.Report).filter_by(session_id=session_id).first()
    session = db.get(models.Session, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found for report recount")

    if report is None:
        total_students = db.query(models.CourseEnrollment).filter_by(course_id=session.course_id).count()
        report = models.Report(
            session_id=session_id,
            course_id=session.course_id,
            started_at=datetime.utcnow(),
            total_students=total_students
        )
        db.add(report)
        db.commit()
        db.refresh(report)

    # Hitung ulang jumlah hadir, sakit, tanpa keterangan
    report.hadir_count = db.query(models.Attendance).filter_by(
        session_id=session_id, status=models.AttendanceStatus.hadir
    ).count()
    report.sakit_count = db.query(models.Attendance).filter_by(
        session_id=session_id, status=models.AttendanceStatus.sakit
    ).count()
    report.tanpa_keterangan_count = db.query(models.Attendance).filter_by(
        session_id=session_id, status=models.AttendanceStatus.tanpa_keterangan
    ).count()

    # Update finished_at jika semua mahasiswa sudah punya status
    if (report.hadir_count + report.sakit_count + report.tanpa_keterangan_count) == report.total_students:
        report.finished_at = datetime.utcnow()

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
    # Pastikan dosen pemilik course
    _ = _ensure_course_owned(db, course_id, lecturer.id)

    # Ambil session sesuai course_id + meeting_no
    session = db.query(models.Session).filter_by(
        course_id=course_id, meeting_no=meeting_no
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Start session first.")

    # Baca file gambar
    content = file.file.read()
    npimg = np.frombuffer(content, np.uint8)
    img_bgr = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    # Deteksi wajah
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

    # ----------------------------
    # Cek apakah mahasiswa sudah absen
    # ----------------------------
    existing_att = db.query(models.Attendance).filter_by(
        student_id=student_id,
        session_id=session.id
    ).first()

    if existing_att:
        # Sudah absen, tidak bisa absen lagi
        return schemas.AttendanceMarkResponse(
            status="already_marked",
            student_id=student_id,
            confidence=confidence
        )

    # Kalau belum absen, lakukan upsert
    _upsert_attendance(
        db,
        student_id,
        session.id,  # session_id
        models.AttendanceStatus.hadir
    )

    # Update report pakai session_id
    _recount_report(db, session.id)

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
    # Pastikan course dimiliki lecturer
    _ = _ensure_course_owned(db, payload.course_id, lecturer.id)

    # Ambil session berdasarkan course_id + meeting_no
    session = db.query(models.Session).filter_by(
        course_id=payload.course_id, meeting_no=payload.meeting_no
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Pastikan student ada
    student = db.get(models.Student, payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Pastikan student terdaftar di course
    enrolled = db.query(models.CourseEnrollment).filter_by(
        course_id=payload.course_id, student_id=payload.student_id
    ).first()
    if not enrolled:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this course")

    # Upsert attendance pakai session.id
    att = _upsert_attendance(
        db,
        payload.student_id,
        session.id,
        payload.status
    )

    # Hitung ulang report pakai session.id
    _recount_report(db, session.id)

    return schemas.AttendanceRecord(
        student_id=att.student_id,
        student_name=student.name,
        status=att.status.value,
        timestamp=att.timestamp
    )

# ---------------------------
# 3) Update attendance
# ---------------------------
@router.put("/{attendance_id}", response_model=schemas.AttendanceRecord)
def update_attendance(
    attendance_id: int,
    payload: schemas.AttendanceUpdate,
    db: Session = Depends(get_db),
    lecturer: models.Lecturer = Security(get_current_lecturer)
):
    att = db.get(models.Attendance, attendance_id)
    if not att:
        raise HTTPException(status_code=404, detail="Attendance not found")

    # pastikan lecturer punya hak di course
    session = db.get(models.Session, att.session_id)
    _ = _ensure_course_owned(db, session.course_id, lecturer.id)

    att.status = payload.status
    att.timestamp = datetime.utcnow()
    db.commit()
    db.refresh(att)

    # update report
    _recount_report(db, session.id)

    student = db.get(models.Student, att.student_id)
    return schemas.AttendanceRecord(
        student_id=att.student_id,
        student_name=student.name if student else "-",
        status=att.status.value,
        timestamp=att.timestamp
    )