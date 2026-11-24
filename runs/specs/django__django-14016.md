# Spec: Q object `|` / `&` combination must not crash on non-pickleable lookup values

## Objective

Combining `django.db.models.Q` objects with the `|` operator raises `TypeError: cannot pickle '<type>' object` when one operand holds a lookup value that cannot be pickled, such as `dict_keys`.

Reproduction from the issue:

```python
>>> from django.db.models import Q
>>> Q(x__in={}.keys())
<Q: (AND: ('x__in', dict_keys([])))>
>>> Q() | Q(x__in={}.keys())
Traceback (most recent call last):
...
TypeError: cannot pickle 'dict_keys' object
```

Constructing the `Q` works. Combining it fails.

**Who is affected:** Django users who build queries by combining `Q` objects. Starting from an empty `Q()` and OR-ing filters onto it is a common pattern, and so is passing lookup values such as `dict.keys()`, views or generators.

**Goal:** If a `Q` object can be constructed, combining it with another `Q` through `|` or `&` should succeed. The result should be semantically equivalent to the operands. Operand type should not matter. Users should not need workarounds such as `Q(x__in={})` or `list(d.keys())`.

**User stories:**
- As a developer, I can write `Q() | Q(x__in=d.keys())` and get a `Q` equivalent to `Q(x__in=d.keys())`.
- As a developer, I can write `Q(x__in=d.keys()) | Q()` and `Q() & Q(x__in=d.keys())` without errors.
- As a developer, combining `Q` objects never mutates either operand.

## Assumptions

1. The failure happens in the `Q` combination path (`Q._combine` or equivalent). When one operand is empty, that path copies the other operand with `copy.deepcopy`, and deepcopy falls back to pickling (`__reduce_ex__`) for types like `dict_keys`. This is inferred from the error message and has not been verified against the source.
2. The issue applies to `&` as well as `|`, because both operators use the same combination path. This is unverified.
3. The fix belongs in Django core (`django.db.models.Q` / `django.utils.tree.Node` area). Exact file paths are unknown and not visible in the issue.
4. The returned `Q` must still be independent of the operand: mutating the result must not mutate the original `Q`. The copy guarantee should stay at the `Q` / tree level and not be dropped entirely.
5. Lookup *values* do not need to be deep-copied. Sharing the same value object, for example the same `dict_keys` instance, between the operand and the result is acceptable.
6. No public API change is intended. This is a bug fix.
7. The target Django version or branch is unknown. Assume the current main development branch.

## Tech Stack

- Python and Django. Exact versions are unknown and not stated in the issue.
- Affected API: `django.db.models.Q` and the operators `|` and `&`, plus possibly `~`.
- No new dependencies.

## Commands

Unknown. The issue does not state the repository's build or test commands.
- Build: unknown
- Test: unknown. Django's own test runner invocation must be confirmed from the repository.
- Lint: unknown

## Project Structure

Unknown and not visible in the issue. Expected relevant areas, unverified:
- The module defining `Q` (under `django/db/models/`, exact file unknown)
- The generic tree/node base class `Q` inherits from (exact location unknown)
- The existing test module(s) covering `Q` behavior (location unknown)

## Code Style

Follow the existing Django code style in the affected modules. No snippet can be given because no source is visible. Conventions to confirm in the repository:
- Existing linting and formatting rules (unknown)
- Regression tests named and placed alongside existing `Q` tests

## Testing Strategy

- **Level:** Unit tests on `Q` combination. No database is required for the core behavior.
- **Regression tests (must fail before the fix and pass after):**
  - `Q() | Q(x__in={}.keys())` does not raise and equals `Q(x__in={}.keys())` in structure.
  - `Q(x__in={}.keys()) | Q()` does not raise.
  - `Q() & Q(x__in={}.keys())` and `Q(x__in={}.keys()) & Q()` do not raise.
- **Non-regression tests:**
  - Combining two non-empty `Q` objects still produces the expected connector and children.
  - The result of combining with an empty `Q` is a new object. Mutating it, for example by adding children, does not change the original operand.
  - Existing `Q` tests and query-construction tests continue to pass.
- **Optional:** an integration check that a queryset filtered with `Q() | Q(pk__in=d.keys())` evaluates correctly against the test database.
- Coverage expectation: unknown, so follow project norms.

## Boundaries

- **Always:**
  - Add regression tests that reproduce the reported traceback.
  - Keep operand immutability: combining must not mutate either operand.
  - Run the full `Q`/query test suites before considering the change done.
- **Ask first:**
  - Changing `Q.__deepcopy__`, `Q.__reduce__`/pickling behavior, or the generic tree node class. These affect other subclasses and serialization, such as pickled querysets.
  - Converting user-supplied lookup values, for example turning `dict_keys` into a `list`, because that changes what users observe in `Q.children`.
  - Any change to `Q` public API or `repr`.
- **Never:**
  - Silently swallow `TypeError` and return a wrong or partially combined `Q`.
  - Remove or weaken existing `Q` tests.
  - Break pickling of `Q` objects or querysets that pickle correctly today.

## Success Criteria

1. `Q() | Q(x__in={}.keys())` returns a `Q` without raising, and it is equal to `Q(x__in={}.keys())`.
2. The same holds for `Q(x__in={}.keys()) | Q()`, `Q() & Q(x__in={}.keys())` and `Q(x__in={}.keys()) & Q()`.
3. The same holds for at least one other non-pickleable value type, for example `dict_values` or a generator-free view object, to show the fix is not specific to `dict_keys`.
4. The returned `Q` is a distinct object from the non-empty operand. Mutating the returned `Q`'s children does not affect the operand.
5. All existing `Q` and query tests pass unchanged.
6. Pickling behavior of `Q` objects with pickleable values is unchanged.

## Open Questions

1. Is the fix accepted in principle? The reporter asks whether there is agreement that this should not crash. Confirm with maintainers before implementing.
2. Should combination keep value identity (share the `dict_keys` object) or normalize values to a list or tuple? This spec assumes identity is kept.
3. Is a shallow, structural copy of the `Q` tree an acceptable replacement for `deepcopy`? Does any code rely on lookup values being deep-copied during combination, for example mutable lists that are later mutated by the caller?
4. Does the same problem affect `~Q(...)` (negation) or other paths that deepcopy `Q`, such as queryset cloning? Are those in scope?
5. Are values that cannot be pickled *and* are consumed on iteration, such as generators, in scope, or only re-iterable views like `dict_keys`?
6. Which Django version or branch is targeted, and is a backport expected?
7. What are the exact test commands and test file locations in the repository?