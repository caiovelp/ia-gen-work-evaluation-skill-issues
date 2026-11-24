## Summary

On the admin change form, the "Save as new" button (`show_save_as_new`) is shown to users who lack add permission for the model. "Save as new" creates a new object, so a user with change permission but no add permission can add objects.

## Steps to reproduce

1. Configure a `ModelAdmin` with `save_as = True`.
2. Log in to the admin as a user who has **change** permission but **not add** permission for that model.
3. Open the change form for an existing object, not in a popup.
4. Look at the submit row and use "Save as new".

## Observed behavior

The "Save as new" option is shown to the user, even though they lack add permission. Per the report's title, the user can add a new object through it.

## Expected behavior

"Save as new" is an add operation. It should not be available to users without add permission for the model.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report.

A test derived from the reproduction steps above could:
1. Create a user with change permission and without add permission for a model whose `ModelAdmin` has `save_as = True`.
2. Request that object's change view in the admin.
3. Assert that `show_save_as_new` is not enabled in the submit row context (no "Save as new" button).

## Code example

The reporter points to the context value `"show_save_as_new"` in `django/contrib/admin/templatetags/admin_modify.py`, line 102. As described, the condition depends on:
- the form not being a popup (`is_popup`)
- `has_change_permission`
- `change`
- `save_as`

It does not consider `has_add_permission`.

## Version and environment

Not provided in the original report. The only reference is line 102 of `django/contrib/admin/templatetags/admin_modify.py`. No Django version is given.