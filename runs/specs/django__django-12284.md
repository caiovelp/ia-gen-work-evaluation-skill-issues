# Spec: Correct `get_FOO_display()` for Fields Overridden in Child Models of Abstract Bases

## Objective

**Problem.** A concrete model can inherit from an abstract base model and redeclare a field with a different `choices` list. When it does, `get_<field>_display()` on the child instance uses the **parent's** choices, not the child's. Values that exist only in the child's choices are returned raw, and their labels are lost.

**Reproduction (from the issue):**

```python
class A(models.Model):
    foo_choice = [("A", "output1"), ("B", "output2")]
    field_foo = models.CharField(max_length=254, choices=foo_choice)

    class Meta:
        abstract = True

class B(A):
    foo_choice = [("A", "output1"), ("B", "output2"), ("C", "output3")]
    field_foo = models.CharField(max_length=254, choices=foo_choice)
```

| Instance of `B` with `field_foo =` | Expected `get_field_foo_display()` | Actual |
|---|---|---|
| `"A"` | `"output1"` | `"output1"` |
| `"B"` | `"output2"` | `"output2"` |
| `"C"` | `"output3"` | `"C"` (wrong) |

**Users.** Django developers who override a field with choices in a subclass of an abstract model.

**Success.** `get_FOO_display()` always resolves labels against the field declared on the model class the instance belongs to, including fields overridden in subclasses. A user-defined `get_FOO_display()` method on a model must still not be overwritten.

## Assumptions

1. The target codebase is Django itself, and the fix belongs in the framework, not in user code.
2. The issue is assigned to the model-fields component. The display method is attached to the model class while the field is contributed to the class. Two hypotheses follow:
   - The parent's `get_FOO_display` is inherited by the child.
   - The "don't override an existing method" guard is true for this inherited method, so the child never gets a version bound to its own field.

   Neither has been verified against the source.
3. "Don't overwrite an existing `get_FOO_display`" exists to protect methods the user defined explicitly. Those must keep working: a user method on the model wins.
4. Overriding fields inherited from **abstract** models is supported behavior. Concrete multi-table inheritance does not allow field overriding, so the abstract case is the focus.
5. The same mechanism may affect other per-field generated methods, such as `get_next_by_FOO` and `get_previous_by_FOO`. That is out of scope unless the investigation shows they share the same defect.
6. Grouped/nested choices behave the same as flat choices for this bug.

## Tech Stack

- Python, Django (exact supported Python and Django versions: **unknown**).
- No new dependencies.

## Commands

The exact commands are **unknown** because the repository was not visible. Django's usual approach is the in-repo test runner, e.g. `tests/runtests.py <test_label>`, but this is unconfirmed.

- Build: N/A (pure Python), unknown otherwise
- Test: unknown
- Lint: unknown (style checker/config not visible)

## Project Structure

Not visible. Expected areas, all **unconfirmed**:

- Model field implementation: where `contribute_to_class` attaches `get_FOO_display`
- Model base class: where `_get_FOO_display` is implemented
- Test suite: model-fields / model-inheritance test modules
- Release notes: for a bugfix entry, if the project requires one

## Code Style

- Follow the project's existing conventions; these are **unknown** here.
- Keep the change minimal and local to the logic that attaches the display method.
- No behavior changes outside the described scenario.

## Testing Strategy

- Framework: the project's existing test framework (**unknown**; likely the Django test runner with `SimpleTestCase`/`TestCase`).
- Add regression tests with in-memory model instances. No DB queries should be needed, since `get_FOO_display` reads only the attribute value.

**Required test cases:**

1. Abstract base with choices, and a child overriding the field with extended choices. The child instance returns the child labels for **new** values (`"C"` → `"output3"`).
2. Same setup: values shared with the parent return the **child's** labels. Use a variant where the child relabels `"A"` to verify the child field is used and not merely a merged lookup.
3. Parent instance behavior is unchanged, if the parent is concrete in a variant, or via another concrete subclass that does not override.
4. A model that explicitly defines `get_FOO_display()` keeps its custom method; the framework does not overwrite it. This is an existing behavior and must not regress.
5. A subclass that does **not** override the field still gets correct display values from the inherited field.
6. Values not in choices still return the raw value, which is the existing behavior.

Coverage: all of the above must pass, and the existing model-field and inheritance test suites must remain green.

## Boundaries

- **Always:**
  - Write a failing regression test reproducing the issue before changing code.
  - Run the related existing test suites.
  - Preserve user-defined `get_FOO_display` overrides.
- **Ask first:**
  - Extending the fix to other generated methods (`get_next_by_FOO`, etc.).
  - Changing any public API or documented behavior.
  - Adding release notes or backporting.
- **Never:**
  - Change the semantics of choices validation.
  - Merge parent and child choices.
  - Remove or weaken existing tests.
  - Add dependencies.

## Success Criteria

- [ ] On an instance of `B` from the reproduction, `get_field_foo_display()` returns `"output1"`, `"output2"`, `"output3"` for `"A"`, `"B"`, `"C"` respectively.
- [ ] When a child overrides an inherited field and changes the label of an existing value, the child's label is returned.
- [ ] A model that explicitly defines `get_<field>_display()` retains its own implementation.
- [ ] Models without inheritance and subclasses that don't override the field behave exactly as before.
- [ ] New regression tests fail before the fix and pass after it, and the existing related test suites pass.

## Open Questions

1. Which Django version/branch is the target, and should the fix be backported?
2. Should the same correction apply to other auto-generated per-field methods (`get_next_by_FOO` / `get_previous_by_FOO`) if they share the root cause?
3. Consider a user-defined `get_FOO_display` on an **abstract parent**, with a child that overrides the field. Should the parent's custom method still take precedence, or should the child get a freshly generated method? Only a method defined directly on the class may need protecting, versus one inherited from any ancestor.
4. Does the project require a release-note entry for this bugfix, and in which file?
5. What are the exact test command and test module locations for adding the regression tests?