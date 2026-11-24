# Spec: Hide "Save as new" in the Django admin when the user lacks add permission

## Objective

On a Django admin change form, the "Save as new" button is shown whenever these conditions hold:

- the form is not a popup
- the user has change permission
- this is an existing object (`change`)
- `ModelAdmin.save_as` is enabled

"Save as new" creates a new object, so it is an add operation. A user with change permission but no add permission still sees the button. Clicking it either fails or attempts something the user is not allowed to do.

**Goal:** Show "Save as new" only when the user also has **add** permission for the model.

**Users affected:** Admin staff who have change permission but not add permission on a model whose `ModelAdmin` sets `save_as = True`.

**Acceptance criteria:**
- The button appears only when all of these are true:
  - `not is_popup`
  - `has_add_permission`
  - `has_change_permission`
  - `change`
  - `save_as`
- If any condition is false, the button does not appear.
- No other submit-row buttons change behaviour, including:
  - "Save"
  - "Save and continue editing"
  - "Save and add another"
  - "Delete"

## Assumptions

1. The fix belongs in the `show_save_as_new` expression inside `submit_row` in `django/contrib/admin/templatetags/admin_modify.py`. The issue cites this location as line 102; I have not seen the file.
2. The context passed to `submit_row` already contains `has_add_permission`. The reporter's patch uses it without adding it, which suggests this.
3. Server-side handling of `_saveasnew` in `ModelAdmin` (changeform view) already checks add permission. If so, this change is a UI/consistency fix, not a security fix. **I have not verified this** (see Open Questions).
4. The issue covers the button's visibility only. Any change to permission enforcement on POST is out of scope unless the open question below shows a gap.
5. The fix targets the current development branch. Whether it gets backported is a maintainer decision.

## Tech Stack

- Python and Django, specifically `django.contrib.admin`.
- Versions: unknown.

## Commands

- Build: unknown (not stated in the issue)
- Test: unknown (not stated in the issue)
- Lint: unknown (not stated in the issue)

## Project Structure

- `django/contrib/admin/templatetags/admin_modify.py` is the `submit_row` template tag that computes `show_save_as_new`. The path comes from the issue.
- Location of the relevant admin tests: unknown (not visible).

## Code Style

The issue's snippet shows the target expression style: a boolean expression chained with `and`, one condition per line.

```python
"show_save_as_new": not is_popup
and has_add_permission
and has_change_permission
and change
and save_as,
```

- Formatting and lint conventions beyond this snippet: unknown.
- The reporter's inline comment (`# This line that I put!!!`) should not be carried into the fix.

## Testing Strategy

- Framework and test locations: unknown.
- Required coverage:
  - **Template-tag/context test:** For a change view with `save_as=True`, a user with change permission and **no** add permission gets `show_save_as_new` as `False`.
  - **Regression test:** A user with both add and change permission still gets `show_save_as_new` as `True`.
  - **Optional view-level test:** The rendered change form for a change-only user does not contain the "Save as new" button.

## Boundaries

- **Always:**
  - Keep the change minimal and limited to the `show_save_as_new` condition.
  - Add regression tests.
  - Run the admin test suite before committing.
- **Ask first:**
  - Changing server-side permission enforcement for `_saveasnew`.
  - Changing other submit-row flags.
  - Backporting to stable branches.
- **Never:**
  - Remove or weaken existing permission checks.
  - Change the public `save_as` API.
  - Alter unrelated admin templates.

## Success Criteria

- [ ] `show_save_as_new` is `False` when `has_add_permission` is `False`, all else being equal.
- [ ] `show_save_as_new` is unchanged, and `True`, for users with both add and change permission, outside popups, on change views, with `save_as=True`.
- [ ] New tests fail before the fix and pass after it.
- [ ] The existing admin test suite passes.
- [ ] A release note is added, if Django's contribution process requires one for this change.

## Open Questions

1. Does the server-side `_saveasnew` POST path in `ModelAdmin` already reject users without add permission?
   - If it does not, this is a permission-bypass bug.
   - In that case it needs a server-side fix and possibly handling as a security issue, not only a UI tweak.
2. Is `has_add_permission` definitely present in the context `submit_row` receives, including for custom `ModelAdmin` subclasses and third-party templates that call the tag?
3. Should this be treated as a bug fix eligible for backport, or only applied to the development branch?
4. Does this change need a release note or documentation update?
5. Should other flags that imply object creation get a similar review? The main candidate is `show_save_and_add_another`, which already depends on add permission. Or is the scope strictly `show_save_as_new`?
6. What are the exact commands for running the admin tests and linters in this repository?