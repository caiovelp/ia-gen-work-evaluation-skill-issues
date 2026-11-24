# Spec: Fix broken "change password" link in UserChangeForm when UserAdmin is opened via `to_field`

## Objective

When the Django admin opens a User change page through a relation that uses `to_field`, the "change the password using this form" link in the Password field's help text returns a 404. It should open the password change page for that user.

**How the bug happens (from the issue):**

- Another model's admin references `User` with a `to_field`, for example `to_field="uuid"`.
- Following that relation opens the UserAdmin change view at a URL like:
  `.../user/22222222-3333-4444-5555-666677778888/change/?_to_field=uuid`
- `UserChangeForm.__init__` builds the help-text link with the hard-coded relative path `"../password/"`.
- That path resolves to `.../user/<uuid>/password/`. The password view looks up the user by **primary key**, so the lookup fails and the page returns 404.

**Who is affected:** admin users who reach a User change page through a `to_field` relation (for example, via a related-object popup or link).

**User story:** As an admin user, when I open a User's change page through any route, including a `to_field` route, I can click the password help-text link and reach that user's password change page.

**Acceptance criteria:**

1. The change page is opened via `.../user/<to_field value>/change/?_to_field=<field>`. The password link resolves to the password change URL for the user's **primary key**, and that URL does not return 404.
2. The change page is opened the normal way (`.../user/<pk>/change/`). The password link still resolves to the same, working password change page. No regression.
3. The link still renders inside the existing translatable help text. The surrounding wording and the `{}` placeholder are unchanged.

**Terminology note:** The issue calls the target the "PasswordResetForm". The link actually points to the admin's `password/` view, which is a password *change* view. See Open Questions.

## Assumptions

1. This is the Django project (`django.contrib.auth`). `UserChangeForm` and `ReadOnlyPasswordHashField` are the classes shown in the issue.
2. The password change view is mounted at `<pk>/password/` relative to the user changelist URL, and it looks up users by primary key only. This is implied by the 404, not shown directly.
3. The change-view URL structure is `<changelist>/<object id>/change/`. The reporter's proposed relative path `../../{pk}/password/` depends on this.
4. `UserChangeForm` is used with a saved instance, so `self.instance.pk` is not `None`. The issue does not cover unsaved instances.
5. The reporter's proposed fix is a candidate approach, not a mandated one. This spec defines the required behaviour. The implementation is chosen during planning and review.
6. A linked PR exists, but its contents are not visible here.

## Tech Stack

- Python and Django. Exact supported versions are **unknown** from the issue.
- Affected component: `django.contrib.auth` (`UserChangeForm`) as used by `django.contrib.auth.admin.UserAdmin`. The latter is inferred from the issue.

## Commands

Unknown. The issue does not specify build, test, or lint commands.

- Build: unknown
- Test: unknown (for example, the project's test runner for the auth and admin test suites)
- Lint: unknown

## Project Structure

Unknown. The issue does not give file paths.

- Location of `UserChangeForm` source: unknown (presumably the auth forms module)
- Location of relevant tests: unknown (presumably the auth and/or admin test suites)

## Code Style

Follow existing project conventions. This snippet is taken from the issue and shows the current code being changed:

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    password = self.fields.get("password")
    if password:
        password.help_text = password.help_text.format("../password/")
```

Conventions to preserve:

- Keep the help text translatable (`_()`).
- Fill the link via the existing `{}` placeholder. Do not change the translated string, so that existing translations are not invalidated.
- Keep the `if password:` guard. Subclasses may remove the field.

## Testing Strategy

- **Framework:** the project's existing test framework. The exact framework and runner are unknown.
- **Unit level (form):** for a saved user, the rendered or computed `password` help text contains a link that resolves to that user's primary-key password URL.
- **Integration level (admin):**
  - Use a user model or setup with a non-pk unique field reachable via `to_field`.
  - Load the change view with `?_to_field=<field>`.
  - Follow the password link from the rendered page and assert it does not return 404 (expect 200 for a permitted user).
- **Regression:** the standard pk-based change view link still works.
- **Coverage expectation:** unknown. At minimum, one failing-before / passing-after test that reproduces the issue.

## Boundaries

- **Always:**
  - Write a test that reproduces the 404 before changing the code.
  - Keep the help text translatable and keep the existing format-placeholder string unchanged.
  - Keep the plain pk-based admin access working.
- **Ask first:**
  - Changing the translatable help-text string itself.
  - Changing the password view's URL pattern or its lookup semantics, for example to accept `to_field` values.
  - Introducing URL reversing that couples the form to a specific admin site or namespace.
- **Never:**
  - Remove or weaken existing tests.
  - Change the security or permission checks of the password change view.
  - Expose the password hash or alter `ReadOnlyPasswordHashField` behaviour beyond the help-text link.

## Success Criteria

- [ ] A test opens the User change view with `?_to_field=<non-pk field>`, follows the password help-text link, and gets the password change page instead of a 404.
- [ ] A test opens the User change view by pk and confirms the password link still works.
- [ ] The help-text string in the translation catalog is unchanged.
- [ ] All existing auth and admin tests pass. The exact command is unknown.

## Open Questions

1. **Approach.** Is the relative path `../../{self.instance.pk}/password/` acceptable? It assumes the `<id>/change/` URL depth. The alternative is reversing the admin URL, but the form does not know the admin site namespace. Should the fix live in the form, or should `UserAdmin` supply the correct URL?
2. **Primary key quoting.** Should the pk be escaped with the admin's URL quoting before it is put into the URL? This matters for primary keys containing characters such as `/` or `_`. Should the help-text HTML also escape it?
3. **Unsaved instance.** What should the link be when `self.instance.pk` is `None`, for example when `UserChangeForm` is used outside the admin change view or on an unsaved instance? Should the link be omitted?
4. **Usage outside the admin.** `UserChangeForm` may be used outside the admin, where the relative link is already meaningless. Is that in scope?
5. **Naming.** Should the issue title be corrected from "PasswordResetForm" to the admin password change view?
6. **Versions.** Which Django versions or branches should get the fix?
7. **Linked PR.** Should the linked PR be taken as the reference implementation? Its contents are not visible here.