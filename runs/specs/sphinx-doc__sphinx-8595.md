# Spec: autodoc honors an empty `__all__` in `automodule :members:`

## Objective

When a module defines `__all__ = []`, `.. automodule:: <module>` with `:members:` should document **no members**. Today autodoc appears to treat an empty `__all__` the same as a missing `__all__`. It falls back to listing every public member, so `foo`, `bar` and `baz` all appear.

**Users:** Sphinx users who rely on `__all__` to control which members autodoc documents. An explicitly empty `__all__` means "export nothing."

**User story:** As a library author, when I set `__all__ = []`, I want `automodule :members:` to document no members, so that the docs match the module's declared public API.

**Acceptance criteria:**
- If `__all__` is defined and empty, `:members:` with no explicit member list documents zero members.
- If `__all__` is not defined, behavior is unchanged: all public members are documented, as now.
- If `__all__` is defined and non-empty, behavior is unchanged: only the listed members are documented.
- The module's own docstring and header are still rendered when `__all__` is empty. Only members are suppressed.

## Assumptions

1. The root cause is that autodoc tests whether `__all__` is truthy rather than whether it is present. That check makes `[]` behave like "not defined." This is a hypothesis to confirm during implementation. The exact code location is **unknown**.
2. The fix targets the Sphinx 3.x branch, the "HEAD of 3.x" reported in the issue, and should also carry forward to later branches.
3. An empty tuple `()` should behave the same as an empty list `[]`.
4. Explicit member lists still override `__all__`, as they do today. For example, `:members: foo` documents `foo` even when `__all__ = []`.
5. Existing options keep their current interaction with `__all__`. This includes `:ignore-module-all:`, `:undoc-members:`, `:private-members:`, `:special-members:` and `:imported-members:`. With `:ignore-module-all:`, an empty `__all__` is ignored and all public members are shown.
6. The behavior is independent of OS and Python version. The reported environment was macOS with Python 3.9.1.
7. An invalid `__all__`, such as a non-list or one containing non-strings, keeps its existing handling. It is out of scope.

## Tech Stack

- Python. The supported version range for the 3.x branch is **unknown**.
- Sphinx, `sphinx.ext.autodoc`, 3.x branch.
- Other dependencies and their versions are **unknown**.

## Commands

- Build: **unknown**
- Test: **unknown**. The project test runner is not visible from the issue.
- Lint: **unknown**
- Reproduce: build a Sphinx project that contains the `example.py` and `index.rst` from the issue. The exact command is **unknown**.

## Project Structure

**Unknown.** The autodoc module source file, the test directory and the test-root fixture layout are not visible from the issue.

## Code Style

**Unknown.** Follow existing Sphinx conventions found in the repository. No snippet is available.

Reproduction fixture from the issue, to serve as the basis of a test:

```python
# example.py
__all__ = []


def foo():
    "docstring"


def bar():
    "docstring"


def baz():
    "docstring"
```

```rst
.. automodule:: example
   :members:
```

## Testing Strategy

- Framework: **unknown**. pytest is presumed but not confirmed.
- Add a regression test using a module with `__all__ = []` and the directive `automodule :members:`. Assert that no `foo`, `bar` or `baz` entries are generated.
- Add or confirm tests for these neighboring cases:
  - No `__all__` documents all public members.
  - A non-empty `__all__` documents only the listed members.
  - An empty `__all__` combined with `:ignore-module-all:` documents all public members.
  - An empty `__all__` with an explicit `:members: foo` documents `foo`.
- Run the full autodoc test suite to catch regressions.

## Boundaries

- **Always:** Add a regression test that fails before the fix and passes after it. Keep behavior unchanged for modules without `__all__`. Run the existing autodoc tests.
- **Ask first:** Changing behavior for an invalid `__all__`. Changing how `:ignore-module-all:` or an explicit `:members:` list interacts with `__all__`. Any change to the public autodoc API or event signatures, such as `autodoc-skip-member`. Adding a CHANGES entry, if the format is unknown.
- **Never:** Change the default for modules without `__all__`. Remove or weaken existing tests. Add new dependencies.

## Success Criteria

- [ ] Building the issue's reproduction produces a module entry with no `foo`, `bar` or `baz` members.
- [ ] A regression test for an empty `__all__` exists and passes.
- [ ] Existing autodoc tests pass unchanged.
- [ ] The behavior for a missing `__all__`, a non-empty `__all__`, `:ignore-module-all:` and an explicit `:members:` list is verified unchanged by tests.

## Open Questions

1. Should `:ignore-module-all:` with an empty `__all__` show all public members? This spec assumes yes.
2. Should an explicit `:members: foo` still document `foo` when `__all__ = []`? This spec assumes yes.
3. Should autosummary, or anything else that reads `__all__` the same way, also be fixed in this change? Or should it be scoped to autodoc only?
4. Which branch should the fix target? Should it be backported?
5. Is a changelog entry required, and in what format?
6. What are the project's test, lint and build commands, and where should the test fixture live?
7. Does anyone rely on the current behavior, where an empty `__all__` shows everything? If so, is a migration or deprecation note needed?