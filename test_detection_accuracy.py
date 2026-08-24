import os
import cv2
import numpy as np
from PIL import Image
import face_recognition

def test_accurate_detection():
    img_path = r"C:\Users\gaura\.gemini\antigravity\brain\008055dc-196d-47bb-a9d9-b13ef690e208\.user_uploaded\media_1787566168729.jpg"
    pil_img = Image.open(img_path).convert('RGB')
    np_img = np.array(pil_img)
    w, h = pil_img.size
    print(f"Testing on image size: {w}x{h}")

    # Method 1: Standard HOG (upsample=0)
    locs_hog0 = face_recognition.face_locations(np_img, number_of_times_to_upsample=0, model="hog")
    print(f"HOG (upsample 0): {len(locs_hog0)} faces")

    # Method 2: HOG (upsample=1)
    locs_hog1 = face_recognition.face_locations(np_img, number_of_times_to_upsample=1, model="hog")
    print(f"HOG (upsample 1): {len(locs_hog1)} faces")

    # Method 3: Haar Cascade Multi-scale
    gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
    # Contrast enhancement (CLAHE) for dark/shadowed faces in back rows
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced_gray = clahe.apply(gray)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    haar_faces = face_cascade.detectMultiScale(enhanced_gray, scaleFactor=1.08, minNeighbors=4, minSize=(22, 22))
    print(f"Haar Cascade (enhanced): {len(haar_faces)} faces")

if __name__ == '__main__':
    test_accurate_detection()
