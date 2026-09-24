"""
Automated Database Initialization Script
scripts/init_db.py

Executes database/schema.sql and database/seed_data.sql against
the configured cloud MySQL DBaaS (Aiven, Railway, AWS RDS, etc.).
"""

import os
import sys
import logging
from pathlib import Path
from sqlalchemy import text

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.db_handler import get_db_manager, load_db_credentials

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("db_init")

def run_sql_script(file_path: str):
    """Parses and executes a multi-statement SQL script file safely."""
    path = Path(file_path)
    if not path.exists():
        logger.error(f"SQL file not found: {file_path}")
        return False

    logger.info(f"Reading SQL script: {path.name} ({path.stat().st_size} bytes)")
    with open(path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    import re

    # Parse statements by semicolon while ignoring comments
    statements = []
    current_stmt = []
    
    for line in sql_content.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("--") or trimmed.startswith("/*"):
            continue
        code_part = re.sub(r'--.*$', '', line).strip()
        if not code_part:
            continue
        current_stmt.append(code_part)
        if code_part.endswith(";"):
            stmt_text = "\n".join(current_stmt).strip().rstrip(";").strip()
            if stmt_text:
                statements.append(stmt_text)
            current_stmt = []

    if current_stmt:
        remainder = "\n".join(current_stmt).strip().rstrip(";").strip()
        if remainder:
            statements.append(remainder)

    engine = get_db_manager().engine
    logger.info(f"Executing {len(statements)} statements against target database...")

    with engine.begin() as conn:
        for i, stmt in enumerate(statements, 1):
            try:
                conn.execute(text(stmt))
            except Exception as e:
                logger.error(f"Error on statement #{i}:\n{stmt[:100]}...\nReason: {e}")
                raise

    logger.info(f"Successfully executed {len(statements)} statements from {path.name}!")
    return True

def main():
    cfg = load_db_credentials()
    logger.info("=" * 60)
    logger.info("Cloud MySQL Database Automated Initialization")
    logger.info(f"Target DB Host: {cfg['host']}:{cfg['port']}")
    logger.info(f"Target Schema:  {cfg['database']}")
    logger.info(f"Target User:    {cfg['user']}")
    logger.info("=" * 60)

    # 1. Test Connectivity
    health = get_db_manager().check_health()
    if health.get("status") != "healthy":
        logger.error(f"Connection test failed: {health.get('error')}")
        logger.error("Please verify credentials in .streamlit/secrets.toml or environment variables.")
        sys.exit(1)

    logger.info(f"Connection verified: MySQL {health.get('version')} (Server time: {health.get('server_time')})")

    # 2. Execute schema.sql
    schema_path = os.path.join("database", "schema.sql")
    logger.info("Step 1: Applying Schema DDL...")
    run_sql_script(schema_path)

    # 3. Execute seed_data.sql
    seed_path = os.path.join("database", "seed_data.sql")
    logger.info("Step 2: Inserting Seed Data...")
    run_sql_script(seed_path)

    logger.info("=" * 60)
    logger.info("Database Initialization Complete! Ready for Streamlit Cloud.")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
