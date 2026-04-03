# Advanced SQL

## Common Table Expressions (CTEs)

A Common Table Expression, also known as CTE, is a named temporary result set that can be referenced within a `SELECT`, `INSERT`, `UPDATE`, or `DELETE` statement. CTEs are particularly helpful when dealing with complex queries, as they enable you to break down the query into smaller, more readable chunks.

**Basic CTE Syntax:**
```sql
WITH cte_name AS (
    SELECT column1, column2
    FROM table_name
    WHERE condition
)
SELECT * FROM cte_name;
```

**Multiple CTEs:**
```sql
WITH 
  cte1 AS (
    SELECT * FROM table1 WHERE condition
  ),
  cte2 AS (
    SELECT * FROM table2 WHERE condition
  )
SELECT c1.*, c2.*
FROM cte1 c1
JOIN cte2 c2 ON c1.id = c2.id;
```

**Resources:**
- [PostgreSQL CTE Documentation](https://www.postgresql.org/docs/current/queries-with.html)
- [PostgreSQL CTE Tutorial](https://www.postgresqlutorial.com/postgresql-tutorial/postgresql-cte/)

## Recursive CTEs

Recursive CTEs are helpful when working with hierarchical or tree-structured data, such as:
- Organizational hierarchies
- Bill of materials
- Graph traversal
- Finding paths

**Syntax:**
```sql
WITH RECURSIVE cte_name AS (
    -- Anchor member (starting point)
    SELECT id, name, parent_id, 0 as level
    FROM table_name
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Recursive member
    SELECT t.id, t.name, t.parent_id, c.level + 1
    FROM table_name t
    INNER JOIN cte_name c ON t.parent_id = c.id
)
SELECT * FROM cte_name;
```

**Example: Employee Hierarchy:**
```sql
WITH RECURSIVE employee_tree AS (
    SELECT id, name, manager_id, name as path, 0 as level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    SELECT e.id, e.name, e.manager_id, 
           et.path || ' > ' || e.name,
           et.level + 1
    FROM employees e
    INNER JOIN employee_tree et ON e.manager_id = et.id
)
SELECT * FROM employee_tree;
```

## Window Functions

Window functions calculate values across a set of table rows related to the current row while preserving the row structure. Unlike aggregate functions, window functions don't collapse rows.

### Common Window Functions

**Ranking Functions:**
- `ROW_NUMBER()`: Unique sequential number
- `RANK()`: Rank with gaps for ties
- `DENSE_RANK()`: Rank without gaps
- `NTILE(n)`: Divide rows into n buckets

**Value Functions:**
- `FIRST_VALUE(expr)`: First value in window
- `LAST_VALUE(expr)`: Last value in window
- `LAG(expr, offset)`: Value from previous row
- `LEAD(expr, offset)`: Value from next row
- `NTH_VALUE(expr, n)`: Nth value in window

**Aggregate Window Functions:**
- `SUM()`, `AVG()`, `COUNT()`, `MIN()`, `MAX()` as window functions

### Window Function Syntax

```sql
function_name(expression) OVER (
    [PARTITION BY partition_column]
    [ORDER BY order_column]
    [frame_clause]
)
```

### Examples

**Row Numbers:**
```sql
SELECT 
    name,
    department,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as overall_rank,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank
FROM employees;
```

**Running Total:**
```sql
SELECT 
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) as running_total
FROM transactions;
```

**Moving Average:**
```sql
SELECT 
    date,
    sales,
    AVG(sales) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7day
FROM daily_sales;
```

**Year-over-Year Comparison:**
```sql
SELECT 
    year,
    month,
    sales,
    LAG(sales, 12) OVER (ORDER BY year, month) as sales_last_year,
    sales / LAG(sales, 12) OVER (ORDER BY year, month) - 1 as yoy_growth
FROM monthly_sales;
```

**Resources:**
- [Data Processing With PostgreSQL Window Functions](https://www.timescale.com/learn/postgresql-window-functions)
- [Why & How to Use Window Functions](https://coderpad.io/blog/development/window-functions-aggregate-data-postgres/)

## Aggregate and Window Functions

Aggregate functions in PostgreSQL perform calculations on a set of rows and return a single value:
- `SUM()`: Total of values
- `AVG()`: Average of values
- `COUNT()`: Count of rows
- `MAX()`: Maximum value
- `MIN()`: Minimum value
- `STRING_AGG()`: Concatenate values into string

These can be used both as regular aggregates and as window functions.

**Resources:**
- [PostgreSQL Aggregate Functions](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [PostgreSQL Window Functions](https://www.postgresql.org/docs/current/functions-window.html)

## Advanced Query Techniques

### Conditional Aggregation

```sql
SELECT 
    department,
    COUNT(*) as total_employees,
    COUNT(*) FILTER (WHERE salary > 100000) as high_earners,
    AVG(salary) FILTER (WHERE hire_date > '2020-01-01') as avg_new_salary
FROM employees
GROUP BY department;
```

### Pivoting Data

Using `crosstab` from tablefunc extension:
```sql
-- First enable the extension
CREATE EXTENSION IF NOT EXISTS tablefunc;

-- Pivot sales data by month
SELECT * FROM crosstab(
    'SELECT product, month, sales 
     FROM sales_data 
     ORDER BY 1, 2',
    'SELECT DISTINCT month FROM sales_data ORDER BY 1'
) AS ct(product text, jan numeric, feb numeric, mar numeric);
```

Manual pivot with CASE:
```sql
SELECT 
    product,
    SUM(CASE WHEN month = 'Jan' THEN sales ELSE 0 END) as jan_sales,
    SUM(CASE WHEN month = 'Feb' THEN sales ELSE 0 END) as feb_sales,
    SUM(CASE WHEN month = 'Mar' THEN sales ELSE 0 END) as mar_sales
FROM sales_data
GROUP BY product;
```

### LATERAL Joins

`LATERAL` allows subqueries in FROM clause to reference columns from preceding tables:

```sql
SELECT u.id, u.name, recent_orders.*
FROM users u
LEFT JOIN LATERAL (
    SELECT * FROM orders 
    WHERE user_id = u.id 
    ORDER BY created_at DESC 
    LIMIT 5
) recent_orders ON true;
```

### Array Aggregation

```sql
-- Aggregate to array
SELECT department, ARRAY_AGG(name ORDER BY salary DESC) as employees
FROM employees
GROUP BY department;

-- Unnest arrays
SELECT * FROM UNNEST(ARRAY[1,2,3], ARRAY['a','b','c']);

-- Array operations
SELECT 
    name,
    tags,
    'urgent' = ANY(tags) as is_urgent,
    array_length(tags, 1) as tag_count
FROM tickets;
```

## Query Optimization Tips

1. **Use EXPLAIN ANALYZE** to understand query execution
2. **Add appropriate indexes** for filtering and sorting columns
3. **Limit columns in SELECT** instead of using `SELECT *`
4. **Use appropriate JOIN types** - avoid unnecessary outer joins
5. **Filter early** with WHERE clauses before joining
6. **Consider materialized views** for complex aggregations
7. **Use LIMIT/OFFSET carefully** - keyset pagination for large datasets
