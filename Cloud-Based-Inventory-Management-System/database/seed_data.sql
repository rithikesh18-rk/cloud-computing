-- ==============================================================================
-- Cloud-Based Multi-Warehouse Inventory Management System
-- Seed Data Script: database/seed_data.sql
-- ==============================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------------------------
-- 1. Warehouses (3 Realistic Geographically Distributed Facilities)
-- ------------------------------------------------------------------------------
TRUNCATE TABLE `warehouses`;
INSERT INTO `warehouses` (`id`, `name`, `location`, `capacity`, `created_at`) VALUES
(1, 'Central Logistics Hub (Dallas)', '4400 Logistics Pkwy, Dallas, TX 75261, USA', 120000, NOW() - INTERVAL 120 DAY),
(2, 'Pacific Northwest Facility (Seattle)', '18200 E Marginal Way S, Seattle, WA 98168, USA', 75000, NOW() - INTERVAL 90 DAY),
(3, 'Great Lakes Transit Depot (Chicago)', '3900 S Central Ave, Chicago, IL 60638, USA', 50000, NOW() - INTERVAL 60 DAY);

-- ------------------------------------------------------------------------------
-- 2. Categories (5 Industrial Supply & Technology Verticals)
-- ------------------------------------------------------------------------------
TRUNCATE TABLE `categories`;
INSERT INTO `categories` (`id`, `name`, `description`, `created_at`) VALUES
(1, 'Industrial Fasteners & Hardware', 'High-tensile structural bolts, anchors, and galvanized brackets', NOW() - INTERVAL 120 DAY),
(2, 'Sensors & Automation Controls', 'IoT telematics, edge sensors, transducers, and industrial controllers', NOW() - INTERVAL 120 DAY),
(3, 'Safety & Personal Protection (PPE)', 'OSHA-compliant head, respiratory, and hand safety equipment', NOW() - INTERVAL 120 DAY),
(4, 'Thermal & Protective Packaging', 'Cold-chain thermal liners, protective film, and strapping systems', NOW() - INTERVAL 120 DAY),
(5, 'Power Distribution & Cabling', 'Industrial-grade shielded cabling, DIN breakers, and power terminals', NOW() - INTERVAL 120 DAY);

-- ------------------------------------------------------------------------------
-- 3. Products (15 Realistic Inventory Items with Unit Economics & Thresholds)
-- ------------------------------------------------------------------------------
TRUNCATE TABLE `products`;
INSERT INTO `products` (`id`, `sku`, `name`, `category_id`, `unit_price`, `reorder_point`, `safety_stock`, `created_at`) VALUES
-- Category 1: Industrial Fasteners & Hardware
(1,  'FST-HEX-M12-100', 'Grade 8.8 M12 Hex Head Bolts (Box of 100)', 1, 42.50, 60, 20, NOW() - INTERVAL 100 DAY),
(2,  'FST-ANCH-SS-050', 'Stainless Steel Wedge Anchor 1/2"x4" (Box of 50)', 1, 68.00, 40, 15, NOW() - INTERVAL 100 DAY),
(3,  'FST-BRKT-HEAVY',  'Heavy-Duty Galvanized Structural Angle Bracket 90°', 1, 14.25, 100, 30, NOW() - INTERVAL 95 DAY),

-- Category 2: Sensors & Automation Controls
(4,  'SNS-IOT-TEMP-01', 'LoRaWAN Industrial Rugged Temp & Humidity Sensor', 2, 125.00, 25, 10, NOW() - INTERVAL 80 DAY),
(5,  'SNS-OPT-PROX-24V', 'Optical Laser Proximity Sensor 24V DC PNP', 2, 89.50, 30, 12, NOW() - INTERVAL 80 DAY),
(6,  'SNS-PRESS-TR-10', 'Ceramic Pressure Transducer 0-10 Bar 4-20mA', 2, 145.00, 20, 8, NOW() - INTERVAL 75 DAY),

-- Category 3: Safety & PPE
(7,  'PPE-RESP-N95-FLT', 'Dual-Cartridge Half-Facepiece Chemical Respirator', 3, 34.75, 50, 20, NOW() - INTERVAL 70 DAY),
(8,  'PPE-GLV-CUT5-PR',  'Level 5 Cut-Resistant Kevlar Nitrile Work Gloves', 3, 12.80, 120, 40, NOW() - INTERVAL 70 DAY),
(9,  'PPE-HELM-LED-WHT', 'ANSI Class E Vented Hard Hat w/ Integrated Headlamp', 3, 48.90, 40, 15, NOW() - INTERVAL 65 DAY),

-- Category 4: Thermal & Protective Packaging
(10, 'PKG-THRM-PAL-CVR', 'Insulated Cold-Chain Thermal Pallet Shroud Cover', 4, 78.00, 35, 10, NOW() - INTERVAL 60 DAY),
(11, 'PKG-BUBL-BIO-500', 'Biodegradable Cushioning Bubble Wrap 500ft Roll', 4, 38.50, 45, 15, NOW() - INTERVAL 55 DAY),
(12, 'PKG-PET-STRAP-HD', 'High-Tensile Polyester Strapping Coil 5/8" x 4000ft', 4, 62.00, 30, 10, NOW() - INTERVAL 50 DAY),

-- Category 5: Power Distribution & Cabling
(13, 'PWR-CBL-4C-100M',  '12 AWG 4-Conductor Shielded Tray Cable (100m Drum)', 5, 215.00, 15, 5, NOW() - INTERVAL 45 DAY),
(14, 'PWR-MCB-3P-063A',  '3-Pole 63A 400V DIN Rail Miniature Circuit Breaker', 5, 52.50, 30, 10, NOW() - INTERVAL 40 DAY),
(15, 'PWR-TRM-DIN-100',  'Screw-Clamp DIN Rail Feed-Through Terminal Block (100pk)', 5, 28.00, 50, 20, NOW() - INTERVAL 35 DAY);

-- ------------------------------------------------------------------------------
-- 4. Inventory Levels (Multi-Warehouse Balances Demonstrating Real-World States)
-- Healthy Stock, Low-Stock Alerts, Critical Depletion, and Out-of-Stock
-- ------------------------------------------------------------------------------
TRUNCATE TABLE `inventory_levels`;
INSERT INTO `inventory_levels` (`id`, `product_id`, `warehouse_id`, `quantity`, `updated_at`) VALUES
-- Warehouse 1: Central Logistics Hub (Dallas) - Primary Regional Staging Hub
(1,   1, 1, 450, NOW() - INTERVAL 2 DAY),   -- HEALTHY (Reorder: 60)
(2,   2, 1, 280, NOW() - INTERVAL 4 DAY),   -- HEALTHY (Reorder: 40)
(3,   3, 1, 620, NOW() - INTERVAL 1 DAY),   -- HEALTHY (Reorder: 100)
(4,   4, 1, 95,  NOW() - INTERVAL 3 DAY),   -- HEALTHY (Reorder: 25)
(5,   5, 1, 80,  NOW() - INTERVAL 5 DAY),   -- HEALTHY (Reorder: 30)
(6,   6, 1, 4,   NOW() - INTERVAL 1 HOUR),  -- CRITICAL ALERT! (Quantity 4 <= Safety 8, Reorder 20)
(7,   7, 1, 190, NOW() - INTERVAL 8 DAY),   -- HEALTHY (Reorder: 50)
(8,   8, 1, 410, NOW() - INTERVAL 2 DAY),   -- HEALTHY (Reorder: 120)
(9,   9, 1, 115, NOW() - INTERVAL 6 DAY),   -- HEALTHY (Reorder: 40)
(10, 10, 1, 140, NOW() - INTERVAL 4 DAY),   -- HEALTHY (Reorder: 35)
(11, 11, 1, 185, NOW() - INTERVAL 3 DAY),   -- HEALTHY (Reorder: 45)
(12, 12, 1, 95,  NOW() - INTERVAL 7 DAY),   -- HEALTHY (Reorder: 30)
(13, 13, 1, 38,  NOW() - INTERVAL 1 DAY),   -- HEALTHY (Reorder: 15)
(14, 14, 1, 110, NOW() - INTERVAL 5 DAY),   -- HEALTHY (Reorder: 30)
(15, 15, 1, 240, NOW() - INTERVAL 2 DAY),   -- HEALTHY (Reorder: 50)

-- Warehouse 2: Pacific Northwest Facility (Seattle)
(16,  1, 2, 75,  NOW() - INTERVAL 10 DAY),  -- HEALTHY (Reorder: 60)
(17,  2, 2, 45,  NOW() - INTERVAL 12 DAY),  -- HEALTHY (Reorder: 40)
(18,  3, 2, 120, NOW() - INTERVAL 6 DAY),   -- HEALTHY (Reorder: 100)
(19,  4, 2, 18,  NOW() - INTERVAL 2 HOUR),  -- LOW STOCK WARNING! (Safety 10 < Qty 18 <= Reorder 25)
(20,  5, 2, 22,  NOW() - INTERVAL 5 HOUR),  -- LOW STOCK WARNING! (Safety 12 < Qty 22 <= Reorder 30)
(21,  6, 2, 14,  NOW() - INTERVAL 8 HOUR),  -- LOW STOCK WARNING! (Safety 8 < Qty 14 <= Reorder 20)
(22,  7, 2, 38,  NOW() - INTERVAL 1 DAY),   -- LOW STOCK WARNING! (Safety 20 < Qty 38 <= Reorder 50)
(23,  8, 2, 85,  NOW() - INTERVAL 2 DAY),   -- LOW STOCK WARNING! (Safety 40 < Qty 85 <= Reorder 120)
(24,  9, 2, 12,  NOW() - INTERVAL 30 MINUTE),  -- CRITICAL ALERT! (Quantity 12 <= Safety 15, Reorder 40)
(25, 10, 2, 42,  NOW() - INTERVAL 5 DAY),   -- HEALTHY (Reorder: 35)
(26, 11, 2, 18,  NOW() - INTERVAL 3 HOUR),  -- LOW STOCK WARNING! (Safety 15 < Qty 18 <= Reorder 45)
(27, 12, 2, 8,   NOW() - INTERVAL 1 HOUR),  -- CRITICAL ALERT! (Quantity 8 <= Safety 10, Reorder 30)
(28, 13, 2, 2,   NOW() - INTERVAL 15 MINUTE),  -- CRITICAL ALERT! (Quantity 2 <= Safety 5, Reorder 15)
(29, 14, 2, 28,  NOW() - INTERVAL 4 DAY),   -- LOW STOCK WARNING! (Safety 10 < Qty 28 <= Reorder 30)
(30, 15, 2, 60,  NOW() - INTERVAL 2 DAY),   -- HEALTHY (Reorder: 50)

-- Warehouse 3: Great Lakes Transit Depot (Chicago)
(31,  1, 3, 25,  NOW() - INTERVAL 4 HOUR),  -- LOW STOCK WARNING! (Safety 20 < Qty 25 <= Reorder 60)
(32,  2, 3, 8,   NOW() - INTERVAL 1 HOUR),  -- CRITICAL ALERT! (Quantity 8 <= Safety 15, Reorder 40)
(33,  3, 3, 85,  NOW() - INTERVAL 3 DAY),   -- LOW STOCK WARNING! (Safety 30 < Qty 85 <= Reorder 100)
(34,  4, 3, 6,   NOW() - INTERVAL 20 MINUTE),  -- CRITICAL ALERT! (Quantity 6 <= Safety 10, Reorder 25)
(35,  5, 3, 0,   NOW() - INTERVAL 10 MINUTE),  -- OUT OF STOCK ALERT! (Quantity 0)
(36,  6, 3, 0,   NOW() - INTERVAL 5 MINUTE),   -- OUT OF STOCK ALERT! (Quantity 0)
(37,  7, 3, 14,  NOW() - INTERVAL 45 MINUTE),  -- CRITICAL ALERT! (Quantity 14 <= Safety 20, Reorder 50)
(38,  8, 3, 210, NOW() - INTERVAL 1 DAY),   -- HEALTHY (Reorder: 120)
(39,  9, 3, 0,   NOW() - INTERVAL 2 HOUR),  -- OUT OF STOCK ALERT! (Quantity 0)
(40, 10, 3, 0,   NOW() - INTERVAL 1 HOUR),  -- OUT OF STOCK ALERT! (Surplus in Dallas, Transfer Candidate)
(41, 11, 3, 55,  NOW() - INTERVAL 2 DAY),   -- HEALTHY (Reorder: 45)
(42, 12, 3, 35,  NOW() - INTERVAL 3 DAY),   -- HEALTHY (Reorder: 30)
(43, 13, 3, 19,  NOW() - INTERVAL 1 DAY),   -- HEALTHY (Reorder: 15)
(44, 14, 3, 9,   NOW() - INTERVAL 30 MINUTE),  -- CRITICAL ALERT! (Quantity 9 <= Safety 10, Reorder 30)
(45, 15, 3, 15,  NOW() - INTERVAL 15 MINUTE);  -- CRITICAL ALERT! (Quantity 15 <= Safety 20, Reorder 50)

-- ------------------------------------------------------------------------------
-- 5. Stock Transactions (Immutable Audit Trail Demonstrating Real Operations)
-- Types: RESTOCK, DISPATCH, TRANSFER, ADJUSTMENT
-- ------------------------------------------------------------------------------
TRUNCATE TABLE `stock_transactions`;
INSERT INTO `stock_transactions` (`id`, `product_id`, `warehouse_id`, `change_quantity`, `transaction_type`, `reference_id`, `created_at`) VALUES
-- Initial Receiving & Restocks
(1,  1,  1, 500,  'RESTOCK',    'PO-2024-8801', NOW() - INTERVAL 15 DAY),
(2,  2,  1, 300,  'RESTOCK',    'PO-2024-8802', NOW() - INTERVAL 15 DAY),
(3,  6,  1, 50,   'RESTOCK',    'PO-2024-8803', NOW() - INTERVAL 14 DAY),
(4,  10, 1, 160,  'RESTOCK',    'PO-2024-8804', NOW() - INTERVAL 12 DAY),
(5,  13, 1, 50,   'RESTOCK',    'PO-2024-8805', NOW() - INTERVAL 10 DAY),

-- Dispatches & Outbound Customer Orders
(6,  1,  1, -50,  'DISPATCH',   'SO-ORD-90210', NOW() - INTERVAL 5 DAY),
(7,  6,  1, -46,  'DISPATCH',   'SO-ORD-90342', NOW() - INTERVAL 2 DAY), -- Drained stock down to critical 4!
(8,  2,  1, -20,  'DISPATCH',   'SO-ORD-90401', NOW() - INTERVAL 1 DAY),
(9,  7,  2, -15,  'DISPATCH',   'SO-ORD-90512', NOW() - INTERVAL 18 HOUR),
(10, 13, 2, -8,   'DISPATCH',   'SO-ORD-90555', NOW() - INTERVAL 4 HOUR),

-- Inter-Warehouse Transfers (Balancing regional imbalances)
(11, 10, 1, -20,  'TRANSFER',   'TR-DAL-SEA-01', NOW() - INTERVAL 6 DAY), -- Origin transfer out
(12, 10, 2, 20,   'TRANSFER',   'TR-DAL-SEA-01', NOW() - INTERVAL 4 DAY), -- Destination receipt
(13, 5,  3, -25,  'DISPATCH',   'SO-ORD-90610', NOW() - INTERVAL 1 DAY), -- Drained to zero
(14, 6,  3, -12,  'DISPATCH',   'SO-ORD-90650', NOW() - INTERVAL 12 HOUR), -- Drained to zero

-- Cycle Count Inventory Adjustments
(15, 3,  1, 10,   'ADJUSTMENT', 'AUDIT-CC-Q3-01', NOW() - INTERVAL 3 DAY), -- Found extra during cycle count
(16, 12, 2, -2,   'ADJUSTMENT', 'DMG-WRH-2024-03', NOW() - INTERVAL 1 DAY); -- Damaged in forklift handling

SET FOREIGN_KEY_CHECKS = 1;
