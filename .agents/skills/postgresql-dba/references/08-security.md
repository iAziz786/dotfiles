# PostgreSQL Security

## Authentication Models

PostgreSQL supports various authentication models to control access:

### Authentication Methods

**Trust**: No password required (for secure environments only)
- Use for local connections on single-user systems
- Never use for remote connections

**Password Methods**:
- `md5`: MD5-hashed passwords (legacy, not recommended)
- `scram-sha-256`: SCRAM-SHA-256 authentication (recommended)

**GSSAPI/SSPI**: Kerberos for secure single sign-on
- Enterprise environments with Kerberos infrastructure

**LDAP**: Centralized user management
- Integration with corporate directory services

**Certificate-based**: SSL certificates for strong authentication
- Most secure method for remote connections

**PAM**: Leveraging OS-managed authentication
- Pluggable Authentication Modules

**Ident**: Verifying OS user names
- Maps OS users to database users

**RADIUS**: Centralized authentication via RADIUS servers

**Resources:**
- [PostgreSQL Authentication Methods](https://www.postgresql.org/docs/current/auth-methods.html)
- [Intro to Authn and Authz](https://www.prisma.io/dataguide/postgresql/authentication-and-authorization/intro-to-authn-and-authz)

## pg_hba.conf Configuration

The `pg_hba.conf` (PostgreSQL Host-Based Authentication) file controls how clients authenticate and connect to your database.

### File Format

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             all                                     peer

# IPv4 local connections:
host    all             all             127.0.0.1/32            scram-sha-256

# IPv6 local connections:
host    all             all             ::1/128                 scram-sha-256

# Allow remote connections with SSL
hostssl all             all             0.0.0.0/0               cert

# Specific database and user
host    mydb            myuser          192.168.1.0/24          scram-sha-256
```

### Connection Types

- `local`: Unix domain socket
- `host`: TCP/IP (with or without SSL)
- `hostssl`: TCP/IP with SSL only
- `hostnossl`: TCP/IP without SSL

### Address Formats

- IP address: `192.168.1.1`
- CIDR: `192.168.1.0/24`
- Hostname: `myhost.example.com`
- `all`: Matches any address
- `samehost`: Same machine
- `samenet`: Same subnet

**Resources:**
- [pg_hba.conf Documentation](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)

## Authorization and Privileges

### Roles

PostgreSQL uses roles to manage access. Roles can be:
- Individual users (with login)
- Group roles (without login)

```sql
-- Create a role
CREATE ROLE readonly;

-- Create a user (role with login)
CREATE USER app_user WITH PASSWORD 'secure_password';

-- Create superuser
CREATE ROLE admin WITH LOGIN SUPERUSER PASSWORD 'admin_pass';
```

### Grant and Revoke

**Table/Column Privileges:**
```sql
-- Grant table privileges
GRANT SELECT, INSERT ON employees TO app_user;
GRANT ALL PRIVILEGES ON employees TO admin;

-- Grant column-level privilege
GRANT UPDATE (salary) ON employees TO hr_manager;

-- Grant schema usage
GRANT USAGE ON SCHEMA public TO app_user;

-- Revoke privileges
REVOKE INSERT ON employees FROM app_user;
```

**Database Privileges:**
```sql
-- Allow connecting to database
GRANT CONNECT ON DATABASE mydb TO app_user;

-- Allow creating schemas
GRANT CREATE ON DATABASE mydb TO developer;
```

**Sequence Privileges:**
```sql
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
```

**Resources:**
- [PostgreSQL GRANT](https://www.postgresql.org/docs/current/sql-grant.html)
- [PostgreSQL REVOKE](https://www.postgresql.org/docs/current/sql-revoke.html)

### Default Privileges

Set default privileges for objects created in the future:

```sql
-- Set default privileges in schema
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO readonly;

-- For specific role
ALTER DEFAULT PRIVILEGES FOR ROLE developer IN SCHEMA app
GRANT ALL ON TABLES TO app_admin;
```

**Resources:**
- [ALTER DEFAULT PRIVILEGES](https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html)
- [Privileges Documentation](https://www.postgresql.org/docs/current/ddl-priv.html)

### Object Privileges

Common privilege types:
- `SELECT`: Read data
- `INSERT`: Add data
- `UPDATE`: Modify data
- `DELETE`: Remove data
- `TRUNCATE`: Empty table
- `REFERENCES`: Create foreign keys
- `TRIGGER`: Create triggers
- `USAGE`: Use schema/sequence
- `CREATE`: Create objects
- `EXECUTE`: Run functions

## Row-Level Security (RLS)

Row Level Security (RLS), introduced in PostgreSQL 9.5, allows you to control access to rows based on a user or role's permissions.

### Enabling RLS

```sql
-- Enable RLS on a table
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;

-- Force RLS for table owner too
ALTER TABLE employees FORCE ROW LEVEL SECURITY;
```

### Creating Policies

```sql
-- Users can only see their own data
CREATE POLICY user_isolation ON employees
    FOR SELECT
    USING (user_id = current_user_id());

-- Users can only update their own data
CREATE POLICY user_update ON employees
    FOR UPDATE
    USING (user_id = current_user_id());

-- Different policies for different operations
CREATE POLICY manager_sees_team ON employees
    FOR SELECT
    TO manager_role
    USING (department_id IN (
        SELECT department_id FROM departments WHERE manager_id = current_user_id()
    ));
```

### Policy Types

- `ALL`: All operations
- `SELECT`: Read operations
- `INSERT`: Insert operations
- `UPDATE`: Update operations
- `DELETE`: Delete operations

**Resources:**
- [Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Video: Setting up RLS](https://www.youtube.com/watch?v=j53NoW9cPtY)

## SSL and Encryption

### SSL Settings

Configure SSL to encrypt client-server communication:

```sql
-- In postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
ssl_ca_file = 'root.crt'
ssl_crl_file = 'root.crl'

-- SSL mode (prefer, require, verify-ca, verify-full)
ssl_mode = 'prefer'
```

### Client SSL Configuration

Connection strings with SSL:
```
postgresql://user:pass@host/db?sslmode=require
postgresql://user:pass@host/db?sslmode=verify-full&sslrootcert=ca.crt
```

SSL modes:
- `disable`: No SSL
- `allow`: Prefer no SSL, but accept SSL
- `prefer`: Prefer SSL, but accept no SSL
- `require`: Require SSL (no cert verification)
- `verify-ca`: Require SSL and verify CA
- `verify-full`: Require SSL and verify CA + hostname

**Resources:**
- [SSL Support](https://www.postgresql.org/docs/current/libpq-ssl.html)
- [Configure SSL on PostgreSQL](https://www.cherryservers.com/blog/how-to-configure-ssl-on-postgresql)

## Data Encryption

### Encryption at Rest

**Transparent Data Encryption (TDE):**
PostgreSQL doesn't have built-in TDE, but can be achieved through:
- Full disk encryption (LUKS, BitLocker)
- File system encryption (ZFS encryption)
- Volume-level encryption (cloud provider encryption)

**Column-Level Encryption:**
```sql
-- Using pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt data
INSERT INTO users (email, ssn)
VALUES ('user@example.com', pgp_sym_encrypt('123-45-6789', 'secret-key'));

-- Decrypt data
SELECT email, pgp_sym_decrypt(ssn, 'secret-key') as ssn
FROM users;
```

### Encryption in Transit

Always use SSL/TLS for remote connections. Configure pg_hba.conf to require SSL:
```
hostssl all all 0.0.0.0/0 scram-sha-256
```

## Security Best Practices

1. **Use strong authentication**: scram-sha-256 or certificates
2. **Restrict network access**: Use pg_hba.conf carefully
3. **Enable SSL**: For all remote connections
4. **Use row-level security**: For multi-tenant applications
5. **Principle of least privilege**: Grant minimal required permissions
6. **Regular audits**: Monitor pg_stat_activity and logs
7. **Keep updated**: Apply security patches promptly
8. **Encrypt sensitive data**: At rest and in transit
9. **Use connection pooling**: Reduces attack surface
10. **Disable unused features**: Remove unused extensions

## Security Resources

**Best Practices:**
- [PostgreSQL Security Best Practices](https://www.percona.com/blog/postgresql-database-security-best-practices/)
- [Azure PostgreSQL Security](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-security)

**Object Privileges:**
- [PostgreSQL Roles and Privileges](https://www.aviator.co/blog/postgresql-roles-and-privileges-explained/)
- [Managing Privileges](https://www.prisma.io/dataguide/postgresql/authentication-and-authorization/managing-privileges)
