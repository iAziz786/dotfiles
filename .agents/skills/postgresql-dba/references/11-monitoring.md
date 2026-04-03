# Monitoring and Maintenance

## System Statistics

PostgreSQL provides comprehensive statistics through `pg_stat_*` views.

### pg_stat_statements

Track query performance and identify slow queries:

```sql
-- Enable pg_stat_statements
-- postgresql.conf:
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all
pg_stat_statements.max = 10000

-- Create extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- View top queries by total time
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    stddev_exec_time,
    rows,
    shared_blks_hit,
    shared_blks_read
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

**Resources:**
- [pg_stat_statements Documentation](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [Optimizing Queries with pg_stat_statements](https://www.timescale.com/blog/using-pg-stat-statements-to-optimize-queries/)

### pg_stat_user_tables

Monitor table access patterns:

```sql
SELECT 
    schemaname,
    relname as table_name,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum,
    last_analyze
FROM pg_stat_user_tables
ORDER BY seq_scan DESC;
```

### pg_stat_user_indexes

Check index usage:

```sql
SELECT 
    schemaname,
    relname as table,
    indexrelname as index,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Find unused indexes
SELECT 
    schemaname,
    relname as table,
    indexrelname as index
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

### pg_statio_user_tables

Monitor buffer/cache activity:

```sql
SELECT 
    schemaname,
    relname as table_name,
    heap_blks_read,
    heap_blks_hit,
    round(100.0 * heap_blks_hit / (heap_blks_hit + heap_blks_read), 2) as cache_hit_ratio
FROM pg_statio_user_tables
WHERE heap_blks_hit + heap_blks_read > 0
ORDER BY heap_blks_read DESC;
```

**Target cache hit ratio: > 99%**

## Vacuum Processing

### Understanding Vacuum

Vacuum processing is essential for maintaining performance. PostgreSQL uses MVCC which creates multiple versions of rows during updates/deletes, resulting in "dead" rows that must be cleaned up.

**What Vacuum Does:**
1. Removes dead tuples (row versions no longer visible)
2. Reclaims storage space
3. Updates visibility map
4. Prevents transaction ID wraparound

### Manual Vacuum

```sql
-- Vacuum specific table
VACUUM ANALYZE employees;

-- Vacuum with verbose output
VACUUM (VERBOSE, ANALYZE) employees;

-- Full vacuum (reclaims more space, but locks table)
VACUUM (FULL) employees;

-- Vacuum all tables
VACUUM;
```

### Autovacuum

Configure automatic vacuum:

```sql
-- postgresql.conf
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.2
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.1

-- Per-table settings
ALTER TABLE large_table SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_scale_factor = 0.05,
    autovacuum_vacuum_cost_limit = 1000
);
```

**Resources:**
- [PostgreSQL Vacuum Guide](https://www.enterprisedb.com/blog/postgresql-vacuum-and-analyze-best-practice-tips)
- [How to Run VACUUM ANALYZE](https://medium.com/@dmitry.romanoff/postgresql-how-to-run-vacuum-analyze-explicitly-5879ec39da47)

### Monitoring Vacuum

```sql
-- Check for tables needing vacuum
SELECT 
    schemaname,
    relname,
    n_dead_tup,
    n_live_tup,
    round(n_dead_tup::numeric/nullif(n_live_tup,0)*100, 2) as dead_pct,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Check vacuum progress (PostgreSQL 9.6+)
SELECT * FROM pg_stat_progress_vacuum;
```

## Logging and Log Analysis

### PostgreSQL Logging Configuration

```sql
-- postgresql.conf
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000  -- Log queries > 1000ms
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
```

### Log Analysis Tools

**pgBadger:**
Fast log analyzer with rich reports:
```bash
pgbadger /var/log/postgresql/postgresql-*.log -o report.html
```

**pganalyze:**
Cloud-based log monitoring and analysis

**Check PostgreSQL Activity:**
```bash
check_pgactivity
```

### Slow Query Identification

```sql
-- Log queries > 1 second
-- postgresql.conf: log_min_duration_statement = 1000

-- Identify slow queries from logs
-- Look for:
-- - duration: 1234.567 ms  statement: SELECT ...

-- Use pg_stat_statements for aggregate data
SELECT 
    query,
    calls,
    mean_exec_time,
    total_exec_time,
    stddev_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC;
```

## Routine Maintenance

### ANALYZE

Update table statistics for the query planner:

```sql
-- Analyze single table
ANALYZE employees;

-- Analyze with verbose output
ANALYZE VERBOSE employees;

-- Analyze all tables
ANALYZE;
```

### REINDEX

Rebuild indexes to remove bloat:

```sql
-- Reindex specific index
REINDEX INDEX idx_employees_name;

-- Reindex table
REINDEX TABLE employees;

-- Reindex database
REINDEX DATABASE mydb;

-- Concurrent reindex (PostgreSQL 12+)
REINDEX INDEX CONCURRENTLY idx_employees_name;
```

### Catalog Maintenance

Check for catalog bloat:

```sql
-- Check catalog table sizes
SELECT 
    relname,
    pg_size_pretty(pg_relation_size(oid)) as size
FROM pg_class
WHERE relkind = 'r'
  AND relnamespace = 'pg_catalog'::regnamespace
ORDER BY pg_relation_size(oid) DESC;
```

## pg_upgrade

Upgrade PostgreSQL to a new major version:

### Standard Upgrade

```bash
# Stop old version
pg_ctl stop -D /var/lib/postgresql/13/main

# Run pg_upgrade
pg_upgrade \
    --old-datadir=/var/lib/postgresql/13/main \
    --new-datadir=/var/lib/postgresql/14/main \
    --old-bindir=/usr/lib/postgresql/13/bin \
    --new-bindir=/usr/lib/postgresql/14/bin \
    --check  # Check mode (dry run)

# Actual upgrade
pg_upgrade \
    --old-datadir=/var/lib/postgresql/13/main \
    --new-datadir=/var/lib/postgresql/14/main \
    --old-bindir=/usr/lib/postgresql/13/bin \
    --new-bindir=/usr/lib/postgresql/14/bin
```

### pg_upgrade Options

- `--link`: Hard links instead of copying (fast, but can't revert)
- `--jobs`: Parallel processing
- `--check`: Verify before running

## Monitoring Tools and Integrations

### Prometheus + Grafana

Popular monitoring stack for PostgreSQL:

**postgres_exporter:**
Exports PostgreSQL metrics for Prometheus:
```bash
# Run exporter
postgres_exporter --config.my-cnf=/etc/postgres_exporter/my.cnf
```

**Metrics to track:**
- Query rate and latency
- Connection count
- Cache hit ratio
- Replication lag
- Lock waits
- Vacuum progress

### pgwatch2

Flexible metrics collector for PostgreSQL:
- Built-in dashboards
- Multiple storage backends
- Configurable metrics

### pgCluu

PostgreSQL cluster utilization:
- Performance reports
- Cluster statistics
- CSV output

### Zabbix

Enterprise monitoring with PostgreSQL templates:
- Query performance
- Table bloat detection
- Connection monitoring

## Maintenance Best Practices

### Daily
- Monitor error logs
- Check replication lag
- Verify backup success
- Monitor connection counts

### Weekly
- Review slow query logs
- Check table bloat levels
- Verify vacuum is running
- Review disk space usage

### Monthly
- Analyze query performance trends
- Review and drop unused indexes
- Check for missing indexes
- Test backup restoration

### Quarterly
- Vacuum full on heavily bloated tables (off-peak)
- Reindex large tables
- Analyze pg_stat_statements trends
- Review and tune configuration

## Alerting

### Key Metrics to Alert On

1. **Replication lag > 30 seconds**
2. **Connection count > 80% of max_connections**
3. **Cache hit ratio < 95%**
4. **Dead tuples > 20% of live tuples**
5. **Disk space > 85%**
6. **Lock waits > 1 minute**
7. **Failed login attempts spike**
8. **Autovacuum workers maxed out**

### Sample Alert Query

```sql
-- Check for long-running queries
SELECT 
    pid,
    now() - query_start as duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - query_start > interval '5 minutes';
```
