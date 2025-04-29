# # OLD Table name
# CYCLE_COUNTS_TABLE = "cycle_counts"

# # SQL for table creation
# CREATE_CYCLE_COUNTS_TABLE = """
# CREATE TABLE IF NOT EXISTS cycle_counts (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     item_id TEXT NOT NULL,
#     description TEXT NOT NULL,
#     lot_number TEXT,
#     expiration_date DATE,
#     unit TEXT,
#     status TEXT,
#     lp TEXT,
#     location TEXT,
#     system_count NUMERIC NOT NULL,
#     actual_count NUMERIC NOT NULL,
#     variance NUMERIC NOT NULL,
#     percent_diff NUMERIC NOT NULL,
#     customer TEXT NOT NULL,
#     notes TEXT,
#     cycle_date DATE NOT NULL,
#     uploaded_by TEXT NOT NULL,
#     uploaded_at TIMESTAMP NOT NULL DEFAULT NOW()
# );
# """

# New schema
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

# Table names
CYCLE_COUNTS_TABLE = "cycle_counts"
WAREHOUSES_TABLE = "warehouses"
USERS_TABLE = "users"

# SQL to create warehouses table
CREATE_WAREHOUSES_TABLE = """
CREATE TABLE IF NOT EXISTS warehouses (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

# SQL to create users table
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'manager')),
    warehouse_id INTEGER REFERENCES warehouses(id),
    created_at TIMESTAMP DEFAULT NOW()
);
"""

# SQL to create cycle_counts table
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
    location TEXT NOT NULL,
    system_count NUMERIC NOT NULL,
    actual_count NUMERIC NOT NULL,
    variance NUMERIC NOT NULL,
    percent_diff NUMERIC NOT NULL,
    customer TEXT NOT NULL,
    notes TEXT,
    cycle_date DATE NOT NULL,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    warehouse_id INTEGER REFERENCES warehouses(id) NOT NULL
);
"""

# Column dictionary mappings (for application reference if needed)
CYCLE_COUNTS_COLUMNS = {
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
    "uploaded_at": "uploaded_at",
    "warehouse_id": "warehouse_id"
}

WAREHOUSES_COLUMNS = {
    "id": "id",
    "name": "name",
    "address": "address",
    "created_at": "created_at"
}

USERS_COLUMNS = {
    "id": "id",
    "username": "username",
    "name": "name",
    "role": "role",
    "warehouse_id": "warehouse_id",
    "created_at": "created_at"
}
