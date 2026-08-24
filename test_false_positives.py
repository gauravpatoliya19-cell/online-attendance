import os
import cv2
import numpy as np
from PIL import Image
import face_recognition

def validate_face_box(np_image, box):
    """
    Checks if candidate bounding box contains actual facial landmarks / features.
    box: (top, right, bottom, left)
    """
    top, right, bottom, left = box
    h, w = np_image.shape[:2]
    
    # Add margin
    pad_w = int((right - left) * 0.2)
    pad_h = int((bottom - top) * 0.2)
    c_top = max(0, top - pad_h)
    c_bottom = min(h, bottom + pad_h)
    c_left = max(0, left - pad_w)
    c_right = min(w, right + pad_w)

    crop = np_image[c_top:c_bottom, c_left:c_right]
    if crop.shape[0] < 15 or crop.shape[1] < 15:
        return False

    # Check for facial landmarks
    landmarks = face_recognition.face_landmarks(crop)
    if landmarks and len(landmarks) > 0:
        lm = landmarks[0]
        # Must have at least eyes or nose
        if ('left_eye' in lm or 'right_eye' in lm) and ('nose_bridge' in lm or 'top_lip' in lm or 'bottom_lip' in lm):
            return True

    # Check for encoding
    encs = face_recognition.face_encodings(crop)
    if encs and len(encs) > 0:
        return True

    return False

def test_validation():
    img_path = r"C:\Users\gaura\.gemini\antigravity\brain\008055dc-196d-47bb-a9d9-b13ef690e208\.user_uploaded\media_1787566168729.jpg"
    pil_img = Image.open(img_path).convert('RGB')
    np_img = np.array(pil_img)
    locs = face_recognition.face_locations(np_img, number_of_times_to_upsample=1, model="hog")
    print(f"Validated true faces count in classroom: {len(locs)}")

if __name__ == '__main__':
    test_validation()
