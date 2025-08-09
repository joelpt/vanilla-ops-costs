-- Terra35 Vanilla Operations Cost Analysis Database Schema
-- SQLite Database Design for Cost Data Collection and Analysis
-- Version: 1.0
-- Created: 2024-12-30

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ================================
-- CORE TAXONOMY TABLES
-- ================================

-- Revenue streams (Grow & Produce, Partner & Produce, Make & Produce)
CREATE TABLE revenue_streams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL UNIQUE, -- 'grow_produce', 'partner_produce', 'make_produce'
    description TEXT NOT NULL,
    production_target TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cost categories within each revenue stream
CREATE TABLE cost_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    revenue_stream_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    description TEXT,
    parent_category_id INTEGER, -- For subcategories
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (revenue_stream_id) REFERENCES revenue_streams(id),
    FOREIGN KEY (parent_category_id) REFERENCES cost_categories(id),
    UNIQUE(revenue_stream_id, code)
);

-- ================================
-- COST DATA TABLES
-- ================================

-- Main cost items table
CREATE TABLE cost_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT NOT NULL UNIQUE, -- User-friendly ID like 'GH_BENCH_001'
    item_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    specifications JSON, -- Flexible specifications storage
    notes TEXT,
    status TEXT DEFAULT 'active', -- 'active', 'deprecated', 'pending'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES cost_categories(id)
);

-- Pricing data with historical tracking
CREATE TABLE cost_pricing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cost_item_id INTEGER NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    unit TEXT NOT NULL, -- 'per_sq_ft', 'per_gallon', 'per_unit', etc.
    currency TEXT DEFAULT 'USD',
    effective_date DATE NOT NULL,
    volume_tier TEXT, -- For bulk pricing: '1000-2499', '2500-4999', etc.
    total_cost_5000sqft DECIMAL(12,2), -- Calculated total for 5000 sq ft baseline
    confidence_level TEXT NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH', 'VERIFIED'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cost_item_id) REFERENCES cost_items(id)
);

-- Volume discount structures
CREATE TABLE volume_discounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cost_item_id INTEGER NOT NULL,
    quantity_min INTEGER,
    quantity_max INTEGER,
    quantity_unit TEXT, -- 'sq_ft', 'units', 'gallons', etc.
    discount_price DECIMAL(10,2) NOT NULL,
    discount_percentage DECIMAL(5,2),
    effective_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cost_item_id) REFERENCES cost_items(id),
    UNIQUE(cost_item_id, quantity_min, quantity_max) -- Prevent conflicting discount tiers
);

-- ================================
-- SOURCE DOCUMENTATION TABLES
-- ================================

-- Source companies and suppliers
CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL UNIQUE, -- Prevent duplicate suppliers
    company_type TEXT, -- 'supplier', 'government', 'industry_report', etc.
    website_url TEXT,
    contact_info JSON, -- Phone, email, address as JSON
    tier INTEGER NOT NULL, -- 1=preferred, 2=acceptable, 3=caution
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Source references for each cost data point
CREATE TABLE source_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cost_pricing_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    reference_type TEXT NOT NULL, -- 'primary', 'validation', 'comparison'
    source_url TEXT NOT NULL,
    product_code TEXT, -- Supplier product code
    quote_number TEXT, -- For direct quotes
    date_accessed DATE NOT NULL,
    screenshot_path TEXT, -- Path to screenshot file
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cost_pricing_id) REFERENCES cost_pricing(id),
    FOREIGN KEY (source_id) REFERENCES sources(id),
    UNIQUE(cost_pricing_id, source_id, reference_type) -- Prevent duplicate references
);

-- ================================
-- DATA VALIDATION TABLES
-- ================================

-- Data validation rules and checks
CREATE TABLE validation_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name TEXT NOT NULL UNIQUE,
    rule_type TEXT NOT NULL, -- 'range_check', 'source_required', 'freshness', etc.
    rule_parameters JSON, -- Rule-specific parameters
    applies_to_category INTEGER, -- NULL for global rules
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (applies_to_category) REFERENCES cost_categories(id)
);

-- Validation results log
CREATE TABLE validation_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cost_pricing_id INTEGER NOT NULL,
    validation_rule_id INTEGER NOT NULL,
    passed BOOLEAN NOT NULL,
    failure_reason TEXT,
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cost_pricing_id) REFERENCES cost_pricing(id),
    FOREIGN KEY (validation_rule_id) REFERENCES validation_rules(id),
    UNIQUE(cost_pricing_id, validation_rule_id) -- Prevent duplicate validation records
);

-- ================================
-- DATA COLLECTION TRACKING
-- ================================

-- Track data collection sessions and progress
CREATE TABLE collection_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_name TEXT NOT NULL,
    milestone TEXT, -- 'milestone_1', 'milestone_2', etc.
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    items_collected INTEGER DEFAULT 0,
    items_validated INTEGER DEFAULT 0,
    status TEXT DEFAULT 'in_progress', -- 'in_progress', 'completed', 'failed'
    notes TEXT,
    UNIQUE(session_name, milestone) -- Prevent duplicate sessions for same milestone
);

-- Log individual data collection activities
CREATE TABLE collection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    cost_item_id INTEGER NOT NULL,
    action_type TEXT NOT NULL, -- 'created', 'updated', 'validated', 'deprecated'
    previous_values JSON, -- Store previous values for updates
    new_values JSON,
    collector_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES collection_sessions(id),
    FOREIGN KEY (cost_item_id) REFERENCES cost_items(id)
);

-- ================================
-- ANALYSIS AND REPORTING VIEWS
-- ================================

-- Current active pricing with source information
CREATE VIEW v_current_pricing AS
SELECT 
    ci.item_id,
    ci.item_name,
    rs.name as revenue_stream,
    cc.name as category,
    cp.unit_cost,
    cp.unit,
    cp.currency,
    cp.total_cost_5000sqft,
    cp.confidence_level,
    cp.effective_date,
    s.company_name as primary_source,
    sr.source_url
FROM cost_items ci
JOIN cost_categories cc ON ci.category_id = cc.id
JOIN revenue_streams rs ON cc.revenue_stream_id = rs.id
JOIN cost_pricing cp ON ci.id = cp.cost_item_id
LEFT JOIN source_references sr ON cp.id = sr.cost_pricing_id AND sr.reference_type = 'primary'
LEFT JOIN sources s ON sr.source_id = s.id
WHERE ci.status = 'active'
AND cp.effective_date = (
    SELECT MAX(effective_date) 
    FROM cost_pricing cp2 
    WHERE cp2.cost_item_id = ci.id
);

-- Cost summary by revenue stream and category
CREATE VIEW v_cost_summary AS
SELECT 
    rs.name as revenue_stream,
    cc.name as category,
    COUNT(ci.id) as item_count,
    AVG(cp.unit_cost) as avg_unit_cost,
    SUM(cp.total_cost_5000sqft) as total_category_cost,
    MIN(cp.confidence_level) as min_confidence,
    MAX(cp.effective_date) as latest_update
FROM revenue_streams rs
JOIN cost_categories cc ON rs.id = cc.revenue_stream_id
JOIN cost_items ci ON cc.id = ci.category_id
JOIN cost_pricing cp ON ci.id = cp.cost_item_id
WHERE ci.status = 'active'
GROUP BY rs.id, cc.id
ORDER BY rs.name, cc.name;

-- Data quality metrics
CREATE VIEW v_data_quality AS
SELECT 
    rs.name as revenue_stream,
    COUNT(ci.id) as total_items,
    SUM(CASE WHEN cp.confidence_level = 'VERIFIED' THEN 1 ELSE 0 END) as verified_items,
    SUM(CASE WHEN cp.confidence_level = 'HIGH' THEN 1 ELSE 0 END) as high_confidence_items,
    SUM(CASE WHEN sr.source_id IS NOT NULL THEN 1 ELSE 0 END) as items_with_sources,
    ROUND(AVG(CASE WHEN cp.confidence_level = 'VERIFIED' THEN 4
                   WHEN cp.confidence_level = 'HIGH' THEN 3
                   WHEN cp.confidence_level = 'MEDIUM' THEN 2
                   ELSE 1 END), 2) as avg_confidence_score
FROM revenue_streams rs
JOIN cost_categories cc ON rs.id = cc.revenue_stream_id
JOIN cost_items ci ON cc.id = ci.category_id
JOIN cost_pricing cp ON ci.id = cp.cost_item_id
LEFT JOIN source_references sr ON cp.id = sr.cost_pricing_id AND sr.reference_type = 'primary'
WHERE ci.status = 'active'
GROUP BY rs.id
ORDER BY rs.name;

-- ================================
-- INITIAL DATA SETUP
-- ================================

-- Insert revenue streams
INSERT INTO revenue_streams (name, code, description, production_target) VALUES
('Grow & Produce', 'grow_produce', 'Indoor greenhouse vanilla cultivation (5000 sq ft, Oregon City, 85°F climate control)', '150 gallons Year 1 extract, 400 gallons total products'),
('Partner & Produce', 'partner_produce', 'White label extract production via processing partners (100+ gallon bulk orders)', 'Outsourced processing with Loran/Lorann, Cooks, Lochhead'),
('Make & Produce', 'make_produce', 'Cell agriculture lab-grown vanilla (Rheaplant service partnership)', '100% quality, high yield target through service provider');

-- Insert supporting operations as a special revenue stream
INSERT INTO revenue_streams (name, code, description, production_target) VALUES
('Supporting Operations', 'supporting_ops', 'Shared costs across all revenue streams', 'Regulatory, marketing, academic research, general business operations');

-- Insert base validation rules
INSERT INTO validation_rules (rule_name, rule_type, rule_parameters) VALUES
('cost_range_check', 'range_check', '{"min_cost": 0.01, "max_cost": 1000000, "currency": "USD"}'),
('source_required', 'source_required', '{"minimum_sources": 1, "prefer_tier_1": true}'),
('data_freshness', 'freshness', '{"max_age_days": 365, "prefer_age_days": 90}'),
('confidence_minimum', 'confidence_check', '{"minimum_level": "MEDIUM"}');

-- ================================
-- INDEXES FOR PERFORMANCE
-- ================================

CREATE INDEX idx_cost_items_category ON cost_items(category_id);
CREATE INDEX idx_cost_items_status ON cost_items(status);
CREATE INDEX idx_cost_pricing_item ON cost_pricing(cost_item_id);
CREATE INDEX idx_cost_pricing_date ON cost_pricing(effective_date);
CREATE INDEX idx_source_references_pricing ON source_references(cost_pricing_id);
CREATE INDEX idx_source_references_type ON source_references(reference_type);
CREATE INDEX idx_collection_log_session ON collection_log(session_id);
CREATE INDEX idx_collection_log_item ON collection_log(cost_item_id);

-- ================================
-- TRIGGERS FOR DATA INTEGRITY
-- ================================

-- Update timestamp trigger for cost_items
CREATE TRIGGER tr_cost_items_updated_at 
AFTER UPDATE ON cost_items
BEGIN
    UPDATE cost_items SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Automatic validation trigger when pricing is inserted/updated
CREATE TRIGGER tr_validate_pricing
AFTER INSERT ON cost_pricing
BEGIN
    INSERT INTO validation_results (cost_pricing_id, validation_rule_id, passed, failure_reason)
    SELECT NEW.id, vr.id, 
           CASE 
               WHEN vr.rule_type = 'range_check' AND (NEW.unit_cost < 0.01 OR NEW.unit_cost > 1000000) THEN 0
               WHEN vr.rule_type = 'confidence_check' AND NEW.confidence_level NOT IN ('MEDIUM', 'HIGH', 'VERIFIED') THEN 0
               ELSE 1
           END,
           CASE 
               WHEN vr.rule_type = 'range_check' AND (NEW.unit_cost < 0.01 OR NEW.unit_cost > 1000000) THEN 'Cost outside acceptable range'
               WHEN vr.rule_type = 'confidence_check' AND NEW.confidence_level NOT IN ('MEDIUM', 'HIGH', 'VERIFIED') THEN 'Confidence level below minimum'
               ELSE NULL
           END
    FROM validation_rules vr 
    WHERE vr.is_active = TRUE;
END;