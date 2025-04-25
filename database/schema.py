# Table name
CYCLE_COUNTS_TABLE = "cycle_counts"

# SQL for table creation
CREATE_CYCLE_COUNTS_TABLE = """
CREATE TABLE IF NOT EXISTS cycle_counts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id TEXT NOT NULL,
    description TEXT NOT NULL,
    lot_number TEXT,
    expiration_date DATE,
    unit TEXT,
    status TEXT,
    lp TEXT,
    location TEXT,
    system_count NUMERIC NOT NULL,
    actual_count NUMERIC NOT NULL,
    variance NUMERIC NOT NULL,
    percent_diff NUMERIC NOT NULL,
    customer TEXT NOT NULL,
    notes TEXT,
    cycle_date DATE NOT NULL,
    uploaded_by TEXT NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);
"""

# Column definitions (for reference in application code)
COLUMNS = {
    "id": "id",
    "item_id": "item_id",
    "description": "description",
    "lot_number": "lot_number",
    "expiration_date": "expiration_date",
    "unit": "unit",
    "status": "status",
    "lp": "lp",
    "location": "location",
    "system_count": "system_count",
    "actual_count": "actual_count",
    "variance": "variance",
    "percent_diff": "percent_diff",
    "customer": "customer",
    "notes": "notes",
    "cycle_date": "cycle_date",
    "uploaded_by": "uploaded_by",
    "uploaded_at": "uploaded_at"
} 