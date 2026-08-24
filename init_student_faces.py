import os
import django
import numpy as np
from PIL import Image
import face_recognition

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

from attendance_app.models import Student

def extract_and_assign_faces():
    img_path = r"C:\Users\gaura\.gemini\antigravity\brain\008055dc-196d-47bb-a9d9-b13ef690e208\.user_uploaded\media_1787566168729.jpg"
    if not os.path.exists(img_path):
        print(f"Image not found at {img_path}")
        return

    pil_img = Image.open(img_path).convert('RGB')
    np_img = np.array(pil_img)
    w, h = pil_img.size
    print(f"Loaded image size: {w}x{h}")

    # Detect faces in this image
    locations = face_recognition.face_locations(np_img, model="hog")
    print(f"Detected {len(locations)} faces in the reference classroom image.")

    # Sort locations top to bottom, left to right
    locations.sort(key=lambda loc: (loc[0] // 80, loc[3]))

    encodings = face_recognition.face_encodings(np_img, known_face_locations=locations)

    students = list(Student.objects.all().order_by('id'))
    print(f"Found {len(students)} students in database.")

    media_dir = os.path.join(os.getcwd(), 'media', 'students', 'profile_photos')
    os.makedirs(media_dir, exist_ok=True)

    for idx, (loc, enc) in enumerate(zip(locations, encodings)):
        if idx < len(students):
            st = students[idx]
            top, right, bottom, left = loc
            pad_x = int((right - left) * 0.3)
            pad_y = int((bottom - top) * 0.3)
            crop_box = (max(0, left - pad_x), max(0, top - pad_y), min(w, right + pad_x), min(h, bottom + pad_y))
            face_crop = pil_img.crop(crop_box)

            photo_filename = f"student_{st.roll_no}.jpg"
            photo_rel_path = f"students/profile_photos/{photo_filename}"
            photo_abs_path = os.path.join(media_dir, photo_filename)
            face_crop.save(photo_abs_path, "JPEG", quality=90)

            st.photo.name = photo_rel_path
            st.set_face_encoding_list(enc)
            st.save()
            print(f"[OK] Assigned face #{idx+1} to Student: {st.name} (Roll: {st.roll_no})")

    print("\nAll student face profiles initialized and linked successfully!")

if __name__ == '__main__':
    extract_and_assign_faces()
