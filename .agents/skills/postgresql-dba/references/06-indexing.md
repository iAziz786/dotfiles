# Indexing in PostgreSQL

## Index Types

### B-Tree Indexes

B-Tree (short for Balanced Tree) is the default index type in PostgreSQL, designed to work efficiently with a broad range of queries. A B-Tree is a data structure that enables fast search, insertion, and deletion of elements in a sorted order.

**Use for:**
- Equality operators (=)
- Range operators (<, >, <=, >=, BETWEEN)
- Pattern matching with LIKE (prefix only: 'abc%')
- IS NULL / IS NOT NULL

**Example:**
```sql
CREATE INDEX idx_employees_name ON employees(name);
CREATE INDEX idx_employees_salary ON employees(salary);
```

**Resources:**
- [PostgreSQL B-Tree](https://www.postgresql.org/docs/current/indexes-types.html#INDEXES-TYPES-BTREE)
- [Video: B-Tree Indexes](https://www.youtube.com/watch?v=NI9wYuVIYcA&t=109s)

### Hash Indexes

Hash indexes store a hash value of the indexed column. They are best for equality comparisons only.

**Use for:**
- Equality operators (=) only
- Not suitable for range queries or sorting

**Example:**
```sql
CREATE INDEX idx_employees_email_hash ON employees USING HASH(email);
```

**Note:** Since PostgreSQL 10, hash indexes are WAL-logged and crash-safe, but B-tree is still preferred in most cases.

### GiST (Generalized Search Tree)

GiST is a flexible index type that supports various data types and query operations.

**Use for:**
- Geometric data (nearest neighbor searches)
- Full-text search
- Network address types
- Range types

**Example:**
```sql
-- For geometric data
CREATE INDEX idx_locations_point ON locations USING GIST(point_column);

-- For range types
CREATE INDEX idx_events_duration ON events USING GIST(duration);
```

### GIN (Generalized Inverted Index)

GIN indexes are optimized for indexing composite values where elements within the composite are queried.

**Use for:**
- Full-text search
- Array values (searching for elements)
- JSONB documents
- HStore data

**Example:**
```sql
-- For arrays
CREATE INDEX idx_products_tags ON products USING GIN(tags);

-- For JSONB
CREATE INDEX idx_events_metadata ON events USING GIN(metadata);

-- For full-text search
CREATE INDEX idx_articles_search ON articles 
    USING GIN(to_tsvector('english', content));
```

### BRIN (Block Range Index)

BRIN indexes are designed for very large tables with naturally ordered data (like timestamps).

**Use for:**
- Very large tables (hundreds of millions to billions of rows)
- Naturally ordered data (timestamps, IDs)
- When full index would be too large

**Example:**
```sql
CREATE INDEX idx_logs_timestamp ON logs 
    USING BRIN(created_at) WITH (pages_per_range = 128);
```

**Advantages:**
- Very small size compared to B-tree
- Fast sequential scans

**Disadvantages:**
- Only effective for ordered data
- Not suitable for random access patterns

## Index Strategies

### Covering Indexes (INCLUDE)

PostgreSQL 11+ supports covering indexes that include non-key columns:

```sql
CREATE INDEX idx_employees_dept ON employees(department_id) 
    INCLUDE (name, salary);
```

This allows index-only scans for queries that need the included columns without accessing the heap.

### Partial Indexes

Partial indexes only index rows matching a WHERE clause:

```sql
-- Index only active users
CREATE INDEX idx_active_users ON users(email) WHERE active = true;

-- Index high-value orders
CREATE INDEX idx_high_value_orders ON orders(customer_id, total) 
    WHERE total > 1000;
```

**Benefits:**
- Smaller index size
- Faster queries on indexed subset
- Reduced maintenance overhead

### Expression Indexes

Index the result of an expression:

```sql
-- Index on lower case email
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- Index on computed full name
CREATE INDEX idx_employees_fullname ON employees 
    ((first_name || ' ' || last_name));

-- Index on JSONB extraction
CREATE INDEX idx_orders_customer_name ON orders ((metadata->>'customer_name'));
```

### Composite Indexes

Index multiple columns:

```sql
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
```

**Column Order Matters:**
- Most selective column first (generally)
- Columns used in WHERE equality filters before range filters
- Consider query patterns

**Usage Rules:**
- Can use leading columns: `WHERE customer_id = 1`
- Can use full index: `WHERE customer_id = 1 AND order_date > '2024-01-01'`
- Cannot skip leading column: `WHERE order_date > '2024-01-01'` won't use index

## Index Maintenance

### Analyzing Index Usage

```sql
-- Check index usage stats
SELECT 
    schemaname,
    relname as table,
    indexrelname as index,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Find unused indexes
SELECT 
    schemaname,
    relname as table,
    indexrelname as index
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

### Index Bloat Detection

```sql
-- Check for bloated indexes
SELECT 
    schemaname,
    relname as table,
    indexrelname as index,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
    idx_scan as scans
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Reindexing

```sql
-- Reindex a specific index
REINDEX INDEX idx_employees_name;

-- Reindex all indexes on a table
REINDEX TABLE employees;

-- Reindex all indexes in a database
REINDEX DATABASE mydb;

-- Concurrent reindex (minimal locking, PG 12+)
REINDEX INDEX CONCURRENTLY idx_employees_name;
```

### Removing Unused Indexes

```sql
-- Drop an index
DROP INDEX idx_unused_index;

-- Drop if exists
DROP INDEX IF EXISTS idx_unused_index;

-- Drop concurrently (avoids table locks)
DROP INDEX CONCURRENTLY idx_unused_index;
```

## Index Best Practices

### When to Create Indexes

**Create indexes for:**
- Primary keys and foreign keys
- Columns frequently used in WHERE clauses
- Columns used in JOIN conditions
- Columns used in ORDER BY
- Columns with high selectivity (many distinct values)

**Avoid indexes on:**
- Tables with frequent bulk inserts (LOAD performance impact)
- Small tables (sequential scan is faster)
- Columns with low cardinality (few distinct values like boolean)
- Columns rarely queried

### Performance Considerations

1. **Index-only scans**: Include frequently accessed columns in index to avoid heap access
2. **Write performance**: Each index adds overhead to INSERT/UPDATE/DELETE
3. **Storage space**: Indexes can be as large as the table data
4. **Maintenance**: Indexes need periodic REINDEX if bloated

### Indexing for Full-Text Search

```sql
-- Create a GIN index for text search
CREATE INDEX idx_articles_search ON articles 
    USING GIN(to_tsvector('english', content));

-- Query with full-text search
SELECT * FROM articles 
WHERE to_tsvector('english', content) @@ to_tsquery('postgresql');
```

### Indexing for JSONB

```sql
-- GIN index for JSONB (all keys)
CREATE INDEX idx_data_gin ON mytable USING GIN(data);

-- B-tree index on specific key
CREATE INDEX idx_data_name ON mytable ((data->>'name'));
```

### Indexing Arrays

```sql
-- GIN index for array containment
CREATE INDEX idx_tags_gin ON posts USING GIN(tags);

-- Query examples that use the index
SELECT * FROM posts WHERE tags @> ARRAY['postgresql'];
SELECT * FROM posts WHERE 'tutorial' = ANY(tags);
```

## Index Commands Reference

```sql
-- List all indexes on a table
\d table_name

-- Detailed index information
SELECT * FROM pg_indexes WHERE tablename = 'employees';

-- Index size
SELECT pg_size_pretty(pg_relation_size('idx_employees_name'));

-- Check if query uses index
EXPLAIN ANALYZE SELECT * FROM employees WHERE name = 'John';

-- Disable index scan for testing
SET enable_indexscan = off;
```
