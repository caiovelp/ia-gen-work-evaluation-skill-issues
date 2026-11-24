# Spec: Correct two-digit year interpretation in `django.utils.http.parse_http_date`

## Objective

`django.utils.http.parse_http_date` parses HTTP date strings. One accepted format is the RFC 850 date, which uses a **two-digit year**. The current logic hard-codes the century:

- `00`–`69` → `2000`–`2069`
- `70`–`99` → `1970`–`1999`

This fixed split does not follow RFC 7231 (§7.1.1.1), which requires:

> Recipients of a timestamp value in rfc850-date format, which uses a two-digit year, MUST interpret a timestamp that appears to be more than 50 years in the future as representing the most recent year in the past that had the same last two digits.

RFC 2822 has similar wording. The fixed split gets more wrong over time. For example, from 2020 onward a year of `70` should eventually resolve relative to the current year rather than always to `1970`. Year `69` resolves to `2069`, which will be more than 50 years in the future once the current year is earlier than 2019. As the current year moves forward, the hard-coded window stops matching the RFC.

**Goal:** Resolve two-digit years in RFC 850 dates relative to the current year, as RFC 7231 specifies:

1. Candidate year = current century + the two-digit year.
2. If the candidate is more than 50 years after the current year, subtract 100.

**Users:**
- Django developers and applications that parse HTTP date headers through `parse_http_date` or `parse_http_date_safe`, for example `If-Modified-Since` and `If-Unmodified-Since` handling.
- Indirectly, HTTP clients that send legacy RFC 850 dates.

**Acceptance criteria:**
- An RFC 850 date whose two-digit year is **not** more than 50 years in the future relative to the current year resolves to the current century.
- An RFC 850 date whose two-digit year would be **more than 50 years** in the future resolves to the previous century (the most recent past year with the same last two digits).
- Four-digit-year formats (RFC 1123 / IMF-fixdate and asctime) behave exactly as before.
- The result does not depend on a hard-coded pivot such as `70`. It depends only on the current date.

## Assumptions

1. The change is limited to the two-digit-year handling inside `parse_http_date` in `django/utils/http.py`. The module name comes from the issue. The exact file path and current code are not visible and are assumed.
2. `parse_http_date_safe` delegates to `parse_http_date`, so it inherits the fix with no separate change.
3. "Current year" means the current year in **UTC**, consistent with HTTP dates being GMT.
4. "More than 50 years in the future" is a strict comparison: exactly 50 years ahead stays in the current century, and 51 or more rolls back. This needs confirmation (see Open Questions).
5. The comparison is done at **year granularity**, not full-timestamp granularity. This needs confirmation (see Open Questions).
6. The public signature, return type (seconds since epoch as an integer), and error behaviour (`ValueError` on invalid input) stay unchanged.
7. No new dependencies are needed; only the standard library is used.
8. Tests that cover this behaviour must control "now" (by mocking or patching the current time) so they are deterministic and do not break as the calendar advances.

## Tech Stack

- Python and Django. Supported versions for the target branch are **unknown**.
- Standard library date/time handling (`datetime` / `calendar`). The specific modules currently imported by `django/utils/http.py` are **unknown**.

## Commands

All commands are **unknown**; they are not stated in the issue. To be confirmed:

```
Test:  [unknown — Django test runner invocation for the utils_tests suite]
Lint:  [unknown — e.g. project flake8/isort configuration]
Build: [not applicable / unknown]
```

## Project Structure

Only the following can be inferred from the issue. Everything else is **unknown**:

```
django/utils/http.py   → contains parse_http_date (inferred from module path in issue)
[unknown]              → existing tests for django.utils.http (likely a utils tests module; path unconfirmed)
[unknown]              → release notes location, if a note is required
```

## Code Style

- Follow existing Django code style in `django/utils/http.py`. The concrete conventions and a sample snippet are **unknown**, since the source is not visible.
- Keep the change minimal and local to the two-digit-year branch.
- Cite RFC 7231 in a short comment at the point of year adjustment.

## Testing Strategy

- **Framework:** Django's test suite. The exact runner command and test module path are **unknown**.
- **Level:** Unit tests on `parse_http_date` only.
- **Determinism:** Patch or mock the current UTC time in every test that exercises two-digit years. No test may depend on the real system clock.
- **Cases to cover**, given a fixed mocked "now":
  - A two-digit year a few years in the past resolves to the current century.
  - A two-digit year a few years in the future, up to 50, resolves to the current century.
  - A two-digit year exactly 50 years in the future, to pin the boundary per the resolved Open Question.
  - A two-digit year 51 or more years in the future resolves to the previous century.
  - At least two different mocked "now" values, for example one around 2020 and one around 2070, to show the pivot moves with the current year and is not hard-coded.
  - A mocked "now" near a century boundary (for example year 2099 or 2100) to confirm century arithmetic is correct.
- **Regression:**
  - Existing tests for the RFC 1123 and asctime formats still pass unchanged.
  - Existing RFC 850 tests are updated only where their expectations relied on the old hard-coded split.
- **Coverage expectation:** Every branch of the new year-adjustment logic is exercised.

## Boundaries

- **Always:**
  - Keep the public API and return values of `parse_http_date` and `parse_http_date_safe` unchanged for four-digit-year formats.
  - Make time-dependent tests deterministic.
  - Reference RFC 7231 in the code comment.
- **Ask first:**
  - Changing behaviour of any format other than RFC 850.
  - Adding a parameter (for example an injectable "now") to the public function signature.
  - Adding a release note or deprecation, or backporting to stable branches.
- **Never:**
  - Replace the hard-coded pivot with another hard-coded pivot.
  - Rely on the real current date in tests.
  - Add third-party dependencies.

## Success Criteria

- For any mocked current UTC year `Y` and two-digit year `yy`, the parsed year is the value in `{century(Y) + yy, century(Y) + yy − 100}` chosen per the RFC 7231 rule:
  - If `century(Y) + yy − Y > 50`, use the past century.
  - Otherwise, use the current century.
  - The boundary handling matches the resolution of Open Question 1.
- With mocked "now" in 2020:
  - `…-69 …` resolves to 2069.
  - `…-70 …` resolves to 2070 if the strict reading (`> 50`) applies; the expected result follows the resolution of Open Question 1.
  - `…-71 …` resolves to 1971.
- With mocked "now" in 2070, `…-37 …` resolves to 2037 and not 1937 or 2137. More generally, the window follows the current year.
- All pre-existing `django.utils.http` tests for RFC 1123 and asctime dates pass unchanged.
- No test outcome changes when run on a different real calendar date.

## Open Questions

1. **Boundary:** Is a year exactly 50 years in the future kept in the current century? The RFC says "more than 50 years", which suggests a strict `>`.
2. **Granularity:** Should the "more than 50 years in the future" check compare whole years, or the full parsed timestamp (month, day, time) against now? The RFC says "a timestamp that appears to be…", which could imply full-timestamp comparison.
3. **Time source:** Should the current time come from UTC (`datetime.utcnow` / timezone-aware now) or local time? UTC is assumed.
4. **Test location and runner:** What is the correct test module path and command for running the `django.utils.http` tests?
5. **Release management:** Does this change need a release note, and is it a candidate for backport to supported stable branches, given it changes parsed values for some inputs?
6. **Existing tests:** Do any existing tests assert the old hard-coded 0–69 / 70–99 behaviour? If so, should they be rewritten with a mocked "now" or replaced?