from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import get_current_lecturer

# Router dengan gembok otomatis
router = APIRouter(
    prefix="/report",
    tags=["Report"],
)

@router.get("/{course_id}/{meeting_no}", response_model=schemas.ReportDetail)
def get_report(
    course_id: int,
    meeting_no: int,
    db: Session = Depends(get_db),
    lecturer: models.Lecturer = Security(get_current_lecturer)
):
    course = db.get(models.Course, course_id)
    if not course or course.lecturer_id != lecturer.id:
        raise HTTPException(status_code=404, detail="Course not found or unauthorized")

    report = db.query(models.Report).filter_by(course_id=course_id, meeting_no=meeting_no).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Buat list Pydantic AttendanceRecord
    records = []
    students = db.query(models.Student).join(
        models.CourseEnrollment, models.CourseEnrollment.student_id == models.Student.id
    ).filter(models.CourseEnrollment.course_id == course_id).all()

    for student in students:
        att = db.query(models.Attendance).filter_by(
            student_id=student.id, course_id=course_id, meeting_no=meeting_no
        ).first()
        records.append(
            schemas.AttendanceRecord(
                student_id=student.id,
                student_name=student.name,
                status=att.status.value if att else "tanpa_keterangan",
                timestamp=att.timestamp if att else None
            )
        )

    return schemas.ReportDetail(
        course_id=report.course_id,
        meeting_no=report.meeting_no,
        total_students=report.total_students,
        records=records,
        started_at=report.started_at,
        finished_at=report.finished_at
    )
