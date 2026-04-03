# Schema Design

## Database Objects

### Databases

A PostgreSQL server can host multiple databases:

```sql
-- Create database
CREATE DATABASE mydb
    WITH 
    OWNER = myuser
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Connect to database
\c mydb

-- Drop database
DROP DATABASE mydb;
```

### Schemas

Schemas are namespaces that contain named objects (tables, views, functions, etc.):

```sql
-- Create schema
CREATE SCHEMA myschema;

-- Create table in specific schema
CREATE TABLE myschema.mytable (id INT, name TEXT);

-- Set search path
SET search_path TO myschema, public;

-- Drop schema (with all objects)
DROP SCHEMA myschema CASCADE;
```

### Tables

```sql
-- Create table
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    department_id INTEGER,
    salary DECIMAL(10,2),
    hire_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

-- Alter table
ALTER TABLE employees
    ADD COLUMN phone VARCHAR(20),
    DROP COLUMN phone,
    ALTER COLUMN name TYPE VARCHAR(150),
    RENAME TO staff;

-- Drop table
DROP TABLE employees;
```

## Constraints

### Types of Constraints

**Primary Key:**
```sql
-- Single column
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT
);

-- Composite primary key
CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    PRIMARY KEY (order_id, product_id)
);
```

**Foreign Key:**
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    total DECIMAL(10,2)
);

-- With explicit constraint
ALTER TABLE orders
ADD CONSTRAINT fk_orders_user
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE SET NULL
ON UPDATE CASCADE;
```

Foreign key actions:
- `CASCADE`: Propagate operation to referenced rows
- `SET NULL`: Set referencing column to NULL
- `SET DEFAULT`: Set to default value
- `RESTRICT`: Prevent operation
- `NO ACTION`: Similar to RESTRICT but deferred check

**Unique Constraint:**
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE,
    name TEXT
);

-- Table-level unique
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    UNIQUE (first_name, last_name)
);
```

**Check Constraint:**
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    price DECIMAL(10,2) CHECK (price > 0),
    quantity INTEGER CHECK (quantity >= 0),
    status TEXT CHECK (status IN ('active', 'inactive', 'discontinued'))
);

-- Named check constraint
ALTER TABLE employees
ADD CONSTRAINT chk_salary_positive
CHECK (salary > 0);
```

**Not Null Constraint:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    phone TEXT  -- nullable
);
```

**Default Values:**
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending',
    counter INTEGER DEFAULT 0
);

-- Use default explicitly
INSERT INTO events (name, created_at)
VALUES ('My Event', DEFAULT);
```

**Exclusion Constraints:**

Used to ensure no overlapping ranges or conflicting entries:
```sql
CREATE TABLE room_reservations (
    room_id INTEGER,
    during TSTZRANGE,
    EXCLUDE USING GIST (room_id WITH =, during WITH &&)
);
```

## Data Types Deep Dive

### Enumerations

```sql
-- Create enum type
CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');

-- Use in table
CREATE TABLE person (
    name TEXT,
    current_mood mood
);

-- Add value to enum
ALTER TYPE mood ADD VALUE 'excited' AFTER 'happy';
```

### Composite Types

```sql
-- Create composite type
CREATE TYPE address AS (
    street TEXT,
    city TEXT,
    zip TEXT
);

-- Use in table
CREATE TABLE contacts (
    name TEXT,
    home_address address
);

-- Access fields
SELECT (home_address).city FROM contacts;
```

### Arrays

```sql
-- Array column
CREATE TABLE posts (
    title TEXT,
    tags TEXT[]
);

-- Insert array
INSERT INTO posts (title, tags)
VALUES ('PostgreSQL Tips', ARRAY['database', 'sql', 'tips']);

-- Array operations
SELECT * FROM posts WHERE 'sql' = ANY(tags);
SELECT * FROM posts WHERE tags @> ARRAY['database'];
```

### JSON and JSONB

```sql
-- JSON vs JSONB
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    data JSON,    -- Stored as text
    metadata JSONB  -- Stored in binary, indexable
);

-- Insert JSON
INSERT INTO events (metadata)
VALUES ('{"user": "john", "action": "login", "ip": "192.168.1.1"}');

-- Query JSONB
SELECT * FROM events WHERE metadata->>'user' = 'john';
SELECT metadata->'action' FROM events;

-- Update JSONB
UPDATE events 
SET metadata = metadata || '{"browser": "Chrome"}'::jsonb;

-- Index JSONB
CREATE INDEX idx_metadata_user ON events ((metadata->>'user'));
```

## Partitioning

### Types of Partitioning

**Range Partitioning:**
```sql
-- Create partitioned table
CREATE TABLE measurements (
    city_id INTEGER,
    logdate DATE NOT NULL,
    peaktemp INTEGER,
    unitsales INTEGER
) PARTITION BY RANGE (logdate);

-- Create partitions
CREATE TABLE measurements_y2023 PARTITION OF measurements
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE measurements_y2024 PARTITION OF measurements
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- Default partition (catches anything else)
CREATE TABLE measurements_default PARTITION OF measurements DEFAULT;
```

**List Partitioning:**
```sql
CREATE TABLE orders (
    order_id SERIAL,
    country TEXT,
    amount DECIMAL(10,2)
) PARTITION BY LIST (country);

CREATE TABLE orders_us PARTITION OF orders
    FOR VALUES IN ('US', 'USA', 'United States');

CREATE TABLE orders_eu PARTITION OF orders
    FOR VALUES IN ('UK', 'DE', 'FR', 'ES', 'IT');
```

**Hash Partitioning:**
```sql
CREATE TABLE transactions (
    id BIGSERIAL,
    user_id INTEGER,
    amount DECIMAL(10,2)
) PARTITION BY HASH (user_id);

-- Create 4 partitions
CREATE TABLE transactions_p0 PARTITION OF transactions
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE transactions_p1 PARTITION OF transactions
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE transactions_p2 PARTITION OF transactions
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE transactions_p3 PARTITION OF transactions
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

### Partition Maintenance

```sql
-- Attach existing table as partition
ALTER TABLE measurements
ATTACH PARTITION measurements_y2025
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Detach partition
ALTER TABLE measurements DETACH PARTITION measurements_y2023;

-- Drop partition (and its data)
DROP TABLE measurements_y2023;

-- Check partition information
SELECT 
    schemaname, tablename, 
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE tablename LIKE 'measurements%';
```

## Inheritance

PostgreSQL supports table inheritance, though partitioning is often preferred:

```sql
-- Parent table
CREATE TABLE cities (
    name TEXT,
    population INTEGER,
    altitude INTEGER
);

-- Child tables
CREATE TABLE capitals (
    state CHAR(2)
) INHERITS (cities);

-- Query parent includes children
SELECT * FROM cities;  -- Includes capitals

-- Query only parent
SELECT * FROM ONLY cities;  -- Excludes capitals
```

## Normalization vs Denormalization

**Normalization Goals:**
- Eliminate data redundancy
- Ensure data integrity
- Support ACID properties
- Typical forms: 1NF, 2NF, 3NF, BCNF

**When to Denormalize:**
- Read-heavy workloads with expensive joins
- Pre-computed aggregations
- Data warehousing and analytics
- Use materialized views or triggers to maintain

## Best Practices

1. **Choose appropriate data types** - Use the most specific type possible
2. **Use constraints** - Enforce data integrity at the database level
3. **Design for access patterns** - Index columns used in WHERE, JOIN, ORDER BY
4. **Consider partitioning** - For large tables (>10M rows typically)
5. **Use schemas** - Organize objects logically
6. **Document with comments**:
   ```sql
   COMMENT ON TABLE employees IS 'Staff information';
   COMMENT ON COLUMN employees.salary IS 'Annual base salary';
   ```
