from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from ..database import get_db
from .. import models, schemas
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=schemas.Token)
def register_lecturer(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    # Cek apakah email sudah dipakai
    if db.query(models.Lecturer).filter(models.Lecturer.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Simpan dosen baru
    lec = models.Lecturer(
        name=name,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(lec)
    db.commit()
    db.refresh(lec)

    # Generate token setelah registrasi
    token = create_access_token({"sub": str(lec.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
def login(
    form_data: schemas.LecturerLogin,   # pakai schema sendiri
    db: Session = Depends(get_db),
):
    lec = db.query(models.Lecturer).filter(models.Lecturer.email == form_data.email).first()

    if not lec or not verify_password(form_data.password, lec.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token({"sub": str(lec.id)})
    return {"access_token": token, "token_type": "bearer"}
