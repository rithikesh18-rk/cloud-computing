-- ==============================================================================
-- Cloud-Based Multi-Warehouse Inventory Management System
-- Database Engine: MySQL 8.0+ / 8.4 (InnoDB)
-- Optimization: DBaaS Multi-Tenant & High-Concurrency Cloud Architectures
-- ==============================================================================

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- ------------------------------------------------------------------------------
-- 1. Table: warehouses
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `warehouses`;
CREATE TABLE `warehouses` (
    `id` INT UNSIGNED AUTO_INCREMENT NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `location` VARCHAR(255) NOT NULL,
    `capacity` INT UNSIGNED NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `chk_warehouse_capacity` CHECK (`capacity` > 0),
    INDEX `idx_warehouses_name` (`name`),
    INDEX `idx_warehouses_location` (`location`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Physical storage and distribution facilities';

-- ------------------------------------------------------------------------------
-- 2. Table: categories
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `categories`;
CREATE TABLE `categories` (
    `id` INT UNSIGNED AUTO_INCREMENT NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `description` TEXT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_category_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Product categorization catalog';

-- ------------------------------------------------------------------------------
-- 3. Table: products
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
    `id` INT UNSIGNED AUTO_INCREMENT NOT NULL,
    `sku` VARCHAR(50) NOT NULL,
    `name` VARCHAR(150) NOT NULL,
    `category_id` INT UNSIGNED NOT NULL,
    `unit_price` DECIMAL(10, 2) NOT NULL,
    `reorder_point` INT UNSIGNED NOT NULL DEFAULT 10,
    `safety_stock` INT UNSIGNED NOT NULL DEFAULT 5,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_product_sku` (`sku`),
    CONSTRAINT `fk_products_category` 
        FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `chk_product_unit_price` CHECK (`unit_price` >= 0.00),
    CONSTRAINT `chk_product_safety_stock` CHECK (`safety_stock` >= 0),
    CONSTRAINT `chk_product_reorder_point` CHECK (`reorder_point` >= `safety_stock`),
    INDEX `idx_products_category_id` (`category_id`),
    INDEX `idx_products_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Master item catalog with reorder parameters';

-- ------------------------------------------------------------------------------
-- 4. Table: inventory_levels
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `inventory_levels`;
CREATE TABLE `inventory_levels` (
    `id` INT UNSIGNED AUTO_INCREMENT NOT NULL,
    `product_id` INT UNSIGNED NOT NULL,
    `warehouse_id` INT UNSIGNED NOT NULL,
    `quantity` INT NOT NULL DEFAULT 0,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `uq_product_warehouse` UNIQUE KEY (`product_id`, `warehouse_id`),
    CONSTRAINT `chk_inventory_quantity_non_negative` CHECK (`quantity` >= 0),
    CONSTRAINT `fk_inventory_product` 
        FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_inventory_warehouse` 
        FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX `idx_inventory_warehouse_product` (`warehouse_id`, `product_id`),
    INDEX `idx_inventory_quantity` (`quantity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Warehouse-specific stock balances';

-- ------------------------------------------------------------------------------
-- 5. Table: stock_transactions
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `stock_transactions`;
CREATE TABLE `stock_transactions` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT NOT NULL,
    `product_id` INT UNSIGNED NOT NULL,
    `warehouse_id` INT UNSIGNED NOT NULL,
    `change_quantity` INT NOT NULL,
    `transaction_type` ENUM('RESTOCK', 'DISPATCH', 'TRANSFER', 'ADJUSTMENT') NOT NULL,
    `reference_id` VARCHAR(100) NULL COMMENT 'PO#, Order#, RMA#, or Transfer Batch#',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_transactions_product` 
        FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_transactions_warehouse` 
        FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX `idx_transactions_product_warehouse` (`product_id`, `warehouse_id`),
    INDEX `idx_transactions_type` (`transaction_type`),
    INDEX `idx_transactions_created_at` (`created_at`),
    INDEX `idx_transactions_reference` (`reference_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Immutable audit ledger for all inventory movements';

-- ------------------------------------------------------------------------------
-- 6. Analytical Views for Real-Time Cloud Reporting
-- ------------------------------------------------------------------------------

-- Unified multi-warehouse inventory status with financial valuation & alert states
CREATE OR REPLACE VIEW `v_inventory_overview` AS
SELECT 
    il.id AS inventory_level_id,
    w.id AS warehouse_id,
    w.name AS warehouse_name,
    w.location AS warehouse_location,
    p.id AS product_id,
    p.sku,
    p.name AS product_name,
    c.id AS category_id,
    c.name AS category_name,
    p.unit_price,
    il.quantity,
    p.reorder_point,
    p.safety_stock,
    ROUND(il.quantity * p.unit_price, 2) AS total_valuation,
    CASE 
        WHEN il.quantity = 0 THEN 'OUT_OF_STOCK'
        WHEN il.quantity <= p.safety_stock THEN 'CRITICAL'
        WHEN il.quantity <= p.reorder_point THEN 'LOW_STOCK'
        ELSE 'HEALTHY'
    END AS stock_status,
    il.updated_at
FROM inventory_levels il
JOIN products p ON il.product_id = p.id
JOIN categories c ON p.category_id = c.id
JOIN warehouses w ON il.warehouse_id = w.id;

-- Actionable low-stock alerts view (items at or below reorder threshold)
CREATE OR REPLACE VIEW `v_low_stock_alerts` AS
SELECT 
    warehouse_name,
    sku,
    product_name,
    category_name,
    quantity,
    safety_stock,
    reorder_point,
    (reorder_point - quantity) AS suggested_replenishment,
    stock_status,
    updated_at
FROM v_inventory_overview
WHERE stock_status IN ('OUT_OF_STOCK', 'CRITICAL', 'LOW_STOCK')
ORDER BY 
    FIELD(stock_status, 'OUT_OF_STOCK', 'CRITICAL', 'LOW_STOCK'),
    quantity ASC;

-- Warehouse capacity utilization summary
CREATE OR REPLACE VIEW `v_warehouse_utilization` AS
SELECT 
    w.id AS warehouse_id,
    w.name AS warehouse_name,
    w.location,
    w.capacity AS max_capacity_units,
    COALESCE(SUM(il.quantity), 0) AS total_stocked_units,
    ROUND((COALESCE(SUM(il.quantity), 0) / w.capacity) * 100, 2) AS utilization_percentage,
    ROUND(COALESCE(SUM(il.quantity * p.unit_price), 0), 2) AS total_inventory_value
FROM warehouses w
LEFT JOIN inventory_levels il ON w.id = il.warehouse_id
LEFT JOIN products p ON il.product_id = p.id
GROUP BY w.id, w.name, w.location, w.capacity;

SET FOREIGN_KEY_CHECKS = 1;
