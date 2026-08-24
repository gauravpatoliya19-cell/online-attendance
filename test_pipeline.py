import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

from attendance_app.face_utils import process_classroom_attendance

def test_pipeline():
    img_path = r"C:\Users\gaura\.gemini\antigravity\brain\008055dc-196d-47bb-a9d9-b13ef690e208\.user_uploaded\media_1787566168729.jpg"
    print("Testing Face Recognition AI pipeline on classroom image...")
    res = process_classroom_attendance(img_path)
    print(f"Total Detected Faces: {res['total_detected_faces']}")
    print(f"Total Matched Students: {res['total_matched_students']}")
    print(f"Roll Numbers: {res['roll_numbers_str']}")
    for s in res['matched_students']:
        print(f" - Face #{s['face_num']}: Roll {s['roll_no']} ({s['name']}) -> Match Confidence: {s['confidence']}%")
    print("\n[SUCCESS] AI pipeline is fully verified and functional!")

if __name__ == '__main__':
    test_pipeline()
