# High Availability and Replication

## Streaming Replication

Streaming Replication is a powerful feature in PostgreSQL that allows efficient real-time replication of data across multiple servers. It ensures high availability and fault tolerance, as well as facilitates load balancing for read-heavy workloads.

### Architecture

- **Primary Server**: Processes write operations and streams changes
- **Standby Servers**: Apply changes from primary, serve read queries
- **Unidirectional**: Data flows only from primary to standbys
- **Asynchronous**: By default, standby may lag behind primary

### Setup Process

**1. Configure Primary:**

```sql
-- postgresql.conf
wal_level = replica
max_wal_senders = 10
wal_keep_size = '1GB'
max_replication_slots = 10

-- pg_hba.conf
host replication replicator 192.168.1.0/24 scram-sha-256
```

**2. Create Replication User:**

```sql
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'secure_password';
```

**3. Base Backup:**

```bash
pg_basebackup -h primary -U replicator -D /var/lib/postgresql/data -Fp -Xs -P
```

**4. Configure Standby:**

```bash
# Create standby.signal (PostgreSQL 12+)
touch /var/lib/postgresql/data/standby.signal

# Configure connection to primary
# postgresql.auto.conf or postgresql.conf:
primary_conninfo = 'host=primary port=5432 user=replicator password=secure_password'
```

**Resources:**
- [Streaming Replication Wiki](https://wiki.postgresql.org/wiki/Streaming_Replication)
- [Video: Postgres Streaming Replication](https://www.youtube.com/watch?v=nnnAmq34STc)

### Synchronous Replication

For zero data loss, configure synchronous replication:

```sql
-- postgresql.conf
synchronous_commit = remote_apply
synchronous_standby_names = 'standby1, standby2'
```

This ensures commits wait until acknowledged by standbys, but impacts write performance.

## Logical Replication

Logical replication allows selective replication of data between databases:

### Key Features

- **Granular Control**: Replicate individual tables
- **Cross-version**: Different PostgreSQL versions possible
- **Multi-master**: Write to multiple nodes (with caveats)
- **Selective**: Filter rows and columns

### Architecture

- **Publication**: Defines changes to replicate (source)
- **Subscription**: Subscribes to changes (target)
- **Replication Slot**: Tracks replication progress

### Setup Example

**On Primary:**
```sql
-- Enable logical replication (wal_level must be 'logical')
-- postgresql.conf: wal_level = logical

-- Create publication
CREATE PUBLICATION mypub FOR TABLE users, orders;

-- Or all tables
CREATE PUBLICATION all_tables FOR ALL TABLES;
```

**On Subscriber:**
```sql
-- Create subscription
CREATE SUBSCRIPTION mysub 
CONNECTION 'host=primary port=5432 user=replicator password=pass dbname=mydb'
PUBLICATION mypub;

-- Check status
SELECT * FROM pg_stat_subscription;
```

### Replication Management

```sql
-- Add table to publication
ALTER PUBLICATION mypub ADD TABLE new_table;

-- Remove table
ALTER PUBLICATION mypub DROP TABLE old_table;

-- Disable subscription
ALTER SUBSCRIPTION mysub DISABLE;

-- Enable subscription
ALTER SUBSCRIPTION mysub ENABLE;

-- Resynchronize table
ALTER SUBSCRIPTION mysub REFRESH PUBLICATION;

-- Drop subscription
DROP SUBSCRIPTION mysub;
```

**Resources:**
- [Logical Replication Documentation](https://www.postgresql.org/docs/current/logical-replication.html)
- [Logical Replication Explained](https://www.enterprisedb.com/postgres-tutorials/logical-replication-postgresql-explained)
- [How to Start Logical Replication](https://www.percona.com/blog/how-to-start-logical-replication-in-postgresql-for-specific-tables-based-on-a-pg-dump/)

## Patroni: Automatic Failover

Patroni automates the setup, management, and failover of PostgreSQL clusters:

### Features

- **High Availability**: Automatic failover in seconds
- **Distributed Consensus**: Uses etcd, Consul, or ZooKeeper
- **Leader Election**: Automatic primary promotion
- **Monitoring**: Health checks and status reporting
- **Flexible**: Supports various replication methods

### Architecture

```
Application → HAProxy/Load Balancer → Patroni-managed PostgreSQL nodes
                       ↓
              etcd/Consul/ZooKeeper (distributed config)
```

### Alternatives to Patroni

**Stolon:**
- Cloud-native PostgreSQL high availability
- Kubernetes integration
- [Stolon GitHub](https://github.com/sorintlab/stolon)

**Repmgr:**
- Replication management and failover
- By 2ndQuadrant
- [Repmgr Website](https://repmgr.org/)

**Pgpool-II:**
- Connection pooling + load balancing + replication
- [Pgpool Website](https://www.pgpool.net/)

**PAF (PostgreSQL Automatic Failover):**
- Uses Pacemaker and Corosync
- By Dalibo
- [PAF GitHub](https://github.com/dalibo/PAF)

**Resources:**
- [Patroni GitHub](https://github.com/zalando/patroni)
- [Patroni Alternatives](https://github.com/zalando/patroni/blob/master/docs/releases.rst)

## Connection Pooling

### PgBouncer

PgBouncer is a lightweight connection pooler for PostgreSQL:

**Pooling Modes:**
- **Session**: Connection held for entire session
- **Transaction**: Connection per transaction (recommended)
- **Statement**: Connection per statement

**Benefits:**
- Reduces connection overhead
- Handles thousands of client connections
- Lowers memory usage
- Improves performance

**Configuration Example:**
```ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_port = 6432
listen_addr = 0.0.0.0
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 10000
default_pool_size = 20
```

**Resources:**
- [PgBouncer Website](https://www.pgbouncer.org/)
- [PgBouncer GitHub](https://github.com/pgbouncer/pgbouncer)

### PgBouncer Alternatives

**Odyssey:**
- Multithreaded connection pooler by Yandex
- Advanced routing capabilities
- [Odyssey GitHub](https://github.com/yandex/odyssey)

**Pgpool-II:**
- Connection pooling with load balancing
- Query caching
- Replication
- [Pgpool Website](https://www.pgpool.net/)

**HAProxy:**
- TCP load balancer
- Health checks
- SSL/TLS support
- [HAProxy Website](http://www.haproxy.org/)

## Failover and Switchover

### Manual Switchover (Planned)

```sql
-- On standby (PostgreSQL 12+)
SELECT pg_promote();

-- Or using pg_ctl
pg_ctl promote -D /var/lib/postgresql/data
```

### Automatic Failover

Use tools like Patroni, Repmgr, or Pacemaker for automatic failover.

### Handling Split-Brain

**Split-brain** occurs when both old and new primaries accept writes:

**Prevention:**
- Use fencing/STONITH (Shoot The Other Node In The Head)
- Configure Patroni/repmgr properly
- Use etcd/Consul for leader election

### Connection String Management

**Service Discovery:**
```
# Connection through PgBouncer
postgresql://user:pass@pgbouncer-host:6432/mydb

# Connection through HAProxy
postgresql://user:pass@haproxy-host:5432/mydb
```

**Application-Level Handling:**
```python
# Example with retry logic
import psycopg2
from psycopg2 import OperationalError

def connect_with_retry(conn_string, max_retries=3):
    for i in range(max_retries):
        try:
            return psycopg2.connect(conn_string)
        except OperationalError:
            if i == max_retries - 1:
                raise
            time.sleep(1)
```

## Monitoring Replication

### Viewing Replication Status

```sql
-- On primary
SELECT 
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;

-- On standby
SELECT 
    status,
    received_lsn,
    latest_end_lsn,
    latest_end_time,
    reply_time
FROM pg_stat_wal_receiver;

-- Check replication lag
SELECT 
    EXTRACT(EPOCH FROM (now() - backend_start)) as lag_seconds
FROM pg_stat_replication;
```

### Replication Slots

```sql
-- Create replication slot
SELECT pg_create_physical_replication_slot('standby_slot', true);

-- Use in pg_basebackup
pg_basebackup -h primary -U replicator -D /data -X stream -S standby_slot

-- Monitor slots
SELECT 
    slot_name,
    plugin,
    slot_type,
    database,
    active,
    restart_lsn,
    confirmed_flush_lsn
FROM pg_replication_slots;

-- Drop slot when no longer needed
SELECT pg_drop_replication_slot('standby_slot');
```

## Best Practices for HA

1. **Monitor replication lag**: Alert if > 30 seconds
2. **Test failover regularly**: Quarterly DR drills
3. **Use synchronous replication only when needed**: Impacts write performance
4. **Keep standbys up to date**: Same hardware/specs as primary
5. **Multiple standbys**: For read scaling and redundancy
6. **Automate failover**: Use Patroni or similar tools
7. **Connection pooling**: Reduces connection storms during failover
8. **Application retry logic**: Handle transient connection failures
9. **Backup from standby**: Reduce primary load
10. **Document procedures**: Keep runbooks updated
