# Spec: `join` filter must not escape the joining string when autoescape is off

## Objective

Make Django's `join` template filter respect the active autoescape setting for **both** the list items and the joining string (the filter argument).

**The bug:** inside `{% autoescape off %}`, the filter `{{ some_list|join:some_var }}` leaves the list items unescaped, which is correct. However, it still HTML-escapes `some_var`. This is inconsistent with the documented behaviour of `autoescape` and `join`.

**Who is affected:** template authors who switch autoescaping off and join lists with a separator that contains HTML. Examples of such separators are `<br/>` and `<li>`.

**Reproduction from the issue.** Template:

```
{% autoescape off %}{{ some_list|join:some_var }}{% endautoescape %}
```

Inputs:

- `some_list = ["<p>Hello World!</p>", "beta & me", "<script>Hi!</script>"]`
- `some_var = "<br/>"`

| | Output |
|---|---|
| Actual | `<p>Hello World!</p>&lt;br/&gt;beta & me&lt;br/&gt;<script>Hi!</script>` |
| Expected | `<p>Hello World!</p><br/>beta & me<br/><script>Hi!</script>` |

**Acceptance criteria:**

1. **Autoescape off.** With autoescape off, `join` returns `some_var.join(some_list)` with no escaping of either the items or the separator.
2. **Autoescape on (default).** With autoescape on, behaviour is unchanged. Both the items and the separator are escaped, so the output equals `escape(some_var.join(some_list))` for plain (non-safe) strings.
3. **Existing semantics preserved.** Existing `join` behaviour is not regressed in these cases:
   - safe strings
   - mark_safe items
   - non-iterable input
   - existing `join` tests

## Tech Stack

- **Python and Django:** Django template engine (`django.template`) and `django.template.defaultfilters`. The exact Python and Django versions are unknown; the issue only says "current main".
- **Test base:** `django.test.SimpleTestCase`, plus the `setup` decorator from `tests/template_tests/utils.py`.

## Commands

- **Test:** unknown. The issue does not show the command. It only says to run the test "inside the template_tests/filter_tests folder".
- **Build, lint, and dev:** unknown.

## Project Structure

These locations are referenced in the issue. Everything else is unknown.

```
django/template/defaultfilters.py              → defines filters incl. `escape` (and presumably `join`; location of `join` not shown in the issue)
django/test/utils.py                            → test utilities (appears in traceback)
tests/template_tests/utils.py                   → `setup` decorator for template tests
tests/template_tests/filter_tests/              → filter tests; reporter used test_regression.py here
```

The issue does not show the existing test file for `join`. It might be `test_join.py`, but that is an unconfirmed assumption.

## Code Style

This is the test style shown in the issue, which should be followed:

```python
@setup({"join02": '{% autoescape off %}{{ some_list|join:some_var }}{% endautoescape %}'})
def test_join02(self):
    some_list = ["<p>Hello World!</p>", "beta & me", "<script>Hi!</script>"]
    some_var = "<br/>"
    output = self.engine.render_to_string("join02", {"some_list": some_list, "some_var": some_var})
    self.assertEqual(output, some_var.join(some_list))
```

Conventions:

- Each test registers its template with `@setup({...})`.
- Each test renders with `self.engine.render_to_string(name, context)`.
- Template names follow the `<filter><NN>` pattern, such as `join01`.

## Testing Strategy

- **Framework:** Django's own test suite, using `SimpleTestCase`.
- **Regression test for autoescape off:** a test equivalent to the issue's `test_join02` must fail before the fix and pass after it.
- **Control test for autoescape on:** a test equivalent to `test_join01` must pass both before and after the fix.
- **Location:** add the tests to the existing `join` filter test module in `tests/template_tests/filter_tests/`. The exact file name is unknown.
- **Unit-level test:** optionally, call the filter function directly with `autoescape=False` and check that the separator is unescaped. This depends on the filter's signature exposing `autoescape`, which is unverified.
- **Full suite:** all existing template and filter tests must still pass.

## Boundaries

**Always:**

- Keep the escaping behaviour for autoescape-on exactly as it is today.
- Add regression tests for both the on and off cases.

**Ask first:**

- Changing the public signature of `join`.
- Changing the behaviour of other filters.
- Adding a release note or changing documentation.

**Never:**

- Make the separator unconditionally unsafe or unconditionally safe.
- Weaken or remove existing `join` tests.

## Success Criteria

- [ ] The `test_join02` scenario from the issue passes, with output `'<p>Hello World!</p><br/>beta & me<br/><script>Hi!</script>'`.
- [ ] The `test_join01` scenario still passes, with output equal to `escape(some_var.join(some_list))`.
- [ ] All pre-existing `join` filter tests pass unchanged.
- [ ] The full template test suite passes (the command is unknown).

## Assumptions

1. The `join` filter lives in `django/template/defaultfilters.py` and receives the active autoescape state. Django filters can declare `needs_autoescape`, but the issue does not show whether `join` does.
2. When autoescape is off, the separator should be treated exactly like the list items, meaning no conditional escaping.
3. A separator already marked safe should remain unescaped under autoescape on, as it presumably is today.
4. The fix is limited to `join`. No other filters are in scope.
5. The issue's `test_regression.py` was only for reproduction. The real tests belong in the existing `join` test module.

## Open Questions

1. What is the exact command to run the template filter tests (for example, a `runtests.py` invocation)?
2. Which file holds the existing `join` tests, and which template names (`joinNN`) are already used?
3. Does this change need a release note or a documentation update? Is it a bugfix for the next release only, or a backport?
4. Should a literal string separator be covered as well as a variable one? For example, `join:"<br/>"` under autoescape off.
5. Are there other filters with the same "argument is always escaped" pattern that should be audited? The current assumption is that they are out of scope.