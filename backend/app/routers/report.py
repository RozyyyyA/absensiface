from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.responses import FileResponse, StreamingResponse
from .. import models, schemas, database
from ..database import get_db
from ..security import get_current_lecturer
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

router = APIRouter(tags=["Report"])

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

@router.get("/{session_id}", response_model=schemas.ReportDetail)
def get_report(
    session_id: int,
    db: Session = Depends(get_db),
    lecturer: models.Lecturer = Security(get_current_lecturer)
):
    session_obj = db.get(models.Session, session_id)
    if not session_obj or session_obj.course.lecturer_id != lecturer.id:
        raise HTTPException(status_code=404, detail="Session not found or unauthorized")

    report = _recount_report(db, session_id)

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

    students = db.query(models.Student).join(
        models.CourseEnrollment, models.CourseEnrollment.student_id == models.Student.id
    ).filter(models.CourseEnrollment.course_id == session_obj.course_id).all()

    absents = []
    for student in students:
        att = db.query(models.Attendance).filter_by(
            student_id=student.id, session_id=session_id
        ).first()
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

@router.get("/{session_id}/pdf")
def get_report_pdf(session_id: int, db: Session = Depends(database.get_db)):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    attendance_records = db.query(models.Attendance).filter(
        models.Attendance.session_id == session_id
    ).all()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Laporan Absensi - Session {session_id}", styles["Title"]))
    elements.append(Spacer(1, 12))

    data = [["NIM", "Nama", "Status"]]
    for record in attendance_records:
        student = db.query(models.Student).filter(models.Student.id == record.student_id).first()
        status_str = getattr(record.status, "value", str(record.status))
        data.append([student.nim, student.name, status_str])

    table = Table(data, colWidths=[100, 200, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)  # reset ke awal stream

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_session_{session_id}.pdf"}
    )