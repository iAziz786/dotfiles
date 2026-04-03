# SQL Basics

## Data Types in PostgreSQL

PostgreSQL offers a rich and diverse set of data types, catering to a wide range of applications and ensuring data integrity and performance.

### Standard Data Types

**Numeric:**
- `SMALLINT`, `INTEGER`, `BIGINT`: Integer types
- `DECIMAL`, `NUMERIC`: Exact precision decimal
- `REAL`, `DOUBLE PRECISION`: Floating point
- `SERIAL`, `BIGSERIAL`: Auto-incrementing integers

**Character:**
- `CHAR(n)`: Fixed-length character string
- `VARCHAR(n)`: Variable-length with limit
- `TEXT`: Variable unlimited length

**Temporal:**
- `DATE`: Date (no time)
- `TIME`: Time of day
- `TIMESTAMP`: Date and time
- `TIMESTAMPTZ`: Date and time with time zone
- `INTERVAL`: Time interval

**Boolean:**
- `BOOLEAN`: TRUE, FALSE, NULL

**Binary:**
- `BYTEA`: Binary data

### Advanced Data Types

**JSON:**
- `JSON`: Stores JSON as text
- `JSONB`: Binary JSON, supports indexing

**Arrays:**
- Any type can be array: `INTEGER[]`, `TEXT[]`

**Geometric:**
- `POINT`, `LINE`, `LSEG`, `BOX`, `PATH`, `POLYGON`, `CIRCLE`

**Network:**
- `CIDR`, `INET`, `MACADDR`

**Text Search:**
- `TSVECTOR`: Document for text search
- `TSQUERY`: Text search query

**UUID:**
- `UUID`: Universally unique identifier

**Learn More:**
- [PostgreSQL Data Types](https://www.postgresql.org/docs/current/datatype.html)
- [Introduction to PostgreSQL Data Types](https://www.prisma.io/dataguide/postgresql/introduction-to-data-types)

## Querying Data

### SELECT Statement

The fundamental query operation:

```sql
-- Basic SELECT
SELECT * FROM table_name;

-- Select specific columns
SELECT column1, column2 FROM table_name;

-- With alias
SELECT column1 AS alias_name FROM table_name;

-- DISTINCT values
SELECT DISTINCT column1 FROM table_name;
```

### Filtering Data

**WHERE Clause:**
```sql
SELECT * FROM table_name
WHERE condition;
```

**Comparison Operators:**
- `=`: Equal
- `!=` or `<>`: Not equal
- `>`: Greater than
- `<`: Less than
- `>=`: Greater than or equal
- `<=`: Less than or equal
- `BETWEEN`: Within range
- `IN`: Match any in list
- `LIKE`: Pattern matching
- `IS NULL`: Check for NULL

**Logical Operators:**
- `AND`: Both conditions must be true
- `OR`: Either condition can be true
- `NOT`: Negate condition

### Sorting Results

**ORDER BY:**
```sql
SELECT * FROM table_name
ORDER BY column1 ASC, column2 DESC;
```

### Limiting Results

```sql
-- LIMIT and OFFSET
SELECT * FROM table_name
ORDER BY column1
LIMIT 10 OFFSET 20;

-- FETCH syntax (SQL standard)
SELECT * FROM table_name
ORDER BY column1
OFFSET 20 ROWS
FETCH NEXT 10 ROWS ONLY;
```

## Joins

### Types of Joins

**INNER JOIN:** Returns matching rows from both tables
```sql
SELECT a.*, b.*
FROM table_a a
INNER JOIN table_b b ON a.id = b.a_id;
```

**LEFT JOIN:** Returns all rows from left table, matching from right
```sql
SELECT a.*, b.*
FROM table_a a
LEFT JOIN table_b b ON a.id = b.a_id;
```

**RIGHT JOIN:** Returns all rows from right table, matching from left
```sql
SELECT a.*, b.*
FROM table_a a
RIGHT JOIN table_b b ON a.id = b.a_id;
```

**FULL OUTER JOIN:** Returns all rows from both tables
```sql
SELECT a.*, b.*
FROM table_a a
FULL OUTER JOIN table_b b ON a.id = b.a_id;
```

**CROSS JOIN:** Cartesian product of both tables
```sql
SELECT a.*, b.*
FROM table_a a
CROSS JOIN table_b b;
```

## Aggregation

**Aggregate Functions:**
- `COUNT(*)`: Count all rows
- `COUNT(column)`: Count non-NULL values
- `SUM(column)`: Sum of values
- `AVG(column)`: Average of values
- `MIN(column)`: Minimum value
- `MAX(column)`: Maximum value
- `STRING_AGG(column, separator)`: Concatenate strings

**GROUP BY:**
```sql
SELECT department, COUNT(*), AVG(salary)
FROM employees
GROUP BY department;
```

**HAVING:**
```sql
SELECT department, COUNT(*) as emp_count
FROM employees
GROUP BY department
HAVING COUNT(*) > 5;
```

## Subqueries

**Scalar Subquery:**
```sql
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);
```

**Row Subquery:**
```sql
SELECT * FROM employees
WHERE (department, salary) = 
  (SELECT department, MAX(salary) 
   FROM employees 
   GROUP BY department);
```

**Correlated Subquery:**
```sql
SELECT e.name
FROM employees e
WHERE salary > (
  SELECT AVG(salary) 
  FROM employees 
  WHERE department = e.department
);
```

**EXISTS:**
```sql
SELECT d.name
FROM departments d
WHERE EXISTS (
  SELECT 1 
  FROM employees e 
  WHERE e.department_id = d.id
);
```

## Data Modification

### INSERT

```sql
-- Insert single row
INSERT INTO table_name (column1, column2)
VALUES (value1, value2);

-- Insert multiple rows
INSERT INTO table_name (column1, column2)
VALUES 
  (value1, value2),
  (value3, value4);

-- Insert from SELECT
INSERT INTO table_name (column1, column2)
SELECT column1, column2 FROM other_table;
```

### UPDATE

```sql
UPDATE table_name
SET column1 = value1, column2 = value2
WHERE condition;
```

### DELETE

```sql
DELETE FROM table_name
WHERE condition;

-- Delete all rows (careful!)
DELETE FROM table_name;

-- Faster truncate (no triggers, no WHERE)
TRUNCATE TABLE table_name;
```

### UPSERT (INSERT ON CONFLICT)

```sql
-- Insert or update
INSERT INTO table_name (id, column1)
VALUES (1, 'value')
ON CONFLICT (id) 
DO UPDATE SET column1 = EXCLUDED.column1;

-- Insert or do nothing
INSERT INTO table_name (id, column1)
VALUES (1, 'value')
ON CONFLICT (id) 
DO NOTHING;
```

## Set Operations

**UNION:** Combines results, removes duplicates
```sql
SELECT column FROM table_a
UNION
SELECT column FROM table_b;
```

**UNION ALL:** Combines results, keeps duplicates
```sql
SELECT column FROM table_a
UNION ALL
SELECT column FROM table_b;
```

**INTERSECT:** Returns common rows
```sql
SELECT column FROM table_a
INTERSECT
SELECT column FROM table_b;
```

**EXCEPT:** Returns rows in first but not second
```sql
SELECT column FROM table_a
EXCEPT
SELECT column FROM table_b;
```

## Resources

- [PostgreSQL SELECT Tutorial](https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-select/)
- [PostgreSQL WHERE Clause](https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-where/)
- [PostgreSQL JOINs](https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-joins/)
- [PostgreSQL GROUP BY](https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-group-by/)
- [PostgreSQL Subquery](https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-subquery/)
- [PostgreSQL INSERT](https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-insert/)
- [PostgreSQL UPDATE](https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-update/)
- [PostgreSQL DELETE](https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-delete/)
