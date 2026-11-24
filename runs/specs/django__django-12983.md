# Spec: Make `django.utils.text.slugify()` strip leading/trailing dashes and underscores

## Objective

`django.utils.text.slugify()` currently keeps leading and trailing dashes and underscores in its output. The issue reports this example:

```
from django.utils import text
text.slugify("___This is a test ---")
# current output:  ___this-is-a-test-
# desired output:  this-is-a-test
```

**Goal:** slugs produced by `slugify()` should not start or end with `-` or `_`. This gives cleaner URL slugs.

**Users:** Django developers who call `slugify()` directly or indirectly, for example through slug-generating code in their apps or templates.

**Acceptance criteria (user-level):**
- `slugify("___This is a test ---")` returns `"this-is-a-test"`.
- Leading and trailing runs of `-` and `_`, in any mix, are removed from the result.
- Other existing behavior of `slugify()` stays the same, apart from this stripping (see Assumptions and Open Questions).

## Assumptions

1. The function in scope is `slugify()` in the `django.utils.text` module, as named in the issue. Its exact signature and current implementation were not visible to me. I assume it has an `allow_unicode` option, based on general knowledge of Django; this needs to be verified.
2. Stripping applies **only at the start and end** of the resulting slug. Interior underscores are preserved (`"foo_bar"` → `"foo_bar"`). Interior dash handling stays as it is today.
3. Stripping happens on the **final** slug, after lowercasing, removal of disallowed characters, and collapsing of whitespace/dashes. So characters that only end up at the edges after earlier steps are also stripped. For example, `"!!-hello-!!"` → `"hello"`.
4. The change applies equally whether `allow_unicode` is true or false.
5. An input made only of dashes, underscores, whitespace, or disallowed characters returns an empty string `""`. It does not raise an error.
6. This is accepted as a deliberate behavior change. It is documented in release notes rather than put behind a flag or deprecation path.
7. The `slugify` template filter delegates to this function, so it inherits the new behavior without separate changes. This needs to be verified.
8. The "PR" linked in the issue was not available to me. This spec is based only on the issue text.

## Tech Stack

- Language: Python. The minimum supported version for the target Django branch is **unknown**.
- Project: Django. The target branch/version is **unknown**.
- No new dependencies are expected.

## Commands

The project's commands are not visible from the issue.
- Build: **unknown**
- Test (full suite): **unknown**
- Test (targeted, for `django.utils.text` tests): **unknown**
- Lint/format: **unknown**

## Project Structure

Only the module path in the issue is known:
- `django/utils/text.py` → location implied by `django.utils.text`; contains `slugify()`
- Tests for `django.utils.text`: location **unknown**
- Template filter tests (if `slugify` filter exists): location **unknown**
- Documentation for `slugify()` (utils reference docs): location **unknown**
- Release notes for the target version: location **unknown**

## Code Style

- Follow the existing conventions of the surrounding code in `django/utils/text.py`. These were not visible to me, so specifics are **unknown**.
- Project-wide style tooling (formatter, linter, import sorting): **unknown**.

## Testing Strategy

- **Level:** unit tests for `slugify()`, plus, if applicable, a check that the template filter reflects the change.
- **Framework / location:** **unknown**. Use whatever the existing `django.utils.text` tests use.
- **Cases to cover:**
  - The issue's example: `"___This is a test ---"` → `"this-is-a-test"`.
  - Leading only: `"__hello"` → `"hello"`; `"--hello"` → `"hello"`.
  - Trailing only: `"hello__"` → `"hello"`; `"hello--"` → `"hello"`.
  - Mixed edges: `"-_-hello_-_"` → `"hello"`.
  - Interior preserved: `"hello_world"` → `"hello_world"`; `"hello-world"` → `"hello-world"`.
  - Edges created by other processing: `"  -hello- "`, `"!hello!"`, which should produce no leading or trailing `-`/`_`.
  - Degenerate input: `"___"`, `"---"`, `"-_- "` → `""`.
  - Both `allow_unicode=False` and `allow_unicode=True`, including a non-ASCII case such as `"__你好__"` with unicode allowed.
  - Regression: all existing `slugify()` tests still pass. Any test that asserts leading/trailing `-`/`_` must be reviewed and flagged, not silently changed (see Boundaries).
- **Coverage expectations:** **unknown** project policy. Every branch of the changed logic should be exercised by at least one test.

## Boundaries

- **Always:**
  - Add regression tests for the issue's example and the edge cases above.
  - Run the existing `django.utils.text` and template filter tests before submitting.
  - Update the function's documentation and the release notes to describe the behavior change.
- **Ask first:**
  - Changing the function signature, for example adding a parameter to opt out of stripping.
  - Changing how interior dashes or underscores are handled.
  - Modifying any existing test whose expected output contains leading/trailing `-`/`_`.
  - Backporting to stable branches.
- **Never:**
  - Change `slugify()` behavior beyond edge stripping, for example lowercasing, allowed character set, or whitespace collapsing.
  - Remove or skip failing tests to make the change pass.
  - Add new third-party dependencies.

## Success Criteria

1. `slugify("___This is a test ---")` returns exactly `"this-is-a-test"`.
2. For any input, the output of `slugify()` neither starts nor ends with `-` or `_`, with both `allow_unicode` values.
3. Interior `_` and `-` characters are unchanged compared to current behavior.
4. All-separator inputs return `""` without raising.
5. All pre-existing `slugify()` tests pass, or any that encoded the old edge behavior are explicitly identified and approved for update.
6. Documentation and release notes mention that leading/trailing dashes and underscores are now stripped.

## Open Questions

1. **Backward compatibility:** Is this an accepted behavior change for the next feature release? Or does it need a deprecation path or an opt-out parameter? Existing stored slugs and URLs may differ when regenerated.
2. **Target version/branch:** Which Django version should this land in? Should it be backported?
3. **Interior underscores:** Should interior underscores be kept as-is (assumed)? Or should runs of underscores also be collapsed or normalized to dashes?
4. **Ordering of stripping:** Should stripping happen on the final slug, as assumed, or only on the raw input before other processing? The two can give different results for inputs like `"!-hello-!"`.
5. **Empty result:** Is returning `""` for all-separator input acceptable, or is another behavior expected?
6. **Template filter:** Does the `slugify` template filter delegate entirely to this function? Does it need its own tests or docs update?
7. **Linked PR:** The issue references a PR that was not available. Does it contain decisions, such as an implementation approach or extra test cases, that should be reflected here?
8. **Project commands and paths:** What are the exact test, lint, and docs-build commands and the test and doc file locations for this repository?