# Spec: `shell -c` / stdin execution loses top-level names inside functions

## Assumptions

1. The bug is in Django's `shell` management command at `django/core/management/commands/shell.py`, in the `handle()` method. This is the path shown in the issue's traceback.
2. Both execution paths in `handle()` are affected and should be fixed the same way:
   - `exec(options['command'])` for `-c`
   - `exec(sys.stdin.read())` for piped stdin
3. **Root cause.** `exec(code)` without explicit namespaces runs with:
   - the module globals of `shell.py` as globals, and
   - `handle()`'s local namespace as locals.

   Top-level statements such as `import django` bind into the locals dict. Functions defined in that code resolve free names through globals, so they cannot see those bindings.
4. **Target behavior** matches `python -c`: top-level code and function bodies share one namespace. Passing a single dict as globals (with no separate locals) gives this. The issue proposes a new, empty dict.
5. Python adds `__builtins__` to the dict automatically when `exec` runs, so builtins stay available.
6. The interactive shells (IPython, bpython, plain Python REPL) are out of scope. The issue only covers `-c` and stdin.
7. The issue reports the bug on Django 2.2.16 with Python 3.7 and 3.8, and says the code is the same on master. The fix targets master. Backporting is not decided here.
8. This is a single capability, so no capability map (Phase 0) is needed.

## Objective

Make code passed to `manage.py shell -c "<code>"` (or `python -m django shell -c`), or piped into `shell` via stdin, run with the same name-resolution rules as `python -c`.

In particular, names bound at the top level of the snippet (imports, assignments, `def`, `class`) must be visible inside functions and classes defined in that snippet.

**User:** developers and scripts that run one-off code against a configured Django project through the `shell` command.

**Acceptance (user story):**

> As a developer, when I run
>
> ```
> python -m django shell -c "import django
> def f():
>     print(django.__version__)
> f()"
> ```
>
> I see the Django version printed, not `NameError: name 'django' is not defined`.

## Tech Stack

- **Language:** Python. The issue reports 3.7 and 3.8. Supported versions on master are **unknown**.
- **Framework:** Django management command framework (`BaseCommand.handle`).
- **Dependencies:** no new dependencies.

## Commands

- **Build:** unknown (none shown in the issue)
- **Test:** unknown. The repository's test runner invocation is not visible in the issue.
- **Lint:** unknown
- **Reproduce (from the issue):**
  ```
  python -m django shell -c "
  import django
  def f():
      print(django.__version__)
  f()"
  ```

## Project Structure

- `django/core/management/commands/shell.py`: location of the `shell` command and the `exec` calls. This is the only file known from the issue.
- Location of the existing `shell` command tests: **unknown**.
- Documentation for the `shell` command and release notes: location **unknown**.

## Code Style

- Follow the existing style of `shell.py`. The full file is not visible, so details beyond the `handle()` excerpt in the issue are **unknown**.
- Keep the change minimal and local to the two `exec` call sites.

## Testing Strategy

- **Framework / location:** **unknown**. Use the project's existing test suite and the existing tests for the `shell` command, if any.
- **Required regression tests** (each must fail before the fix and pass after):
  1. **`-c` with a function using a top-level import.** The `command` option contains an `import` plus a `def` that uses the imported name and a call to it. Expected output is produced and no `NameError` is raised.
  2. **Stdin with the same snippet.** The test mocks or patches stdin and the readiness check. Expected output is produced.
- **Optional/regression coverage:**
  - Top-level variables and classes are visible inside functions.
  - Simple single-line commands (e.g. `-c "print(1)"`) still work.
- **Test level:** unit/integration at the management command level, for example calling the command programmatically and capturing stdout. No end-to-end shell spawning is required, unless that is the existing convention (**unknown**).

## Boundaries

**Always:**
- Fix both the `-c` path and the stdin path consistently.
- Add regression tests for both paths.
- Run the existing `shell` command tests.

**Ask first:**
- Pre-populating the exec namespace with anything beyond what the issue proposes, such as `__name__`, Django models, or settings.
- Changing interactive-shell behavior.
- Backporting to stable branches.
- Adding a release note or docs change.

**Never:**
- Expose `shell.py`'s module globals or `handle()`'s locals to user code as a "fix".
- Add dependencies.
- Change the command's CLI options.
- Remove or weaken existing tests.

## Success Criteria

1. The reproduction snippet from the issue prints the Django version via `shell -c` and exits successfully.
2. The same snippet piped through stdin to `shell` (on non-Windows platforms) prints the Django version.
3. Within executed code, names bound at module (snippet) top level resolve inside nested functions and classes, matching `python -c` semantics.
4. Builtins (e.g. `print`, `len`) remain available in executed code.
5. The new regression tests fail on the current code and pass with the fix.
6. All existing `shell` command tests pass.

## Open Questions

1. **Backward compatibility.** Today, user code implicitly sees `shell.py`'s module globals (e.g. `sys`, `select`, and whatever else that module imports) without importing them. A fresh empty dict removes these names. Is this acceptable as a bug fix, or does it need a release note?
2. **`__name__`.** Should the exec namespace set `__name__ = '__main__'` (or similar) so that `if __name__ == '__main__':` behaves as it does under `python -c`? Or is a strictly empty dict preferred, as the issue suggests?
3. **Shared namespace.** Should the `-c` and stdin paths share a helper or namespace-construction logic, or stay as two independent `exec` calls?
4. **Versions.** Which branches should receive the fix: master only, or also 2.2.x / other stable branches?
5. **Test conventions.** Where do the existing `shell` command tests live, and how do they capture output and mock stdin?
6. **Documentation.** Should the `shell` command docs mention the execution semantics?