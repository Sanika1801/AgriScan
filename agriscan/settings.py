import os
import dj_database_url
from pathlib import Path

# ... (Keep your existing imports) ...

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Allow all hosts for Render (or set your specific Render URL)
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