# Spec: PostgreSQL `dbshell` — pass extra parameters before the database name

## Objective

Running `./manage.py dbshell -- <extra args>` against a PostgreSQL database currently builds a `psql` command line where the database name comes **before** the user-supplied extra arguments. `psql` expects all options to come before the database name. It treats anything after the database name as extra positional arguments and ignores them with warnings:

```
$ ./manage.py dbshell -- -c "select * from some_table;"
psql: warning: extra command-line argument "-c" ignored
psql: warning: extra command-line argument "select * from some_table;" ignored
psql (10.21)
Type "help" for help.
some_database=>
```

**Goal:** On PostgreSQL, build the `psql` argument list so that user-supplied extra parameters come before the database name, and the database name is the last argument. Options such as `-c "<sql>"` will then take effect.

**Users:** Developers and operators who run `manage.py dbshell` with extra `psql` arguments, for example to run one-off queries non-interactively or in scripts.

**User story:** As a developer, when I run `./manage.py dbshell -- -c "select 1;"` against PostgreSQL, the query runs, and `psql` does not warn that my arguments were ignored.

## Assumptions

1. The project is Django. The issue uses `manage.py dbshell` and the `--` passthrough of extra parameters.
2. The bug is limited to the PostgreSQL backend. Other backends (MySQL, SQLite, Oracle) are out of scope unless they turn out to have the same ordering problem (see Open Questions).
3. The PostgreSQL backend's database client builds the args list as roughly `[executable, <connection options>..., dbname, <extra parameters>...]`. The fix changes the order to `[executable, <connection options>..., <extra parameters>..., dbname]`. I have not seen the exact code or file path; this is inferred from the issue text.
4. Connection options derived from settings (for example user, host and port) can stay before the extra parameters. Only the relative position of the database name and the extra parameters must change.
5. When no database name is configured, the database name is simply left out and the extra parameters are still passed through unchanged.
6. Environment-based settings (for example a password or SSL options passed via environment variables) are not affected by this change.
7. Existing unit tests for the PostgreSQL client's argument construction exist and should be updated or extended. Their exact location is unknown.

## Tech Stack

- Language: Python (version unknown)
- Framework: Django (version and branch unknown)
- External tool: `psql`. The reporter uses 10.21. The ordering requirement applies to `psql` in general.

## Commands

Unknown. They are not visible in the issue. To be confirmed:

- Test: unknown (for example the project's test runner for the PostgreSQL dbshell tests)
- Lint: unknown
- Manual reproduction (from the issue): `./manage.py dbshell -- -c "select * from some_table;"`

## Project Structure

Unknown. They are not visible in the issue. Expected, but unconfirmed, areas:

- The PostgreSQL database backend's client module, which builds the `psql` argument list. Path unknown.
- Tests for the PostgreSQL dbshell / client argument construction. Path unknown.

## Code Style

Unknown. Follow the existing conventions of the surrounding module and the project's linters. No snippet is available from the issue.

## Testing Strategy

- **Unit tests (primary).** Test the function or method that builds the PostgreSQL client args and environment directly, without launching `psql`. Cover these cases:
  - With database name and extra parameters: the extra parameters appear before the database name, and the database name is the final element.
  - With database name and no extra parameters: the output is unchanged from current behavior.
  - With extra parameters and no database name: the extra parameters are present and no stray empty argument is added.
  - With connection options (user/host/port) and extra parameters: the connection options are preserved, and the database name is still last.
- **Existing tests.** Update any existing assertions that encode the old order, where the database name came before the parameters.
- **Manual check (optional, needs a real PostgreSQL).** Run `./manage.py dbshell -- -c "select 1;"`. It should run the query without the "extra command-line argument ... ignored" warnings.
- Coverage expectation: unknown. At minimum, every case listed above is asserted.

## Boundaries

- **Always:**
  - Keep the database name as the last argument when it is present.
  - Preserve the existing pass-through semantics of extra parameters: same values, same relative order.
  - Run the relevant backend tests before committing.
- **Ask first:**
  - Changing argument ordering for any non-PostgreSQL backend.
  - Changing how the database name is passed, for example switching to `-d dbname` instead of a positional argument.
  - Changing the public signature of the client argument-building API.
- **Never:**
  - Silently drop or reorder user-supplied parameters among themselves.
  - Remove or weaken existing tests without approval.
  - Change environment or password handling as part of this fix.

## Success Criteria

1. On PostgreSQL, the generated command line has the form `psql [connection options] [extra parameters] [dbname]`, with `dbname` last whenever it is set.
2. `./manage.py dbshell -- -c "select * from some_table;"` runs the query, and `psql` emits no "extra command-line argument ... ignored" warnings.
3. With no extra parameters, the generated command line is identical to current behavior.
4. With no database name configured, the extra parameters are still passed and no empty or placeholder argument is added.
5. Unit tests assert the cases above and pass. Existing tests updated for the new order pass.
6. Behavior of other database backends is unchanged.

## Open Questions

1. What are the exact file paths for the PostgreSQL client implementation and its tests, and what is the test command?
2. Should the database name stay a positional argument, or switch to `-d`/`--dbname`, which works regardless of position? The positional approach is assumed.
3. Do any other backends (MySQL, SQLite, Oracle) have the same ordering problem? Should they be fixed in this change or tracked separately?
4. Does this change need a release note or a documentation update for `dbshell`?
5. Which Django branch or versions should receive the fix (main only, or backports)?
6. Could the current order be intentional for some users, for example passing extra positional args such as a username after the dbname? Does that count as a backward-compatibility concern?