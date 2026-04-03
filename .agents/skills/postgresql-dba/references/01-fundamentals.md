# PostgreSQL Fundamentals

## Introduction to PostgreSQL

PostgreSQL is a powerful, open-source Object-Relational Database Management System (ORDBMS) that is known for its robustness, extensibility, and SQL compliance. It was initially developed at the University of California, Berkeley, in the 1980s and has since become one of the most popular open-source databases in the world.

**Key Resources:**
- [PostgreSQL Official](https://www.postgresql.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [History of PostgreSQL](https://www.postgresql.org/docs/current/history.html)

## Relational Database Concepts

### What are Relational Databases?

Relational databases are a type of database management system (DBMS) that stores and organizes data in a structured format called tables. These tables are made up of rows (also known as records or tuples) and columns (also called attributes or fields). The term "relational" comes from the fact that these tables can be related to one another through keys and relationships.

**Learn More:**
- [IBM: Relational Databases](https://www.ibm.com/cloud/learn/relational-databases)
- [Udacity: Intro To Relational Databases](https://www.udacity.com/course/intro-to-relational-databases--ud197)
- [edX: Databases and SQL](https://www.edx.org/course/databases-5-sql)

### RDBMS Concepts

Relational Database Management Systems (RDBMS) are a type of database management system which stores and organizes data in tables, making it easy to manipulate, query, and manage the information. They follow the relational model defined by E.F. Codd in 1970, which means that data is represented as tables with rows and columns.

**Learn More:**
- [Understanding Relational Database Management Systems](https://www.essentialsql.com/understanding-relational-databases-a-beginners-guide/)

## PostgreSQL vs Other Databases

PostgreSQL stands out among other RDBMS options due to its open-source nature, advanced features, and robust performance. Unlike proprietary systems like Oracle or Microsoft SQL Server, PostgreSQL is free to use and highly extensible, allowing users to add custom functions, data types, and operators. It supports a wide range of indexing techniques and provides advanced features such as full-text search, JSON support, and geographic information system (GIS) capabilities through PostGIS.

While systems like MySQL are also popular and known for their speed in read-heavy environments, PostgreSQL often surpasses them in terms of functionality and compliance with ACID properties, making it a versatile choice for complex, transactional applications.

**Comparison Resources:**
- [PostgreSQL vs MySQL: The Critical Differences](https://www.integrate.io/blog/postgresql-vs-mysql-which-one-is-better-for-your-use-case/)
- [AWS: Difference between PostgreSQL and MySQL](https://aws.amazon.com/compare/the-difference-between-mysql-vs-postgresql/)

## High Level Database Concepts

High-level database concepts encompass fundamental principles that underpin the design, implementation, and management of database systems. These concepts form the foundation of effective database management, enabling the design of robust, efficient, and scalable systems.

**Learn More:**
- [10 Crucial PostgreSQL Concepts and Files](https://medium.com/@RohitAjaygupta/demystifying-postgresql-10-crucial-concepts-and-files-explained-with-practical-examples-a5a70cd2b848)

## Object Model in PostgreSQL

PostgreSQL is an object-relational database management system (ORDBMS). That means it combines features of both relational (RDBMS) and object-oriented databases (OODBMS). The object model in PostgreSQL provides features like user-defined data types, inheritance, and polymorphism, which enhances its capabilities beyond a typical SQL-based RDBMS.

**Learn More:**
- [PostgreSQL Object Model](https://www.postgresql.org/docs/current/tutorial-concepts.html)
- [PostgreSQL Server and Database Objects](https://neon.com/postgresql/postgresql-tutorial/postgresql-server-and-database-objects)

## Relational Model

The relational model is an approach to organizing and structuring data using tables, also referred to as "relations". It was first introduced by Edgar F. Codd in 1970 and has since become the foundation for most database management systems (DBMS), including PostgreSQL. This model organizes data into tables with rows and columns, where each row represents a single record and each column represents an attribute or field of the record.

**Learn More:**
- [PostgreSQL Relational Model](https://www.postgresql.org/docs/7.1/relmodel-oper.html)

## Core Database Concepts

### ACID Properties

ACID are the four properties of relational database systems that help in making sure that we are able to perform the transactions in a reliable manner. It's an acronym which refers to the presence of four properties:

- **Atomicity**: All operations in a transaction complete successfully or none do
- **Consistency**: Database remains in a consistent state before and after the transaction
- **Isolation**: Concurrent transactions do not interfere with each other
- **Durability**: Once committed, transactions persist even in case of system failure

**Resources:**
- [What is ACID Compliant Database?](https://retool.com/blog/whats-an-acid-compliant-database/)
- [ACID Compliance Explained](https://fauna.com/blog/what-is-acid-compliance-atomicity-consistency-isolation)
- [Video: ACID Explained](https://www.youtube.com/watch?v=yaQ5YMWkxq4)

### Multi-Version Concurrency Control (MVCC)

Multi-Version Concurrency Control (MVCC) is a technique used by PostgreSQL to allow multiple transactions to access the same data concurrently without conflicts or delays. It ensures that each transaction has a consistent snapshot of the database and can operate on its own version of the data.

**Resources:**
- [PostgreSQL MVCC Intro](https://www.postgresql.org/docs/current/mvcc-intro.html)
- [MVCC on Wikipedia](https://en.wikipedia.org/wiki/Multiversion_concurrency_control)
- [What is MVCC?](https://www.theserverside.com/blog/Coffee-Talk-Java-News-Stories-and-Opinions/What-is-MVCC-How-does-Multiversion-Concurrencty-Control-work)

### Transactions

Transactions are a fundamental concept in database management systems, allowing multiple statements to be executed within a single transaction context. In PostgreSQL, transactions provide ACID properties, which ensure that your data remains in a consistent state even during concurrent access or system crashes. By leveraging transaction control, savepoints, concurrency control, and locking, you can build robust and reliable applications.

**Resources:**
- [PostgreSQL Transactions Tutorial](https://www.postgresql.org/docs/current/tutorial-transactions.html)
- [Video: How to implement transactions](https://www.youtube.com/watch?v=DvJq4L41ru0)

### Write Ahead Log (WAL)

The Write Ahead Log, also known as the WAL, is a crucial part of PostgreSQL's data consistency strategy. The WAL records all changes made to the database in a sequential log before they are written to the actual data files. In case of a crash, PostgreSQL can use the WAL to bring the database back to a consistent state without losing any crucial data. This provides durability and crash recovery capabilities for your database.

**Resources:**
- [PostgreSQL WAL Intro](https://www.postgresql.org/docs/current/wal-intro.html)
- [Working With Postgres WAL](https://hevodata.com/learn/working-with-postgres-wal/)
- [Video: Write Ahead Logging](https://www.youtube.com/watch?v=yV_Zp0Mi3xs)
