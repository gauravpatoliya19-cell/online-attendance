import os
import cv2
import numpy as np
from PIL import Image
import face_recognition

def calculate_iou(boxA, boxB):
    # box format: (top, right, bottom, left)
    xA = max(boxA[3], boxB[3])
    yA = max(boxA[0], boxB[0])
    xB = min(boxA[1], boxB[1])
    yB = min(boxA[2], boxB[2])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[1] - boxA[3]) * (boxA[2] - boxA[0])
    boxBArea = (boxB[1] - boxB[3]) * (boxB[2] - boxB[0])

    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
    return iou

def ensemble_detect_faces(np_image):
    h, w = np_image.shape[:2]
    all_boxes = []

    # 1. dlib / face_recognition HOG with upsample=1
    hog_locations = face_recognition.face_locations(np_image, number_of_times_to_upsample=1, model="hog")
    for loc in hog_locations:
        all_boxes.append((loc[0], loc[1], loc[2], loc[3], 1.0)) # (top, right, bottom, left, score)

    # 2. OpenCV Multi-Scale Detector with CLAHE Contrast
    gray = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    haar_detections = face_cascade.detectMultiScale(
        enhanced_gray,
        scaleFactor=1.06,
        minNeighbors=4,
        minSize=(22, 22),
        maxSize=(int(w * 0.5), int(h * 0.5))
    )

    for (x, y, fw, fh) in haar_detections:
        top = max(0, y)
        right = min(w, x + fw)
        bottom = min(h, y + fh)
        left = max(0, x)
        all_boxes.append((top, right, bottom, left, 0.8))

    # 3. Non-Maximum Suppression (NMS)
    # Sort by confidence / area
    all_boxes.sort(key=lambda b: (b[4], (b[2]-b[0]) * (b[1]-b[3])), reverse=True)

    kept_boxes = []
    for b in all_boxes:
        overlap = False
        for k in kept_boxes:
            if calculate_iou(b[:4], k[:4]) > 0.30:
                overlap = True
                break
        if not overlap:
            kept_boxes.append(b)

    # Convert back to clean (top, right, bottom, left)
    final_locations = [(b[0], b[1], b[2], b[3]) for b in kept_boxes]

    # Spatial sort: top to bottom, left to right
    final_locations.sort(key=lambda loc: (loc[0] // 60, loc[3]))
    return final_locations

def run_test():
    img_path = r"C:\Users\gaura\.gemini\antigravity\brain\008055dc-196d-47bb-a9d9-b13ef690e208\.user_uploaded\media_1787566168729.jpg"
    pil_img = Image.open(img_path).convert('RGB')
    np_img = np.array(pil_img)
    locs = ensemble_detect_faces(np_img)
    print(f"Total High-Accuracy Ensemble Detected Faces: {len(locs)}")
    for i, l in enumerate(locs, 1):
        print(f" - Face #{i}: Box (top={l[0]}, right={l[1]}, bottom={l[2]}, left={l[3]}), Width={l[1]-l[3]}, Height={l[2]-l[0]}")

if __name__ == '__main__':
    run_test()
