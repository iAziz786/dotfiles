# Advanced Topics

## Extensions

PostgreSQL's extensibility is one of its key strengths.

### PostGIS

Geospatial database extender:

```sql
-- Enable PostGIS
CREATE EXTENSION postgis;

-- Create spatial data
CREATE TABLE places (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location GEOGRAPHY(POINT)
);

-- Insert spatial data
INSERT INTO places (name, location)
VALUES ('Eiffel Tower', ST_MakePoint(2.2945, 48.8584));

-- Spatial queries
SELECT * FROM places
WHERE ST_DWithin(
    location,
    ST_MakePoint(2.3, 48.86),
    10000  -- within 10km
);
```

### pg_stat_statements

Track query statistics (essential for monitoring):

```sql
-- Already covered in monitoring section
-- postgresql.conf:
shared_preload_libraries = 'pg_stat_statements'

-- Create extension
CREATE EXTENSION pg_stat_statements;
```

### pg_trgm

Text similarity and trigram matching:

```sql
-- Enable extension
CREATE EXTENSION pg_trgm;

-- Create trigram index for fuzzy search
CREATE INDEX idx_employees_name_trgm ON employees 
    USING GIN(name gin_trgm_ops);

-- Fuzzy search
SELECT * FROM employees 
WHERE name % 'Johnn'  -- similarity search
LIMIT 5;
```

### btree_gist and btree_gin

Allow B-tree equivalent operators in GiST/GIN indexes:

```sql
CREATE EXTENSION btree_gist;

-- Exclusion constraint using GiST
CREATE TABLE reservations (
    room_id INT,
    during TSTZRANGE,
    EXCLUDE USING GIST (room_id WITH =, during WITH &&)
);
```

### hstore

Key-value store within PostgreSQL:

```sql
CREATE EXTENSION hstore;

-- Create table with hstore
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    attributes hstore
);

-- Insert data
INSERT INTO products (name, attributes)
VALUES ('Laptop', 'brand => "Dell", ram => "16GB", cpu => "i7"');

-- Query hstore
SELECT * FROM products WHERE attributes->'brand' = 'Dell';
SELECT * FROM products WHERE attributes @> 'ram=>16GB';
```

### dblink and postgres_fdw

Cross-database queries:

```sql
-- dblink for ad-hoc queries
CREATE EXTENSION dblink;

SELECT * FROM dblink('host=otherdb user=postgres', 
    'SELECT * FROM remote_table') AS t(id INT, name TEXT);

-- postgres_fdw for persistent connections
CREATE EXTENSION postgres_fdw;

CREATE SERVER foreign_server 
    FOREIGN DATA WRAPPER postgres_fdw 
    OPTIONS (host 'otherhost', dbname 'otherdb');

CREATE USER MAPPING FOR current_user
    SERVER foreign_server
    OPTIONS (user 'remote_user', password 'password');

IMPORT FOREIGN SCHEMA public 
    LIMIT TO (remote_table)
    FROM SERVER foreign_server INTO local_schema;
```

## Programming with PL/pgSQL

### Stored Procedures (PostgreSQL 11+)

```sql
-- Create procedure
CREATE OR REPLACE PROCEDURE transfer_money(
    from_account INT,
    to_account INT,
    amount DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Deduct from source
    UPDATE accounts 
    SET balance = balance - amount 
    WHERE id = from_account;
    
    -- Add to destination
    UPDATE accounts 
    SET balance = balance + amount 
    WHERE id = to_account;
    
    -- Commit is automatic at end of procedure
END;
$$;

-- Call procedure
CALL transfer_money(1, 2, 100.00);
```

### Functions

```sql
-- Create function
CREATE OR REPLACE FUNCTION calculate_bonus(
    employee_id INT,
    performance_rating DECIMAL
)
RETURNS DECIMAL
LANGUAGE plpgsql
AS $$
DECLARE
    base_salary DECIMAL;
    bonus DECIMAL;
BEGIN
    SELECT salary INTO base_salary
    FROM employees
    WHERE id = employee_id;
    
    bonus := base_salary * (performance_rating / 100);
    
    RETURN bonus;
END;
$$;

-- Use function
SELECT name, calculate_bonus(id, 15) as bonus
FROM employees;
```

### Triggers

```sql
-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, new_data)
        VALUES (TG_TABLE_NAME, 'INSERT', row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, old_data, new_data)
        VALUES (TG_TABLE_NAME, 'UPDATE', row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, old_data)
        VALUES (TG_TABLE_NAME, 'DELETE', row_to_json(OLD));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$;

-- Attach trigger
CREATE TRIGGER employees_audit
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger();
```

### Dynamic SQL

```sql
CREATE OR REPLACE FUNCTION get_table_count(table_name TEXT)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    result INTEGER;
BEGIN
    EXECUTE format('SELECT COUNT(*) FROM %I', table_name)
    INTO result;
    
    RETURN result;
END;
$$;
```

## Sharding and Scaling

### Application-Level Sharding

Split data across multiple PostgreSQL instances:

```
Shard 1: IDs 1-1,000,000
Shard 2: IDs 1,000,001-2,000,000
Shard 3: IDs 2,000,001-3,000,000
```

**Sharding Strategies:**
- **Hash Sharding**: Distribute by hash of key
- **Range Sharding**: Distribute by range of key
- **List Sharding**: Distribute by category

### Foreign Data Wrappers (FDW)

Access remote data as if local:

```sql
-- Partition table across servers
CREATE TABLE events (id BIGINT, data JSONB, created_at TIMESTAMP)
    PARTITION BY RANGE (created_at);

-- Create partitions as foreign tables
CREATE TABLE events_2024q1 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

-- Use postgres_fdw for remote partition
CREATE SERVER events_server FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'shard1.internal', dbname 'events');

CREATE FOREIGN TABLE events_2024q1 (
    id BIGINT,
    data JSONB,
    created_at TIMESTAMP
) SERVER events_server;
```

### Read Scaling

Distribute read load across replicas:

```python
# Application-level read replica routing
import random

def get_read_connection():
    replicas = ['replica1', 'replica2', 'replica3']
    return connect_to(random.choice(replicas))

def get_write_connection():
    return connect_to('primary')
```

## Bulk Loading and Data Processing

### COPY Command

Fast bulk data loading:

```sql
-- Load from file
COPY employees FROM '/data/employees.csv' 
    WITH (FORMAT csv, HEADER true);

-- Load to file
COPY (SELECT * FROM employees WHERE department = 'Engineering')
    TO '/data/engineering.csv' WITH CSV HEADER;

-- Load from program
COPY employees FROM PROGRAM 'curl -s https://example.com/data.csv'
    WITH CSV HEADER;
```

### Tips for Fast Loading

1. **Disable indexes temporarily**:
   ```sql
   -- Drop indexes before load
   DROP INDEX idx_employees_name;
   
   -- Load data
   COPY employees FROM '/data/employees.csv' CSV;
   
   -- Recreate index
   CREATE INDEX idx_employees_name ON employees(name);
   ```

2. **Increase maintenance_work_mem**:
   ```sql
   SET maintenance_work_mem = '1GB';
   ```

3. **Disable autovacuum during load**:
   ```sql
   ALTER TABLE employees SET (autovacuum_enabled = false);
   -- Load data...
   ALTER TABLE employees SET (autovacuum_enabled = true);
   ```

4. **Use UNLOGGED tables for staging**:
   ```sql
   CREATE UNLOGGED TABLE staging_data (...);
   -- Load data, process, then insert into permanent table
   ```

## Working with Large Objects

### Large Object Storage

```sql
-- Create large object
SELECT lo_create(0);

-- Import file as large object
SELECT lo_import('/path/to/file.pdf');

-- Export large object to file
SELECT lo_export(12345, '/path/to/output.pdf');

-- Delete large object
SELECT lo_unlink(12345);
```

### Alternative: Bytea

For smaller binary data:

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    name TEXT,
    content BYTEA
);

-- Insert binary data
INSERT INTO documents (name, content)
VALUES ('report.pdf', lo_get(lo_import('/path/to/report.pdf')));
```

## Golden Signals

Key metrics for PostgreSQL health (inspired by Google's SRE book):

### The Four Golden Signals

1. **Latency**: Query response time
   ```sql
   SELECT mean_exec_time FROM pg_stat_statements;
   ```

2. **Traffic**: Query rate and connection count
   ```sql
   SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
   ```

3. **Errors**: Failed queries, deadlocks, locks
   ```sql
   SELECT deadlocks FROM pg_stat_database;
   ```

4. **Saturation**: Resource utilization
   ```sql
   -- Check buffer cache ratio
   -- Check connection saturation
   ```

## Getting Involved in Development

### Contributing to PostgreSQL

1. **Mailing Lists**: pgsql-hackers@postgresql.org
2. **Bug Reporting**: https://www.postgresql.org/support/bugs/
3. **Documentation**: https://www.postgresql.org/docs/current/docguide.html
4. **Patch Submission**: Follow the commitfest process

### Community Resources

- **PostgreSQL Weekly**: Newsletter with updates
- **Planet PostgreSQL**: Aggregated blogs
- **Conferences**: PGCon, Postgres Vision, PGConf events
- **Meetups**: Local PostgreSQL user groups

## Additional Tools

### psql Meta-Commands

```sql
\l              -- List databases
\c database     -- Connect to database
\dt             -- List tables
\d table        -- Describe table
\di             -- List indexes
\du             -- List users
\timing on      -- Enable timing
\x on           -- Expanded display
\pset format    -- Set output format
\copy           -- Copy to/from file
\i file.sql     -- Execute file
\o output.txt   -- Output to file
```

### Command-Line Tools

**psql**: Interactive terminal
```bash
psql -h host -U user -d database
```

**createdb**: Create database
```bash
createdb -h host -U user newdb
```

**dropdb**: Drop database
```bash
dropdb -h host -U user olddb
```

**createuser**: Create user
```bash
createuser -h host -U admin --interactive newuser
```

**reindexdb**: Reindex database
```bash
reindexdb -h host -U user mydb
```

**vacuumdb**: Vacuum database
```bash
vacuumdb -h host -U user -z mydb  # with analyze
```

### Debugging and Profiling

**Core Dumps:**
```bash
# Enable core dumps
ulimit -c unlimited

# Analyze with gdb
gdb /usr/lib/postgresql/14/bin/postgres core.12345
```

**GDB Debugging:**
```bash
# Attach to running process
gdb -p $(pgrep -f "postgres: postgres")

# Common commands
(gdb) bt              -- backtrace
(gdb) info locals     -- local variables
(gdb) continue        -- continue execution
```

**eBPF/BCC:**
Advanced tracing for PostgreSQL internals:
- IO analysis
- Query profiling
- Lock analysis

## Best Practices Summary

1. **Use appropriate data types** for efficiency
2. **Normalize your schema** but denormalize when needed
3. **Create indexes strategically** for query patterns
4. **Monitor and tune** autovacuum settings
5. **Set up replication** for high availability
6. **Test your backups** regularly
7. **Monitor query performance** with pg_stat_statements
8. **Use connection pooling** for high concurrency
9. **Keep PostgreSQL updated** for security patches
10. **Document your setup** and procedures

## Resources

- **Official Documentation**: https://www.postgresql.org/docs/
- **PostgreSQL Wiki**: https://wiki.postgresql.org/
- **Planet PostgreSQL**: https://planet.postgresql.org/
- **Mailing Lists**: https://www.postgresql.org/list/
