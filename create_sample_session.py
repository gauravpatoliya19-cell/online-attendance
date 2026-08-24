import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

from django.utils import timezone
from attendance_app.models import Student, AttendanceSession, AttendanceRecord

def create_sample_session():
    students = Student.objects.all()[:12]
    session = AttendanceSession.objects.create(
        date=timezone.now().date(),
        time=timezone.now().time(),
        faculty_name="Prof. Sharma",
        department_name="FoS",
        course_name="Computer Science",
        degree_name="MCA",
        semester="Semester 3",
        division="22",
        subject="MCA-302 (AI & Machine Learning)",
        total_detected_faces=12,
        total_matched_students=12
    )

    for st in students:
        AttendanceRecord.objects.create(
            session=session,
            student=st,
            status='Present',
            confidence_score=98.5
        )

    print(f"[SUCCESS] Sample session #{session.id} created with {len(students)} student attendance records.")

if __name__ == '__main__':
    create_sample_session()
