# Spec: Correct Admin Site Namespace for Readonly ForeignKey Links in Custom Admin Sites

## Assumptions

1. The codebase is Django. The affected code is `get_admin_url` in `django.contrib.admin.helpers`, which the issue describes as a method with access to `self.model_admin`. I have not seen the file, so its exact signature and surroundings are unverified.
2. The faulty line is the one quoted in the issue: `url = reverse(url_name, args=[quote(remote_obj.pk)])`. Because it has no `current_app`, `reverse` falls back to the default `admin` instance namespace.
3. A "custom Admin Site" means an `AdminSite` instance whose `name` differs from `"admin"`, mounted at a different URL prefix such as `/custom-admin/`.
4. The intended behavior matches other admin code paths, such as `ModelAdmin.response_add`, which pass `current_app=self.admin_site.name` (or an equivalent) to `reverse`.
5. `self.model_admin.admin_site.name` is the correct source for the current admin site's name inside `get_admin_url`.
6. This spec covers only the link generated for a readonly ForeignKey. Other readonly relation types (for example OneToOne, if it shares the same helper) are covered only to the extent that they go through the same `get_admin_url` code path.
7. Existing behavior for the default admin site (`name="admin"`) must not change.
8. A test can be added to Django's existing admin test suites. The suite name and location are not visible from the issue and are therefore unknown.

## Objective

When a model instance is viewed or edited in a custom `AdminSite`, a ForeignKey listed in `readonly_fields` renders as a link to the related object's change page. That link currently points to the default admin site (`/admin/...`) instead of the custom admin site the user is working in (`/custom-admin/...`).

**Who is affected:** Developers who register models on a non-default `AdminSite`, and their staff users, who are sent to the wrong admin site. That site may not exist, may not have the model registered, or may have different permissions.

**What success looks like:** The readonly ForeignKey link resolves inside the same admin site that rendered the page, consistent with how the rest of `ModelAdmin` reverses admin URLs.

### Acceptance Criteria (user stories)

- As a staff user on a custom admin site, when I open a change or view page whose ForeignKey field is readonly, the link to the related object takes me to that object's change page **in the same custom admin site**.
- As a staff user on the default admin site, the readonly ForeignKey link behaves exactly as it does today.
- When the related object's change URL cannot be reversed (for example, the related model is not registered on the current site), the existing fallback behavior is kept. I assume the fallback is to render plain text without a link, but this is unverified (see Open Questions).

## Tech Stack

- Python / Django. Versions are unknown and not stated in the issue.
- Affected module: `django.contrib.admin.helpers`, function or method `get_admin_url` (assumed to live on `AdminReadonlyField`; unverified).
- Related reference: `django.contrib.admin.options.ModelAdmin.response_add`, which already uses `current_app`.
- URL reversal: `django.urls.reverse` with the `current_app` argument.

## Commands

| Purpose | Command |
|---|---|
| Build | Unknown. Not stated in the issue. |
| Test (full suite) | Unknown. Not stated in the issue. |
| Test (admin-related subsets) | Unknown. The relevant test module names are not visible. |
| Lint / format | Unknown. Not stated in the issue. |

## Project Structure

Only the paths named in the issue are known:

```
django/contrib/admin/helpers.py   → contains get_admin_url (the defect location)
django/contrib/admin/options.py   → contains ModelAdmin.response_add (reference pattern using current_app)
```

The test directory layout and the location of existing tests for custom admin sites and readonly fields are **unknown**.

## Code Style

The style to follow is the existing pattern already used elsewhere in the admin, as reported in the issue: pass the admin site's name as `current_app` when reversing admin URLs. The issue reporter suggests this shape:

```python
url = reverse(
    url_name,
    args=[quote(remote_obj.pk)],
    current_app=self.model_admin.admin_site.name,
)
```

This snippet records the reporter's proposal to show the convention. It is not an approved implementation. Other conventions (formatting tool, line length, and so on) are unknown.

## Testing Strategy

- **Framework:** Django's own test framework (`django.test`). The exact test runner invocation is unknown.
- **Required test levels:**
  - **Regression test (integration level, admin views):** Use a model with a ForeignKey in `readonly_fields`, registered on a custom `AdminSite` with a non-default `name` and URL prefix. Render the change page in that site and assert that the readonly field's link points to the custom site's URL prefix and not to `/admin/`.
  - **Non-regression test for the default site:** The same scenario on the default admin site still produces `/admin/...` links. Existing tests may already cover this; confirming that is an open question.
  - **Fallback behavior:** If a test exists for the unreversible case (related model not registered on the site), it must keep passing unchanged.
- **Where tests live:** Unknown. Ideally next to existing tests that cover custom admin sites and/or readonly fields.
- **Coverage expectation:** The changed line is exercised by at least one test that fails before the fix and passes after it.
- **Full suite:** The reporter has not run the full test suite. The full admin-related tests must pass before the change is considered done.

## Boundaries

- **Always:**
  - Keep default admin site behavior byte-for-byte identical in rendered link output.
  - Follow the existing `current_app` pattern used in `ModelAdmin` rather than inventing a new mechanism.
  - Add a regression test that reproduces the `/admin/` vs `/custom-admin/` mismatch.
  - Run the admin-related test suites before considering the change complete.
- **Ask first:**
  - Changing the signature of `get_admin_url` or of `AdminReadonlyField`'s constructor.
  - Extending the fix to other `reverse` calls in `helpers.py` or elsewhere that may have the same omission. That would broaden the scope beyond this issue.
  - Any change to the fallback behavior when reversal fails.
  - Adding release notes or documentation entries, since the project's conventions for these are unknown.
- **Never:**
  - Hard-code the `"admin"` namespace or any URL prefix.
  - Remove or weaken existing tests to make the change pass.
  - Change URL routing or `AdminSite` registration semantics as part of this fix.

## Success Criteria

1. On a custom `AdminSite` (non-default `name`, non-`/admin/` prefix), the readonly ForeignKey link on the change and view page resolves to `<custom-prefix>/<app_label>/<model_name>/<pk>/change/` (or the project's equivalent change URL) within that custom site.
2. On the default admin site, the rendered readonly ForeignKey link is unchanged from current behavior.
3. A new automated test fails on the current code and passes after the fix.
4. All existing admin-related tests pass, including any existing tests for readonly fields and custom admin sites.
5. The case where the related model is not registered on the current site still follows the existing fallback behavior without raising an error.

## Open Questions

1. Is `self.model_admin` always available and non-`None` in `get_admin_url`? For example, could it be `None` for inline formsets, or for readonly fields rendered outside a `ModelAdmin` context? If it can be absent, what should the fallback be?
2. Should the fix use `self.model_admin.admin_site.name`, or is there a more canonical source of the current app in this context (for example `request.current_app`)?
3. Are there other `reverse` calls in `django/contrib/admin/helpers.py`, or in related admin helpers, with the same missing `current_app`? Should they be fixed in this change or tracked separately?
4. What is the current fallback when reversing the related object's URL fails (`NoReverseMatch`)? Does passing `current_app` change which cases fall back? For example, if the related model is registered only on the default site but not on the custom site, should the link now disappear (plain text) rather than pointing to `/admin/`?
5. Does this behavior also apply to readonly fields in inlines on a custom admin site? Should those be covered by the regression test?
6. Which Django versions or branches should receive the fix, and does the project expect a release note for this kind of bug fix?
7. What are the exact commands for running the full test suite and the admin-specific test modules, and where should the new regression test be placed?