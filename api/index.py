import os
import sys
import shutil
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')

# Copy database to writable /tmp on Vercel
src_db = BASE_DIR / 'db.sqlite3'
dst_db = Path('/tmp/db.sqlite3')
if src_db.exists() and not dst_db.exists():
    try:
        shutil.copy2(str(src_db), str(dst_db))
    except Exception:
        pass

try:
    os.makedirs('/tmp/media', exist_ok=True)
except Exception:
    pass

import django
django.setup()

# Auto-migrate if needed
try:
    if not dst_db.exists() or dst_db.stat().st_size == 0:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
except Exception:
    pass

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
