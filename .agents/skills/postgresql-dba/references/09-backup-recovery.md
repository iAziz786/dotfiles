# Backup and Recovery

## Backup Strategies

### Logical Backups

**pg_dump**: Backs up a single database

```bash
# Basic backup
pg_dump -h hostname -U username -d database > backup.sql

# Custom format (compressed, selective restore)
pg_dump -h hostname -U username -d database -Fc > backup.dump

# Directory format (parallel, compressed)
pg_dump -h hostname -U username -d database -Fd -j 4 -f backup_dir

# Specific tables
pg_dump -h hostname -U username -d database -t table1 -t table2 > tables.sql

# Exclude tables
pg_dump -h hostname -U username -d database -T large_table > backup.sql

# Data only (no schema)
pg_dump -h hostname -U username -d database --data-only > data.sql

# Schema only (no data)
pg_dump -h hostname -U username -d database --schema-only > schema.sql
```

**pg_dumpall**: Backs up all databases (including globals)

```bash
# Backup entire cluster
pg_dumpall -h hostname -U postgres > full_backup.sql

# Backup only globals (roles, tablespaces)
pg_dumpall -h hostname -U postgres --globals-only > globals.sql
```

**Resources:**
- [pg_dump Documentation](https://www.postgresql.org/docs/current/app-pgdump.html)

### Physical Backups

**pg_basebackup**: Creates a binary copy of the database cluster

```bash
# Basic base backup
pg_basebackup -h hostname -U replicator -D backup_dir -Fp

# Compressed tar backup
pg_basebackup -h hostname -U replicator -D - -Ft | gzip > backup.tar.gz

# Parallel backup
pg_basebackup -h hostname -U replicator -D backup_dir -Fp -j 4

# Include WAL files
pg_basebackup -h hostname -U replicator -D backup_dir -Fp -X stream

# Create replication slot
pg_basebackup -h hostname -U replicator -D backup_dir -Fp -X stream -S backup_slot -C
```

**Resources:**
- [pg_basebackup Documentation](https://www.postgresql.org/docs/current/app-pgbasebackup.html)

## Restore Methods

### Restoring from pg_dump

```bash
# Plain SQL restore
psql -h hostname -U username -d database < backup.sql

# Custom format restore
pg_restore -h hostname -U username -d database backup.dump

# Selective restore
pg_restore -h hostname -U username -d database -t specific_table backup.dump

# Restore to new database
pg_restore -h hostname -U username -C -d postgres backup.dump

# Parallel restore
pg_restore -h hostname -U username -d database -j 4 backup.dump

# List contents of backup
pg_restore -l backup.dump

# Selective restore by TOC list
pg_restore -L toc_list.txt backup.dump
```

**Resources:**
- [pg_restore Documentation](https://www.postgresql.org/docs/current/app-pgrestore.html)
- [pg_restore Guide](https://www.timescale.com/learn/a-guide-to-pg_restore-and-pg_restore-example)

### Restoring from pg_basebackup

```bash
# Stop PostgreSQL
pg_ctl stop -D /var/lib/postgresql/data

# Remove old data (be careful!)
rm -rf /var/lib/postgresql/data/*

# Restore backup
cp -r backup_dir/* /var/lib/postgresql/data/

# Fix permissions
chown -R postgres:postgres /var/lib/postgresql/data
chmod 700 /var/lib/postgresql/data

# Start PostgreSQL
pg_ctl start -D /var/lib/postgresql/data
```

## Advanced Backup Tools

### Barman (Backup and Recovery Manager)

Barman is a robust tool for managing PostgreSQL backups and disaster recovery:

**Features:**
- Full and incremental backups
- Remote backups
- Backup retention policies
- Compression
- Point-in-time recovery (PITR)
- WAL archiving integration

**Resources:**
- [pgBarman Website](https://www.pgbarman.org/)
- [Barman GitHub](https://github.com/EnterpriseDB/barman)

### pgBackRest

pgBackRest is a comprehensive backup and restore solution:

**Features:**
- Full, differential, and incremental backups
- Parallel processing
- Backup validation
- Compression
- Point-in-time recovery (PITR)
- Encryption
- Remote operations

**Resources:**
- [pgBackRest Documentation](https://pgbackrest.org)
- [pgBackRest GitHub](https://github.com/pgbackrest/pgbackrest)

### WAL-G

WAL-G is an advanced backup and recovery tool for PostgreSQL:

**Features:**
- Delta backups
- Compression and encryption
- Cloud storage integration (S3, GCS, Azure)
- Deduplication
- Continuous archiving
- Point-in-time recovery

**Resources:**
- [WAL-G GitHub](https://github.com/wal-g/wal-g)
- [Continuous PostgreSQL Backups using WAL-G](https://supabase.com/blog/continuous-postgresql-backup-walg)

### pg_probackup

pg_probackup is a backup and recovery manager for PostgreSQL:

**Features:**
- Incremental backups
- Merge strategies
- Validation
- Parallelization
- Backup from standby
- Remote operations
- Compression

**Resources:**
- [pg_probackup GitHub](https://github.com/postgrespro/pg_probackup)
- [PostgresPro pg_probackup](https://postgrespro.com/products/extensions/pg_probackup)

## Continuous Archiving and PITR

### Write Ahead Log (WAL)

The Write Ahead Log is crucial for data consistency and recovery:

**Key Concepts:**
- Records all changes before writing to data files
- Used for crash recovery
- Enables point-in-time recovery

**WAL Configuration:**
```sql
-- In postgresql.conf
wal_level = replica          -- minimal, replica, or logical
archive_mode = on
archive_command = 'cp %p /wal_archive/%f'
max_wal_size = '2GB'
min_wal_size = '1GB'
```

**Resources:**
- [WAL Documentation](https://www.postgresql.org/docs/current/wal-intro.html)
- [Working With Postgres WAL](https://hevodata.com/learn/working-with-postgres-wal/)

### Point-in-Time Recovery (PITR)

PITR allows recovering to a specific moment in time:

**Setup:**
```sql
-- postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'
archive_timeout = 600
```

**Recovery Process:**
1. Stop PostgreSQL
2. Restore base backup
3. Create recovery.conf (PG < 12) or recovery.signal (PG >= 12)
4. Configure restore command
5. Start PostgreSQL

**recovery.conf / postgresql.conf (PG12+):**
```
restore_command = 'cp /path/to/archive/%f %p'
recovery_target_time = '2024-01-15 14:30:00'
recovery_target_action = 'promote'
```

## Backup Validation

### Importance of Validation

It's not enough to just take backups; you must also ensure that your backups are valid and restorable. A corrupt or incomplete backup can lead to data loss or downtime during a crisis.

### Key Validation Procedures

**Restore Test:**
Regularly perform a restore test using your backups to ensure that the backup files can be used for a successful restoration. This process can be automated using scripts and scheduled tasks.

**Checksum Verification:**
Use checksums during the backup process to validate the backed-up data. Checksums can help detect errors caused by corruption or data tampering. PostgreSQL provides built-in checksum support, which can be enabled at the database level.

**File-Level Validation:**
Compare the files in your backup with the source files in your PostgreSQL database. This will ensure that your backup contains all the necessary files and that their content matches the original data.

**Backup Logs Monitoring:**
Monitor and analyze the logs generated during your PostgreSQL backup process. Pay close attention to any warnings, errors, or unusual messages. Investigate and resolve any issues to maintain the integrity of your backups.

**Automated Testing:**
Set up automated tests to simulate a disaster recovery scenario and see if your backup can restore the database fully. This will not only validate your backups but also test the overall reliability of your recovery plan.

### Post-validation Actions

After validating your backups, it's essential to document the results and address any issues encountered during the validation process. This may involve refining your backup and recovery strategies, fixing any errors or updating your scripts and tools.

**Tools:**
- [pg_verifybackup](https://www.postgresql.org/docs/current/app-pgverifybackup.html)
- [PostgreSQL Backup and Restore Validation](https://portal.nutanix.com/page/documents/solutions/details?targetId=NVD-2155-Nutanix-Databases:postgresql-backup-and-restore-validation.html)

## Backup Best Practices

### Strategy Planning

1. **Determine RPO/RTO:**
   - Recovery Point Objective: How much data can you afford to lose?
   - Recovery Time Objective: How quickly must you recover?

2. **Backup Types:**
   - Daily full logical backups for small databases
   - Weekly full physical backups + continuous WAL for large databases
   - Retention: 7-30 days typically, longer for compliance

3. **Storage:**
   - Keep backups in multiple locations
   - Store offsite or in cloud storage
   - Encrypt sensitive backups

4. **Automation:**
   - Schedule backups using cron/systemd
   - Automate validation testing
   - Set up monitoring and alerting

### Backup Script Example

```bash
#!/bin/bash
# Backup script with rotation

BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="mydb"
RETENTION_DAYS=7

# Create backup
pg_dump -Fc $DB_NAME > $BACKUP_DIR/${DB_NAME}_${DATE}.dump

# Verify backup
if pg_restore -l $BACKUP_DIR/${DB_NAME}_${DATE}.dump > /dev/null 2>&1; then
    echo "Backup verified successfully"
else
    echo "Backup verification failed!" >&2
    exit 1
fi

# Clean old backups
find $BACKUP_DIR -name "${DB_NAME}_*.dump" -mtime +$RETENTION_DAYS -delete

# Upload to cloud (example with AWS S3)
aws s3 cp $BACKUP_DIR/${DB_NAME}_${DATE}.dump s3://my-backup-bucket/postgresql/
```

## Disaster Recovery

### Recovery Scenarios

**Scenario 1: Accidental Data Deletion**
```sql
-- If within retention window, use PITR
-- Restore to before deletion, extract data, reinsert
```

**Scenario 2: Hardware Failure**
```bash
# Restore from latest physical backup + WAL
# Or restore to new server, redirect application
```

**Scenario 3: Database Corruption**
```bash
# Restore from last known good backup
# Consider PITR if corruption time is known
```

### Testing Recovery Procedures

1. **Quarterly DR drills:**
   - Simulate various failure scenarios
   - Time your recovery procedures
   - Document lessons learned

2. **Documentation:**
   - Keep recovery runbooks updated
   - Store offline (don't rely on the database!)
   - Include contact information

3. **Automation:**
   - Script common recovery procedures
   - Pre-stage backup files for critical systems
   - Practice automated failover
