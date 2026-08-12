import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'attendance-super-secret-key-2026'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Uploads directory
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

    # Database Configuration:
    # Set MYSQL_URI environment variable or default to local MySQL. Fallback to SQLite if MySQL is unavailable.
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'attendance_db')

    # Try MySQL URI by default, or SQLite fallback path
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    
    SQLITE_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'attendance.db')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
