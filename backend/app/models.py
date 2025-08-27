from datetime import datetime
import enum
from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Enum
)
from sqlalchemy.orm import relationship
from .database import Base

# =========================
# Status Absensi
# =========================
class AttendanceStatus(str, enum.Enum):
    hadir = "hadir"
    sakit = "sakit"
    tanpa_keterangan = "tanpa_keterangan"

# =========================
# Dosen
# =========================
class Lecturer(Base):
    __tablename__ = "lecturers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    courses = relationship("Course", back_populates="lecturer", cascade="all, delete")

# =========================
# Mahasiswa
# =========================
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    nim = Column(String, unique=True, index=True, nullable=False)
    face_id = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)

    enrollments = relationship("CourseEnrollment", back_populates="student", cascade="all, delete")
    attendances = relationship("Attendance", back_populates="student")

# =========================
# Mata Kuliah
# =========================
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    code = Column(String, unique=True, nullable=False) 
    lecturer_id = Column(Integer, ForeignKey("lecturers.id"))

    lecturer = relationship("Lecturer", back_populates="courses")
    # attendances = relationship("Attendance", back_populates="course")
    reports = relationship("Report", back_populates="course")
    enrollments = relationship("CourseEnrollment", back_populates="course")
    sessions = relationship("Session", back_populates="course")

# =========================
# Relasi Mahasiswa ↔ Mata Kuliah
# =========================
class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))

    course = relationship("Course", back_populates="enrollments")
    student = relationship("Student", back_populates="enrollments")

# =========================
# Sesi per Pertemuan
# =========================
class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    meeting_no = Column(Integer)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    course = relationship("Course", back_populates="sessions")
    attendances = relationship("Attendance", back_populates="session")
    reports = relationship("Report", back_populates="session")

# =========================
# Absensi
# =========================
class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.hadir)
    confidence = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="attendances")
    student = relationship("Student", back_populates="attendances")
    # course = relationship("Course", back_populates="attendances", viewonly=True)

# =========================
# Laporan
# =========================
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False) 
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    total_students = Column(Integer, default=0)
    hadir_count = Column(Integer, default=0)
    sakit_count = Column(Integer, default=0)
    tanpa_keterangan_count = Column(Integer, default=0)

    course = relationship("Course", back_populates="reports")
    session = relationship("Session", back_populates="reports")




