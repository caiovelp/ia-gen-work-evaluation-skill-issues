# Spec: Optional named URL groups must not cause extra positional arguments in view calls

## Objective

A regression in Django 3.0 breaks views routed through `re_path()` patterns that contain an **optional named group**, when that group is absent from the request URL.

**Reported case:**

```python
# URLConf
re_path(r'^module/(?P<format>(html|json|xml))?/?$', views.modules, name='modules'),

# View
def modules(request, format='html'):
    ...
    return render(...)
```

- With Django ≤ 2.2, requesting `/module/` called `modules(request)`. The view's default `format='html'` applied.
- With Django 3.0, requesting `/module/` raises:
  `TypeError: modules() takes from 1 to 2 positional arguments but 3 were given`
  The error is raised from `django/core/handlers/base.py`, in `_get_response`, at `wrapped_callback(request, *callback_args, **callback_kwargs)`.

**Observed mechanism (inferred from the error, not yet confirmed in source):**

1. Because `format` is unmatched, it is dropped from the keyword arguments.
2. Resolution then appears to fall back to passing all groups positionally. That includes the nested unnamed group `(html|json|xml)`.
3. The view therefore receives `request, None, None`.

**Users affected:** Django developers using regex URL patterns with optional named groups, especially named groups that contain nested unnamed groups, and relying on view default arguments.

**What success looks like:**

- When a pattern contains at least one named group, unnamed groups are never passed positionally. This matches the documented rule that named groups take precedence over unnamed groups.
- An unmatched optional named group is omitted from kwargs, so the view's default value applies.

## Assumptions

1. This is a regression in Django's URL resolver introduced in 3.0. It is not a bug in the user's code.
2. The intended behavior is "if the regex has named groups, pass only kwargs and ignore unnamed groups." This rule should depend on whether named groups *exist in the pattern*, not on whether they *matched with a non-None value*.
3. The 3.0 behavior of dropping `None`-valued named groups from kwargs is intentional, so view defaults apply. It should be kept.
4. The fix belongs in URL resolution (regex pattern matching). It does not belong in the request handler that appears in the traceback.
5. The fix only needs to cover `re_path()` / regex patterns. Path converters (`path()`) do not support optional groups in this way and are out of scope unless they are found to share the code path.
6. The fix targets the main development branch and is a candidate for backport to the 3.0.x series as a regression fix.
7. The user's Python version (3.6) is not relevant to the bug.

## Tech Stack

- Python and the Django framework.
- Exact versions supported on the target branch: **unknown**.
- Affected version: Django 3.0. Last known working version: Django 2.2.

## Commands

The issue does not include any commands. All of the following are **unknown** and must be confirmed from the repository:

- Build: unknown
- Test, full suite: unknown
- Test, URL resolver subset only: unknown
- Lint: unknown

## Project Structure

- Known from the traceback: `django/core/handlers/base.py` and `django/core/handlers/exception.py`.
- Location of the URL resolver / regex pattern matching code: **unknown**. It is likely under `django/urls/`, but this is unconfirmed.
- Location of existing URL resolver tests and test URLConfs: **unknown**.
- Location of the release notes for a 3.0.x regression fix: **unknown**.

## Code Style

- Follow existing Django conventions in the surrounding module. These conventions are not visible here and are **unknown**.
- Keep the change minimal and localized to the argument-extraction logic.

## Testing Strategy

- **Framework:** Django's own test suite. The runner and invocation are **unknown**.
- **Regression tests** should cover:
  - An optional named group with a nested unnamed group, **not matched**. Example: `/module/` against the pattern above. Expected: `args == ()` and `kwargs == {}`. The view is called with only `request` and the default applies.
  - The same pattern, **matched**. Example: `/module/json/`. Expected: `args == ()` and `kwargs == {'format': 'json'}`.
  - An optional named group without nested groups, not matched. Expected: `args == ()` and `kwargs == {}`.
  - A pattern with **only unnamed groups**. Expected: groups are still passed positionally. This behavior must be unchanged.
  - A pattern **mixing named and unnamed groups**, with the named group matched. Expected: only kwargs are passed. This behavior must be unchanged.
- **Test levels:**
  - Unit tests at the resolver level, through `resolve()` returning `args`/`kwargs`.
  - At least one end-to-end request through the test client to a view with a default argument. It should return 200, not raise `TypeError`.
- **Reverse resolution:** confirm that `reverse('modules')` and `reverse('modules', kwargs={'format': 'json'})` behave the same as before the fix.

## Boundaries

- **Always:**
  - Add regression tests that fail before the fix and pass after it.
  - Keep the documented precedence rule: named groups make unnamed groups ignored.
  - Run the full URL-related test suite.
- **Ask first:**
  - Changing the 3.0 behavior of omitting `None`-valued kwargs.
  - Touching `path()` converter handling.
  - Changing public APIs or the `ResolverMatch` structure.
  - Backport decisions.
- **Never:**
  - Change the request handler (`base.py`) to work around the issue, for example by swallowing `TypeError`.
  - Remove or loosen existing resolver tests.
  - Change behavior for patterns containing only unnamed groups.

## Success Criteria

1. With the reported URLConf, `GET /module/` calls `modules(request)` with no extra positional arguments and returns a normal response.
2. `GET /module/json/` calls `modules(request, format='json')`.
3. `resolve('/module/')` yields `args == ()` and `kwargs == {}`.
4. For any regex pattern that defines at least one named group, resolved `args` is always `()`, whether or not those named groups matched.
5. Patterns with only unnamed groups still produce positional `args` equal to the matched groups. Existing tests pass unchanged.
6. Named groups that did not match (value `None`) are still omitted from `kwargs`.
7. The new regression tests are present and pass. The full existing test suite passes.
8. A release note entry is added for the regression fix, if this project's practice requires one for a 3.0.x bugfix. The location of that note is unknown.

## Open Questions

1. Is omitting unmatched (`None`) named groups from kwargs the intended 3.0 behavior that must be preserved? Or should those groups be passed as `kwargs={'format': None}`, as in 2.2? Passing `None` would override the view's default, so this choice affects views.
2. Does the same argument-extraction logic apply to nested/included resolvers (`include()` with a regex prefix)? If so, must those be covered by the same fix and tests?
3. Should the fix be backported to the 3.0.x stable branch, and which release notes file should document it?
4. Are there related code paths (e.g. `path()` route patterns, `LocalePrefixPattern`) that share this logic and need verification?
5. What are the exact commands to run the URL resolver tests and the full suite in this repository?
6. Should the documentation on named versus unnamed groups be clarified? Specifically, it could state that the presence of named groups in the pattern, not whether they matched, determines whether positional args are passed.