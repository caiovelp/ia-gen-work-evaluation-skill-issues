# Spec: Ignore `empty_permitted` in `form_kwargs` when building a formset's `empty_form`

## Objective

When a formset is created with `form_kwargs` containing `empty_permitted`, either `{'empty_permitted': True}` or `{'empty_permitted': False}`, rendering `formset.empty_form` crashes. The issue reports a `KeyError`.

`empty_form` is a template form. It is never bound to data and never validated, so `empty_permitted` has no meaning for it. A user-supplied `empty_permitted` in `form_kwargs` should be ignored when building `empty_form`. It should not cause an error.

**Users affected:** Django developers who pass `empty_permitted` through `form_kwargs` to formsets (including model formsets) and render `formset.empty_form`. A common reason to render it is to add forms dynamically on the client side.

**User story:** As a developer, I can pass `form_kwargs={'empty_permitted': <bool>}` to a formset and still render `{{ formset.empty_form }}` without an exception.

**Reproduction (from the issue):**
```python
ff = modelformset_factory(MyModel, fields=['a_field'])
formset = ff(
    queryset=MyModel.objects.none(),
    form_kwargs={'empty_permitted': True},  # or False
)
# Template: {{ formset }} renders; {{ formset.empty_form }} crashes
```

## Assumptions

1. The crash happens because `empty_form` sets its own `empty_permitted` value and also passes the user's `form_kwargs`, so the same keyword arrives twice. This is not confirmed: the source is not visible, and the reported exception type (`KeyError`) needs verifying against the actual traceback.
2. The defect is in the base formset logic (`BaseFormSet.empty_form` or equivalent), not in model formsets specifically. Any formset that passes `empty_permitted` via `form_kwargs` is affected.
3. `empty_form` should keep its current internal `empty_permitted` value, whatever the existing code sets. The user-supplied value is dropped for `empty_form` only.
4. Regular forms (`formset.forms`, bound or unbound) should keep receiving the user's `empty_permitted` from `form_kwargs` exactly as they do today. This fix does not change their behavior.
5. Other keys in `form_kwargs` should still reach `empty_form` unchanged.
6. The fix targets the Django main branch. Whether to backport is not decided here.

## Tech Stack

- Python and Django (the forms/formsets subsystem). Exact versions are **unknown**; the issue does not state them.

## Commands

- Build: **unknown** (not visible in the issue)
- Test: **unknown**. This is probably Django's own test runner, but the exact command and flags cannot be confirmed without the repository.
- Lint: **unknown**
- Dev: not applicable (library change)

## Project Structure

**Unknown.** The repository is not visible. The relevant code is expected to be the formset implementation in Django's forms package. Matching tests are expected in Django's formset test suite. Exact paths are to be confirmed.

## Code Style

**Unknown.** Follow the existing conventions of the surrounding Django forms code and the Django contributing guidelines. No snippet is available.

## Testing Strategy

- **Unit/regression tests** in the existing formset test module (location unknown):
  - A formset with `form_kwargs={'empty_permitted': True}`: accessing `formset.empty_form` does not raise.
  - The same check with `form_kwargs={'empty_permitted': False}`.
  - In both cases, `formset.empty_form.empty_permitted` equals the value `empty_form` uses without the user override.
  - Other `form_kwargs` keys still reach `empty_form`. Existing tests may already cover this; confirm.
  - Rendering `empty_form` (for example, `str(formset.empty_form)` or via template) succeeds.
- **Model formset coverage:** at least one test using `modelformset_factory`, mirroring the reported scenario. This is optional if a base-formset test is judged sufficient.
- The existing formset and model formset test suites must still pass.

## Boundaries

- **Always:** Add regression tests that fail before the fix and pass after it. Keep changes minimal and local to `empty_form` construction. Run the full forms/formsets test suites.
- **Ask first:** Changing behavior of non-empty forms with respect to `empty_permitted`. Raising a warning or error instead of silently ignoring the key. Changing the public `get_form_kwargs()` contract. Touching inline formsets or admin beyond what the shared base requires.
- **Never:** Mutate the user's `form_kwargs` dict in place in a way that affects other forms. Remove or weaken existing tests. Change `empty_form`'s prefix, `use_required_attribute`, or other construction arguments as a side effect.

## Success Criteria

1. Accessing and rendering `formset.empty_form` does not raise when `form_kwargs` contains `empty_permitted=True`.
2. The same holds when `form_kwargs` contains `empty_permitted=False`.
3. `formset.empty_form.empty_permitted` is unaffected by the user-supplied value.
4. Forms in `formset.forms` still honor `empty_permitted` from `form_kwargs` exactly as before.
5. All other `form_kwargs` entries are still applied to `empty_form`.
6. The caller's `form_kwargs` dictionary is not modified.
7. New regression tests cover criteria 1–3 (and 5 if not already covered), and all existing formset and model formset tests pass.
8. The reproduction from the issue renders without error.

## Open Questions

1. What is the exact exception and traceback? The issue says `KeyError`, but a duplicate keyword would normally raise `TypeError`. Is the `KeyError` coming from a different code path, such as template rendering or a `get_form_kwargs()` override?
2. Which Django version(s) reproduce this, and should the fix be backported?
3. Should silently ignoring `empty_permitted` for `empty_form` be documented, for example in the formsets docs or release notes?
4. Do other construction arguments that `empty_form` sets itself (e.g. `auto_id`, `prefix`, `use_required_attribute`, `renderer`) have the same conflict if passed via `form_kwargs`? Should they be handled here or tracked separately?
5. Do subclasses that override `get_form_kwargs()` to inject `empty_permitted` need the same protection? Is ignoring the key at `empty_form` construction the agreed approach?
6. What are the exact test command and test file locations in the repository?