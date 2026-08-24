"""
WSGI config for attendance_project project on Vercel and production.
"""

import os
import shutil
from pathlib import Path
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')

# In Vercel serverless environment, ensure writable database exists in /tmp
if 'VERCEL' in os.environ:
    base_dir = Path(__file__).resolve().parent.parent
    src_db = base_dir / 'db.sqlite3'
    dst_db = Path('/tmp/db.sqlite3')
    if src_db.exists() and not dst_db.exists():
        try:
            shutil.copy2(str(src_db), str(dst_db))
        except Exception:
            pass

application = get_wsgi_application()
app = application
