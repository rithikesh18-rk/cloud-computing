"""
Cloud-Optimized Database Connection and Query Execution Module.
Engineered for DBaaS (AWS RDS, PlanetScale, Aiven, Azure) and Streamlit Cloud.
"""

import logging
from typing import Optional, Dict, Any, List
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
import pymysql

from src.config import get_database_config

logger = logging.getLogger(__name__)

_engine: Optional[Engine] = None

def get_engine() -> Engine:
    """
    Returns or initializes a singleton SQLAlchemy Engine configured
    with connection pooling, SSL/TLS, and auto-reconnect pre-ping.
    """
    global _engine
    if _engine is not None:
        return _engine

    cfg = get_database_config()

    # Build MySQL connection URL
    # Format: mysql+pymysql://<user>:<password>@<host>:<port>/<dbname>
    user = cfg.get("user", "root")
    password = cfg.get("password", "")
    host = cfg.get("host", "localhost")
    port = cfg.get("port", 3306)
    database = cfg.get("database", "inventory_db")

    db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"

    connect_args: Dict[str, Any] = {
        "connect_timeout": 10,
        "read_timeout": 30,
        "write_timeout": 30
    }

    # Cloud DBaaS SSL / TLS Configuration
    if cfg.get("ssl_ca"):
        connect_args["ssl"] = {"ca": cfg["ssl_ca"]}
    elif cfg.get("ssl_verify_cert") is True:
        connect_args["ssl"] = {"check_hostname": True}

    _engine = create_engine(
        db_url,
        connect_args=connect_args,
        poolclass=QueuePool,
        pool_size=int(cfg.get("pool_size", 5)),
        max_overflow=int(cfg.get("max_overflow", 10)),
        pool_timeout=int(cfg.get("pool_timeout", 30)),
        pool_recycle=int(cfg.get("pool_recycle", 1800)),
        pool_pre_ping=True,  # Crucial for cloud DBaaS: checks connection health before use
        future=True
    )

    return _engine

def test_connection() -> Dict[str, Any]:
    """
    Validates database connectivity and returns latency and engine version.
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION() as version, NOW() as server_time;")).mappings().first()
            return {
                "status": "connected",
                "version": result["version"],
                "server_time": str(result["server_time"])
            }
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Executes a SELECT SQL query and returns results as a pandas DataFrame.
    """
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql_query(text(query), conn, params=params)

def execute_mutation(query: str, params: Optional[Dict[str, Any]] = None) -> int:
    """
    Executes an INSERT, UPDATE, or DELETE SQL statement within a transactional block.
    Returns number of rows affected.
    """
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(text(query), params or {})
        return result.rowcount
