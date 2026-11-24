# Spec: Add `hostname` and `timestamp` attributes to the JUnit XML `<testsuite>` element

## Objective

pytest can write JUnit XML reports (the `--junitxml` feature). Its `<testsuite>` element is missing two attributes that JUnit-style reports commonly include:

- `hostname`: the machine that ran the tests.
- `timestamp`: when the test run started.

Many CI dashboards, report aggregators and archival tools read these attributes to sort, group or trace runs. Because pytest leaves them out, users cannot tell from the report alone where or when a run happened. The reporter asked whether an option exists to include them. This spec assumes there is none today and proposes adding them.

**Users:** pytest users who produce JUnit XML for CI systems or report tooling.

**Current output (from the issue):**
```xml
<testsuite errors="0" failures="2" name="check" skipped="0" tests="4" time="0.049">
```

**Desired output (shape taken from the issue's JUnit example):**
```xml
<testsuite name="..." tests="..." skipped="..." failures="..." errors="..." time="..."
           timestamp="2019-04-22T10:32:27" hostname="Anass-MacBook-Pro.local">
```

### User stories / acceptance criteria
1. When I generate a JUnit XML report, the `<testsuite>` element has a `hostname` attribute containing the name of the machine that ran the tests.
2. When I generate a JUnit XML report, the `<testsuite>` element has a `timestamp` attribute containing the start time of the test session in ISO 8601 format (`YYYY-MM-DDTHH:MM:SS`, as in the JUnit example).
3. Existing attributes (`errors`, `failures`, `name`, `skipped`, `tests`, `time`) and all `<testcase>` content stay unchanged.
4. The report still conforms to the JUnit XML schema(s) pytest targets or validates against.

## Assumptions
1. No option to emit these attributes exists in pytest today. The issue shows them absent from default output, and this spec treats the request as a feature, not a support question.
2. Both attributes will be emitted **unconditionally**, with no new CLI flag or ini option. They are standard JUnit attributes and adding XML attributes is backward compatible for well-behaved consumers.
3. `timestamp` means the **start** of the test session, not the moment the report is written. This matches JUnit, where `timestamp` marks when the suite began.
4. `timestamp` uses ISO 8601 without a timezone suffix, matching the issue's example. Whether to use local time or UTC is an open question; this spec defaults to **local time**, as in the example.
5. `timestamp` may include fractional seconds only if the schema permits them. The default is seconds precision to match the example.
6. `hostname` comes from the standard OS hostname lookup available to Python.
7. If the hostname lookup fails, the code falls back to a safe value (e.g. omit the attribute or use an empty string) rather than crashing the run.
8. Attribute ordering in the XML does not matter.
9. Behaviour is the same for every supported JUnit "family"/schema variant pytest offers, unless one of them forbids these attributes.

## Tech Stack
- Language: Python (pytest itself).
- Supported Python and pytest versions: **unknown**, not visible in the issue.
- XML generation mechanism inside pytest: **unknown**, not visible in the issue.
- New dependencies: none expected. Hostname and time can come from the Python standard library.

## Commands
Not visible in the issue; all **unknown**.
- Build: unknown
- Test: unknown (likely the project's standard pytest/tox invocation, unconfirmed)
- Lint: unknown
- Dev: unknown

## Project Structure
Not visible in the issue; all **unknown**.
- Location of the JUnit XML reporting code: unknown
- Location of the JUnit XML tests: unknown
- Location of changelog/news fragments and documentation for JUnit XML output: unknown

## Code Style
Unknown. Follow the conventions of the existing JUnit XML reporting module and its tests. No snippet is available from the issue.

## Testing Strategy
- **Framework:** pytest's own test suite. The exact layout and helpers are unknown.
- **Unit / integration tests** (generate a report from a sample test file, then parse the XML):
  - The `<testsuite>` element has a `hostname` attribute equal to the hostname the test environment reports. Mock or compare against the same lookup function.
  - The `<testsuite>` element has a `timestamp` attribute that:
    - parses as ISO 8601 (`%Y-%m-%dT%H:%M:%S` or the agreed format);
    - falls between a time captured just before the session started and one captured just after it ended;
    - reflects session **start**, not report write time. Check this, for example, with a test that sleeps and asserting `timestamp` is at least the sleep duration earlier than the end time.
  - Existing attributes and their values are unchanged (regression).
  - If pytest validates generated XML against a schema in its tests, the output with the new attributes still validates for each supported family.
  - Hostname lookup failure is handled gracefully (simulated via mocking).
- **Coverage:** new code paths fully covered. Overall coverage target is unknown.

## Boundaries
- **Always:**
  - Keep existing `<testsuite>`/`<testcase>` attributes and structure unchanged.
  - Keep output valid against the JUnit schema(s) pytest supports.
  - Add tests for the new attributes.
  - Add a changelog entry and update docs per project convention (mechanism unknown).
- **Ask first:**
  - Adding a CLI flag or ini option to toggle these attributes.
  - Choosing UTC vs local time, or adding a timezone offset to `timestamp`.
  - Any change to the XML that is not purely additive.
  - Adding any third-party dependency.
- **Never:**
  - Remove or rename existing XML attributes or elements.
  - Make report generation fail because the hostname cannot be determined.
  - Change test outcome semantics or timing (`time`) computation.

## Success Criteria
1. A report generated with pytest's JUnit XML option contains `hostname="<machine hostname>"` on `<testsuite>`.
2. The same report contains `timestamp="<ISO 8601 datetime>"` on `<testsuite>`, equal to the session start time within one second.
3. All pre-existing JUnit XML tests pass unchanged, except tests that assert the exact full attribute set, which are updated deliberately.
4. Generated XML validates against the schema(s) used in pytest's test suite, if any.
5. New tests covering criteria 1–2 and hostname-failure handling pass.
6. The changelog and documentation mention the new attributes.

## Open Questions
1. Should the attributes always be emitted, or sit behind an opt-in or opt-out option (CLI flag or ini setting)? The reporter asked about "an option".
2. Should `timestamp` be local time (as in the JUnit example) or UTC? Should it carry a timezone offset? The common JUnit XSD types `timestamp` as an ISO 8601 datetime without timezone; is that the schema we must satisfy?
3. Should `timestamp` mark session start (assumed) or the first test's start?
4. Which hostname source is preferred: the short hostname or a fully qualified domain name? The example shows `Anass-MacBook-Pro.local`.
5. Which JUnit XML families/schemas does pytest currently support, and do any of them forbid `hostname`/`timestamp`?
6. How should distributed or parallel runs (e.g. plugins that run tests on several workers or hosts) populate `hostname`? Should it be the controller's host or something else?
7. Are there privacy concerns about embedding the hostname in reports that might be published, and would that justify an opt-out?
8. Should other JUnit attributes or elements absent from the pytest example be added at the same time, such as `<properties/>`, suite-level `<system-out>`, or `<system-err>`? Or is that out of scope? (Assumed out of scope.)
9. What is the project's changelog/news-fragment convention, and where are the JUnit XML docs?