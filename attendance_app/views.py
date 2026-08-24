import os
import io
import json
import base64
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
import pandas as pd

from .models import Department, Course, Student, AttendanceSession, AttendanceRecord
from .face_utils import extract_face_encoding, process_classroom_attendance


def mark_attendance_view(request):
    """
    PART 2: Faculty Attendance Marking Interface
    """
    faculties = Department.objects.prefetch_related('courses').all()
    faculties_data = []
    for f in faculties:
        courses_list = [{"id": c.id, "name": c.name, "degree": c.degree or c.name} for c in f.courses.all()]
        faculties_data.append({
            "code": f.code or f.name,
            "name": f.name,
            "id": f.id,
            "courses": courses_list
        })
    
    semesters = ["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6", "Semester 7", "Semester 8"]
    divisions = ["21", "22", "23", "24", "A", "B", "C", "D"]
    
    context = {
        'departments': faculties,
        'courses': Course.objects.all(),
        'faculties_json': json.dumps(faculties_data),
        'semesters': semesters,
        'divisions': divisions,
        'portal_type': 'faculty',
    }
    return render(request, 'attendance_app/mark_attendance.html', context)


@csrf_exempt
def api_process_attendance(request):
    """
    AJAX endpoint for AI Face detection and recognition on uploaded/captured group photo.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)

    try:
        image_data = None
        if 'image' in request.FILES:
            image_data = request.FILES['image']
        elif 'image_b64' in request.POST and request.POST['image_b64']:
            image_data = request.POST['image_b64']
        else:
            return JsonResponse({'status': 'error', 'message': 'No image provided. Please upload or capture an image.'}, status=400)

        dept_code = request.POST.get('department', '')
        course_id = request.POST.get('course', '')
        semester = request.POST.get('semester', '')
        division = request.POST.get('division', '')

        # Process the image
        results = process_classroom_attendance(
            image_input=image_data,
            department_code=dept_code if dept_code else None,
            course_id=course_id if course_id else None,
            semester=semester if semester else None,
            division=division if division else None
        )

        return JsonResponse({
            'status': 'success',
            'data': results
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def api_save_attendance(request):
    """
    Persists marked attendance into the database.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        
        dept_name = data.get('department_name', 'FoS')
        course_name = data.get('course_name', 'Computer Science')
        degree_name = data.get('degree_name', 'MCA')
        semester = data.get('semester', 'Semester 3')
        division = data.get('division', '22')
        subject = data.get('subject', 'AI & Machine Learning')
        faculty_name = data.get('faculty_name', 'Admin / Faculty')
        
        total_detected = data.get('total_detected_faces', 0)
        total_matched = data.get('total_matched_students', 0)
        
        matched_students = data.get('matched_students', [])
        annotated_image_b64 = data.get('annotated_image_b64', '')
        
        # Create session
        session = AttendanceSession(
            department_name=dept_name,
            course_name=course_name,
            degree_name=degree_name,
            semester=semester,
            division=division,
            subject=subject,
            faculty_name=faculty_name,
            total_detected_faces=total_detected,
            total_matched_students=total_matched,
            date=timezone.now().date(),
            time=timezone.now().time()
        )
        
        # Save annotated image if provided
        if annotated_image_b64 and 'base64,' in annotated_image_b64:
            format_str, imgstr = annotated_image_b64.split(';base64,')
            ext = format_str.split('/')[-1]
            file_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            session.annotated_image.save(file_name, ContentFile(base64.b64decode(imgstr)), save=False)
            
        session.save()
        
        # Create Attendance Records
        records_created = 0
        for student_data in matched_students:
            student_id = student_data.get('student_id')
            confidence = student_data.get('confidence', 0.0)
            thumb_b64 = student_data.get('detected_thumbnail_b64', '')
            
            try:
                student = Student.objects.get(id=student_id)
                AttendanceRecord.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={
                        'status': 'Present',
                        'confidence_score': confidence,
                        'detected_thumbnail': thumb_b64,
                        'timestamp': timezone.now()
                    }
                )
                records_created += 1
            except Student.DoesNotExist:
                continue

        return JsonResponse({
            'status': 'success',
            'message': f'Attendance for {records_created} students saved successfully!',
            'session_id': session.id
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def api_check_student_status(request):
    """
    Real-time AJAX endpoint to check if a roll number is already registered across any browser/device.
    """
    roll_no = request.GET.get('roll_no', '').strip()
    if not roll_no:
        return JsonResponse({'is_registered': False})

    student = Student.objects.filter(roll_no__iexact=roll_no).first()
    if student:
        return JsonResponse({
            'is_registered': True,
            'name': student.name,
            'roll_no': student.roll_no,
            'department': student.department.name if student.department else '',
            'course': student.course.degree if student.course else '',
            'semester': student.semester,
            'division': student.division,
            'created_at': student.created_at.strftime('%d-%m-%Y'),
        })
    return JsonResponse({'is_registered': False})


def register_student_view(request):
    """
    Universal Locked One-Time Student Registration.
    Guaranteed single registration per student across ANY browser, device, incognito window:
    1. Server-side Roll Number uniqueness lock.
    2. AI Biometric Face Duplicate Protection (blocks registering same face under multiple roll numbers).
    3. Persistent 1-Year Cookie + LocalStorage + Live AJAX status checking.
    """
    departments = Department.objects.all()
    courses = Course.objects.all()

    # Check for persistent cookie from previous registration
    cookie_roll = request.COOKIES.get('enrolled_student_roll', '').strip()
    existing_cookie_student = None
    if cookie_roll:
        existing_cookie_student = Student.objects.filter(roll_no__iexact=cookie_roll).first()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        roll_no = request.POST.get('roll_no', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        faculty_input = request.POST.get('faculty', '').strip() or request.POST.get('faculty_code', '').strip()
        dept_input = request.POST.get('department', '').strip()
        course_input = request.POST.get('course', '').strip()
        semester = request.POST.get('semester', 'Semester 3').strip() or 'Semester 3'
        division = request.POST.get('division', '22').strip() or '22'

        photo_file = request.FILES.get('photo')
        captured_image_b64 = request.POST.get('captured_image_data')

        if not name or not roll_no:
            messages.error(request, 'Please enter both Name and Roll Number.')
            return redirect('register_student')

        # 1. SERVER-SIDE ROLL NUMBER DUPLICATE CHECK
        existing_student = Student.objects.filter(roll_no__iexact=roll_no).first()
        if existing_student:
            messages.error(request, f'🔒 Roll Number "{roll_no}" is ALREADY REGISTERED as "{existing_student.name}". One student is allowed only one registration.')
            return redirect('register_student')

        # Determine image input
        image_input = None
        if photo_file:
            image_input = photo_file
        elif captured_image_b64 and 'base64,' in captured_image_b64:
            image_input = captured_image_b64
        else:
            messages.error(request, 'Please upload a photo or capture one using your camera.')
            return redirect('register_student')

        # Extract face encoding
        encoding, err = extract_face_encoding(image_input)
        if err or encoding is None:
            messages.error(request, f'Face validation failed: {err or "No face detected"}. Please ensure clear frontal lighting.')
            return redirect('register_student')

        # 2. AI BIOMETRIC DUPLICATE FACE CHECK (Prevents same person from registering twice with different roll numbers)
        all_registered_students = Student.objects.filter(is_active=True).exclude(face_encoding__isnull=True).exclude(face_encoding__exact='')
        for ex in all_registered_students:
            ex_enc = ex.get_face_encoding_list()
            if ex_enc is not None:
                matches = face_recognition.compare_faces([np.array(ex_enc)], np.array(encoding), tolerance=0.48)
                if matches and matches[0]:
                    messages.error(request, f'🔒 Biometric Duplicate Blocked: Your face is ALREADY REGISTERED in the system as student "{ex.name}" (Roll No: {ex.roll_no}). Re-registration is strictly locked.')
                    return redirect('register_student')

        # Resolve or create Department from user text input
        dept_obj = None
        if faculty_input:
            dept_obj = Department.objects.filter(Q(code__iexact=faculty_input) | Q(name__iexact=faculty_input) | Q(name__icontains=faculty_input)).first()
            if not dept_obj:
                dept_obj = Department.objects.create(name=faculty_input, code=faculty_input[:20].upper())
        elif dept_input:
            dept_obj = Department.objects.filter(name__icontains=dept_input).first()

        # Resolve or create Course from user text input
        course_obj = None
        if course_input:
            if course_input.isdigit():
                course_obj = Course.objects.filter(id=int(course_input)).first()
            if not course_obj:
                course_obj = Course.objects.filter(Q(degree__iexact=course_input) | Q(name__iexact=course_input) | Q(degree__icontains=course_input)).first()
            if not course_obj:
                course_obj = Course.objects.create(
                    department=dept_obj or Department.objects.first(),
                    name=dept_input or course_input,
                    degree=course_input
                )

        student = Student(
            name=name,
            roll_no=roll_no,
            email=email,
            phone=phone,
            semester=semester,
            division=division,
            department=dept_obj,
            course=course_obj
        )

        # Save photo file
        if photo_file:
            student.photo = photo_file
        elif captured_image_b64:
            format_str, imgstr = captured_image_b64.split(';base64,')
            ext = format_str.split('/')[-1] if 'image/' in format_str else 'jpg'
            file_name = f"student_{roll_no}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
            student.photo.save(file_name, ContentFile(base64.b64decode(imgstr)), save=False)

        # Store 128-d face encoding
        student.set_face_encoding_list(encoding)
        student.save()

        # Render clean success card on student registration portal & set persistent cookie
        context = {
            'registered_student': student,
            'is_standalone_registration': True,
        }
        response = render(request, 'attendance_app/register_success.html', context)
        # Set 1-year persistent cookie
        response.set_cookie('enrolled_student_roll', student.roll_no, max_age=31536000, httponly=False)
        return response

    faculties = Department.objects.prefetch_related('courses').all()
    faculties_data = []
    for f in faculties:
        courses_list = [{"id": c.id, "name": c.name, "degree": c.degree or c.name} for c in f.courses.all()]
        faculties_data.append({
            "code": f.code or f.name,
            "name": f.name,
            "id": f.id,
            "courses": courses_list
        })

    semesters = ["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6", "Semester 7", "Semester 8"]
    divisions = ["21", "22", "23", "24", "A", "B", "C", "D"]

    context = {
        'departments': faculties,
        'courses': Course.objects.all(),
        'faculties_json': json.dumps(faculties_data),
        'semesters': semesters,
        'divisions': divisions,
        'is_standalone_registration': True,
        'existing_cookie_student': existing_cookie_student,
    }
    return render(request, 'attendance_app/register_student.html', context)


def student_list_view(request):
    """
    List of registered students with search, filters, and face profile view.
    """
    students = Student.objects.all().select_related('department', 'course')
    search_query = request.GET.get('search', '')
    course_filter = request.GET.get('course', '')
    semester_filter = request.GET.get('semester', '')
    division_filter = request.GET.get('division', '')

    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) | Q(roll_no__icontains=search_query) | Q(email__icontains=search_query)
        )
    if course_filter:
        students = students.filter(course_id=course_filter)
    if semester_filter:
        students = students.filter(semester__iexact=semester_filter)
    if division_filter:
        students = students.filter(division__iexact=division_filter)

    courses = Course.objects.all()
    context = {
        'students': students,
        'courses': courses,
        'search_query': search_query,
        'selected_course': course_filter,
        'selected_sem': semester_filter,
        'selected_div': division_filter,
        'portal_type': 'faculty',
    }
    return render(request, 'attendance_app/student_list.html', context)


def delete_student_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        name = student.name
        student.delete()
        messages.success(request, f'Student "{name}" has been deleted.')
    return redirect('student_list')


def re_encode_student_view(request, student_id):
    """
    Manually trigger face extraction/encoding for a student with a photo.
    """
    student = get_object_or_404(Student, id=student_id)
    if not student.photo:
        messages.error(request, f'Student "{student.name}" has no photo uploaded.')
        return redirect('student_list')

    try:
        encoding, err = extract_face_encoding(student.photo.path)
        if err or encoding is None:
            messages.error(request, f'Face detection failed for "{student.name}": {err or "No clear face found in photo."}')
        else:
            student.set_face_encoding_list(encoding)
            student.save()
            messages.success(request, f'🎉 Face AI generated successfully for "{student.name}" (Roll: {student.roll_no})!')
    except Exception as e:
        messages.error(request, f'Error generating Face AI: {str(e)}')

    return redirect('student_list')


def re_encode_all_students_view(request):
    """
    Batch process all students missing face encodings.
    """
    students_missing = Student.objects.filter(is_active=True).exclude(photo='').filter(Q(face_encoding__isnull=True) | Q(face_encoding__exact=''))
    count = 0
    errors = 0

    for st in students_missing:
        if st.photo and os.path.exists(st.photo.path):
            enc, err = extract_face_encoding(st.photo.path)
            if enc is not None:
                st.set_face_encoding_list(enc)
                st.save()
                count += 1
            else:
                errors += 1

    messages.success(request, f'✔ Processed {count} student face profiles successfully! ({errors} photos skipped due to unclear faces)')
    return redirect('student_list')



def dashboard_view(request):
    """
    Admin / Teacher Dashboard for attendance logs and analytics.
    """
    today = timezone.now().date()
    sessions = AttendanceSession.objects.all().order_by('-date', '-time')
    
    # Filter by date if requested
    date_filter = request.GET.get('date', '')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            sessions = sessions.filter(date=filter_date)
        except ValueError:
            pass

    total_students = Student.objects.filter(is_active=True).count()
    total_sessions = AttendanceSession.objects.count()
    today_sessions = AttendanceSession.objects.filter(date=today)
    today_marked_count = AttendanceRecord.objects.filter(session__date=today, status='Present').count()

    context = {
        'sessions': sessions[:30],
        'total_students': total_students,
        'total_sessions': total_sessions,
        'today_marked_count': today_marked_count,
        'date_filter': date_filter,
        'portal_type': 'faculty',
    }
    return render(request, 'attendance_app/dashboard.html', context)


def session_detail_view(request, session_id):
    """
    Detail page of a specific attendance session with face recognition results.
    """
    session = get_object_or_404(AttendanceSession, id=session_id)
    records = session.records.select_related('student')
    
    context = {
        'session': session,
        'records': records,
        'portal_type': 'faculty',
    }
    return render(request, 'attendance_app/session_detail.html', context)


def export_attendance_excel(request, session_id):
    """
    Exports attendance sheet to Excel format (.xlsx).
    """
    session = get_object_or_404(AttendanceSession, id=session_id)
    records = session.records.select_related('student').all()

    data = []
    for idx, rec in enumerate(records, start=1):
        data.append({
            'S.No': idx,
            'Roll Number': rec.student.roll_no,
            'Student Name': rec.student.name,
            'Email': rec.student.email or '',
            'Department': session.department_name,
            'Course': session.course_name,
            'Semester': session.semester,
            'Division': session.division,
            'Subject': session.subject,
            'Attendance Status': rec.status,
            'Match Confidence %': f"{rec.confidence_score}%",
            'Date': session.date.strftime('%d-%m-%Y'),
            'Time': session.time.strftime('%H:%M:%S'),
        })

    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance Report')

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=Attendance_{session.course_name}_{session.date}.xlsx'
    return response


def attendance_sheet_view(request):
    """
    Roll Number-wise Ascending Master Attendance Sheet for All Students.
    """
    students = Student.objects.filter(is_active=True).select_related('department', 'course')
    
    course_filter = request.GET.get('course', '')
    semester_filter = request.GET.get('semester', '')
    division_filter = request.GET.get('division', '')
    search_query = request.GET.get('search', '').strip()
    sort_order = request.GET.get('sort', 'asc')  # default ASC

    if course_filter:
        students = students.filter(course_id=course_filter)
    if semester_filter:
        students = students.filter(semester__iexact=semester_filter)
    if division_filter:
        students = students.filter(division__iexact=division_filter)
    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) | Q(roll_no__icontains=search_query) | Q(email__icontains=search_query)
        )

    # Sort students in Ascending natural numerical/string order (e.g. 01, 2, 3, 10, 35...)
    def sort_key(st):
        digits = ''.join(ch for ch in st.roll_no if ch.isdigit())
        num = int(digits) if digits else 999999
        return (num, st.roll_no.lower())

    student_list = list(students)
    student_list.sort(key=sort_key, reverse=(sort_order == 'desc'))

    # Compute attendance statistics for each student
    total_sessions_count = AttendanceSession.objects.count()
    attendance_data = []
    total_present_all = 0
    total_classes_all = 0
    eligible_count = 0
    defaulter_count = 0

    for st in student_list:
        records = AttendanceRecord.objects.filter(student=st)
        total_st_classes = records.count()
        present_count = records.filter(status='Present').count()
        absent_count = total_st_classes - present_count
        pct = round((present_count / total_st_classes * 100), 1) if total_st_classes > 0 else 0.0

        if pct >= 75:
            eligible_count += 1
        elif total_st_classes > 0:
            defaulter_count += 1

        total_present_all += present_count
        total_classes_all += total_st_classes

        attendance_data.append({
            'student': st,
            'total_classes': total_st_classes,
            'present_count': present_count,
            'absent_count': absent_count,
            'percentage': pct,
            'is_eligible': pct >= 75,
        })

    avg_attendance = round((total_present_all / total_classes_all * 100), 1) if total_classes_all > 0 else 0.0

    courses = Course.objects.all()
    semesters = ["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6", "Semester 7", "Semester 8"]
    divisions = ["21", "22", "23", "24", "A", "B", "C", "D"]

    context = {
        'attendance_data': attendance_data,
        'courses': courses,
        'semesters': semesters,
        'divisions': divisions,
        'selected_course': course_filter,
        'selected_sem': semester_filter,
        'selected_div': division_filter,
        'search_query': search_query,
        'sort_order': sort_order,
        'total_students_count': len(student_list),
        'total_sessions_count': total_sessions_count,
        'avg_attendance': avg_attendance,
        'eligible_count': eligible_count,
        'defaulter_count': defaulter_count,
        'portal_type': 'faculty',
    }
    return render(request, 'attendance_app/attendance_sheet.html', context)


def export_master_attendance_excel(request):
    """
    Exports the complete Ascending Roll Number-wise Master Attendance Sheet to Excel (.xlsx).
    """
    students = Student.objects.filter(is_active=True).select_related('department', 'course')
    
    course_filter = request.GET.get('course', '')
    semester_filter = request.GET.get('semester', '')
    division_filter = request.GET.get('division', '')

    if course_filter:
        students = students.filter(course_id=course_filter)
    if semester_filter:
        students = students.filter(semester__iexact=semester_filter)
    if division_filter:
        students = students.filter(division__iexact=division_filter)

    def sort_key(st):
        digits = ''.join(ch for ch in st.roll_no if ch.isdigit())
        num = int(digits) if digits else 999999
        return (num, st.roll_no.lower())

    student_list = list(students)
    student_list.sort(key=sort_key)

    data = []
    for idx, st in enumerate(student_list, start=1):
        records = AttendanceRecord.objects.filter(student=st)
        total = records.count()
        present = records.filter(status='Present').count()
        absent = total - present
        pct = round((present / total * 100), 1) if total > 0 else 0.0

        data.append({
            'S.No': idx,
            'Roll Number': st.roll_no,
            'Student Name': st.name,
            'Faculty / Department': st.department.name if st.department else 'General',
            'Course / Degree': st.course.degree if st.course else 'General',
            'Semester': st.semester,
            'Division': st.division,
            'Total Classes': total,
            'Classes Present': present,
            'Classes Absent': absent,
            'Attendance %': f"{pct}%",
            'Eligibility Status': 'Eligible (>= 75%)' if pct >= 75 else 'Defaulter (< 75%)',
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Master Attendance Sheet')

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=Master_Attendance_Sheet_{timezone.now().strftime("%Y%m%d")}.xlsx'
    return response


def student_portal_view(request):
    """
    Student view: check own attendance by roll number.
    """
    roll_no = request.GET.get('roll_no', '').strip()
    student = None
    records = []
    total_classes = 0
    present_classes = 0
    percentage = 0.0

    if roll_no:
        student = Student.objects.filter(roll_no__iexact=roll_no).first()
        if student:
            records = AttendanceRecord.objects.filter(student=student).select_related('session').order_by('-session__date', '-session__time')
            total_classes = records.count()
            present_classes = records.filter(status='Present').count()
            if total_classes > 0:
                percentage = round((present_classes / total_classes) * 100, 2)
        else:
            messages.warning(request, f'No student found with Roll Number "{roll_no}".')

    context = {
        'student': student,
        'records': records,
        'roll_no': roll_no,
        'total_classes': total_classes,
        'present_classes': present_classes,
        'percentage': percentage,
        'portal_type': 'student',
    }
    return render(request, 'attendance_app/student_portal.html', context)
