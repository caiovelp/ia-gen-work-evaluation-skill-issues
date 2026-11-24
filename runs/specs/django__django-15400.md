# Spec: Add `__radd__` support to `SimpleLazyObject`

## Objective

`SimpleLazyObject` is a lazy proxy that defers evaluating a wrapped object until first use. It forwards many magic methods to the wrapped object, but it does not implement `__radd__`. Because of this, an expression with the lazy object on the **right** of `+` fails even when the same expression works on the unwrapped value:

```python
lazy = SimpleLazyObject(lambda: 1)
5 + lazy   # expected: 6 (same as 5 + 1); currently raises TypeError
```

**Goal:** `other + lazy_obj` should behave exactly like `other + wrapped_obj`. Evaluating the expression must trigger setup of the wrapped object if that has not happened yet.

**User:** Developers who pass `SimpleLazyObject` instances into code that puts them on the right-hand side of `+`. Examples include string concatenation, numeric arithmetic and `sum()`-style accumulation.

**Why the obvious one-liner fails** (from the issue):
- `new_method_proxy(operator.radd)` cannot be used because `operator.radd` does not exist.
- `new_method_proxy(operator.attrgetter("__radd__"))` is incorrect. Many types (for example `str`) have no `__radd__`, and `attrgetter` would raise `AttributeError` instead of following Python's normal binary-operator fallback.

**Reporter's working implementation (reference only, not yet adopted):**
```python
def __radd__(self, other):
    if self._wrapped is empty:
        self._setup()
    return other + self._wrapped
```

### Acceptance criteria
1. `other + lazy` returns the same value as `other + wrapped` for wrapped types that support it, including types with no `__radd__` of their own:
   - `int`: `1 + SimpleLazyObject(lambda: 2) == 3`
   - `str`: `"a" + SimpleLazyObject(lambda: "b") == "ab"`
   - `list`: `[1] + SimpleLazyObject(lambda: [2]) == [1, 2]`
2. If the wrapped object has not been set up yet, `other + lazy` sets it up (lazy setup is triggered exactly as for other proxied methods).
3. If `other + wrapped` would raise `TypeError`, then `other + lazy` also raises `TypeError` and not some other exception such as `AttributeError`.
4. A custom type that defines `__radd__` has that `__radd__` invoked when wrapped.
5. Existing proxied behaviour of `SimpleLazyObject`/`LazyObject` does not regress, including `lazy + other` via `__add__` if it exists.

## Assumptions
1. This issue is about Django, and `SimpleLazyObject`, `LazyObject`, `new_method_proxy` and the `empty` sentinel live in `django.utils.functional`. This is inferred from the names; the file was not seen.
2. The scope is `__radd__` only. Other missing reflected or in-place operators (`__rsub__`, `__rmul__`, `__iadd__`, …) are out of scope unless the Open Questions say otherwise.
3. The correct semantics are "evaluate `other + wrapped` using normal Python operator dispatch", not "call `wrapped.__radd__(other)` directly". This is what makes types without `__radd__` (such as `str`) work.
4. The method may be defined on `SimpleLazyObject` or on its base `LazyObject`. The placement should follow wherever the existing proxied magic methods are defined, which is unknown here.
5. Tests are added to the project's existing test suite for `django.utils.functional` lazy objects. The location is unknown.
6. No new dependencies are needed (for example, `wrapt` must not be introduced).

## Tech Stack
- Python, in the Django codebase (assumed). The supported Python and Django versions are **unknown**.

## Commands
- Build: **unknown** (not stated in the issue)
- Test: **unknown** (likely the project's own test runner; exact command and flags not visible)
- Lint: **unknown**

## Project Structure
- Implementation: **unknown path** (assumed module `django.utils.functional`)
- Tests: **unknown path** (existing tests for `SimpleLazyObject`/`LazyObject`)
- Docs/release notes: **unknown** whether a release note is required

## Code Style
- Follow the existing conventions for proxied magic methods in the same class. Use `new_method_proxy` if a suitable callable can be expressed. Otherwise use an explicit method that performs lazy setup using the same `_wrapped is empty` / `_setup()` pattern the class already uses.
- No concrete style snippet is available from the repository. The reporter's snippet above is the only reference.

## Testing Strategy
- **Unit tests** cover each acceptance criterion:
  - int, str and list on the right-hand side
  - a custom class with `__radd__`
  - an unsupported combination raising `TypeError`
  - setup triggered from the un-evaluated state
- Run tests against both `SimpleLazyObject` and, if the method is placed there, `LazyObject` subclasses.
- Run the full existing lazy-object test suite to confirm there are no regressions.
- The test framework and coverage expectations are **unknown**; use whatever the existing tests use.

## Boundaries
- **Always:**
  - Preserve laziness (no evaluation before the operator is used).
  - Keep normal Python operator semantics.
  - Add regression tests.
  - Run existing lazy-object tests.
- **Ask first:**
  - Adding other reflected or in-place operators beyond `__radd__`.
  - Changing `new_method_proxy`'s behaviour.
  - Moving methods between `LazyObject` and `SimpleLazyObject`.
- **Never:**
  - Add a dependency such as `wrapt`.
  - Use `operator.attrgetter("__radd__")`.
  - Swallow or convert `TypeError` into other exceptions.
  - Change public behaviour of existing proxied methods.

## Success Criteria
- All five acceptance criteria above are covered by passing automated tests.
- `1 + SimpleLazyObject(lambda: 2) == 3` and `"a" + SimpleLazyObject(lambda: "b") == "ab"` both hold.
- An unsupported combination raises `TypeError`, matching unwrapped behaviour.
- The existing test suite passes with no regressions.

## Open Questions
1. Should this fix cover only `__radd__`, or all missing reflected operators (`__rsub__`, `__rmul__`, `__rtruediv__`, …) for consistency? The issue notes "a whole bunch" are missing.
2. Should `__radd__` live on `LazyObject` (so all lazy subclasses get it) or only on `SimpleLazyObject`?
3. Is `other + self._wrapped` the agreed semantics, or should it be `self._wrapped.__radd__(other)` with a `NotImplemented` fallback? They differ when `other.__add__` accepts the wrapped type: Python already tried `other.__add__(lazy)` before reaching `__radd__`.
4. Should behaviour be specified when both operands are lazy objects (for example, `lazy_a + lazy_b`)?
5. Which Django and Python versions does this target, and does it need a release note or backport?
6. What are the exact test command and test file location for lazy-object tests?