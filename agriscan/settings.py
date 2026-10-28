import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

# ... (Keep your existing imports) ...
# 1. Load environment variables FIRST
load_dotenv()

# 2. THEN define BASE_DIR (this must be BEFORE DATABASES)
BASE_DIR = Path(__file__).resolve().parent.parent

# 3. THEN the security settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key-change-me')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['*']


# ... (Keep INSTALLED_APPS, etc.) ...

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <-- Add this right after security
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... (rest of your middleware)
]

# Database Configuration
# Use DATABASE_URL if provided by Render, otherwise fall back to SQLite
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles" # <-- Add this
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # <-- Add this

# Media files (Uploaded images)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"