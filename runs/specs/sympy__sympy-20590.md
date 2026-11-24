# Spec: Restore `__dict__`-free (fully slotted) `Symbol` instances

## Objective

**Problem.** In SymPy 1.6.2, `Symbol` instances had no `__dict__`:

```python
>>> sympy.Symbol('s').__dict__
AttributeError: 'Symbol' object has no attribute '__dict__'
>>> sympy.Symbol('s').__slots__
('name',)
```

In SymPy 1.7, `sympy.Symbol('s').__dict__` exists and returns `{}`. The reporter suspects that a class in `Symbol`'s inheritance chain stopped defining `__slots__`. In Python, a class without `__slots__` gives every instance of every subclass a `__dict__`, which removes the memory and attribute-restriction benefits of the `__slots__` that `Symbol` declares.

**Goal.**
1. Confirm whether this is a regression. It looks like one, but this needs confirming (see Open Questions).
2. If it is, make `Symbol` instances slotted again so that accessing `__dict__` raises `AttributeError`.
3. Do this without breaking existing behavior: construction, pickling, copying, assumptions, caching, hashing and equality.

**Users affected.**
- SymPy users who create large numbers of symbols or expressions and rely on the memory footprint of slotted objects.
- Downstream code that relies on `Symbol` rejecting arbitrary attribute assignment.

**Acceptance criteria (draft).**
- `Symbol('s').__dict__` raises `AttributeError`, matching 1.6.2.
- Every class in `type(Symbol('s')).__mro__`, except `object`, defines `__slots__` in its own class body.
- Setting an undeclared attribute on a `Symbol` instance raises `AttributeError`, as in 1.6.2.
- The existing test suite passes. Pickling, copying, assumptions and caching of `Symbol` behave as before.

## Assumptions

1. This is the SymPy project, and the regression appeared between releases 1.6.2 and 1.7.
2. The cause is one or more classes in `Symbol`'s MRO that lack a `__slots__` declaration. Candidates could include a newly added base class or mixin, or a class whose `__slots__` was removed. This is the reporter's hypothesis and has not been verified.
3. The 1.6.2 behavior, fully slotted with no `__dict__`, is the intended design, and the 1.7 behavior was unintentional.
4. The fix should apply to the whole affected hierarchy, not only `Symbol`. If a shared base class is unslotted, other `Basic` subclasses probably gained a `__dict__` too.
5. No public API relies on storing arbitrary attributes on `Symbol` instances or on instances of the affected base classes.
6. Python behavior is standard CPython semantics for `__slots__`: a single unslotted class anywhere in the MRO reintroduces `__dict__`.

## Tech Stack

- Language: Python. Supported versions are **unknown**; check the project's packaging metadata.
- Library: SymPy. Affected versions are 1.7 and possibly later. 1.6.2 is the known-good version.
- External dependencies relevant to this change: **unknown** (none are expected).

## Commands

Commands not visible in the issue are marked unknown.

```
Reproduce:  python -c "import sympy; sympy.Symbol('s').__dict__"   # should raise AttributeError
Test:       unknown (project test runner / command not given in issue)
Lint:       unknown
Build:      unknown (pure-Python package; likely none needed)
```

## Project Structure

Not visible in the issue; all of the following are **unknown**:
- The module that defines `Symbol`.
- The modules that define each base class in `Symbol`'s MRO.
- Where tests for core classes live.
- Whether a project-wide test or check already exists for `__slots__` coverage.

## Code Style

Unknown. Follow the existing conventions of the SymPy codebase. The pattern the issue implies, as visible in its output, is that each class declares its own `__slots__` tuple, for example `__slots__ = ('name',)` on `Symbol`. A base class with no new attributes would declare `__slots__ = ()`.

## Testing Strategy

- **Regression test:** assert that `Symbol('s')` has no `__dict__`, for example that accessing it raises `AttributeError`.
- **Hierarchy test (proposed):** assert that every class in `Symbol.__mro__` other than `object` has `'__slots__'` in its own `__dict__`. Optionally extend this to other core `Basic` subclasses, pending Open Question 3.
- **Behavior preservation:** run the existing tests for:
  - pickling and unpickling `Symbol`, `Dummy` and `Wild`
  - `copy` and `deepcopy`
  - assumptions such as `Symbol('x', positive=True)`
  - caching
- Test framework, test file locations and coverage requirements are **unknown**.

## Boundaries

- **Always:**
  - Add a regression test that fails on the current code and passes after the fix.
  - Run the full existing test suite.
  - Keep the public behavior of `Symbol` unchanged apart from removing `__dict__`.
- **Ask first:**
  - Removing a base class or mixin, or changing the class hierarchy.
  - Extending the fix to classes outside `Symbol`'s MRO.
  - Any change that alters pickling format or the public attributes of affected classes.
  - Adding a project-wide `__slots__` enforcement check.
- **Never:**
  - Remove or weaken existing tests to make the change pass.
  - Hack around the issue in a way that only hides `__dict__`, such as overriding `__getattribute__`, instead of restoring real slotting.
  - Introduce new runtime dependencies.

## Success Criteria

- `sympy.Symbol('s').__dict__` raises `AttributeError`.
- `Symbol('s').__slots__ == ('name',)` still holds, or matches the 1.6.2 value.
- No class in `Symbol`'s MRO, other than `object`, lacks its own `__slots__`.
- A new regression test covers the conditions above and is part of the suite.
- The entire existing test suite passes with no new failures.

## Open Questions

1. **Intent:** Was the loss of `__slots__` deliberate, for example to support some feature that needs instance attributes, or accidental as the reporter believes? If deliberate, this becomes a "won't fix" or a documentation issue rather than a bug.
2. **Root cause:** Which class or classes in `Symbol`'s MRO lack `__slots__` in 1.7? Was a base class or mixin added, or were `__slots__` removed from an existing one? This needs to be identified from the 1.6.2→1.7 diff, which is not visible here.
3. **Scope:** Should the fix and its tests cover only `Symbol`, all `Basic` subclasses, or every class that previously had `__slots__`? A shared unslotted base likely affects many classes.
4. **Dependence on `__dict__`:** Does any code in 1.7 or later now rely on setting instance attributes on these objects, which would break when `__dict__` is removed? Possible examples are caching, printing, or assumption machinery.
5. **Enforcement:** Should a permanent test guard against future regressions by asserting that all core classes define `__slots__`?
6. **Backport:** Should the fix target only the next release, or be backported to a 1.7.x patch release?
7. **Tooling:** What are the project's test, lint and CI commands, and what Python versions are supported? These are unknown from the issue.