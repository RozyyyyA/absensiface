from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from enum import Enum

# ----------------------
# Auth
# ----------------------
class LecturerCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class LecturerLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ----------------------
# Students
# ----------------------
class StudentBase(BaseModel):
    id: int
    name: str
    nim: str

    class Config:
        orm_mode = True

class StudentCreate(BaseModel):
    name: str
    nim: str

class StudentUpdate(BaseModel):
    name: str
    nim: str

# ----------------------
# Courses
# ----------------------

class CourseBase(BaseModel):
    id: int
    name: str
    code: str
    lecturer_id: int

    class Config:
        orm_mode = True

class CourseCreate(BaseModel):
    name: str
    code: str
    lecturer_id: int

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    lecturer_id: Optional[int] = None

# ----------------------
# Attendance
# ----------------------
class AttendanceMarkResponse(BaseModel):
    status: str
    student_id: Optional[int] = None
    confidence: Optional[float] = None

class AttendanceStatus(str, Enum):
    hadir = "hadir"
    sakit = "sakit"
    tanpa_keterangan = "tanpa_keterangan"

class AttendanceStatusUpdate(BaseModel):
    student_id: int
    course_id: int
    meeting_no: int
    status: AttendanceStatus

class AttendanceRecord(BaseModel):
    student_id: int
    student_name: str
    status: str
    timestamp: Optional[datetime]

    class Config:
        from_attributes = True

# ----------------------
# Report
# ----------------------
class ReportSummary(BaseModel):
    course_id: int
    meeting_no: int
    total_students: int
    hadir_count: int
    sakit_count: int
    tanpa_keterangan_count: int
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

class AbsentItem(BaseModel):
    student_id: int
    name: str
    nim: str
    status: str

class ReportDetail(BaseModel):
    summary: ReportSummary
    absents: List[AbsentItem]

# ----------------------
# Session Schemas
# ----------------------
class SessionBase(BaseModel):
    course_id: int
    meeting_no: int

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: int
    started_at: datetime
    finished_at: Optional[datetime]

    class Config:
        orm_mode = True

# =========================
# Enrollment Schemas
# =========================
class EnrollmentCreateMultiple(BaseModel):
    course_id: int
    student_ids: List[int]

class EnrollmentResponse(BaseModel):
    course_id: int
    student_id: int

    class Config:
        orm_mode = True