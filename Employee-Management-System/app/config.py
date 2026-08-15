import os

basedir = os.path.abspath(os.path.dirname(__file__))

def get_db_uri():
    """Resolves and formats database URI from DATABASE_URL or MYSQL_URL with SQLite fallback."""
    db_url = os.environ.get('DATABASE_URL') or os.environ.get('MYSQL_URL')
    if db_url:
        if db_url.startswith("postgres://"):
            return db_url.replace("postgres://", "postgresql://", 1)
        elif db_url.startswith("mysql://"):
            return db_url.replace("mysql://", "mysql+pymysql://", 1)
        return db_url
    return f"sqlite:///{os.path.join(basedir, '..', 'instance', 'employee_system.db')}"

class Config:
    """Base application configuration with dual MySQL & SQLite fallback support."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-12345'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Connection pool options for MySQL resilience
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280
    }

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return get_db_uri()


