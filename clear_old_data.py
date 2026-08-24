import os
import shutil
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

from attendance_app.models import Student, AttendanceSession, AttendanceRecord

def clear_data():
    print("Clearing all old attendance records and sample student data...")

    # 1. Delete Attendance Records and Sessions
    rec_count, _ = AttendanceRecord.objects.all().delete()
    sess_count, _ = AttendanceSession.objects.all().delete()
    print(f"[OK] Deleted {rec_count} attendance records and {sess_count} sessions.")

    # 2. Delete Students
    st_count, _ = Student.objects.all().delete()
    print(f"[OK] Deleted {st_count} students.")

    # 3. Clean up Media folders
    media_dir = os.path.join(os.getcwd(), 'media')
    if os.path.exists(media_dir):
        for item in os.listdir(media_dir):
            item_path = os.path.join(media_dir, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"Could not delete {item_path}: {e}")

    # Re-create empty media subfolders
    os.makedirs(os.path.join(media_dir, 'students', 'profile_photos'), exist_ok=True)
    os.makedirs(os.path.join(media_dir, 'attendance_sessions', 'original'), exist_ok=True)
    os.makedirs(os.path.join(media_dir, 'attendance_sessions', 'annotated'), exist_ok=True)

    print("[OK] Cleaned media directory.")
    print("\nAll old data removed successfully! Database is completely fresh and ready.")

if __name__ == '__main__':
    clear_data()
