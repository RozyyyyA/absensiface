import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, Depends, status, Security
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .database import get_db
from . import models, database

# JWT Config
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretjwtkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")  # tanpa leading slash

def get_current_lecturer(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        lecturer_id: int = payload.get("sub")
        if lecturer_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    lecturer = db.query(models.Lecturer).filter(models.Lecturer.id == lecturer_id).first()
    if lecturer is None:
        raise credentials_exception
    return lecturer

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency to get current lecturer from JWT
def get_current_lecturer(
    db: Session = Depends(get_db),
    token: str = Security(oauth2_scheme)   # ⬅️ pakai Security, bukan Depends
) -> models.Lecturer:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        lecturer_id = payload.get("sub")
        if lecturer_id is None:
            raise credentials_exception
        lecturer_id = int(lecturer_id)
    except (JWTError, ValueError):
        raise credentials_exception

    lecturer = db.get(models.Lecturer, lecturer_id)
    if lecturer is None:
        raise credentials_exception
    return lecturer
