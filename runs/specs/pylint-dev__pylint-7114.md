# Spec: Lint a directory without `__init__.py` that contains a module of the same name

## Assumptions

1. The directory `a/` in the report has no `__init__.py`. Pylint should treat it as an implicit namespace package (PEP 420, Python 3.3+). The reporter's note that `__init__.py` "shouldn't be necessary anymore" supports this.
2. The trigger is a module file named the same as its parent directory (`a/a.py` inside `a/`). It is not about namespace packages in general, since renaming `a.py` to `c.py` makes the failure go away.
3. The defect is in how pylint maps the command-line argument `a` to files and modules. It is not in parsing the empty files, because the error says pylint tried to open a non-existent `a/__init__.py`.
4. The `E0611 no-name-in-module` error on `r.py` is a side effect of the same mis-resolution. Linting `a` seems to register or cache `a` as something other than the directory `a/`, so `from a import b` then fails. Fixing the root cause should fix both symptoms.
5. The reported versions (pylint 3.0.0a3, astroid 2.5.6, Python 3.8.5) are the reference environment. The fix should hold on whatever Python versions the project currently supports (unknown).
6. Directories that do have an `__init__.py` must behave exactly as they do today.
7. The fix may belong in pylint, in astroid, or in both. This spec states behaviour only and does not prescribe where the fix goes.

## Objective

**What:** Make `pylint <dir>` work when `<dir>` has no `__init__.py` and contains a module named `<dir>.py`. Make module resolution in the same run stay correct for other files that import from `<dir>`.

**Why:** Python 3 projects often leave out `__init__.py`. Today pylint emits a fatal `F0010 parse-error` for a file that does not exist. It also emits false `E0611` errors in unrelated modules, but only when the directory happens to contain a same-named file. That is confusing and blocks CI for valid code.

**User:** Developers running pylint on Python 3 code that uses implicit namespace packages.

**User stories / acceptance:**
- As a developer with a `a/` folder that has `a.py` and `b.py` and no `__init__.py`, I run `pylint a` and get a normal lint run with no `F0010` about `a/__init__.py`.
- As a developer with `r.py` containing `from a import b`, I run `pylint -E r a` and get no `E0611` for `r.py` and no `F0010` for `a`. The result is the same as `pylint -E r`.

## Tech Stack

- Python. The supported version range is unknown; the reference is 3.8.5.
- pylint (reported on 3.0.0a3).
- astroid (reported on 2.5.6). It provides module and file resolution and AST building.
- Exact pinned dependency versions in the repository are unknown.

## Commands

All unknown, because the repository is not visible:

- Build: unknown
- Test: unknown (likely pytest-based, unconfirmed)
- Lint: unknown
- Dev / install: unknown

Manual reproduction commands taken from the issue:

```
$ pylint a          # with a/a.py and a/b.py, no a/__init__.py
$ pylint -E r       # r.py contains: from a import b
$ pylint -E r a
```

## Project Structure

Unknown. These locations need to be identified before planning:
- the code that expands command-line arguments (files, directories, module names) into modules to lint
- where astroid resolves a module name or path to a file, including the namespace-package handling
- where pylint's functional or regression tests and their input fixtures live

## Code Style

Unknown. Follow the existing conventions of the pylint and astroid codebases. No example snippet is available.

## Testing Strategy

The framework and test locations are unknown. The required test cases are:

**Regression tests (must fail before the fix, pass after):**
1. Fixture `a/{a.py, b.py}` with all files empty and no `__init__.py`. Lint `a`, expect no `F0010` and no `parse-error`. Expect `a/a.py` and `a/b.py` to be the files that get linted.
2. Same fixture plus `r.py` containing `from a import b`. Lint `r` and `a` together, expect no `E0611` and no `F0010`.
3. Argument order variant: lint `a` then `r`, expect the same clean result.

**Non-regression tests (must pass before and after):**
4. Same fixture with `a.py` renamed to `c.py`. Lint `a`, expect a clean result.
5. Same fixture plus an `a/__init__.py`. Lint `a`, expect a clean result, and the existing module naming and behaviour is unchanged.
6. `pylint -E r` alone with the original fixture stays clean.
7. A genuinely missing or invalid target still produces the error pylint emits today. The fix must not silence real errors.

**Edge cases to cover or deliberately decide on (see Open Questions):**
8. The file passed directly: `pylint a/a.py`.
9. Nested same-name chains, e.g. `a/a/a.py` with no `__init__.py` files.
10. A same-name module inside a regular package that has `__init__.py`. This must not change.

Coverage target: unknown. At least cover the new or changed branch in the resolution logic.

## Boundaries

- **Always:** Add regression tests that reproduce both symptoms from the issue. Keep behaviour for directories with `__init__.py` unchanged. Run the full existing test suite.
- **Ask first:** Changing the module names pylint reports for namespace-package files (e.g. `a.a` vs `a`), since this affects message output, `# pylint: disable` scoping, and config. Making the fix in astroid instead of or in addition to pylint. Raising minimum astroid version requirements. Changing the public argument-handling behaviour.
- **Never:** Create or require an `__init__.py` as a workaround. Suppress `F0010`/`E0611` generically to hide the symptom. Special-case the literal names `a`/`b` from the issue in tests or code.

## Success Criteria

1. With `a/a.py` and `a/b.py` (empty, no `__init__.py`), `pylint a` exits with no messages and no `F0010`. It does not try to open `a/__init__.py`.
2. With the same layout plus `r.py` (`from a import b`), `pylint -E r a` emits no `E0611` and no `F0010`. Its output matches the run with `a.py` renamed to `c.py`.
3. `pylint -E r` alone continues to emit nothing.
4. Results do not depend on whether the directory contains a file named after itself. Renaming `a/a.py` to `a/c.py` does not change which diagnostics are reported, apart from module names.
5. Every existing test still passes, and packages with `__init__.py` behave as before.
6. New regression tests for criteria 1–2 exist and fail on the unfixed code.

## Open Questions

1. When linting the directory `a`, what module name should `a/a.py` get in output: `a.a`, or something else? This must match how other namespace-package files are already named.
2. Should the fix live in pylint, in astroid, or in both? The `E0611` symptom suggests astroid's module cache or resolution is also involved.
3. Which Python, pylint, and astroid versions must the fix support? Should it be backported to a stable branch?
4. Should a bare argument like `a` be resolved first as a filesystem path or first as an importable module name? This matters when both interpretations exist, e.g. `a/` as a directory and `a.py` reachable via `sys.path`.
5. Is the nested same-name case (`a/a/a.py`) in scope for this change?
6. Are there related open issues about namespace-package discovery that should be addressed or referenced together?
7. What are the repository's test, lint, and build commands, and where do regression fixtures belong?