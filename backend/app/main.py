# backend/app/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db
from .routers import auth, courses, enrollments, session, student, attendance, report

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Absensi Face Recognition API",
    description="API untuk sistem absensi dengan autentikasi JWT",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(enrollments.router, prefix="/enrollments", tags=["Enrollments"])
app.include_router(session.router, prefix="/session", tags=["Session"])
app.include_router(student.router, prefix="/student", tags=["Student"])
app.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
app.include_router(report.router, prefix="/report", tags=["Report"])


# Custom schema untuk JWT di Swagger
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Absensi Face Recognition API",
        version="1.0.0",
        description="API untuk sistem absensi dengan autentikasi JWT",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.get("/")
def root():
    return {"message": "API Absensi Face Recognition aktif"}
