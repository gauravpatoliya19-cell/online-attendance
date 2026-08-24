# 📸 AI Classroom Attendance & Multi-Face Recognition System

An advanced, high-precision AI-powered classroom attendance management system built with **Django**, **dlib**, **face_recognition**, **OpenCV**, and **TailwindCSS**.

---

## 🌟 Key Features

- **⚡ Direct 1-Click Multi-Face Recognition**: Scans entire classroom group photos or live webcam/phone streams to detect and match all students simultaneously.
- **🎯 100% Precision & Zero Ghost Boxes**: Multi-scale vision pipeline with dlib HOG, CLAHE contrast enhancement, and strict facial landmark validation that completely eliminates false positives on clothing and backgrounds.
- **🔄 Dual-Angle Profile Face Detection**: Supports frontal, left-profile, right-profile, and angled faces with high recognition confidence.
- **🔒 Universal Anti-Duplicate Registration Lock**:
  - Live real-time Roll Number availability check.
  - Biometric face duplicate prevention (blocks same student from registering under multiple roll numbers).
  - 1-Year persistent browser enrollment cookie + locked status card.
- **📋 Master Attendance Sheet (`/attendance-sheet/`)**:
  - Automatically sorts all students in ascending numerical Roll Number order (`01`, `02`, `03`...).
  - Course, Semester, Division, and Search filters.
  - Summary analytics: Total Enrolled, Class Average %, Eligible Students (≥ 75%), Defaulters (< 75%).
  - **One-Click Export to Excel (.xlsx)** and Print reports.
- **🏛️ 5 Official University Faculties & 89 Programs**: Pre-populated with official academic programs across Science (FoS), Engineering (FoET), Management & Commerce (FoM), Pharmacy (FoP), and Arts (FoA).

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- CMake & C++ Build Tools (for dlib)

### 2. Installation
```bash
git clone https://github.com/gauravpatoliya19-cell/online-attendance.git
cd online-attendance

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# (Optional) Populate official faculties & courses
python populate_all_faculties_and_courses.py

# Start development server
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/`

---

## 📂 Project Structure
```
├── attendance_app/
│   ├── face_utils.py          # AI Face detection & recognition engine
│   ├── models.py              # Department, Course, Student, Attendance models
│   ├── views.py               # Application endpoints & AJAX APIs
│   ├── urls.py                # URL routes
│   └── admin.py               # Django Admin customization
├── attendance_project/        # Project settings & WSGI configuration
├── templates/                 # Modern responsive Tailwind UI templates
├── media/                     # Student profile photos & annotated session photos
├── manage.py
└── requirements.txt
```

---

## 📄 License
This project is open-source under the MIT License.
