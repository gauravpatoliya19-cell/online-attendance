import json
from django.db import models
from django.utils import timezone


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. FoS (Faculty of Science)")

    def __str__(self):
        return f"{self.code} - {self.name}" if self.code else self.name

    class Meta:
        ordering = ['name']


class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=100, help_text="e.g. Computer Science")
    degree = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. MCA, BCA, B.Tech")

    def __str__(self):
        return f"{self.name} ({self.degree})" if self.degree else self.name

    class Meta:
        ordering = ['name']


class Student(models.Model):
    name = models.CharField(max_length=150)
    roll_no = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    semester = models.CharField(max_length=50, default="Semester 3")
    division = models.CharField(max_length=50, default="22")
    
    photo = models.ImageField(upload_to='students/profile_photos/')
    # Face encoding stored as JSON string (128-dimensional list of floats)
    face_encoding = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.roll_no} - {self.name}"

    def get_face_encoding_list(self):
        if self.face_encoding:
            try:
                return json.loads(self.face_encoding)
            except Exception:
                return None
        return None

    def set_face_encoding_list(self, encoding_array):
        if encoding_array is not None:
            self.face_encoding = json.dumps(list(encoding_array))
        else:
            self.face_encoding = None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # If face_encoding is missing and photo exists, automatically generate it
        if not self.face_encoding and self.photo:
            try:
                import os
                from .face_utils import extract_face_encoding
                if hasattr(self.photo, 'path') and os.path.exists(self.photo.path):
                    enc, err = extract_face_encoding(self.photo.path)
                    if enc is not None:
                        self.set_face_encoding_list(enc)
                        super().save(update_fields=['face_encoding'])
            except Exception as e:
                pass

    class Meta:
        ordering = ['roll_no']


class AttendanceSession(models.Model):
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    faculty_name = models.CharField(max_length=100, default="Faculty")
    
    department_name = models.CharField(max_length=100, blank=True, default="FoS")
    course_name = models.CharField(max_length=100, blank=True, default="Computer Science")
    degree_name = models.CharField(max_length=50, blank=True, default="MCA")
    semester = models.CharField(max_length=50, default="Semester 3")
    division = models.CharField(max_length=50, default="22")
    subject = models.CharField(max_length=100, blank=True, default="AI & Machine Learning")
    
    uploaded_image = models.ImageField(upload_to='attendance_sessions/original/', blank=True, null=True)
    annotated_image = models.ImageField(upload_to='attendance_sessions/annotated/', blank=True, null=True)
    
    total_detected_faces = models.IntegerField(default=0)
    total_matched_students = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session #{self.id} - {self.course_name} ({self.semester} Div {self.division}) - {self.date}"

    class Meta:
        ordering = ['-date', '-time']


class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    )
    
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Present')
    confidence_score = models.FloatField(default=0.0, help_text="Recognition confidence percentage")
    detected_thumbnail = models.TextField(blank=True, null=True, help_text="Base64 or URL of detected face crop")
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.roll_no} ({self.student.name}) - {self.status} ({self.confidence_score}%)"

    class Meta:
        ordering = ['student__roll_no']
        unique_together = ('session', 'student')
