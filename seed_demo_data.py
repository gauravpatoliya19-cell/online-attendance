import os
import django
import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

from django.contrib.auth.models import User
from attendance_app.models import Department, Course, Student

def seed():
    # 1. Create Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@university.edu.in', 'admin123')
        print("[OK] Superuser 'admin' created with password 'admin123'")

    # 2. Create Departments
    fos, _ = Department.objects.get_or_create(name='Faculty of Science', code='FoS')
    foet, _ = Department.objects.get_or_create(name='Faculty of Engg & Tech', code='FoET')
    fom, _ = Department.objects.get_or_create(name='Faculty of Management', code='FoM')

    # 3. Create Courses
    mca, _ = Course.objects.get_or_create(department=fos, name='Computer Science', degree='MCA')
    bca, _ = Course.objects.get_or_create(department=fos, name='Computer Applications', degree='BCA')
    btech, _ = Course.objects.get_or_create(department=foet, name='Computer Science', degree='B.Tech')
    print("[OK] Departments and Courses created.")

    # 4. Sample Students from Screenshot
    sample_students = [
        {"roll_no": "3", "name": "Raghavria Pavan Hiteshkumar", "email": "15618225003@university.edu.in"},
        {"roll_no": "5", "name": "Bharad Parthkumar Harshadbhai", "email": "15618225005@university.edu.in"},
        {"roll_no": "10", "name": "Dahelesh Samirbin Farukbhai", "email": "15618225010@university.edu.in"},
        {"roll_no": "15", "name": "Dhruv Brijesh Ashokbhai", "email": "15618225015@university.edu.in"},
        {"roll_no": "16", "name": "Fofandi Yash Denishbhai", "email": "15618225016@university.edu.in"},
        {"roll_no": "20", "name": "Goswami Manavpuri Dharmendrapari", "email": "15618225020@university.edu.in"},
        {"roll_no": "23", "name": "Jethava Mihir Maheshbhai", "email": "15618225023@university.edu.in"},
        {"roll_no": "24", "name": "Joshi Rohan Pareshbhai", "email": "15618225024@university.edu.in"},
        {"roll_no": "25", "name": "Kanani Harsh Pankajkumar", "email": "15618225025@university.edu.in"},
        {"roll_no": "29", "name": "Kotak Yash Dipak", "email": "15618225029@university.edu.in"},
        {"roll_no": "37", "name": "Papaniya Deep Kanubhai", "email": "15618225037@university.edu.in"},
        {"roll_no": "40", "name": "Rachhadiya Vasu Ashokbhai", "email": "15618225040@university.edu.in"},
        {"roll_no": "43", "name": "Ratnotar Jaydeep Vasantbhai", "email": "15618225043@university.edu.in"},
        {"roll_no": "44", "name": "Sanghani Krupesh Girishbhai", "email": "15618225044@university.edu.in"},
        {"roll_no": "50", "name": "Zankat Krunal Devabhai", "email": "15618225050@university.edu.in"},
    ]

    for s in sample_students:
        student, created = Student.objects.get_or_create(
            roll_no=s["roll_no"],
            defaults={
                "name": s["name"],
                "email": s["email"],
                "department": fos,
                "course": mca,
                "semester": "Semester 3",
                "division": "22",
            }
        )
        if created:
            print(f"[OK] Student {s['name']} (Roll: {s['roll_no']}) registered.")

    print("\nSeed data populated successfully!")

if __name__ == '__main__':
    seed()
