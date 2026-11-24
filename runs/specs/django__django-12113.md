# Spec: `admin_views.test_multidb` must pass with persistent (file-based) SQLite test databases

## Objective

**Problem.** When Django's own test suite is run against SQLite with a file-based `TEST["NAME"]` configured for **both** the `default` and `other` aliases, so that `--keepdb` can reuse the databases, `admin_views.test_multidb.MultiDatabaseTests` errors in `setUpClass`:

```
django.db.utils.OperationalError: database is locked
```

The error is raised from `setUpTestData` (`tests/admin_views/test_multidb.py`, line 40) while it calls `create_superuser(username='admin', password='something', email='test@test.org')` and the user is saved with `using=self._db`. The reporter says the error does not occur when only `default` has a `TEST["NAME"]`. The reporter also notes that "at least some test" fails, so other multi-database tests may be affected.

**Who is affected.** Contributors who run Django's test suite locally on SQLite and want `--keepdb` to speed up repeated runs.

**What success looks like.** With file-based `TEST["NAME"]` configured for both aliases, the reproduction command below completes without `database is locked`, on a first run and on a rerun with `--keepdb`. Behaviour with the default in-memory SQLite configuration does not change.

**Reproduction (from the issue).** Add the following to the `DATABASES` setting in `tests/test_sqlite.py`:

```python
'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'TEST': {'NAME': 'test_default.sqlite3'},
},
'other': {
    'ENGINE': 'django.db.backends.sqlite3',
    'TEST': {'NAME': 'test_other.sqlite3'},
},
```

Then run:

```
tests/runtests.py admin_views.test_multidb -v 3 --keepdb --parallel 1
```

## Assumptions

1. The target is the Django repository itself. "Tests" means Django's own suite, run through `tests/runtests.py` with the settings module `tests/test_sqlite.py`.
2. The failure is deterministic with `--parallel 1`, so parallel test workers are not the cause.
3. The root cause is unknown. Working hypothesis: while `setUpTestData` writes to one SQLite file, a second connection holds an open, uncommitted write transaction on that same file. SQLite allows only one writer per file, so the write fails with `database is locked`.
   - Possible sources of that second connection: the class-level atomic blocks that `TestCase` opens for each alias in `databases`, or a database router that sends writes to an unexpected alias.
   - With in-memory databases, each alias has its own isolated database, so the conflict cannot appear there.
   - This must be confirmed before choosing a fix.
4. The fix may belong in the test (`tests/admin_views/test_multidb.py`, for example how it declares databases or creates data), in the test framework (`django/test/testcases.py`), or in the SQLite backend's test-database handling. No location is assumed.
5. Changing the committed default `tests/test_sqlite.py` to use file-based databases is **not** in scope. The diff above is only a way to reproduce the bug.
6. The working directory where the `.sqlite3` files are created is irrelevant to the bug.

## Tech Stack

- Python, Django (version or branch unknown; the traceback references `django/test/testcases.py` line 1137).
- SQLite through `django.db.backends.sqlite3` and the stdlib `sqlite3` module (versions unknown).
- Django's own test runner, `tests/runtests.py`.

## Commands

- Reproduce or verify (from the issue): `tests/runtests.py admin_views.test_multidb -v 3 --keepdb --parallel 1`
- Same run without keepdb: `tests/runtests.py admin_views.test_multidb -v 3 --parallel 1` (flags as above with `--keepdb` removed)
- Full suite: `tests/runtests.py` (default flags; the exact CI invocation is unknown)
- Lint: unknown

## Project Structure

Only paths that appear in the issue are listed:

```
tests/runtests.py                  → Django's test-suite runner
tests/test_sqlite.py               → Default SQLite settings for the suite (DATABASES with 'default' and 'other')
tests/admin_views/test_multidb.py  → Failing test module (MultiDatabaseTests, setUpTestData)
django/test/testcases.py           → TestCase.setUpClass → setUpTestData
django/db/backends/sqlite3/base.py → SQLite cursor execute
django/contrib/auth/models.py      → UserManager.create_superuser / _create_user
```

Any other relevant locations (SQLite test-database creation code, routers used by the test) are unknown and need to be found by reading the code.

## Code Style

Unknown beyond the issue. Follow the existing style of Django's test suite and of the file being changed. No snippet is available.

## Testing Strategy

- **Regression check:** The reproduction command above passes with file-based `TEST["NAME"]` for both aliases, in each of these cases:
  - a first run with no existing files
  - a second run with `--keepdb` that reuses the files
  - a run without `--keepdb`
- **Default-configuration check:** `admin_views.test_multidb` and the full suite still pass with the unmodified `tests/test_sqlite.py` (in-memory databases).
- **Breadth check:** Run the other multi-database tests under the same file-based configuration. This finds other tests covered by "at least some test fails". How to select these tests is unknown, for example tests that declare the `other` alias.
- **Automated regression test:** Whether one is feasible in CI is an open question, because CI presumably uses in-memory SQLite. If the fix is in framework or backend code, add a test that exercises a file-based configuration if possible. If the fix only touches the test module, manual verification with the reproduction may be enough.

## Boundaries

- **Always:**
  - Reproduce the failure before changing anything.
  - Confirm the root cause (which connection holds the lock, and why) before choosing a fix.
  - Keep in-memory SQLite behaviour unchanged.
  - Run the affected test module under both configurations.
- **Ask first:**
  - Changing `TestCase` or transaction handling in `django/test/testcases.py`.
  - Changing SQLite backend or test-database creation behaviour.
  - Changing the committed `tests/test_sqlite.py` settings.
  - Fixing other affected tests beyond `admin_views.test_multidb`.
- **Never:**
  - Mask the error by skipping the test, retrying on lock, or raising SQLite timeouts without understanding the cause.
  - Remove or weaken the multi-database assertions in the test.
  - Commit the generated `.sqlite3` files.

## Success Criteria

1. The reproduction command passes, with no `OperationalError: database is locked`, using file-based `TEST["NAME"]` for both `default` and `other`. This holds on a fresh run and on a `--keepdb` rerun.
2. `admin_views.test_multidb` still passes with the default `tests/test_sqlite.py`.
3. The full Django test suite shows no new failures under the default configuration.
4. The root cause is written up in the change description: which connection or transaction held the lock, and why it only appears with file-based databases.
5. Any other tests found to fail for the same reason under the file-based configuration are either fixed or listed as follow-ups. Which of these applies depends on the scope decision below.

## Open Questions

1. **Scope:** Is the goal limited to `admin_views.test_multidb`, or should every test that fails with persistent SQLite databases for both aliases be fixed? ("at least some test fails")
2. **Officially supported?** Is running Django's suite with file-based SQLite test databases for multiple aliases a supported configuration, or only a convenience? This decides whether a framework or backend change is justified, versus a test-only fix.
3. **Root cause:** Is the lock held by `TestCase`'s per-alias class-level atomic blocks, by a router in the test module, or by something else? This needs investigation.
4. **Both names required?** Does the failure need both aliases to be file-based, or only `other`? The issue only reports that `default` alone works.
5. **Shared file?** Could both aliases end up pointing at the same file, for example through test-name or mirror resolution under `--keepdb`?
6. **CI coverage:** Should CI cover a file-based multi-alias SQLite configuration so this does not regress?
7. **Versions:** Which Django branch or commit, Python version, and SQLite library version is the reporter using?