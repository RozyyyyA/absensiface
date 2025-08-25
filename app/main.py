from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import auth, attendance, report, session

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Absensi Wajah – FastAPI")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Bisa diganti dengan list domain frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router)
app.include_router(attendance.router)
app.include_router(report.router)
app.include_router(session.router)  

# Root endpoint
@app.get("/")
def root():
    return {"message": "Absensi Face Recognition API Ready 🚀"}
