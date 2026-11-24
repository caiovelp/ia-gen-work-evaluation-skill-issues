# Spec: Clearer Module-Level Skip Handling in pytest

## Assumptions

1. The project is **pytest**. The relevant public API is `pytest.skip(msg=..., allow_module_level=...)` together with the `pytest.mark.skip` and `pytest.mark.skipif` markers. These are taken from the issue text.
2. The quoted error message is the current wording raised when `pytest.skip` is called outside a test without `allow_module_level=True`. Its exact source location is **unknown**.
3. `pytestmark = pytest.mark.skipif(...)` cannot help when the module fails at **import or collection time**. Examples include syntax that is invalid on older Python versions, or names used inside `@pytest.mark.parametrize` arguments. The marker is only applied after the module has been imported successfully.
4. `skip(..., allow_module_level=True)` is the supported and intended way to skip a whole module before the rest of it is imported.
5. Existing behavior of `pytest.skip` and its `allow_module_level` parameter must stay backward compatible. No deprecation is planned in this change.
6. The scope may include any combination of three items:
   - (a) a revised error message
   - (b) a documentation update
   - (c) a new convenience API such as `skip_module("reason")`

   The issue does not decide between them, so this spec covers all three. The choice is listed under Open Questions.
7. The issue's example of a module that is invalid on Python < 3.8 is illustrative only. The improvement must not depend on any particular Python version.

## Objective

Users who need to skip an entire test module, especially before importing code that cannot be imported or parsed on the current interpreter, should be guided to the working solution rather than away from it.

**Problem today:**
- A naive `pytest.skip("...")` at module level raises an error.
- That error recommends only `pytestmark = pytest.mark.{skip,skipif}`.
- `pytestmark` does not prevent pytest from importing the rest of the module. So in the import-failure case it fails.
- The working approach, `skip(msg=..., allow_module_level=True)`, is never mentioned. The wording of the error actively discourages calling `skip` as a function.

**Users:** test authors maintaining code across several Python versions or optional dependencies. They need to skip a module whose top-level code, imports, or parametrize arguments are unavailable or invalid in some environments.

**User stories:**
- As a test author who calls `pytest.skip()` at module level by mistake, I want the error message to tell me about `allow_module_level=True`. Then I can fix the problem without searching issues.
- As a test author whose module contains version-specific imports or parametrize values, I want to know which module-skip mechanism works for my case. That means knowing when `pytestmark` is enough and when it is not.
- *(If option (c) is accepted)* As a test author, I want a self-describing API to skip the current module, so I don't have to remember a keyword flag.

## Tech Stack

- Python, pytest codebase. Supported Python versions are **unknown**.
- Specific files implementing `skip`, `Skipped`, and the module-level skip error are **unknown**.
- Documentation format and location are **unknown**, likely Sphinx/reST, but unverified.

## Commands

**Unknown.** The issue gives no build, test, lint, or docs commands. They must be taken from the repository's contributor documentation or CI config.

- Build: unknown
- Test: unknown
- Lint: unknown
- Docs build: unknown

## Project Structure

**Unknown.** The relevant areas to locate are:
- the implementation of `pytest.skip` and the `allow_module_level` handling
- the code that raises the "Using pytest.skip outside of a test is not allowed" error during collection
- the public API export surface (`pytest` namespace), if a new function is added
- the test suite covering skip and collection behavior
- the user docs page(s) on skipping and the API reference
- the changelog mechanism

## Code Style

**Unknown.** Follow existing conventions in the surrounding skip/outcomes code. Any new public function must match the signature and docstring conventions of `pytest.skip`.

Illustrative user-facing usage, from the issue (not project code):

```python
import sys
import pytest

if sys.version_info < (3, 8):
    pytest.skip(msg="Requires Python >= 3.8", allow_module_level=True)

from pos_only import *  # must come after the module-level skip
```

## Testing Strategy

The framework is pytest itself. Its in-repo testing helpers for running pytest on generated test files are assumed to exist but are **unverified**. The test location is **unknown**.

Behaviors to cover:

1. **Error message content.** Calling `pytest.skip("...")` at module level without `allow_module_level=True` still produces a collection error. That error now mentions `allow_module_level=True`, and still mentions `pytestmark` for the decorator case.
2. **Module-level skip with `allow_module_level=True`.** The module is reported as skipped. Code after the skip is not executed or imported. This works even when that code would raise an `ImportError`, a `SyntaxError` in an imported module, or fail during parametrize evaluation.
3. **New API, if adopted.** `skip_module("reason")`, or whatever name is chosen, behaves identically to `skip(msg=reason, allow_module_level=True)` at module level. That includes the skip reason shown in the reporting output. Behavior when called inside a test function is decided per Open Question 4, and tested accordingly.
4. **Regression.** Existing `pytest.skip` uses inside tests and fixtures, and `pytestmark = pytest.mark.skip/skipif`, behave unchanged.
5. **Docs.** If the docs build has checks (doctests, link checks), they pass. Commands are unknown.

## Boundaries

**Always:**
- Keep `pytest.skip(..., allow_module_level=True)` working exactly as today.
- Add tests for every behavior change, including the error message.
- Add a changelog entry per project convention (mechanism unknown).
- Keep the error message actionable. It should name the concrete call to use for each scenario.

**Ask first:**
- Adding any new public API, such as `skip_module` or an alternative name. This becomes a permanent public surface.
- Deprecating or changing the semantics of `allow_module_level`.
- Changing the type or class of the exception raised for a module-level skip without the flag.
- Restructuring the skipping docs page beyond adding or clarifying a section.

**Never:**
- Silently allow `pytest.skip()` at module level without the flag. That would remove the guard against accidentally skipping whole modules.
- Remove the existing `pytestmark` recommendation. It is still correct for the common case.
- Make the change depend on a specific Python version.

## Success Criteria

1. When `pytest.skip("reason")` is called at module level without `allow_module_level=True`, the resulting error message:
   - still states that this usage is not allowed as written
   - mentions `pytestmark = pytest.mark.{skip,skipif}` for decorating or skipping a module whose code imports fine
   - explicitly mentions `pytest.skip(msg=..., allow_module_level=True)` for skipping a module before the rest of it is imported or evaluated
   - and/or mentions the new API, if one is added
2. The skipping documentation states:
   - that `pytestmark` markers apply only after the module has been imported or collected, so they cannot prevent import or syntax errors in that module
   - that `pytest.skip(..., allow_module_level=True)` must be placed **before** the problematic imports or definitions
   - a short example equivalent to the issue's scenario
3. *(If option (c) is adopted)* A public function, name TBD, exists in the `pytest` namespace that skips the current module with the given reason. It has a docstring, appears in the API reference, and is referenced by the error message and the docs.
4. A module skipped via the recommended mechanism is reported as skipped with the given reason, not as an error. This holds even when code later in the module would fail to import.
5. All existing skip-related tests pass unchanged, except tests that assert the exact old error text, which are updated deliberately.

## Open Questions

1. **Scope choice:** should this change cover (a) the error message only, (b) the docs only, (c) a new API, or a combination? The issue proposes (a) and (c). The maintainers' preference is unknown.
2. **New API name and shape:** if a new API is added, what should it be called? Candidates include `skip_module("reason")` and `pytest.skip.module(...)`. Should it accept only a reason string, or mirror `skip`'s parameters?
3. **Relationship to `importorskip`:** should the docs and error message also point to `pytest.importorskip` for the case where the blocker is a missing or unimportable module rather than a version check?
4. **Misuse of a new API:** if `skip_module` is called inside a test function, should it raise an error, behave like `skip`, or skip the remaining tests in the module?
5. **Error message length:** is a multi-sentence error message acceptable, or should it stay short and link to the docs instead? Is there a stable docs URL convention for that?
6. **Version-check helpers:** should anything beyond messaging be considered, such as documenting `sys.version_info` checks with `collect_ignore` in `conftest.py` as another option? Or is that out of scope?
7. **Backport and release target:** which release line should this ship in? Does an error-message-only change count as user-visible enough to need a changelog entry of a specific type?
8. **Exact current locations:** where are the error text, the `skip` implementation, the skipping docs, and the changelog fragments located? What are the repository's test, lint, and docs commands? All of these are unknown from the issue.