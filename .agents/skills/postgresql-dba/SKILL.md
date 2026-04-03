---
name: postgresql-dba
description: Guide users through PostgreSQL database administration learning path - from fundamentals to production operations. Use when users want to learn PostgreSQL, become a DBA, optimize database performance, setup replication, manage backups, secure PostgreSQL instances, or need guidance on any PostgreSQL administration topic.
license: MIT
compatibility: Designed for OpenCode and Claude Code
metadata:
  author: Aziz
  version: "1.0"
  source: https://github.com/kamranahmedse/developer-roadmap/tree/master/src/data/roadmaps/postgresql-dba
  topics_count: 170
---

# PostgreSQL DBA Skill

Comprehensive guide for learning PostgreSQL database administration from beginner to advanced levels.

## When To Use

Activate this skill when the user:
- Wants to "learn PostgreSQL" or "become a PostgreSQL DBA"
- Asks about PostgreSQL performance tuning or optimization
- Needs help with backup and recovery strategies
- Wants to setup PostgreSQL replication or high availability
- Asks about PostgreSQL security, authentication, or authorization
- Needs guidance on indexing strategies or query optimization
- Wants to understand PostgreSQL architecture and internals
- Asks about any PostgreSQL administration topic

## Core Learning Path

The PostgreSQL DBA roadmap is organized into progressive stages:

### 1. Fundamentals

**Relational Database Concepts:**
- RDBMS basics, object model (tables, schemas, databases)
- Relational model (domains, attributes, tuples, relations)
- ACID properties, MVCC, transactions
- Write-ahead logging (WAL) and query processing

**PostgreSQL Basics:**
- Installation (Docker, package managers, cloud)
- psql command-line interface
- Server management (systemd, pg_ctl, pg_ctlcluster)

### 2. SQL Mastery

**Querying Data:**
- SELECT, WHERE, ORDER BY, LIMIT/OFFSET
- JOINs (INNER, LEFT, RIGHT, FULL, CROSS)
- Aggregation (GROUP BY, HAVING, aggregate functions)
- Subqueries and set operations

**Data Modification:**
- INSERT, UPDATE, DELETE, UPSERT
- Transactions and savepoints

**Advanced SQL:**
- Common Table Expressions (CTEs)
- Window functions (ROW_NUMBER, RANK, LAG, LEAD)
- Recursive queries
- Pivoting and unpivoting data

### 3. Schema Design

**Data Types:**
- Numeric, character, date/time, boolean
- JSON/JSONB, arrays, geometric types
- Custom domains and composite types

**Constraints & Integrity:**
- Primary keys, foreign keys, unique, check
- Exclusion constraints
- NOT NULL and DEFAULT values

**Advanced Design:**
- Partitioning strategies (range, list, hash)
- Inheritance
- Normalization and denormalization

### 4. Performance Optimization

**Indexing:**
- B-tree, hash, GiST, GIN indexes
- Partial and expression indexes
- Index selection and maintenance
- Covering indexes (INCLUDE)

**Query Optimization:**
- EXPLAIN and EXPLAIN ANALYZE
- Query planning and execution
- Statistics and analyze
- Vacuum and autovacuum tuning

**Configuration Tuning:**
- Memory settings (shared_buffers, work_mem)
- Connection settings (max_connections)
- Checkpoint and WAL settings
- Fine-grained tuning for workloads

### 5. Security

**Authentication:**
- pg_hba.conf configuration
- Password methods (md5, scram-sha-256)
- LDAP, Kerberos (GSSAPI), RADIUS
- Certificate-based auth (SSL)

**Authorization:**
- Roles and privileges
- Row-Level Security (RLS)
- Column-level permissions
- Database-level security

**Data Protection:**
- SSL/TLS encryption
- Data encryption at rest (TDE)
- Column-level encryption
- Audit logging (pgaudit)

### 6. Backup & Recovery

**Backup Strategies:**
- Logical backups (pg_dump, pg_dumpall)
- Physical backups (pg_basebackup)
- Continuous archiving (WAL archiving)
- Point-in-Time Recovery (PITR)

**Tools & Automation:**
- Barman, pgBackRest, WAL-G
- Backup scheduling and retention
- Backup validation procedures
- pg_verifybackup

### 7. High Availability

**Replication:**
- Streaming replication (async and sync)
- Logical replication (publications/subscriptions)
- Replication slots and failover
- Patroni for automatic failover

**Connection Management:**
- Connection pooling (PgBouncer)
- Load balancing
- Read replicas and routing

### 8. Monitoring & Maintenance

**Monitoring:**
- System statistics (pg_stat_* views)
- pg_stat_statements for query stats
- Logging and log analysis
- Slow query identification

**Routine Maintenance:**
- VACUUM, ANALYZE, REINDEX
- Bloat detection and cleanup
- Catalog maintenance
- pg_upgrade for major version upgrades

### 9. Advanced Topics

**Extensions:**
- PostGIS for geospatial data
- pg_stat_statements, pg_trgm, btree_gist
- Custom extension development

**Programming:**
- PL/pgSQL stored procedures
- Functions, triggers, rules
- Dynamic SQL and cursors

**Scaling:**
- Sharding strategies
- Read scaling with replicas
- Connection pooling at scale
- Partitioning for large tables

## Skill Usage Patterns

### Learning Path Guidance
```
User: "I want to learn PostgreSQL"
Agent: Use this skill to provide a structured learning path starting from fundamentals
```

### Specific Topic Help
```
User: "How do I optimize slow queries?"
Agent: Reference the Performance Optimization section and indexing topics
```

### Problem Solving
```
User: "My backup is failing"
Agent: Reference Backup & Recovery section and troubleshooting guides
```

## Required Inputs

Before providing detailed guidance, the agent should understand:
- **User's experience level** (beginner, intermediate, advanced)
- **Current context** (learning mode vs solving a specific problem)
- **Environment** (self-hosted, cloud, Docker, version)
- **Specific goals** (certification, job preparation, production issue)

## Output Contract

The skill provides:
1. **Structured learning guidance** organized by topic area
2. **Concept explanations** with practical examples
3. **Resource links** to official documentation and tutorials
4. **Hands-on exercises** where applicable
5. **Progressive disclosure** - surface overview first, load details from references/

## Gotchas

- **Version differences**: PostgreSQL features vary significantly between versions (9.x vs 10+ vs 14+). Always clarify version context.
- **Cloud vs self-hosted**: Managed services (RDS, Cloud SQL, Azure) have limitations on superuser access and certain configurations
- **OS differences**: Configuration file locations differ between Linux distributions and Windows
- **Performance tuning is workload-specific**: There is no one-size-fits-all configuration; tuning depends on workload type (OLTP vs OLAP)
- **Backup strategies depend on RTO/RPO**: Recovery Time Objective and Recovery Point Objective determine the right backup approach
- **Replication has trade-offs**: Synchronous replication impacts write performance; async replication risks data loss on failover

## References

Detailed topic guides are available in the `references/` directory:

- `references/01-fundamentals.md` - RDBMS basics, ACID, architecture
- `references/02-installation.md` - Setup and server management
- `references/03-sql-basics.md` - Querying and data modification
- `references/04-advanced-sql.md` - CTEs, window functions, recursion
- `references/05-schema-design.md` - Data types, constraints, partitioning
- `references/06-indexing.md` - Index types, strategies, maintenance
- `references/07-performance.md` - Query optimization, tuning, EXPLAIN
- `references/08-security.md` - Authentication, authorization, encryption
- `references/09-backup-recovery.md` - Backup strategies, PITR, tools
- `references/10-high-availability.md` - Replication, failover, pooling
- `references/11-monitoring.md` - Statistics, logging, maintenance
- `references/12-advanced-topics.md` - Extensions, PL/pgSQL, scaling

Load reference files on demand based on the specific topic being discussed.
