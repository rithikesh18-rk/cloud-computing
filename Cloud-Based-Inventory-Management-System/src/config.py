"""
Configuration and secrets management module.
Loads connection parameters from st.secrets (Streamlit Cloud) with fallback
to environment variables (.env) or local configuration files.
"""

import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def get_database_config() -> Dict[str, Any]:
    """
    Extracts database configuration from Streamlit secrets if available,
    falling back to environment variables.
    """
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "mysql" in st.secrets:
            return dict(st.secrets["mysql"])
    except Exception:
        pass

    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "database": os.getenv("MYSQL_DATABASE", "inventory_db"),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "pool_size": int(os.getenv("DB_POOL_SIZE", 5)),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", 10)),
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", 1800)),
        "ssl_verify_cert": os.getenv("DB_SSL_VERIFY", "false").lower() in ("true", "1", "yes"),
        "ssl_ca": os.getenv("DB_SSL_CA", "")
    }
