# Spec: Make `Q` ↔ `Exists` combination commutative for `&` and `|`

## Assumptions
1. This is the Django codebase. The affected code is `django/db/models/query_utils.py` (`Q._combine`, `Q.__and__`) and `django/db/models/expressions.py` (`Exists`), as shown in the traceback. I have not seen the current state of those files.
2. The reporter is on Python 3.8 and a Django version that is not named. The fix targets the current development branch. Whether it should be backported is unknown.
3. `Exists(...) & Q(...)` already works, and it returns a `Q` that wraps the `Exists` object. The left-hand `Exists` handles the combination, probably through a mixin on the expression side. Its exact mechanism has not been checked.
4. `|` is affected in the same way as `&`. The issue claims this but only shows `&`.
5. `Q(...) & <arbitrary non-Q object>` should still raise `TypeError`. Only "conditional" expressions such as `Exists` should be accepted.
6. The reporter's guess about a missing `__rand__` is unverified. Because `Q.__and__` raises `TypeError` rather than returning `NotImplemented`, Python never tries the reflected operator. Adding `__rand__` on its own may therefore have no effect. The root cause still needs to be confirmed.

## Objective
Django users build query filters by combining `Q` objects with boolean expressions such as `Exists(...)`. Today, the result of combining them depends on operand order:

- `Exists(qs) & Q()` works.
- `Q() & Exists(qs)` raises `TypeError: <Exists object>` from `Q._combine`.

The goal is to make `&` and `|` work whichever side the `Q` is on, for `Q`/`Exists` pairs. The "commutativity" in the issue means both orders are accepted and produce filters with equivalent SQL semantics. It does not require structurally identical objects.

### Acceptance criteria (user stories)
- As a developer, I can write `Q(...) & Exists(qs)` and get a valid combined condition usable in `.filter()`.
- As a developer, I can write `Q(...) | Exists(qs)` with the same result.
- Using either order in `Model.objects.filter(...)` returns the same rows.
- Combining `Q` with a non-conditional, unsupported object still raises `TypeError`.

## Tech Stack
- Python, Django ORM. The supported Python and Django versions for the target branch are **unknown** from the issue.
- Relevant modules (from the traceback): `django/db/models/query_utils.py` and `django/db/models/expressions.py`.

## Commands
- Build: not applicable (pure Python library). The exact install command is **unknown**.
- Test: **unknown**. Django's usual runner lives in its `tests/` directory, but the exact command and settings are not visible in the issue.
- Lint: **unknown**.
- Dev: not applicable.

## Project Structure
- `django/db/models/query_utils.py` defines `Q`, `Q._combine` and `Q.__and__` (from the traceback).
- `django/db/models/expressions.py` defines `Exists` (from the traceback).
- Test location: **unknown**. It is likely the existing `Q`/expressions test modules in Django's test suite, but these have not been verified.

## Code Style
- Follow the existing Django code style in the touched modules. The concrete conventions are **unknown** because the code was not visible.
- Observed behavior to preserve: `Q._combine` raises `TypeError(other)` for unsupported operands. The error type should stay the same for genuinely unsupported operands.

## Testing Strategy
- **Unit tests**, at the expression/`Q` level:
  - `Q() & Exists(qs)` and `Q() | Exists(qs)` do not raise.
  - Non-empty `Q(field=value) & Exists(qs)` and `Q(field=value) | Exists(qs)` do not raise.
  - The results are usable conditions, for example when passed to `.filter()`.
  - The existing behavior of `Exists(qs) & Q()` and `Exists(qs) | Q()` stays unchanged.
  - `Q() & object()` (and `|`) still raises `TypeError`.
- **Integration (DB-backed) tests:**
  - `Model.objects.filter(Q(...) & Exists(...))` returns the same rows as `Model.objects.filter(Exists(...) & Q(...))`.
  - The same check applies for `|`.
- **Edge cases:**
  - Empty `Q()` combined with `Exists` must not drop the `Exists`. In the old path, an empty other `Q` was ignored.
  - Negated `~Exists(...)` combined on either side.
- Coverage threshold: **unknown**. At minimum, the new behavior must be exercised by regression tests.

## Boundaries
- **Always:**
  - Add regression tests that reproduce the issue's exact example.
  - Keep `TypeError` for unsupported operands.
  - Cover both `&` and `|`.
- **Ask first:**
  - Widening `Q` combination to accept *all* expressions rather than only conditional/boolean ones.
  - Changing the structure or `repr` of existing `Exists & Q` results.
  - Changing `Q.deconstruct()` output.
  - Backporting to release branches.
- **Never:**
  - Silently swallow invalid operands.
  - Change the SQL semantics of existing `Q`-only combinations.
  - Remove or weaken existing tests.

## Success Criteria
- `Q() & Exists(Product.objects.all())` no longer raises. The same holds for `|` and for non-empty `Q`.
- For a given dataset, `filter(Q(a) & Exists(s))` and `filter(Exists(s) & Q(a))` return identical results. The same holds for `|`.
- An empty `Q()` combined with `Exists(...)` in either order yields a condition equivalent to the `Exists(...)` alone.
- `Q() & object()` still raises `TypeError`.
- The full existing test suite passes.

## Open Questions
1. **Scope of accepted operands:** Should `Q._combine` accept only `Exists`, or any expression with `conditional = True`? Other candidates include boolean `Case`/`When`, lookups and `ExpressionWrapper(output_field=BooleanField())`.
2. **Result shape:** Must `Q() & Exists(...)` produce a `Q` wrapping the `Exists`, mirroring the reverse order? Or is SQL-level equivalence enough?
3. **Root-cause direction:** Should the fix make `Q` accept conditional expressions, or should `Q` return `NotImplemented` so Python falls back to a reflected operator on the expression? Is adding `__rand__`/`__ror__` on the expression side desired at all?
4. **Empty `Q` handling:** Should combining an empty `Q()` with `Exists` return just the `Exists`, wrapped or unwrapped? Note that the current "ignore empty other `Q`" shortcut does not apply here.
5. **Other operators:** Should `^` (XOR), if supported on `Q` in the target version, get the same treatment?
6. **Versions:** Which Django version did the reporter use, and which branches should receive the fix?
7. **Pickling/deconstruction:** Must a `Q` containing an `Exists` support `deconstruct()`/copy/pickle in the new order, for example for migrations or caching?