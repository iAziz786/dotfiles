# Performance Optimization

## Query Analysis with EXPLAIN

Understanding query performance is crucial. PostgreSQL's `EXPLAIN` command provides insights into query execution plans.

### EXPLAIN Basics

`EXPLAIN` generates a query execution plan without executing the query:

```sql
EXPLAIN SELECT * FROM employees WHERE department_id = 5;
```

`EXPLAIN ANALYZE` executes the query and shows actual timing:

```sql
EXPLAIN ANALYZE SELECT * FROM employees WHERE department_id = 5;
```

### Reading EXPLAIN Output

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM employees 
WHERE department_id = 5 
ORDER BY salary DESC;
```

**Options:**
- `ANALYZE`: Execute query and show actual times
- `BUFFERS`: Show buffer hit/read statistics
- `FORMAT JSON`: JSON output for better analysis
- `COSTS`: Include cost estimates (default)
- `TIMING`: Include timing (for ANALYZE)

**Key Metrics:**
- **Cost**: Estimated execution cost (arbitrary units)
- **Rows**: Estimated/actual rows
- **Width**: Average row width in bytes
- **Time**: Actual execution time (with ANALYZE)
- **Buffers**: Shared/Local read/hit/dirtied/written

### Plan Node Types

**Scan Types:**
- `Seq Scan`: Sequential scan (table scan)
- `Index Scan`: Index scan with heap lookup
- `Index Only Scan`: Index scan without heap lookup
- `Bitmap Index Scan` + `Bitmap Heap Scan`: Bitmap scan

**Join Types:**
- `Nested Loop`: Nested loop join
- `Hash Join`: Hash join (good for large datasets)
- `Merge Join`: Merge join (requires sorted input)

**Other Nodes:**
- `Sort`: Sorting operation
- `Aggregate`: Aggregation (GROUP BY)
- `Gather`: Parallel query coordination

### Plan Analysis Examples

**Good Plan (Using Index):**
```
Index Scan using idx_employees_dept on employees
  Index Cond: (department_id = 5)
  Rows Removed by Index Recheck: 0
  Planning Time: 0.123 ms
  Execution Time: 0.456 ms
```

**Bad Plan (Sequential Scan):**
```
Seq Scan on employees
  Filter: (department_id = 5)
  Rows Removed by Filter: 99995
  Planning Time: 0.089 ms
  Execution Time: 45.234 ms
```

## Performance Tuning Techniques

### Connection Pooling with PgBouncer

PgBouncer is a lightweight connection pooler for PostgreSQL that reduces overhead of establishing connections:

**Key Features:**
- Session pooling
- Transaction pooling
- Statement pooling
- Reduces memory usage
- Improves performance under high connection counts

**Resources:**
- [PgBouncer Website](https://www.pgbouncer.org/)
- [PgBouncer GitHub](https://github.com/pgbouncer/pgbouncer)

**Alternatives:**
- **Pgpool-II**: Connection pooler with load balancing and replication
- **HAProxy**: Load balancer for distributing connections
- **Odyssey**: Multithreaded connection pooler by Yandex

### Buffer Management

PostgreSQL uses shared buffers to cache data:

```sql
-- View buffer statistics
SELECT 
    schemaname,
    relname,
    heap_blks_read,
    heap_blks_hit,
    round(100.0 * heap_blks_hit / (heap_blks_hit + heap_blks_read), 2) as cache_hit_ratio
FROM pg_statio_user_tables
WHERE heap_blks_hit + heap_blks_read > 0
ORDER BY heap_blks_read DESC;
```

**Recommended cache hit ratio: > 99%**

### Checkpoints and Background Writer

Checkpoints write dirty buffers to disk:

**Key Parameters:**
- `checkpoint_timeout`: Time between checkpoints (default 5 min)
- `max_wal_size`: Max WAL size before forcing checkpoint
- `checkpoint_completion_target`: Spread checkpoint I/O (default 0.9)

**Monitor checkpoints:**
```sql
SELECT 
    checkpoints_timed,
    checkpoints_req,
    checkpoint_write_time,
    checkpoint_sync_time
FROM pg_stat_bgwriter;
```

## Configuration Tuning

### Memory Settings

**shared_buffers**: Main memory cache
- Default: 128MB
- Recommended: 25% of RAM (up to 8-16GB)

```sql
ALTER SYSTEM SET shared_buffers = '4GB';
```

**work_mem**: Memory per query operation
- Default: 4MB
- Recommended: 256MB to 1GB (but watch for high connection counts)
- Used for: sorts, hashes, materialized views

```sql
ALTER SYSTEM SET work_mem = '256MB';
```

**maintenance_work_mem**: Memory for maintenance operations
- Default: 64MB
- Recommended: 512MB to 2GB
- Used for: VACUUM, CREATE INDEX, ALTER TABLE

```sql
ALTER SYSTEM SET maintenance_work_mem = '512MB';
```

**effective_cache_size**: Planner's estimate of available cache
- Default: 4GB
- Recommended: 75% of total RAM
- Only affects query planner decisions

```sql
ALTER SYSTEM SET effective_cache_size = '12GB';
```

### Connection Settings

**max_connections**: Maximum concurrent connections
- Default: 100
- Recommended: Keep low (200-500), use connection pooler for more

```sql
ALTER SYSTEM SET max_connections = 200;
```

### WAL and Checkpoint Settings

**wal_buffers**: WAL buffer size
- Default: -1 (auto, typically 1/32 of shared_buffers)
- Usually best to leave as default

**max_wal_size**: Maximum WAL size before forcing checkpoint
- Default: 1GB
- Recommended: 4-16GB for better performance

```sql
ALTER SYSTEM SET max_wal_size = '8GB';
```

**min_wal_size**: Minimum WAL size to maintain
- Default: 80MB
- Recommended: 1-2GB

### Autovacuum Tuning

```sql
-- Make autovacuum more aggressive for large tables
ALTER SYSTEM SET autovacuum_max_workers = 6;
ALTER SYSTEM SET autovacuum_naptime = '10s';
ALTER SYSTEM SET autovacuum_vacuum_threshold = 50;
ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.1;

-- Per-table settings
ALTER TABLE large_table 
SET (autovacuum_vacuum_scale_factor = 0.05,
     autovacuum_analyze_scale_factor = 0.02);
```

### Query Planner Settings

```sql
-- Disable certain plan types for testing
SET enable_seqscan = off;      -- Force index usage
SET enable_nestloop = off;     -- Prefer hash/merge joins
SET enable_hashjoin = off;     -- Prefer nested loop/merge

-- Random page cost (lower for SSD)
ALTER SYSTEM SET random_page_cost = 1.1;  -- SSD
ALTER SYSTEM SET random_page_cost = 4.0;  -- HDD (default)

-- Effective IO concurrency
ALTER SYSTEM SET effective_io_concurrency = 200;  -- SSD
```

## Fine-Grained Tuning

### For OLTP Workloads

- Lower `work_mem` (64-128MB)
- Lower `shared_buffers` relative to RAM
- Enable connection pooling
- Frequent checkpoints
- Aggressive autovacuum

### For OLAP/Data Warehouse

- Higher `work_mem` (512MB-2GB)
- Higher `shared_buffers` (25-40% of RAM)
- Enable parallel query
- Less frequent checkpoints
- Parallel workers:
  ```sql
  ALTER SYSTEM SET max_parallel_workers_per_gather = 8;
  ALTER SYSTEM SET max_parallel_workers = 16;
  ALTER SYSTEM SET max_parallel_maintenance_workers = 4;
  ```

### For Mixed Workloads

Balance settings between OLTP and OLAP needs.

## Monitoring Performance

### Key Views

```sql
-- Slow queries
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Table statistics
SELECT 
    relname,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables
ORDER BY seq_scan DESC;

-- Lock waits
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity 
    ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.relation = blocked_locks.relation
JOIN pg_catalog.pg_stat_activity blocking_activity 
    ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

## Optimization Best Practices

1. **Always use EXPLAIN ANALYZE** to understand query performance
2. **Create appropriate indexes** for WHERE, JOIN, and ORDER BY columns
3. **Keep statistics updated** with ANALYZE
4. **Monitor buffer cache hit ratio** - aim for >99%
5. **Use connection pooling** for high connection counts
6. **Vacuum regularly** to prevent bloat
7. **Partition large tables** (>10M rows typically)
8. **Use appropriate data types** - smaller is faster
9. **Avoid SELECT *** - fetch only needed columns
10. **Batch operations** instead of many single-row operations
