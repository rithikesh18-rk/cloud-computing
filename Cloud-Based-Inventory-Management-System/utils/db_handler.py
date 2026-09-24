"""
Cloud-Based Multi-Warehouse Inventory Management System
Database Handler Module: utils/db_handler.py

Engineered for:
- Streamlit Community Cloud & Managed MySQL DBaaS (AWS RDS, PlanetScale, Aiven, Azure)
- Dynamic connection pooling (pool_recycle=3600, pool_pre_ping=True, thread-safe)
- Strict ACID transaction guarantees with row-level locking (SELECT ... FOR UPDATE)
- Deadlock detection, exponential backoff retries, and constraint violation mapping
"""

import os
import time
import random
import logging
import threading
from typing import Dict, Any, Optional, Tuple, List, Union
from uuid import uuid4

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import (
    OperationalError,
    IntegrityError,
    DBAPIError,
    SQLAlchemyError
)

# Configure structured logging
logger = logging.getLogger("inventory.db_handler")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


# ==============================================================================
# Domain Exceptions
# ==============================================================================

class InventoryException(Exception):
    """Base exception for inventory operations."""
    pass


class InsufficientStockError(InventoryException):
    """Raised when available inventory is less than requested quantity."""
    def __init__(self, product_id: int, warehouse_id: int, available: int, requested: int):
        self.product_id = product_id
        self.warehouse_id = warehouse_id
        self.available = available
        self.requested = requested
        super().__init__(
            f"Insufficient stock for Product ID {product_id} in Warehouse ID {warehouse_id}. "
            f"Available: {available}, Requested: {requested} (Deficit: {requested - available})"
        )


class ResourceNotFoundError(InventoryException):
    """Raised when a requested warehouse, product, or inventory record does not exist."""
    pass


class DeadlockRetryExhaustedError(InventoryException):
    """Raised when maximum transaction retries have been exhausted due to concurrency deadlocks."""
    pass


class DatabaseConstraintViolationError(InventoryException):
    """Raised when a database integrity constraint (check constraint, foreign key, or unique key) fails."""
    pass


class DatabaseConnectionError(InventoryException):
    """Raised when unable to establish or maintain a connection with the DBaaS."""
    pass


class DatabaseTransactionError(InventoryException):
    """Raised when an unexpected error occurs during database query or transaction execution."""
    pass



# ==============================================================================
# Deadlock & Lock Wait Timeout Retry Decorator
# ==============================================================================

MYSQL_DEADLOCK_ERROR_CODES = {1213, 1205}  # 1213: ER_LOCK_DEADLOCK, 1205: ER_LOCK_WAIT_TIMEOUT

def retry_on_deadlock(max_retries: int = 3, initial_delay: float = 0.1, backoff_factor: float = 2.0):
    """
    Decorator that retries database transactions upon encountering transient
    MySQL deadlocks (1213) or lock wait timeouts (1205) using exponential backoff with jitter.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = initial_delay
            while True:
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    # Inspect underlying DBAPI error code
                    err_code = None
                    if hasattr(e, "orig") and hasattr(e.orig, "args") and e.orig.args:
                        err_code = e.orig.args[0]

                    is_deadlock = (
                        err_code in MYSQL_DEADLOCK_ERROR_CODES or
                        "deadlock" in str(e).lower() or
                        "lock wait timeout" in str(e).lower()
                    )

                    if is_deadlock and attempt < max_retries:
                        attempt += 1
                        jitter = random.uniform(0.01, 0.05)
                        sleep_time = current_delay + jitter
                        logger.warning(
                            f"MySQL deadlock/lock-timeout detected (Code: {err_code}) in {func.__name__}. "
                            f"Retrying attempt {attempt}/{max_retries} after {sleep_time:.3f}s..."
                        )
                        time.sleep(sleep_time)
                        current_delay *= backoff_factor
                    else:
                        if is_deadlock:
                            logger.error(f"Exhausted {max_retries} deadlock retries in {func.__name__}.")
                            raise DeadlockRetryExhaustedError(
                                f"Transaction failed after {max_retries} retries due to concurrent lock contention."
                            ) from e
                        raise
        return wrapper
    return decorator


# ==============================================================================
# Dynamic Configuration & Secrets Loader
# ==============================================================================

def load_db_credentials() -> Dict[str, Any]:
    """
    Dynamically loads database connection parameters supporting:
    1. st.secrets["connections"]["mysql"] (Streamlit 1.28+ native SQL connection format)
    2. st.secrets["mysql"] (Custom Streamlit secrets format)
    3. Direct .streamlit/secrets.toml file parsing (for CLI/background scripts)
    4. Environment variables (MYSQL_HOST, MYSQL_USER, etc.)
    """
    secrets_data: Dict[str, Any] = {}

    # Attempt 1 & 2: Streamlit runtime secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if "connections" in st.secrets and "mysql" in st.secrets["connections"]:
                secrets_data = dict(st.secrets["connections"]["mysql"])
            elif "mysql" in st.secrets:
                secrets_data = dict(st.secrets["mysql"])
    except Exception:
        pass

    # Attempt 3: Direct secrets.toml parsing if not running inside Streamlit
    if not secrets_data:
        local_secrets_path = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
        if os.path.exists(local_secrets_path):
            try:
                try:
                    import tomllib  # Python 3.11+
                    with open(local_secrets_path, "rb") as f:
                        parsed = tomllib.load(f)
                except ImportError:
                    import toml  # Python <3.11 fallback
                    with open(local_secrets_path, "r", encoding="utf-8") as f:
                        parsed = toml.load(f)

                if "connections" in parsed and "mysql" in parsed["connections"]:
                    secrets_data = parsed["connections"]["mysql"]
                elif "mysql" in parsed:
                    secrets_data = parsed["mysql"]
            except Exception as e:
                logger.debug(f"Could not parse local secrets.toml directly: {e}")

    # Fallback to Environment Variables
    host = secrets_data.get("host") or os.getenv("MYSQL_HOST", "localhost")
    port = int(secrets_data.get("port") or os.getenv("MYSQL_PORT", 3306))
    database = secrets_data.get("database") or os.getenv("MYSQL_DATABASE", "inventory_db")
    user = secrets_data.get("username") or secrets_data.get("user") or os.getenv("MYSQL_USER", "root")
    password = secrets_data.get("password") or os.getenv("MYSQL_PASSWORD", "")
    
    # Pool options
    pool_size = int(secrets_data.get("pool_size", os.getenv("DB_POOL_SIZE", 10)))
    max_overflow = int(secrets_data.get("max_overflow", os.getenv("DB_MAX_OVERFLOW", 20)))
    pool_timeout = int(secrets_data.get("pool_timeout", os.getenv("DB_POOL_TIMEOUT", 30)))
    pool_recycle = int(secrets_data.get("pool_recycle", 3600))  # Requirement: pool_recycle=3600

    # TLS / SSL options
    ssl_ca = secrets_data.get("ssl_ca") or os.getenv("DB_SSL_CA", "")
    ssl_verify = secrets_data.get("ssl_verify_cert", False)
    if isinstance(ssl_verify, str):
        ssl_verify = ssl_verify.lower() in ("true", "1", "yes")

    return {
        "host": host,
        "port": port,
        "database": database,
        "user": user,
        "password": password,
        "pool_size": pool_size,
        "max_overflow": max_overflow,
        "pool_timeout": pool_timeout,
        "pool_recycle": pool_recycle,
        "ssl_ca": ssl_ca,
        "ssl_verify_cert": ssl_verify
    }


# ==============================================================================
# Thread-Safe Database Engine Singleton
# ==============================================================================

class DatabaseManager:
    """
    Thread-safe database manager with dynamic connection pooling,
    health verification, and transaction management.
    """
    _instance: Optional["DatabaseManager"] = None
    _lock: threading.Lock = threading.Lock()

    def __init__(self):
        self._engine: Optional[Engine] = None
        self._init_engine()

    def _init_engine(self):
        cfg = load_db_credentials()
        db_url = f"mysql+pymysql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}?charset=utf8mb4"

        connect_args: Dict[str, Any] = {
            "connect_timeout": 10,
            "read_timeout": 30,
            "write_timeout": 30,
            "autocommit": False
        }

        # Apply SSL/TLS parameters for cloud DBaaS
        if cfg.get("ssl_ca") and os.path.exists(cfg["ssl_ca"]):
            connect_args["ssl"] = {"ca": cfg["ssl_ca"]}
        elif cfg.get("ssl_verify_cert"):
            connect_args["ssl"] = {"check_hostname": True}

        try:
            self._engine = create_engine(
                db_url,
                connect_args=connect_args,
                poolclass=QueuePool,
                pool_size=cfg["pool_size"],
                max_overflow=cfg["max_overflow"],
                pool_timeout=cfg["pool_timeout"],
                pool_recycle=3600,       # Dynamic recycling to avoid DBaaS timeout disconnection
                pool_pre_ping=True,      # Tests connection liveness before checkout
                future=True
            )
            logger.info(f"Initialized SQLAlchemy connection pool for {cfg['host']}:{cfg['port']}/{cfg['database']}")
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise DatabaseConnectionError(f"Engine initialization error: {e}") from e

    @classmethod
    def get_instance(cls) -> "DatabaseManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._init_engine()
        return self._engine

    def check_health(self) -> Dict[str, Any]:
        """Validates connection health and returns DB server metrics."""
        try:
            with self.engine.connect() as conn:
                res = conn.execute(text("SELECT VERSION() as version, NOW() as server_time, DATABASE() as db;")).mappings().first()
                return {
                    "status": "healthy",
                    "version": res["version"],
                    "server_time": str(res["server_time"]),
                    "database": res["db"]
                }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Global accessor
def get_db_manager() -> DatabaseManager:
    return DatabaseManager.get_instance()


# ==============================================================================
# ACID Transaction & Query Handlers
# ==============================================================================

def get_inventory_summary() -> pd.DataFrame:
    """
    Returns an aggregated multi-warehouse stock overview across all facilities.
    Leverages pre-computed analytical view v_inventory_overview for high throughput.
    """
    query = """
        SELECT 
            warehouse_id,
            warehouse_name,
            warehouse_location,
            product_id,
            sku,
            product_name,
            category_name,
            unit_price,
            quantity,
            reorder_point,
            safety_stock,
            total_valuation,
            stock_status,
            updated_at
        FROM v_inventory_overview
        ORDER BY warehouse_name ASC, category_name ASC, product_name ASC;
    """
    try:
        engine = get_db_manager().engine
        with engine.connect() as conn:
            return pd.read_sql_query(text(query), conn)
    except SQLAlchemyError as e:
        logger.error(f"Error querying inventory summary: {e}")
        raise DatabaseTransactionError(f"Failed to fetch inventory summary: {e}") from e


def get_critical_low_stock() -> pd.DataFrame:
    """
    Returns prioritized low-stock alerts where current on-hand quantity <= reorder_point.
    Classifies items into OUT_OF_STOCK, CRITICAL, and LOW_STOCK.
    """
    query = """
        SELECT 
            warehouse_name,
            sku,
            product_name,
            category_name,
            quantity,
            safety_stock,
            reorder_point,
            suggested_replenishment,
            stock_status,
            updated_at
        FROM v_low_stock_alerts;
    """
    try:
        engine = get_db_manager().engine
        with engine.connect() as conn:
            return pd.read_sql_query(text(query), conn)
    except SQLAlchemyError as e:
        logger.error(f"Error querying critical low stock alerts: {e}")
        raise DatabaseTransactionError(f"Failed to fetch low stock alerts: {e}") from e


@retry_on_deadlock(max_retries=3, initial_delay=0.1)
def execute_restock(
    product_id: int,
    warehouse_id: int,
    quantity: int,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Atomically increases inventory level for a product in a warehouse and logs
    an immutable RESTOCK transaction to stock_transactions.

    Guarantees:
    - Row-level lock acquisition (SELECT ... FOR UPDATE)
    - Automatic upsert if inventory record does not yet exist
    - Integrity check for positive quantity
    """
    if quantity <= 0:
        raise ValueError(f"Restock quantity must be strictly positive (> 0), got: {quantity}")

    ref_id = notes or f"RESTOCK-{uuid4().hex[:8].upper()}"
    engine = get_db_manager().engine

    try:
        with engine.begin() as conn:
            # 1. Validate Product and Warehouse existence
            prod_check = conn.execute(
                text("SELECT id, name, sku FROM products WHERE id = :p;"),
                {"p": product_id}
            ).mappings().first()
            if not prod_check:
                raise ResourceNotFoundError(f"Product ID {product_id} does not exist.")

            wh_check = conn.execute(
                text("SELECT id, name FROM warehouses WHERE id = :w;"),
                {"w": warehouse_id}
            ).mappings().first()
            if not wh_check:
                raise ResourceNotFoundError(f"Warehouse ID {warehouse_id} does not exist.")

            # 2. Acquire row-level lock on inventory_levels
            inv_row = conn.execute(
                text("SELECT id, quantity FROM inventory_levels WHERE product_id = :p AND warehouse_id = :w FOR UPDATE;"),
                {"p": product_id, "w": warehouse_id}
            ).mappings().first()

            if inv_row:
                new_quantity = inv_row["quantity"] + quantity
                conn.execute(
                    text("UPDATE inventory_levels SET quantity = :q WHERE id = :id;"),
                    {"q": new_quantity, "id": inv_row["id"]}
                )
            else:
                new_quantity = quantity
                conn.execute(
                    text("INSERT INTO inventory_levels (product_id, warehouse_id, quantity) VALUES (:p, :w, :q);"),
                    {"p": product_id, "w": warehouse_id, "q": new_quantity}
                )

            # 3. Log immutable audit transaction
            txn_result = conn.execute(
                text("""
                    INSERT INTO stock_transactions (product_id, warehouse_id, change_quantity, transaction_type, reference_id)
                    VALUES (:p, :w, :change, 'RESTOCK', :ref);
                """),
                {"p": product_id, "w": warehouse_id, "change": quantity, "ref": ref_id}
            )

            logger.info(
                f"[RESTOCK SUCCESS] Product {prod_check['sku']} (+{quantity}) in Warehouse '{wh_check['name']}'. "
                f"New Balance: {new_quantity}. Ref: {ref_id}"
            )

            return {
                "status": "success",
                "transaction_id": txn_result.lastrowid,
                "transaction_type": "RESTOCK",
                "product_id": product_id,
                "sku": prod_check["sku"],
                "warehouse_id": warehouse_id,
                "warehouse_name": wh_check["name"],
                "quantity_added": quantity,
                "new_balance": new_quantity,
                "reference_id": ref_id
            }

    except IntegrityError as e:
        logger.error(f"Database integrity violation in execute_restock: {e}")
        raise DatabaseConstraintViolationError(f"Restock violates database constraints: {e}") from e
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error in execute_restock: {e}")
        raise


@retry_on_deadlock(max_retries=3, initial_delay=0.1)
def execute_dispatch(
    product_id: int,
    warehouse_id: int,
    quantity: int,
    order_ref: str
) -> Dict[str, Any]:
    """
    Safely decrements inventory level for outbound fulfillment inside a strict ACID transaction.

    Guarantees:
    - Acquires row-level exclusive lock with SELECT ... FOR UPDATE
    - Verifies available on-hand quantity >= requested quantity
    - Rolls back immediately and raises InsufficientStockError if quantity is deficient
    - Logs outbound DISPATCH transaction with change_quantity = -quantity
    """
    if quantity <= 0:
        raise ValueError(f"Dispatch quantity must be strictly positive (> 0), got: {quantity}")
    if not order_ref or not str(order_ref).strip():
        raise ValueError("A valid order reference (order_ref) is required for stock dispatch.")

    engine = get_db_manager().engine

    try:
        with engine.begin() as conn:
            # 1. Acquire row lock and inspect current balance
            inv_row = conn.execute(
                text("""
                    SELECT il.id, il.quantity, p.sku, p.name AS product_name, w.name AS warehouse_name
                    FROM inventory_levels il
                    JOIN products p ON il.product_id = p.id
                    JOIN warehouses w ON il.warehouse_id = w.id
                    WHERE il.product_id = :p AND il.warehouse_id = :w
                    FOR UPDATE;
                """),
                {"p": product_id, "w": warehouse_id}
            ).mappings().first()

            if not inv_row:
                raise InsufficientStockError(
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                    available=0,
                    requested=quantity
                )

            current_qty = inv_row["quantity"]

            # 2. Strict availability check
            if current_qty < quantity:
                logger.warning(
                    f"[DISPATCH REJECTED] Product {inv_row['sku']} in WH {inv_row['warehouse_name']}. "
                    f"Available: {current_qty}, Requested: {quantity}."
                )
                raise InsufficientStockError(
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                    available=current_qty,
                    requested=quantity
                )

            new_qty = current_qty - quantity

            # 3. Decrement stock balance
            conn.execute(
                text("UPDATE inventory_levels SET quantity = :q WHERE id = :id;"),
                {"q": new_qty, "id": inv_row["id"]}
            )

            # 4. Insert DISPATCH audit record (-quantity)
            txn_result = conn.execute(
                text("""
                    INSERT INTO stock_transactions (product_id, warehouse_id, change_quantity, transaction_type, reference_id)
                    VALUES (:p, :w, :change, 'DISPATCH', :ref);
                """),
                {"p": product_id, "w": warehouse_id, "change": -quantity, "ref": order_ref.strip()}
            )

            logger.info(
                f"[DISPATCH SUCCESS] Product {inv_row['sku']} (-{quantity}) from WH '{inv_row['warehouse_name']}'. "
                f"Remaining: {new_qty}. Ref: {order_ref}"
            )

            return {
                "status": "success",
                "transaction_id": txn_result.lastrowid,
                "transaction_type": "DISPATCH",
                "product_id": product_id,
                "sku": inv_row["sku"],
                "product_name": inv_row["product_name"],
                "warehouse_id": warehouse_id,
                "warehouse_name": inv_row["warehouse_name"],
                "quantity_dispatched": quantity,
                "remaining_balance": new_qty,
                "reference_id": order_ref.strip()
            }

    except IntegrityError as e:
        logger.error(f"Database integrity violation during dispatch: {e}")
        raise DatabaseConstraintViolationError(f"Dispatch failed check constraint: {e}") from e
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error during dispatch: {e}")
        raise


@retry_on_deadlock(max_retries=3, initial_delay=0.15)
def execute_transfer(
    product_id: int,
    from_warehouse_id: int,
    to_warehouse_id: int,
    quantity: int,
    transfer_ref: Optional[str] = None
) -> Dict[str, Any]:
    """
    Performs an atomic, bidirectional stock transfer between two facilities inside
    a single database transaction.

    Deadlock Prevention Strategy:
    - Deterministic locking order: Acquires locks strictly in ascending warehouse_id order
      (i.e. min(w1, w2) followed by max(w1, w2)). This completely eliminates circular wait
      deadlocks between concurrent opposing transfers (e.g. WH1->WH2 and WH2->WH1).
    - Checks source stock availability before applying modifications.
    - Decrements source inventory and increments destination inventory.
    - Records paired immutable TRANSFER records in stock_transactions.
    """
    if quantity <= 0:
        raise ValueError(f"Transfer quantity must be strictly positive (> 0), got: {quantity}")
    if from_warehouse_id == to_warehouse_id:
        raise ValueError(f"Source and destination warehouses cannot be the same (ID: {from_warehouse_id}).")

    ref = transfer_ref or f"TRF-{uuid4().hex[:8].upper()}"
    engine = get_db_manager().engine

    # Deterministic lock ordering: always lock lowest warehouse_id first
    first_wh, second_wh = sorted([from_warehouse_id, to_warehouse_id])

    try:
        with engine.begin() as conn:
            # 1. Validate Product Existence
            prod_row = conn.execute(
                text("SELECT id, sku, name FROM products WHERE id = :p;"),
                {"p": product_id}
            ).mappings().first()
            if not prod_row:
                raise ResourceNotFoundError(f"Product ID {product_id} does not exist.")

            # 2. Validate Warehouses
            wh_records = conn.execute(
                text("SELECT id, name FROM warehouses WHERE id IN (:w1, :w2);"),
                {"w1": from_warehouse_id, "w2": to_warehouse_id}
            ).mappings().all()
            wh_map = {row["id"]: row["name"] for row in wh_records}

            if from_warehouse_id not in wh_map:
                raise ResourceNotFoundError(f"Source Warehouse ID {from_warehouse_id} does not exist.")
            if to_warehouse_id not in wh_map:
                raise ResourceNotFoundError(f"Destination Warehouse ID {to_warehouse_id} does not exist.")

            # 3. Ensure destination inventory record exists so it can be locked FOR UPDATE
            conn.execute(
                text("""
                    INSERT INTO inventory_levels (product_id, warehouse_id, quantity)
                    VALUES (:p, :w, 0)
                    ON DUPLICATE KEY UPDATE product_id = product_id;
                """),
                {"p": product_id, "w": to_warehouse_id}
            )

            # 4. Acquire Row Locks in Strict Deterministic Order
            first_lock = conn.execute(
                text("SELECT id, warehouse_id, quantity FROM inventory_levels WHERE product_id = :p AND warehouse_id = :w FOR UPDATE;"),
                {"p": product_id, "w": first_wh}
            ).mappings().first()

            second_lock = conn.execute(
                text("SELECT id, warehouse_id, quantity FROM inventory_levels WHERE product_id = :p AND warehouse_id = :w FOR UPDATE;"),
                {"p": product_id, "w": second_wh}
            ).mappings().first()

            # Map locked rows to source and destination
            locks = {first_wh: first_lock, second_wh: second_lock}
            source_inv = locks.get(from_warehouse_id)
            dest_inv = locks.get(to_warehouse_id)

            source_qty = source_inv["quantity"] if source_inv else 0

            # 5. Check Sufficient Inventory at Origin
            if source_qty < quantity:
                logger.warning(
                    f"[TRANSFER REJECTED] Insufficient stock for {prod_row['sku']} at WH {wh_map[from_warehouse_id]}. "
                    f"Available: {source_qty}, Requested: {quantity}."
                )
                raise InsufficientStockError(
                    product_id=product_id,
                    warehouse_id=from_warehouse_id,
                    available=source_qty,
                    requested=quantity
                )

            new_source_qty = source_qty - quantity
            new_dest_qty = (dest_inv["quantity"] if dest_inv else 0) + quantity

            # 6. Apply atomic balance modifications
            conn.execute(
                text("UPDATE inventory_levels SET quantity = :q WHERE id = :id;"),
                {"q": new_source_qty, "id": source_inv["id"]}
            )
            conn.execute(
                text("UPDATE inventory_levels SET quantity = :q WHERE id = :id;"),
                {"q": new_dest_qty, "id": dest_inv["id"]}
            )

            # 7. Insert Paired Transfer Audit Entries
            outbound_ref = f"{ref} [OUT: WH-{to_warehouse_id}]"
            inbound_ref = f"{ref} [IN: WH-{from_warehouse_id}]"

            # Outbound debit (-quantity)
            conn.execute(
                text("""
                    INSERT INTO stock_transactions (product_id, warehouse_id, change_quantity, transaction_type, reference_id)
                    VALUES (:p, :w, :change, 'TRANSFER', :ref);
                """),
                {"p": product_id, "w": from_warehouse_id, "change": -quantity, "ref": outbound_ref}
            )

            # Inbound credit (+quantity)
            conn.execute(
                text("""
                    INSERT INTO stock_transactions (product_id, warehouse_id, change_quantity, transaction_type, reference_id)
                    VALUES (:p, :w, :change, 'TRANSFER', :ref);
                """),
                {"p": product_id, "w": to_warehouse_id, "change": quantity, "ref": inbound_ref}
            )

            logger.info(
                f"[TRANSFER SUCCESS] {prod_row['sku']} ({quantity} units) transferred from "
                f"'{wh_map[from_warehouse_id]}' -> '{wh_map[to_warehouse_id]}'. Batch: {ref}"
            )

            return {
                "status": "success",
                "reference_id": ref,
                "product_id": product_id,
                "sku": prod_row["sku"],
                "product_name": prod_row["name"],
                "from_warehouse_id": from_warehouse_id,
                "from_warehouse_name": wh_map[from_warehouse_id],
                "to_warehouse_id": to_warehouse_id,
                "to_warehouse_name": wh_map[to_warehouse_id],
                "transferred_quantity": quantity,
                "source_remaining_balance": new_source_qty,
                "destination_new_balance": new_dest_qty
            }

    except IntegrityError as e:
        logger.error(f"Database constraint violation during transfer: {e}")
        raise DatabaseConstraintViolationError(f"Transfer violated integrity rules: {e}") from e
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error during transfer: {e}")
        raise


def get_warehouses_list() -> pd.DataFrame:
    """Returns active warehouse facilities."""
    query = "SELECT id, name, location, capacity FROM warehouses ORDER BY name ASC;"
    try:
        engine = get_db_manager().engine
        with engine.connect() as conn:
            return pd.read_sql_query(text(query), conn)
    except SQLAlchemyError as e:
        logger.error(f"Error fetching warehouses: {e}")
        raise DatabaseTransactionError(f"Failed to fetch warehouses: {e}") from e


def get_products_list() -> pd.DataFrame:
    """Returns catalog products with category details."""
    query = """
        SELECT 
            p.id, 
            p.sku, 
            p.name, 
            p.category_id, 
            c.name AS category_name, 
            p.unit_price, 
            p.reorder_point, 
            p.safety_stock
        FROM products p
        JOIN categories c ON p.category_id = c.id
        ORDER BY p.name ASC;
    """
    try:
        engine = get_db_manager().engine
        with engine.connect() as conn:
            return pd.read_sql_query(text(query), conn)
    except SQLAlchemyError as e:
        logger.error(f"Error fetching products: {e}")
        raise DatabaseTransactionError(f"Failed to fetch products: {e}") from e


def get_transactions_ledger(limit: int = 500) -> pd.DataFrame:
    """Returns historical transaction audit records with joined details."""
    query = """
        SELECT 
            st.id,
            st.created_at,
            w.name AS warehouse_name,
            p.sku,
            p.name AS product_name,
            c.name AS category_name,
            st.transaction_type,
            st.change_quantity,
            st.reference_id
        FROM stock_transactions st
        JOIN warehouses w ON st.warehouse_id = w.id
        JOIN products p ON st.product_id = p.id
        JOIN categories c ON p.category_id = c.id
        ORDER BY st.created_at DESC
        LIMIT :limit;
    """
    try:
        engine = get_db_manager().engine
        with engine.connect() as conn:
            return pd.read_sql_query(text(query), conn, params={"limit": limit})
    except SQLAlchemyError as e:
        logger.error(f"Error fetching transaction ledger: {e}")
        raise DatabaseTransactionError(f"Failed to fetch transactions: {e}") from e


def get_stock_for_product_warehouse(product_id: int, warehouse_id: int) -> Dict[str, Any]:
    """Returns current on-hand quantity and reorder parameters for a product in a facility."""
    query = """
        SELECT 
            COALESCE(il.quantity, 0) AS quantity,
            p.reorder_point,
            p.safety_stock,
            p.unit_price,
            p.sku,
            p.name AS product_name,
            w.name AS warehouse_name
        FROM products p
        CROSS JOIN warehouses w
        LEFT JOIN inventory_levels il ON il.product_id = p.id AND il.warehouse_id = w.id
        WHERE p.id = :p AND w.id = :w;
    """
    try:
        engine = get_db_manager().engine
        with engine.connect() as conn:
            row = conn.execute(text(query), {"p": product_id, "w": warehouse_id}).mappings().first()
            if not row:
                return {"quantity": 0, "reorder_point": 0, "safety_stock": 0, "status": "UNKNOWN"}
            
            qty = row["quantity"]
            reorder = row["reorder_point"]
            safety = row["safety_stock"]
            
            if qty == 0:
                status = "OUT_OF_STOCK"
            elif qty <= safety:
                status = "CRITICAL"
            elif qty <= reorder:
                status = "LOW_STOCK"
            else:
                status = "HEALTHY"

            return {
                "quantity": qty,
                "reorder_point": reorder,
                "safety_stock": safety,
                "unit_price": float(row["unit_price"]),
                "sku": row["sku"],
                "product_name": row["product_name"],
                "warehouse_name": row["warehouse_name"],
                "status": status
            }
    except SQLAlchemyError as e:
        logger.error(f"Error fetching stock detail: {e}")
        return {"quantity": 0, "reorder_point": 0, "safety_stock": 0, "status": "ERROR"}

