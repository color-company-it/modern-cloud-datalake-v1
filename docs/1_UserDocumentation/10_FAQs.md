# 1.10 Frequently Asked Questions

**Q: What is the purpose of this codebase?**

- A: The codebase is designed to reduce duplicate code in a cloud environment and data lake by following DRY (Don't
  Repeat
  Yourself) principles, and to properly support unit testing and integration testing.

**Q: How is the codebase available?**

- A: The codebase is available in AWS S3 as a .whl file, .zip file, and a lambda layer .zip file.

**Q: What is the purpose of using a pushdown query for JDBC extract?**

- A: A pushdown query, also known as a "predicate pushdown", is a way to optimize the extraction of data from a JDBC
  source by reducing the amount of data that needs to be transferred over the network. By specifying a WHERE condition
  in
  the pushdown query, the JDBC driver can filter the data at the source before sending it to the client, reducing the
  amount of data transferred and improving performance.

**Q: Why is the alias added to the query in the get_pushdown_query() method?**

- A: The alias is added to the query to give a name to the temporary table that is created when the query is run. This
  can
  be useful for referencing the table in subsequent queries or for referencing the table's columns.
