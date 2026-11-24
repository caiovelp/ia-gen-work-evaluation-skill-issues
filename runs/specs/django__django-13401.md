# Spec: Fields Inherited from an Abstract Model Must Not Compare Equal Across Concrete Models

## Objective

When a concrete model inherits a field from an abstract base model, Django gives each concrete model its own copy of that field. Today those copies compare equal and hash identically, because field comparison uses only `self.creation_counter`. Copies made from the same abstract field share that counter.

Reproduction from the issue:

```python
class A(models.Model):
    class Meta:
        abstract = True
    myfield = IntegerField()

class B(A):
    pass

class C(A):
    pass

B._meta.get_field('myfield') == C._meta.get_field('myfield')                 # currently True
len({B._meta.get_field('myfield'), C._meta.get_field('myfield')}) == 1       # currently True
```

**Goal:** Field identity should account for the model the field is attached to. Fields from different models then stay distinct in sets and dicts and compare unequal. Existing orderings of fields that do not hit this collision must not change.

**Users:** Developers and Django internals that collect fields from several models into sets, dict keys, or sorted sequences. Examples include introspection tools, migrations tooling and admin utilities.

**Acceptance criteria / user stories:**
- As a developer, if I put `B._meta.get_field('myfield')` and `C._meta.get_field('myfield')` into one set, I get two elements.
- As a developer, `B._meta.get_field('myfield') != C._meta.get_field('myfield')`.
- As a developer, sorting fields gives the same order as today for every pair whose `creation_counter` values differ.

## Assumptions

1. The affected code is the base field class in Django's ORM (`django.db.models.Field`), specifically `__eq__`, `__hash__` and `__lt__`. The exact file path is not given in the issue and is treated as unknown here.
2. A field may have no `model` attribute yet, for example on an abstract model before `contribute_to_class`, or as a standalone unbound field. Comparison must still work in that state and must not raise.
3. Two fields count as "the same model" only when they have the same `model` object. Comparison by identity or equality of the model class is enough; app label or name matching is not needed.
4. `creation_counter` stays the primary key for ordering. `model` is only a tie-breaker, as the issue recommends, so that unaffected orderings are preserved.
5. The tie-breaker for `__lt__` must be deterministic and must not depend on memory addresses. A likely key is the model's app label and model name, but this is a design choice to confirm (see Open Questions).
6. `__eq__` and `__hash__` stay consistent: equal fields have equal hashes.
7. Comparing a field with a non-`Field` object keeps its current behaviour, i.e. returns `NotImplemented`. This is assumed and not verified against the source.
8. Fields within a single model keep comparing as they do today, because their `creation_counter` values already differ.
9. The change targets the current Django development branch. Backporting is out of scope unless maintainers request it.

## Tech Stack

- Python, Django ORM (`django.db.models` field classes).
- Exact supported Python and Django versions: **unknown**, not stated in the issue.

## Commands

The issue does not specify any commands, and the repository is not available.

| Purpose | Command |
|---|---|
| Build | Unknown (Django is a pure-Python package; no build step stated) |
| Test (full) | Unknown, presumably the Django test runner under `tests/` |
| Test (targeted) | Unknown, the relevant test module or label is not identified |
| Lint | Unknown |

## Project Structure

Unknown; no repository access. Expected areas, to be confirmed:

```
<django source>/db/models/fields/  → Field base class (__eq__, __hash__, __lt__): exact file unknown
<django tests>/                     → existing tests for field comparison/ordering: location unknown
<django docs>/                      → release notes for behaviour change: location unknown
```

## Code Style

- Follow Django's existing coding style for the field module. The conventions are not visible here, so no snippet is given.
- Keep the comparison logic minimal and symmetric across `__eq__`, `__hash__` and `__lt__`.
- Use a safe lookup for `model`, since the attribute may be absent on unbound fields (Assumption 2).

## Testing Strategy

- **Framework:** Django's own test suite. The exact runner invocation is unknown.
- **Unit tests** for the field comparison behaviour should cover:
  - Abstract-inherited fields on two different concrete models are unequal, hash to distinct values in practice, and both survive in a set.
  - A field compares equal to itself, and its hash is stable.
  - Two different fields on the same model keep today's ordering, driven by `creation_counter`.
  - Fields with equal `creation_counter` but different models get a deterministic, consistent order: `a < b` and `b < a` are never both true, and the order does not vary between runs.
  - Comparing and hashing works for fields with no `model` attribute, and does not raise.
  - Comparing with a non-field object behaves as before.
- **Regression:** the full existing suite must pass. Particular attention goes to the test the reporter saw break when ordering by model first. Which test that was is unknown (see Open Questions).
- **Coverage expectation:** every new branch in `__eq__`, `__hash__` and `__lt__` is exercised by at least one test.

## Boundaries

- **Always:**
  - Keep `__eq__` and `__hash__` consistent.
  - Order by `creation_counter` first.
  - Handle a missing `model` attribute safely.
  - Add regression tests reproducing the issue example.
  - Run the full test suite.
- **Ask first:**
  - Choosing the tie-breaker key for `__lt__` (e.g. app label and model name, or something else).
  - Adding a release note or documenting this as a backwards-incompatible change.
  - Any change to how fields are copied from abstract models.
  - Touching `Field.__copy__`/`__deepcopy__` or `creation_counter` assignment.
- **Never:**
  - Change ordering for fields whose `creation_counter` values differ.
  - Make ordering depend on `id()` or other non-deterministic values.
  - Remove or weaken existing tests to make the change pass.
  - Alter field behaviour unrelated to comparison and hashing.

## Success Criteria

1. `B._meta.get_field('myfield') == C._meta.get_field('myfield')` evaluates to `False` for the issue's example models.
2. `len({B._meta.get_field('myfield'), C._meta.get_field('myfield')}) == 2`.
3. For any two fields `f1` and `f2`, if `f1 == f2` then `hash(f1) == hash(f2)`.
4. For any fields `f1` and `f2` with `f1.creation_counter != f2.creation_counter`, the result of `f1 < f2` is unchanged from the current behaviour.
5. For fields with equal `creation_counter` on different models, `<` gives a strict, deterministic order.
6. Comparison and hashing do not raise for fields that are not attached to any model.
7. The full existing Django test suite passes, including the test the reporter saw break, without modification.

## Open Questions

1. Which existing test broke in the reporter's branch when ordering by model first? It should be identified so it can be explicitly protected.
2. What tie-breaker should `__lt__` use when `creation_counter` is equal but models differ? App label plus model name is one option. Is another key preferred, and how should a field with no model sort against one that has a model?
3. Should `__hash__` include the model? Including it gives better set and dict distribution. Keeping `creation_counter` only is still correct, given the inequality, but causes collisions. Is there a concern about the hash changing once a field is attached to a model, e.g. a field placed in a set before `contribute_to_class`?
4. Should this be documented as a backwards-incompatible change in the release notes? Code that relied on cross-model equality of inherited fields would change behaviour.
5. Is equality by model identity enough? Or must swapped or proxy models and other edge cases (e.g. the same model class reloaded) be considered?
6. Which Django version or branch does this target, and is a backport expected?
7. Do any internal callers, such as migrations autodetector, `Options` field caches, or admin, rely on fields from different models comparing equal? If so, what is expected of them?