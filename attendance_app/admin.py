from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Course, Student, AttendanceSession, AttendanceRecord


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'degree', 'department')
    list_filter = ('department', 'degree')
    search_fields = ('name', 'degree')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('photo_preview', 'roll_no', 'name', 'course', 'semester', 'division', 'is_active', 'has_face_encoding')
    list_filter = ('course', 'semester', 'division', 'is_active')
    search_fields = ('name', 'roll_no', 'email')
    readonly_fields = ('photo_preview_large', 'created_at')

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width:42px; height:42px; object-fit:cover; border-radius:50%; border:2px solid #3b82f6;" />', obj.photo.url)
        return "No Photo"
    photo_preview.short_description = "Photo"

    def photo_preview_large(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-width:200px; border-radius:8px;" />', obj.photo.url)
        return "No Photo"

    def has_face_encoding(self, obj):
        if obj.face_encoding:
            return format_html('<span style="color:green; font-weight:bold;">✔ Registered</span>')
        return format_html('<span style="color:red;">❌ Missing</span>')
    has_face_encoding.short_description = "Face AI"


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0
    readonly_fields = ('student', 'status', 'confidence_score', 'timestamp')


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'time', 'course_name', 'semester', 'division', 'subject', 'total_detected_faces', 'total_matched_students')
    list_filter = ('date', 'course_name', 'semester', 'division')
    search_fields = ('subject', 'faculty_name')
    inlines = [AttendanceRecordInline]


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'confidence_score', 'timestamp')
    list_filter = ('status', 'session__date', 'session__course_name')
    search_fields = ('student__name', 'student__roll_no')
