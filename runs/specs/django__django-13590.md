# Spec: Preserve Named Tuples as `__range` Lookup Values in `Query.resolve_lookup_value`

## Objective

**Problem.** After upgrading Django from 2.2 to 3.0, a queryset filter that passes a **named tuple** as the value of a `__range` lookup fails with:

```
TypeError: __new__() missing 1 required positional argument: 'far'
```

(`far` is a field name of the reporter's named tuple.) The same code works on 2.2.

**Root cause (as reported).** `django.db.models.sql.query.Query.resolve_lookup_value`:

1. iterates over the elements of a tuple or list value,
2. resolves each element, and
3. rebuilds the container with the original type, passing an **iterator** to the constructor.

This works for plain `tuple` and `list`, which accept a single iterable. A named tuple's constructor expects one positional argument per field. Given a single iterator, it raises a `TypeError` for missing positional arguments.

**Users.** Django users who pass named tuples, or other tuple subclasses with positional-field constructors, as lookup values. The main case is the 2-element value for `__range`.

**Goal.** Restore the 2.2 behaviour. A named tuple passed as a lookup value must be accepted, its elements must be resolved, and the rebuilt value must have the same type.

**Acceptance criteria**
- `Model.objects.filter(field__range=SomeNamedTuple(near=a, far=b))` runs without error. It returns the same rows as `field__range=(a, b)`.
- Named-tuple elements that are expressions (for example `F()`) are still resolved. This is the behaviour that 3.0's element-wise resolution introduced.
- The rebuilt value keeps its original type. A named tuple stays a named tuple, a `tuple` stays a `tuple`, and a `list` stays a `list`.
- Plain `tuple` and `list` lookup values behave exactly as before. There are no regressions in existing lookup tests.

## Assumptions

1. The fault is in `Query.resolve_lookup_value` in `django/db/models/sql/query.py`, as the issue states. I have not checked this against the source.
2. The reporter's named tuple is a standard `collections.namedtuple` or `typing.NamedTuple` with two fields, one of them named `far`.
3. The affected branch handles values that are instances of `list` or `tuple`, including subclasses. Named tuples enter it because they subclass `tuple`.
4. The suggested direction, unpacking the resolved elements into the constructor, must keep working for plain `tuple` and `list`. That needs checking: `list(*elements)` and `tuple(*elements)` behave differently from `list(elements)` and `tuple(elements)`. Plain types and named tuples may therefore need different handling. This spec does not choose the implementation.
5. The scope is a regression fix for the 3.0 series, which suggests the fix should be backported to 3.0.x. This is a guess; see Open Questions.
6. The fix should be small and local, with no public API change and no deprecation.

## Tech Stack

- Django (regression between 2.2 and 3.0). Python version support follows Django 3.0's supported range, which the issue does not state.
- Module named in the issue: `django.db.models.sql.query` (`Query.resolve_lookup_value`).
- Other dependencies: unknown.

## Commands

The issue gives no commands. All of these are unknown:

```
Build: unknown
Test (full suite): unknown
Test (targeted, e.g. queries/lookup tests): unknown
Lint: unknown
```

## Project Structure

Known from the issue:

```
django/db/models/sql/query.py  → Query.resolve_lookup_value (location of the bug)
```

Unknown:
- where the regression test should go (test package or module for queries and lookups)
- the test models available there

## Code Style

The issue does not show any project code. Conventions, such as formatting, the linter, and comment style, are unknown. They should follow the existing style of `django/db/models/sql/query.py`.

## Testing Strategy

- **Framework:** Django's own test suite. The runner command and location are unknown.
- **Regression test (required):** Filter with `__range` using a named tuple whose fields are concrete values. Assert that there is no error and that the expected rows are returned.
- **Expression resolution (required):** Use a named tuple whose elements include an expression such as `F()`. Assert that the expressions resolve and the query returns the correct results.
- **Type preservation:** Check that the resolved value keeps its type for:
  - a named tuple
  - a plain `tuple`
  - a plain `list`
- **Non-regression:** The existing lookup and query tests must still pass, especially those covering `__in` and `__range` with tuples and lists.
- **Level:** Unit and integration tests against the test database. End-to-end tests are not needed.
- **Coverage:** Every branch of the rebuild logic touched by the change must be exercised.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix and passes after it.
  - Preserve the original container type.
  - Keep resolving expressions inside tuples and lists.
  - Run the relevant test suites.
- **Ask first:**
  - Changing behaviour for other iterable types, such as sets or generators, or arbitrary tuple and list subclasses beyond named tuples.
  - Changing the public signature or semantics of `resolve_lookup_value`.
  - Backport targets.
- **Never:**
  - Drop element-wise resolution to "fix" the error.
  - Convert named tuples to plain tuples silently, unless this is approved as the intended behaviour.
  - Remove or weaken existing tests.
  - Refactor code outside the scope of this regression.

## Success Criteria

- A `__range` filter whose value is a named tuple runs on 3.0 with the fix and returns the same results as on 2.2.
- A named tuple containing expressions resolves correctly.
- Values that are named tuples, `tuple`s, or `list`s keep their type after resolution.
- The new regression test(s) fail without the fix and pass with it.
- The full relevant test suite passes with no regressions.

## Open Questions

1. Should the fix cover only named tuples, detected for example by the presence of `_fields`, or any `tuple`/`list` subclass whose constructor takes positional elements instead of a single iterable?
2. Is keeping the named-tuple type the desired result, or would returning a plain `tuple` be acceptable? The issue implies the type should be kept.
3. Which release branches should get the fix: 3.0.x only, or later branches as well? Does it need a release note?
4. Where should the regression test go, and which existing test models suit a `__range` query?
5. Does the same bug affect lookups other than `__range` that go through `resolve_lookup_value`, such as `__in`? Should they be tested explicitly?
6. Which exact commands should be used to run the targeted and full test suites, and to lint?