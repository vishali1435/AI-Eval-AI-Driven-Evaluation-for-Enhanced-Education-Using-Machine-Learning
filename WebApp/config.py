import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ai-eval-super-secret-key-2026')
    # Default to SQLite for zero-setup portability; MySQL easily configurable
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "aep.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = BASE_DIR
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
