## Summary

On PostgreSQL, extra parameters given to `manage.py dbshell` after `--` are placed after the database name on the `psql` command line. `psql` expects all options to come before the database name, so it ignores them and opens an interactive session instead of running them.

## Steps to reproduce

1. Configure a Django project to use a PostgreSQL database (in the report, `some_database`).
2. Run `dbshell` with extra `psql` parameters after `--`, for example:
   ```
   ./manage.py dbshell -- -c "select * from some_table;"
   ```

## Observed behavior

`psql` warns that the extra arguments are ignored. It does not run the query. Instead it opens an interactive prompt connected to the database.

## Expected behavior

The extra parameters (`-c "select * from some_table;"`) should be passed to `psql` before the database name. `psql` should then accept them and run the given query.

## Stack trace / error output

```
$ ./manage.py dbshell -- -c "select * from some_table;"
psql: warning: extra command-line argument "-c" ignored
psql: warning: extra command-line argument "select * from some_table;" ignored
psql (10.21)
Type "help" for help.
some_database=>
```

## Test case

Not provided in the original report.

## Code example

```
./manage.py dbshell -- -c "select * from some_table;"
```

## Version and environment

- Database client: `psql` 10.21 (from the command output)
- Database backend: PostgreSQL
- Django version: Not provided in the original report.
- Python version and operating system: Not provided in the original report.