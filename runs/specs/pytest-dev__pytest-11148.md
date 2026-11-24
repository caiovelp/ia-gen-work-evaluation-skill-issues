# Spec: Single Module Identity Under `--import-mode=importlib`

## Objective

Under `--import-mode=importlib`, pytest should not create a second, separate module object for a module that is already importable through the normal import system.

**Reported situation (pmxbot/pmxbot@7f189ad):**

- The project is moving from `pkg_resources`-style namespace packages to PEP 420 namespace packages.
- To do that, the reporter switched to `import-mode=importlib` and reorganized the tests.
- `tests/unit/test_commands.py` calls `core.initialize(config)`, which sets the class attribute `pmxbot.logging.Logger.store`.
- On the next line, the test reads `logging.Logger.store` and gets `AttributeError: type object 'Logger' has no attribute 'store'`.
- PDB shows two distinct module objects, both named `pmxbot.logging` and both loaded from the same file `/Users/jaraco/code/pmxbot/pmxbot/pmxbot/logging.py`:
  - `sys.modules['pmxbot.logging']`
  - `tests.unit.test_commands.logging`
- `sys.modules['pmxbot.logging'] is logging` is `False`.

**Who is affected:** users of `--import-mode=importlib` whose project package sits under the rootdir and is also importable from `sys.path`, for example as an editable or development install. Namespace-package projects are an important case. The bug hits them when pytest also loads files of that package directly, for example during collection.

**What success looks like:** a single source file used during one test session maps to a single module object. That object is the one registered in `sys.modules` under its canonical name. Any state that application code sets on that module, or on classes in it, is visible to test code that imported it.

## Assumptions

1. The defect is in pytest's `importlib` import mode, not in pmxbot. The duplicate is created because pytest loads a file by path and executes it as a fresh module, rather than reusing the module already registered in `sys.modules` or importable from `sys.path`.
2. Something causes pytest to import `pmxbot/logging.py` (and possibly other `pmxbot/*.py` files) by file path during collection. The most likely candidate is `--doctest-modules` or a `python_files` / `testpaths` setting in `pytest.ini`. **This is unverified**, because the `pytest.ini` contents are not in the issue.
3. pmxbot is importable from `sys.path`. The `plugins:` line lists `pmxbot-1122.14.3.dev13+g7f189ad`, which suggests it is installed, probably editable, in the tox environment.
4. The reported environment is Python 3.11.1, pytest 7.2.0 and macOS. The bug is assumed not to be platform-specific.
5. The original purpose of `importlib` mode must be preserved: test files with the same basename in different directories must not collide, and pytest should not need to change `sys.path`.
6. No minimal reproducer exists yet. One must be built as part of this work, independent of pmxbot.

## Tech Stack

- **Language:** Python. Reported on 3.11.1; the supported version range is unknown.
- **Software under change:** pytest. Reported against 7.2.0; the target branch or version is unknown.
- **Relevant feature:** the `--import-mode=importlib` option (`import-mode` ini/CLI setting).
- **Possibly relevant:** doctest module collection (unconfirmed) and PEP 420 namespace packages.

## Commands

All of these are unknown, because the pytest repository is not visible.

- Build: unknown
- Test: unknown
- Lint: unknown
- Reproduce (reporter's environment): run via tox (inferred from `cachedir: .tox/python/.pytest_cache`). The exact command is unknown.

## Project Structure

Unknown for pytest itself. The location of the import-mode implementation is not visible in the issue.

Known from the issue, in the pmxbot reproduction context only:

```
/Users/jaraco/code/pmxbot/pmxbot/        → rootdir (contains pytest.ini)
  pmxbot/logging.py                      → module that gets duplicated
  tests/unit/test_commands.py            → failing test (setup_class, line 37)
  tests/unit/testconf.yaml               → config loaded by the test
```

## Code Style

Unknown. Follow the existing conventions of the pytest codebase.

## Testing Strategy

Framework: pytest's own test suite. The location and fixtures are unknown, though tests that build temporary projects are assumed to be the norm.

Required tests:

1. **Minimal reproducer (regression test), with no pmxbot dependency.**
   - Setup:
     - Create a temporary project with a package under rootdir. The package is importable via `sys.path`.
     - A module in the package defines a class.
     - A test module imports that module and calls a function that sets a class attribute.
     - Configure whatever causes pytest to also load the package file by path (per Assumption 2).
   - Run with `--import-mode=importlib`.
   - Assert that:
     - the attribute is visible from the test, and
     - `sys.modules[name] is imported_module`.
2. **Namespace variant.** Repeat test 1 with the package laid out as a PEP 420 namespace package.
3. **Non-regression for the purpose of `importlib` mode.**
   - Two test files with the same basename in different directories, without `__init__.py`, still collect and run under `importlib` mode.
4. **Non-regression for other modes.**
   - Existing `prepend` and `append` mode behavior is unchanged.

## Boundaries

- **Always:**
  - Add a regression test that fails before the change and passes after it.
  - Keep `importlib` mode from changing `sys.path`.
  - Keep each change scoped to `importlib` mode.
- **Ask first:**
  - Changing the default import mode.
  - Changing how module names are derived from paths in `importlib` mode in ways visible to users, such as the `__name__` of test modules.
  - Adding new configuration options.
  - Changing doctest collection behavior.
- **Never:**
  - Work around the bug inside pmxbot or other downstream projects as the "fix".
  - Remove or weaken existing import-mode tests.
  - Silently overwrite an existing `sys.modules` entry that points to a different file.

## Success Criteria

1. Under `--import-mode=importlib`, in one session, a source file importable via `sys.path` under canonical name `X` is represented by exactly one module object, and that object is `sys.modules['X']`.
2. In the reproducer, state set on a class by application code (as `core.initialize` sets `Logger.store`) is visible to the test that imported the module. No `AttributeError` occurs.
3. The pmxbot scenario at commit 7f189ad no longer shows `sys.modules['pmxbot.logging'] is logging == False`. This is verified manually if a pmxbot environment is available.
4. Same-basename test files in separate directories still work under `importlib` mode.
5. The full existing pytest suite passes, using an unknown command.

## Open Questions

1. What causes pytest to load `pmxbot/logging.py` by path? Is `--doctest-modules` (or a similar option) enabled in pmxbot's `pytest.ini`? Can the issue be reproduced without it?
2. Which import produced `tests.unit.test_commands.logging`? Was it a plain `from pmxbot import logging`, or something else? And which of the two objects did `core.initialize` modify: the `sys.modules` one, or a third?
3. What should the intended behavior be when the module to load is already in `sys.modules` under its canonical name? Options:
   - reuse that object,
   - attempt a normal import first and fall back to path-based loading, or
   - something else.
4. What should happen when `sys.modules` already has an entry with the same name pointing to a *different* file: error, warning, or a separate module?
5. Does the fix need to cover only `importlib` mode, or also the conftest and plugin loading paths?
6. Which pytest version or branch is the target, and should the fix be backported to 7.2.x?
7. Is a change in the `__name__` of test modules collected under `importlib` mode acceptable if the fix requires it? (See Boundaries: ask first.)
8. Can the reporter supply a minimal reproducer, or confirm the one built for this work matches their failure?