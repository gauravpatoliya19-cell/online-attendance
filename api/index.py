import os
import sys
import shutil
from pathlib import Path

# Add root directory to sys.path
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')

# Copy database to writable /tmp on Vercel invocation
src_db = ROOT_DIR / 'db.sqlite3'
dst_db = Path('/tmp/db.sqlite3')
if src_db.exists() and not dst_db.exists():
    try:
        shutil.copy2(str(src_db), str(dst_db))
    except Exception:
        pass

# Ensure media directory exists in /tmp
try:
    os.makedirs('/tmp/media', exist_ok=True)
except Exception:
    pass

from django.core.wsgi import get_wsgi_application

django_app = get_wsgi_application()


def app(environ, start_response):
    """WSGI Handler with detailed error capture for Vercel Serverless."""
    try:
        return django_app(environ, start_response)
    except Exception as exc:
        import traceback
        error_msg = traceback.format_exc()
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, response_headers)
        return [f"Serverless Runtime Error:\n\n{error_msg}".encode('utf-8')]
