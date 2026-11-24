# Spec: Keep traceback file paths relative to the original invocation directory when a fixture changes the working directory

## Objective

When a test or fixture changes the current working directory (with `os.chdir()` or `monkeypatch.chdir()`), pytest's failure report shows the location of the failing test relative to the *new* directory. For example, it prints `../test_path_error.py:29: AssertionError` instead of `test_path_error.py:29: AssertionError`.

Editors and IDEs that parse pytest output (such as Emacs compilation-mode, which runs with `default-directory: "~/src/pytest_path_error/"`) resolve paths against the directory pytest was launched from. Because the cwd change is invisible to them, they cannot jump to the error location.

**Goal:** File paths in failure reports stay relative to the directory pytest was invoked from, even if the test or fixture changes the cwd before the report is produced.

**Users:**
- Developers who run pytest from editors or IDEs that link `file:line` locations.
- CI log readers.
- Anyone whose fixtures `chdir` into temporary or private directories, which is a common pattern.

**Acceptance criteria (user-level):**
- Given the reproducer below, running `pytest` from the directory that contains `test_path_error.py` prints `test_path_error.py:29: AssertionError`, not `../test_path_error.py:29: AssertionError`.
- The same holds when the directory change is done through `monkeypatch.chdir(out_dir)` instead of `os.chdir`.

**Reproducer (from the issue):**

```python
import os
import errno
import shutil

import pytest


@pytest.fixture
def private_dir():  # or (monkeypatch)
    out_dir = 'ddd'

    try:
        shutil.rmtree(out_dir)
    except OSError as ex:
        if ex.errno != errno.ENOENT:
            raise
    os.mkdir(out_dir)

    old_dir = os.getcwd()
    os.chdir(out_dir)
    yield out_dir
    os.chdir(old_dir)

    # Same issue if using:
    # monkeypatch.chdir(out_dir)


def test_show_wrong_path(private_dir):
    assert False
```

```diff
+ Expected: test_path_error.py:29: AssertionError
- Displayed: ../test_path_error.py:29: AssertionError
```

## Assumptions

1. The affected code is pytest itself, not a plugin. The reporter environment was pytest 5.3.2, py 1.8.1, pluggy 0.13.1, Python 3.7.5, Linux.
2. The bug is still present on the current development branch. This has not been verified.
3. The wrong path comes from paths being made relative to `os.getcwd()` at the time the report or traceback is formatted. In the reproducer, that moment is while the fixture's `chdir` is still in effect, because teardown has not run yet when the longrepr is built. This is inferred from the symptom and has not been confirmed in code.
4. "Original directory" means the cwd at the moment pytest was invoked. It does not mean `rootdir`. In the issue the two are the same (`/home/lhn/src/pytest_path_error`), but they can differ.
5. The fix targets the "long" traceback location line (`path:lineno: ExceptionType`). Other path-bearing output is in scope only if it uses the same mechanism (see Open Questions).
6. Absolute-path output modes (if any are configured) are unaffected. Only relative-path rendering changes.
7. Behaviour when no cwd change happens must remain byte-for-byte identical.

## Tech Stack

- Python project: pytest.
  - Supported Python versions for the target branch: unknown.
- Relevant dependencies seen in the issue: `py` (1.8.1, provides `py.path.local`), `pluggy` (0.13.1).
  - Whether the current code still uses `py.path` or `pathlib` for this: unknown.

## Commands

All unknown, because the repository is not visible. To be filled in from the project's contributing docs or CI config:

```
Build:   unknown
Test:    unknown (pytest's own test suite; exact invocation, e.g. tox env, unknown)
Lint:    unknown
Dev:     unknown
```

Reproduce (from the issue): run `pytest` in a directory containing only `test_path_error.py` above. The reporter used `nox` with a session that runs `pip install pytest>=5.3` and then `pytest`.

## Project Structure

Unknown. Locations of the following must be identified before planning:

- The code that formats traceback entry locations (`path:lineno: ExcType`).
- The code that computes relative paths for reporting.
- The test files covering traceback/terminal reporting.
- The changelog directory and its entry convention.

## Code Style

Unknown. Follow the existing conventions of the pytest codebase (formatter, linters, type annotations, changelog fragment format), which must be checked in the repository.

## Testing Strategy

- **Framework:** pytest's own test suite. It likely uses the `testdir`/`pytester`-style fixture for running inner pytest sessions; the exact fixture name on the target branch is unknown.
- **Required regression tests** (acceptance tests, written to fail before the fix):
  1. A test module whose fixture uses `os.chdir()` into a subdirectory and then fails. The output contains `test_<name>.py:<line>: AssertionError` and does not contain `../test_<name>.py`.
  2. The same scenario using `monkeypatch.chdir()`.
  3. A control case without any cwd change. Output is unchanged from current behaviour.
- **Possibly useful extra cases** (see Open Questions for whether they are in scope):
  - A cwd change inside the test body itself rather than a fixture.
  - A cwd change to a directory outside the rootdir.
  - A cwd change that is not restored.
  - The `--tb=short`, `--tb=line` and `--tb=native` traceback styles.
- **Level:** Integration / functional tests through the terminal output. Unit tests are optional if a pure path-formatting helper is touched.
- **Coverage expectation:** Unknown project threshold. At minimum, the new behaviour and the no-chdir control case are covered.

## Boundaries

- **Always:**
  - Add a regression test reproducing the issue before changing behaviour.
  - Keep output identical when the cwd is not changed.
  - Add a changelog entry per project convention.
  - Run the full test suite before submitting.
- **Ask first:**
  - Changing which directory pytest considers the reference for relative paths beyond the "invocation directory" definition.
  - Changing output of other reporters or path-bearing lines not covered by this issue.
  - Changing public APIs (e.g. signatures of traceback/repr classes).
  - Adding dependencies.
- **Never:**
  - Change user-visible behaviour of `monkeypatch.chdir` or forbid cwd changes in tests.
  - Switch relative paths to absolute paths as a workaround without approval.
  - Remove or loosen existing tests to make the change pass.

## Success Criteria

1. With the reproducer, run from its containing directory, the failure location line reads exactly `test_path_error.py:29: AssertionError`.
2. Criterion 1 holds both with `os.chdir` in a fixture and with `monkeypatch.chdir` in a fixture.
3. No `../` prefix appears in the reported location for files located under the invocation directory, regardless of cwd changes made by fixtures or tests.
4. Runs with no cwd change produce unchanged output. The existing test suite passes.
5. New regression tests exist and fail on the unfixed code.
6. A changelog entry references the issue.

## Open Questions

1. What is the reference directory: the invocation cwd or `rootdir`? These differ when pytest is run from a subdirectory or with `--rootdir`. Which one do editor integrations expect?
2. Which traceback styles are in scope (`long`, `short`, `line`, `native`)? Do `native` tracebacks, which come from Python's own formatting, need to change?
3. Are other path-bearing outputs in scope? Examples: the short test summary info (`-r`) lines, collection error messages, warnings summary locations, and `--junitxml` file attributes.
4. If a test changes into a directory outside the invocation directory and the failing file is also outside it, what should be shown: a relative path with `../` from the original directory, or an absolute path?
5. Should a warning or note be shown when cwd changed during a test, or should the change be silent?
6. Which branch or version should the fix target? Is a backport to a maintenance branch expected?
7. Is this already fixed on the current development branch? It needs confirmation against the repository.
8. What are the exact test, lint and changelog commands and conventions for the project? These are unknown from the issue.