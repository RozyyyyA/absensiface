from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from datetime import datetime
from .. import models, schemas
from ..database import get_db
from ..security import get_current_lecturer

router = APIRouter(
    prefix="/report",
    tags=["Report"],
)

def _recount_report(db: Session, session_id: int) -> models.Report:
    report = db.query(models.Report).filter_by(session_id=session_id).first()
    session = db.get(models.Session, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found for report recount")

    if report is None:
        total_students = db.query(models.CourseEnrollment).filter_by(course_id=session.course_id).count()
        # Buat Report hanya dengan field yang valid
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

@router.get("/{session_id}", response_model=schemas.ReportDetail)
def get_report(
    session_id: int,
    db: Session = Depends(get_db),
    lecturer: models.Lecturer = Security(get_current_lecturer)
):
    session_obj = db.get(models.Session, session_id)
    if not session_obj or session_obj.course.lecturer_id != lecturer.id:
        raise HTTPException(status_code=404, detail="Session not found or unauthorized")

    # Hitung dan ambil report
    report = _recount_report(db, session_id)

    # Buat summary
    summary = schemas.ReportSummary(
        course_id=report.course_id,
        meeting_no=session_obj.meeting_no,
        total_students=report.total_students,
        hadir_count=report.hadir_count,
        sakit_count=report.sakit_count,
        tanpa_keterangan_count=report.tanpa_keterangan_count,
        started_at=getattr(report, "started_at", None),
        finished_at=getattr(report, "finished_at", None)
    )

    # Ambil daftar mahasiswa dan status absen
    students = db.query(models.Student).join(
        models.CourseEnrollment, models.CourseEnrollment.student_id == models.Student.id
    ).filter(models.CourseEnrollment.course_id == session_obj.course_id).all()

    absents = []
    for student in students:
        att = db.query(models.Attendance).filter_by(
            student_id=student.id, session_id=session_id
        ).first()
        if att is None or att.status != models.AttendanceStatus.hadir:
            absents.append(
                schemas.AbsentItem(
                    student_id=student.id,
                    name=student.name,
                    nim=student.nim,
                    status=att.status.value if att else "tanpa_keterangan"
                )
            )

    return schemas.ReportDetail(
        summary=summary,
        absents=absents
    )
