import cv2
import joblib
import numpy as np
from ultralytics import YOLO
from skimage.feature import hog
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load YOLOv5su
yolo_model = YOLO(os.path.join(BASE_DIR, "model_files", "yolov5su.pt"))

# Load SVM
svm_model = joblib.load(os.path.join(BASE_DIR, "model_files", "svm_face_recognition.pkl"))

# Ukuran seragam untuk wajah
FACE_SIZE = (128, 128)  # crop wajah
HOG_SIZE = (64, 64)     # resize sebelum HOG


def detect_face(image):
    """
    Deteksi wajah dengan YOLO, lalu pilih wajah terbesar.
    Terapkan crop sesuai pipeline training: ambil 60% bagian atas bounding box.
    """
    results = yolo_model.predict(image, verbose=False)
    faces = []

    for result in results:
        for box in result.boxes.xyxy.cpu().numpy():
            x1, y1, x2, y2 = map(int, box[:4])
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
            if x2 > x1 and y2 > y1:
                faces.append((x1, y1, x2, y2))

    if not faces:
        return None

    # pilih wajah terbesar
    x1, y1, x2, y2 = max(faces, key=lambda f: (f[2] - f[0]) * (f[3] - f[1]))

    # crop hanya 60% bagian atas bbox
    face_height = y2 - y1
    y2 = y1 + int(face_height * 0.6)

    return (x1, y1, x2, y2)


def extract_hog_features(image):
    """
    Ekstrak fitur HOG dari wajah.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, HOG_SIZE, interpolation=cv2.INTER_CUBIC)
    features = hog(
        resized,
        pixels_per_cell=(8, 8),
        cells_per_block=(2, 2),
        orientations=9,
        visualize=False,
        block_norm="L2-Hys"
    )
    return features


def recognize_face(image):
    """
    Return: (student_name:str, probability:float) atau (None, None)
    """
    face = detect_face(image)
    if face is None:
        return None, None

    x1, y1, x2, y2 = face
    face_crop = image[y1:y2, x1:x2]

    if face_crop.shape[0] < 10 or face_crop.shape[1] < 10:
        return None, None

    # resize sesuai pipeline training
    resized_face = cv2.resize(face_crop, FACE_SIZE, interpolation=cv2.INTER_CUBIC)
    hog_features = extract_hog_features(resized_face).reshape(1, -1)

    pred = svm_model.predict(hog_features)[0]  # nama mahasiswa
    prob = svm_model.predict_proba(hog_features).max()

    return str(pred), float(prob)


# Alias untuk attendance.py
def recognize_bgr(frame_bgr):
    return recognize_face(frame_bgr)
