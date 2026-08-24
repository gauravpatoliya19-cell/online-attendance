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

# Ensure /tmp writable database exists
src_db = ROOT_DIR / 'db.sqlite3'
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

# If db is not yet migrated, run migrate
try:
    if not dst_db.exists() or dst_db.stat().st_size == 0:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
except Exception:
    pass

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
handler = app
