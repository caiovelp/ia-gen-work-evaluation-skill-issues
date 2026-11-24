# Spec: saferepr must not raise INTERNALERROR when an object's `__repr__` and attribute access both raise

## Objective

pytest crashes with `INTERNALERROR` instead of reporting a normal test failure when a failing test has a traceback-frame local whose `__repr__` raises **and** whose attribute access (`__getattribute__`) also raises. The session ends with "no tests ran" and the real failure is never shown.

**Who is affected:** Users whose tests involve objects with unusual dunder behaviour, such as proxies, mocks, lazy objects or deliberately broken objects. When such a test fails, pytest itself breaks.

**Observed behaviour (from the issue, pytest 5.4.1, Python 3.8.1):**

1. `test()` raises inside `SomeClass().attr`. A bare `raise` in `__getattribute__` gives `RuntimeError: No active exception to reraise`.
2. While building the failure report, `repr_args` calls `saferepr(argvalue)` on frame locals (`_pytest/_code/code.py`, line 693).
3. `SafeRepr.repr_instance` catches the exception from `repr(x)`. It then calls `_format_repr_exception(exc, x)` (`_pytest/_io/saferepr.py`, line 60).
4. `_format_repr_exception` evaluates `obj.__class__.__name__` (saferepr.py, line 23). That goes through the object's raising `__getattribute__` and raises again.
5. The new exception escapes `repr_instance`. `SafeRepr.repr` catches it (line 47/51) and calls `_format_repr_exception` again, which raises the same way.
6. The exception escapes `saferepr` and propagates to `wrap_session`, which produces `INTERNALERROR`.

**Root-cause hypothesis (based on the traceback, not verified against source):** The fallback path that formats a failed repr still touches the object's attributes (`obj.__class__`). That runs user-defined `__getattribute__`, so `saferepr` is not actually safe for these objects.

**Desired behaviour:** `saferepr` never raises for any object, whatever that object's `__repr__`, `__getattribute__`, or the exception it raises does. The test is reported as a normal failure, and pytest exits with the normal "tests failed" status, not the internal-error status.

### Acceptance criteria / user stories

- As a user, when my test fails and a frame local has a broken `__repr__` and a broken `__getattribute__`, I see a normal FAILED report with a placeholder repr for that object, and no INTERNALERROR.
- As a pytest maintainer, `saferepr(obj)` returns a string for every input object, even when every user-overridable hook on it raises.

## Assumptions

1. The bug is in pytest's `_pytest/_io/saferepr.py`, specifically the formatting of the "repr raised" placeholder. Paths come from the installed-package traceback. The paths in the source tree are assumed to match under some source root (unknown, possibly `src/_pytest/...`).
2. The class name in the placeholder should be obtained without invoking the instance's `__getattribute__`, for example from the object's actual type rather than via attribute lookup on the instance. This is a behavioural requirement, not a prescribed implementation.
3. The exact format of the placeholder string (something like `<[ExcType(...) raised in repr()] ClassName object at 0x...>`) should stay as it is for the ordinary case where only `__repr__` raises. Existing users and tests may depend on it.
4. Formatting the *exception itself* (its repr/str) inside the placeholder could also raise, if a user-defined exception class has a broken `__repr__`. Assumed in scope: "saferepr never raises" should cover it too.
5. A bare `raise` with no active exception gives `RuntimeError`, as in the reproducer. The fix must not depend on the specific exception type raised.
6. `BaseException` subclasses meant to stop the run (`KeyboardInterrupt`, `SystemExit`) raised from `__repr__` are assumed to keep their current handling, whatever that is. Behaviour for them is not changed by this work unless the maintainers decide otherwise (see Open Questions).
7. The fix targets the current development branch. Back-porting to 5.4.x is not assumed.
8. Similar "safe" formatting helpers may also access instance attributes, for example a `safeformat` / pretty-print variant in the same module. They are assumed to fall under the same requirement if they exist. This is unverified.

## Tech Stack

- Language: Python. The issue was reported on 3.8.1. The full supported version range of the project is **unknown**.
- Project: pytest. The reported version is 5.4.1, with dependencies py 1.8.1 and pluggy 0.13.1.
- Relevant stdlib: `reprlib.Repr`, which `SafeRepr` subclasses according to the traceback.

## Commands

Not visible in the issue. All are **unknown** and must be taken from the repository (e.g. `tox.ini`, `setup.cfg`, CI config):

```
Build:   unknown
Test:    unknown (presumably pytest run against the repo's own test suite; exact invocation/tox env unknown)
Lint:    unknown
Dev:     unknown
```

## Project Structure

Only these locations are known, from the traceback of the installed package:

```
_pytest/_io/saferepr.py   → SafeRepr, saferepr(), _format_repr_exception()  (primary area of change)
_pytest/_code/code.py     → FormattedExcinfo.repr_args() calls saferepr on frame locals (caller)
_pytest/reports.py        → TestReport.from_item_and_call (where the crash surfaces)
_pytest/main.py           → wrap_session (where INTERNALERROR is emitted)
```

- Source root in the repository: **unknown**.
- Test directory and file for saferepr tests: **unknown**. Presumably a dedicated saferepr test module exists. To be confirmed.

## Code Style

**Unknown.** Follow the existing conventions in `_pytest/_io/saferepr.py` and the repo's lint/format configuration, which is not visible. No snippet is provided, because inventing one would misrepresent the project's style.

## Testing Strategy

- **Framework:** pytest testing itself. The exact harness and fixtures (e.g. an in-process "run pytest" fixture) are **unknown** and must be checked in the repo.
- **Unit level (saferepr):**
  - Object whose `__repr__` raises and whose `__getattribute__` raises: `saferepr` returns a string and does not raise.
  - Object whose `__repr__` raises with a bare `raise` (`RuntimeError`): returns a placeholder string.
  - Object whose `__repr__` raises an exception whose own `__repr__`/`__str__` raises (per Assumption 4): returns a string.
  - Regression: an object whose `__repr__` raises but whose attribute access works still produces the existing placeholder format, including the correct class name.
- **Integration level (end-to-end run):**
  - Running the reproducer from the issue as a test file gives a normal failed test outcome: 1 failed, no `INTERNALERROR` in the output, and the "tests failed" exit code rather than the internal-error one.
- **Coverage expectations:** **Unknown** project threshold. At minimum, the new fallback branches in saferepr are exercised.

## Boundaries

- **Always:**
  - Keep `saferepr` total: it must return a string for every input.
  - Keep the existing placeholder format for the ordinary "repr raised" case.
  - Add regression tests reproducing the issue's scenario.
  - Run the existing test suite before committing.
- **Ask first:**
  - Changing the placeholder string format.
  - Changing how `KeyboardInterrupt`/`SystemExit`/other `BaseException`s raised from `__repr__` are handled.
  - Back-porting to a maintenance branch.
  - Touching callers in `_pytest/_code/code.py` rather than fixing inside saferepr.
  - Adding a changelog entry, if the project's changelog mechanism is unknown.
- **Never:**
  - Swallow the *test's* original failure.
  - Remove or weaken existing saferepr tests.
  - Make reporting call user-overridable instance attribute hooks in the fallback path.
  - Add new dependencies.

## Success Criteria

1. Running the issue's reproducer under pytest reports `test` as FAILED with a readable traceback. The output contains no `INTERNALERROR`, and the exit status is the normal "tests failed" status.
2. In that failure report, the frame-local `SomeClass` instance appears as a placeholder string. The class name should be resolved without calling the instance's `__getattribute__`. If the name cannot be determined at all, a generic placeholder is acceptable.
3. `saferepr(x)` returns a `str` and raises nothing (within the scope agreed in Open Questions) for:
   - (a) a raising `__repr__`;
   - (b) a raising `__repr__` combined with a raising `__getattribute__`;
   - (c) a raising `__repr__` whose exception has a raising `__repr__`.
4. Existing saferepr output for well-behaved objects and for the plain "repr raised" case is unchanged. Existing tests pass unmodified.
5. New unit and integration regression tests covering criteria 1–3 are added and pass.

## Open Questions

1. Should the placeholder use the object's real type name, obtained without touching instance attributes, or is a fully generic placeholder acceptable when attribute access raises? Should it instead report that the class name lookup *also* failed?
2. How should `BaseException` subclasses raised from `__repr__` or `__getattribute__` be treated, especially `KeyboardInterrupt` and `SystemExit`? Propagate them, or format them as placeholders?
3. Is the nested case in scope for this issue, where the exception's own `__repr__`/`__str__` raises, or should it be a follow-up?
4. Are there other "safe" formatting entry points that can hit the same path and should get the same guarantee? Examples: a pretty-format variant, assertion rewriting's repr helpers, or `repr_locals` with `showlocals`.
5. Which branch should the fix target, and is a back-port to 5.4.x wanted?
6. What are the repo's exact test, lint and build commands, its source/test directory layout, and its changelog convention? None of these are visible in the issue.
7. Should `repr_args` in `_pytest/_code/code.py` also get a defensive guard, so that a future regression in saferepr cannot escalate to INTERNALERROR? Or is fixing saferepr considered sufficient?