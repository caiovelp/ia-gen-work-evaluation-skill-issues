# Spec: `sqlmigrate` should not wrap output in BEGIN/COMMIT when the database cannot roll back DDL

## Objective

`sqlmigrate` prints the SQL for a migration. Today it wraps that SQL in `BEGIN;` / `COMMIT;` whenever `migration.atomic` is true. The migration executor behaves differently. It adds the outer transaction only when **both** of these hold:

1. the migration is atomic, **and**
2. the schema editor can roll back DDL (`connection.features.can_rollback_ddl`).

On backends without transactional DDL, `sqlmigrate` output therefore misrepresents what the executor actually runs. It shows a transaction wrapper that is never applied and that cannot give atomicity for DDL on that backend.

**Goal:** `sqlmigrate` wraps output in BEGIN/COMMIT under the same condition the executor uses: `migration.atomic and connection.features.can_rollback_ddl`.

**Users:** Django developers and DBAs who inspect migration SQL, often to run it by hand, on backends that may lack transactional DDL.

### Acceptance criteria
- With an atomic migration and `can_rollback_ddl = True`, output is wrapped in BEGIN/COMMIT. This is the current behavior and is unchanged.
- With an atomic migration and `can_rollback_ddl = False`, output is **not** wrapped in BEGIN/COMMIT.
- With a non-atomic migration, output is **not** wrapped, whatever `can_rollback_ddl` says. This is the current behavior and is unchanged.
- The decision uses the connection for the database `sqlmigrate` targets (its `--database` option), not always the default connection.

## Assumptions
1. The wrapping is controlled by `self.output_transaction` on the `sqlmigrate` command, as the issue states. The actual BEGIN/COMMIT emission comes from the base management command machinery, which is out of scope.
2. The `sqlmigrate` command lives in Django's management commands package. The exact file path is **not shown in the issue and is unknown**.
3. `connection.features.can_rollback_ddl` is the canonical feature flag, and the executor's condition is exactly `atomic and can_rollback_ddl`. This comes from the issue's description of the executor.
4. The connection to use is the one `sqlmigrate` already resolves for the chosen database alias.
5. No change to the executor, schema editor, or backend feature flags is required.
6. No deprecation or release note is required beyond what the project normally needs for a bug fix. This needs confirmation; see Open Questions.

## Tech Stack
- Django (Python). The version or branch is **unknown**.
- The test framework is Django's own test suite. The runner invocation is **unknown** because it is not visible in the issue.

## Commands
- Build: **unknown / not applicable**
- Test (targeted): **unknown**. It must run the tests in `tests/migrations/test_commands.py`.
- Test (full migrations suite): **unknown**
- Lint: **unknown**

## Project Structure
- `tests/migrations/test_commands.py` holds the tests for migration management commands. This path is given in the issue.
- The `sqlmigrate` command source file path is **unknown**.
- The location of the existing non-atomic migration test fixture is **unknown**. The issue says an existing test overrides `MIGRATION_MODULES` to point at a non-atomic migration.

## Code Style
- Follow the existing Django code style in the touched files.
- No snippet is available from the issue. Conventions are **unknown** beyond "match the surrounding code."

## Testing Strategy
- **Level:** management-command tests in `tests/migrations/test_commands.py`.
- **New test:** model it on the existing `sqlmigrate` test for non-atomic migrations. Instead of overriding `MIGRATION_MODULES` to use a non-atomic migration, use a normal atomic migration and **mock `connection.features.can_rollback_ddl` to `False`**.
  - Assert that the output contains no BEGIN/COMMIT transaction wrapper. Use the same assertion style as the existing non-atomic test.
- **Regression coverage:** the existing tests must still pass. These are the atomic-migration test (wrapped output) and the non-atomic test (unwrapped output).
- The tests should not depend on the real backend's feature flag. Mocking keeps them deterministic across backends.

## Boundaries
- **Always:**
  - Keep the `sqlmigrate` condition the same as the executor's condition.
  - Use the connection for the selected database alias.
  - Add the regression test in `tests/migrations/test_commands.py`.
- **Ask first:**
  - Changing the executor or schema editor logic.
  - Extracting a shared helper for the "should wrap in transaction" condition.
  - Changing behavior for backends' feature flags.
  - Adding documentation or release notes.
- **Never:**
  - Change the generated SQL statements themselves.
  - Alter or remove existing tests' expectations.
  - Change the default value of `can_rollback_ddl` for any backend.

## Success Criteria
- [ ] `sqlmigrate` sets `output_transaction` to true only when `migration.atomic` and `connection.features.can_rollback_ddl` are both true.
- [ ] A new test in `tests/migrations/test_commands.py` mocks `can_rollback_ddl = False` on an atomic migration and verifies there is no BEGIN/COMMIT in the output.
- [ ] The existing `sqlmigrate` tests for atomic and non-atomic migrations pass unchanged.
- [ ] The full migrations test module passes. The command for this is unknown; see Commands.

## Open Questions
1. What is the exact path of the `sqlmigrate` command source, and how does it currently obtain the connection? The issue does not show either.
2. What is the name of the existing non-atomic `sqlmigrate` test that should be used as the template?
3. Should the condition be factored into a shared helper so the executor and `sqlmigrate` cannot drift apart again, or kept inline as the issue suggests?
4. Does this bug fix need a release note, and if so, for which Django version?
5. Should the new test also cover a non-default `--database` alias whose backend has `can_rollback_ddl = False`?
6. How should the test suite be run (runner command and settings)? This is not visible in the issue.