from django.urls import path
from . import views

urlpatterns = [
    path('', views.mark_attendance_view, name='mark_attendance'),
    path('api/process-attendance/', views.api_process_attendance, name='api_process_attendance'),
    path('api/save-attendance/', views.api_save_attendance, name='api_save_attendance'),
    
    path('register/', views.register_student_view, name='register_student'),
    path('api/check-student-status/', views.api_check_student_status, name='api_check_student_status'),
    path('students/', views.student_list_view, name='student_list'),
    path('students/delete/<int:student_id>/', views.delete_student_view, name='delete_student'),
    path('students/re-encode/<int:student_id>/', views.re_encode_student_view, name='re_encode_student'),
    path('students/sync-all-faces/', views.re_encode_all_students_view, name='sync_all_faces'),
    
    path('attendance-sheet/', views.attendance_sheet_view, name='attendance_sheet'),
    path('attendance-sheet/export/', views.export_master_attendance_excel, name='export_master_attendance_excel'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('session/<int:session_id>/', views.session_detail_view, name='session_detail'),
    path('session/<int:session_id>/export/', views.export_attendance_excel, name='export_attendance_excel'),
    
    path('student-portal/', views.student_portal_view, name='student_portal'),
]
