# Spec: Reject or Flag `related_name` on Symmetrical `ManyToManyField`s

## Assumptions

1. The project is Django. `ManyToManyField`, `symmetrical` and `related_name` match Django's ORM API. The issue does not name the project.
2. "Self-referential" in the issue means a self-referential M2M where `symmetrical` is left at its default. In Django, a relation to `"self"` defaults to `symmetrical=True`. A self-referential M2M with an explicit `symmetrical=False` does create a reverse accessor, so `related_name` is meaningful there and must stay allowed.
3. The diagnostic should go through the existing model-field validation path (the system check framework, run by `manage.py check` and at startup). It should not raise an exception at field construction time. This is not stated in the issue; see Open Questions.
4. The framework may assign its own internal `related_name` to symmetrical relations. Only a `related_name` supplied by the developer should trigger the diagnostic. An internally generated value must not.
5. Existing behaviour of symmetrical relations does not change. This includes no reverse accessor, automatic mirroring of rows, and the through-table layout. The only change is a new diagnostic.
6. Commands, file paths, check IDs and code style are not visible in the issue. They are marked unknown below.

## Objective

When a developer declares a symmetrical `ManyToManyField` and passes `related_name`, Django ignores the argument without saying so. No reverse accessor is created under that name. Developers expect the name to work and are confused until they find the documentation on symmetrical relationships.

**Goal:** When a `related_name` will have no effect because the relation is symmetrical, tell the developer clearly and early (at check or startup time). The message should explain why.

**User:** Django application developers who define models with M2M relations.

**User stories / acceptance criteria:**

- As a developer, if I write `friends = ManyToManyField("self", related_name="befriended_by")`, I get a diagnostic. It tells me `related_name` has no effect on a symmetrical relationship.
- As a developer, if I write `ManyToManyField("self", symmetrical=False, related_name="followers")`, I get no diagnostic, and the reverse accessor works as before.
- As a developer, if I write a symmetrical M2M without `related_name`, I get no new diagnostic.
- As a developer, if I write a non-self M2M with `related_name`, I get no new diagnostic. Whether `symmetrical=True` is even permitted on a non-self relation is an open question.

## Tech Stack

- Python and Django. Exact versions are unknown.
- Mechanism: Django's model field validation / system check framework (assumed; see Open Questions).

## Commands

Unknown. Not visible in the issue. Likely forms are listed below but unconfirmed:

- Test: unknown (e.g., the project's test runner invoked on the model field / invalid-models check test suites)
- Lint: unknown
- Build: unknown / likely not applicable

## Project Structure

Unknown. Not visible in the issue. The change is expected to touch:

- The `ManyToManyField` implementation: location unknown.
- Tests for invalid model / relational field checks: location unknown.
- Documentation listing system check messages: location unknown.
- Release notes for the target version: location unknown.

## Code Style

Unknown. Follow the conventions of the surrounding `ManyToManyField` check methods and existing check messages. This includes message wording, `hint` usage, `obj=` targeting, and ID numbering. No snippet is provided because none is visible in the issue.

## Testing Strategy

- **Framework:** the project's existing test framework (unknown specifics).
- **Level:** unit tests at the model-check level. Define models in test-isolated apps, run the field or model checks, and assert the exact list of returned messages (level, message, hint, obj, id).
- **Cases required:**
  1. Self-referential M2M, default symmetry, with `related_name` → exactly one new diagnostic.
  2. Self-referential M2M, explicit `symmetrical=True`, with `related_name` → exactly one new diagnostic.
  3. Self-referential M2M, `symmetrical=False`, with `related_name` → no new diagnostic.
  4. Symmetrical M2M without `related_name` → no new diagnostic. This guards against false positives from any internally generated `related_name`.
  5. Non-self M2M with `related_name` → no new diagnostic.
  6. Symmetrical M2M with a hidden-style `related_name` ending in `+`. Expected outcome is unresolved; see Open Questions.
- **Regression:** the full existing test suite, especially the relational-field check tests and M2M behaviour tests, must still pass. Existing tests or project models that pass `related_name` on symmetrical fields may now emit the diagnostic. These must be reviewed, not silently changed.
- **Coverage:** every branch of the new condition is exercised by the cases above.

## Boundaries

- **Always:**
  - Base the diagnostic on whether the relation is effectively symmetrical. Do not base it on syntax such as whether `symmetrical=` was written.
  - Include a hint that explains why `related_name` has no effect.
  - Add tests for both the positive and negative cases.
  - Document the new check message and add a release note.
- **Ask first:**
  - Whether the diagnostic is an error or a warning (see Open Questions).
  - Choosing or assigning a new check ID.
  - Any change to how symmetrical relations set their internal `related_name`.
  - Changing existing tests or fixtures that now trigger the diagnostic.
- **Never:**
  - Change runtime behaviour of symmetrical relations.
  - Raise at field instantiation time, unless the open question about the mechanism is resolved in favour of that.
  - Flag `related_name` on `symmetrical=False` self-referential relations.
  - Remove or weaken existing tests.

## Success Criteria

- [ ] A model with a symmetrical M2M and a developer-supplied `related_name` produces exactly one new check message. That message identifies the field and explains that `related_name` has no effect on symmetrical relationships.
- [ ] A symmetrical M2M without `related_name` produces no new message.
- [ ] A self-referential M2M with `symmetrical=False` and `related_name` produces no new message, and its reverse accessor keeps working.
- [ ] Non-self M2M fields with `related_name` produce no new message.
- [ ] The new message has a documented ID and appears in the system check reference documentation.
- [ ] A release note describes the new diagnostic.
- [ ] The entire existing test suite passes.

## Open Questions

1. **Error or warning?** The issue says "raise an error". Making it a hard error would break existing projects that harmlessly pass `related_name` on symmetrical fields, which is a backwards-compatibility concern. Is a warning acceptable or preferable?
2. **Mechanism:** Should this be a system check (reported by `check` and at startup), or an exception raised in the field's constructor? A constructor exception would block model import entirely.
3. **Internal `related_name`:** Does the framework set a `related_name` internally for symmetrical relations? If so, how should a user-supplied value be told apart from the internal one, given that the check may run after the internal value is assigned?
4. **Hidden reverse names:** Should a `related_name` ending in `+`, which explicitly requests no reverse relation, also be flagged? It is redundant but consistent with what symmetry already does.
5. **Non-self symmetrical:** Is `symmetrical=True` allowed on a non-self-referential M2M in the target version? If it is, is `related_name` ignored there too, and should it be flagged?
6. **`related_query_name`:** Does the same problem apply to `related_query_name` on symmetrical fields? Should it be covered here or left out of scope?
7. **Check ID:** Which ID and numbering should the new message use?
8. **Target version:** Which release does this go into, for the release note?
9. **Commands and paths:** What are the exact test, lint and build commands, and the file locations? None are visible in the issue.