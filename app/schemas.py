from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, EmailStr
from enum import Enum

# Auth
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

# Students / Courses
class StudentBase(BaseModel):
    id: int
    name: str
    nim: str

    class Config:
        orm_mode = True

class CourseBase(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        orm_mode = True

# Attendance
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

class SessionStart(BaseModel):
    course_id: int
    meeting_no: int

class SessionFinish(BaseModel):
    course_id: int
    meeting_no: int

# Report
class ReportSummary(BaseModel):
    course_id: int
    meeting_no: int
    total_students: int
    hadir_count: int
    sakit_count: int
    tanpa_keterangan_count: int
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

class AttendanceRecord(BaseModel):
    student_id: int
    student_name: str
    status: str
    timestamp: Optional[datetime]

    class Config:
        orm_mode = True

class ReportDetail(BaseModel):
    course_id: int
    meeting_no: int
    total_students: int
    records: List[AttendanceRecord]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

    class Config:
        orm_mode = True

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


# ----------------------
# Attendance Schemas
# ----------------------
class AttendanceBase(BaseModel):
    session_id: int
    student_id: int
    status: AttendanceStatus

class AttendanceResponse(AttendanceBase):
    id: int
    confidence: Optional[float]

    class Config:
        orm_mode = True