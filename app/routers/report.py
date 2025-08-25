from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..security import get_current_lecturer
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

router = APIRouter(prefix="/report", tags=["Report"])


@router.get("/{course_id}/{meeting_no}", response_model=schemas.ReportDetail)
def get_report(
    course_id: int,
    meeting_no: int,
    db: Session = Depends(get_db),
    lecturer=Depends(get_current_lecturer),
):
    # Pastikan course milik dosen yang login
    course = db.get(models.Course, course_id)
    if not course or course.lecturer_id != lecturer.id:
        raise HTTPException(status_code=404, detail="Course not found or unauthorized")

    # Ambil report berdasarkan course dan pertemuan
    report = (
        db.query(models.Report)
        .filter(
            models.Report.course_id == course_id,
            models.Report.meeting_no == meeting_no,
        )
        .first()
    )
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    # Cari mahasiswa yang absen
    absents = []
    q = (
        db.query(models.Student)
        .join(models.CourseEnrollment, models.CourseEnrollment.student_id == models.Student.id)
        .filter(models.CourseEnrollment.course_id == course_id)
    )
    for st in q.all():
        att = (
            db.query(models.Attendance)
            .filter_by(student_id=st.id, course_id=course_id, meeting_no=meeting_no)
            .first()
        )
        if att is None or att.status != models.AttendanceStatus.hadir:
            absents.append(
                schemas.AbsentItem(
                    student_id=st.id,
                    name=st.name,
                    nim=st.nim,
                    status=(att.status.value if att else "tanpa_keterangan"),
                )
            )

    # Buat summary
    summary = schemas.ReportSummary(
        course_id=report.course_id,
        meeting_no=report.meeting_no,
        total_students=report.total_students,
        hadir_count=report.hadir_count,
        sakit_count=report.sakit_count,
        tanpa_keterangan_count=report.tanpa_keterangan_count,
        started_at=report.started_at,
        finished_at=report.finished_at,
    )

    return schemas.ReportDetail(summary=summary, absents=absents)
