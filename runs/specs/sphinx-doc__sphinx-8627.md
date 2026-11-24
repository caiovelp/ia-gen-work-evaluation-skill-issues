# Spec: Resolve `struct.Struct` Type Annotations in autodoc Cross-References

## Objective

When autodoc renders a function signature whose annotations include `struct.Struct`, Sphinx emits `class reference target not found: Struct`. With `-n -W` that warning fails the build. Other standard-library classes such as `pathlib.Path` resolve correctly in the same setup.

**Users:** Sphinx users who document Python code with `sphinx.ext.autodoc`, often alongside `sphinx.ext.intersphinx`, and who use stdlib types in their annotations. Many of them build in nitpicky, warnings-as-errors mode.

**Goal:** Annotations that use `struct.Struct` should produce a cross-reference to the fully qualified name `struct.Struct`, just as `pathlib.Path` already does. The bare name `Struct` must no longer be emitted. With intersphinx configured for the Python docs, the reference should resolve.

**User story:** As a developer documenting a module with `def make_struct() -> struct.Struct`, I want `sphinx -nW` to succeed and the return type to link to the Python docs for `struct.Struct`.

### Reproduction (from the issue)

`docs/index.rst`:
```rst
Hello World
===========

code docs
=========

.. automodule:: helloworld.helloworld
```

`helloworld/helloworld.py`:
```python
import struct
import pathlib

def consume_struct(_: struct.Struct) -> None:
    pass

def make_struct() -> struct.Struct:
    mystruct = struct.Struct('HH')
    return mystruct

def make_path() -> pathlib.Path:
    return pathlib.Path()
```

Command:
```
python3 -m sphinx -b html docs/ doc-out -nvWT
```

- **Observed:** `class reference target not found: Struct`, and the build fails.
- **Expected:** no warning, and `struct.Struct` is rendered and resolved like `pathlib.Path`.

## Assumptions

1. **Likely cause:** the reference target is built from the class's `__module__` and `__qualname__`. `struct.Struct` is implemented in C (`_struct`) and reports a misleading `__module__`, possibly `builtins`. Sphinx then treats it as a builtin and emits the bare name `Struct`. This is unverified; the issue only shows the unqualified `Struct` target.
2. Other C-implemented stdlib classes may have the same problem, for example `types.TracebackType`. They are in scope only if they share the same root cause, and should be confirmed during investigation.
3. Intersphinx is configured against the Python docs in the reporter's project; it is listed in their extensions. Without intersphinx, a correctly qualified `struct.Struct` would still be an unresolved target under `-n`. The fix should make the target *correct*, not make every external reference resolve.
4. The fix belongs in Sphinx's annotation-to-reference conversion. Users should not need to add `nitpick_ignore` entries.
5. The affected version is Sphinx 3.2.1 on Python 3.8.2. Behaviour on other Python versions may differ if `__module__` for `struct.Struct` changed between versions.
6. The fix covers both rendering paths: annotations shown in signatures and annotations shown in the description (`autodoc_typehints = "description"`).
7. Genuine builtins (`int`, `str`, `None`, etc.) must keep their current rendering.

## Tech Stack

- Python (the reporter uses 3.8.2; the supported range for the fix is unknown)
- Sphinx (the reporter uses 3.2.1; the target branch is unknown)
- Extensions involved: `sphinx.ext.autodoc` and `sphinx.ext.intersphinx`

## Commands

- **Reproduce (from issue):** `python3 -m sphinx -b html docs/ doc-out -nvWT`
- **Build:** unknown, not visible in the issue
- **Test:** unknown (repo test runner and flags not visible)
- **Lint / type check:** unknown

## Project Structure

Unknown. No repository access, so the module(s) that turn annotations into reference targets and the location of the existing tests are not known. These must be identified before planning.

## Code Style

Unknown. Follow the existing conventions of the Sphinx codebase. No snippet is available.

## Testing Strategy

- **Unit level:** tests for the annotation-to-text/reference conversion should assert that:
  - `struct.Struct` produces the qualified target `struct.Struct`.
  - `pathlib.Path` is unchanged.
  - True builtins such as `int` are unchanged.
  - Compound annotations like `Optional[struct.Struct]` and `List[struct.Struct]` qualify the inner type correctly.
- **Integration level:** a test project mirroring the reproduction should be built in nitpicky mode and should assert:
  - The rendered output contains a reference to `struct.Struct`.
  - No `reference target not found: Struct` warning is emitted.
- **Regression:** the existing autodoc and typing-utility test suites must pass unchanged.
- Framework, test locations and coverage expectations are unknown.

## Boundaries

- **Always:**
  - Reproduce the failure with a test before changing behaviour.
  - Keep rendering of genuine builtins and already-working stdlib types unchanged.
  - Run the existing test suite.
- **Ask first:**
  - Adding a general mechanism, such as a mapping table, for other misreported C-implemented classes beyond `struct.Struct`.
  - Changing public configuration options or output format for unrelated annotations.
  - Backporting to maintenance branches.
- **Never:**
  - Silence the warning, for example by suppressing nitpicky warnings or adding default `nitpick_ignore` entries.
  - Monkeypatch `struct.Struct.__module__` globally.
  - Remove or loosen existing tests.

## Success Criteria

1. The reproduction project builds successfully with `-nvWT` when intersphinx maps the Python docs. No `class reference target not found: Struct` warning appears.
2. In the HTML output, `consume_struct` and `make_struct` show `struct.Struct` as a cross-reference with target `struct.Struct`, rendered consistently with how `pathlib.Path` is rendered for `make_path`.
3. Without intersphinx, any remaining nitpicky warning names the fully qualified `struct.Struct`, never the bare `Struct`.
4. Nested annotations (`Optional[struct.Struct]`, `Union[struct.Struct, int]`, `List[struct.Struct]`) produce qualified targets.
5. Builtin annotations (`int`, `str`, `None`) and `pathlib.Path` render exactly as before. Existing tests pass.
6. Both `autodoc_typehints = "signature"` and `"description"` modes produce the qualified target.
7. New tests cover criteria 2–5 and fail without the fix.

## Open Questions

1. Which Sphinx branch and release should the fix target (3.2.x maintenance vs. next minor)?
2. Which Python versions must be supported? Does `struct.Struct.__module__` report the same value on all of them, so the fix behaves consistently?
3. Should the fix be narrowly scoped to `struct.Struct`, or generalized to other C-implemented stdlib classes with misleading `__module__` values (e.g. `types.TracebackType`)? If generalized, which classes are included?
4. Should string or forward-reference annotations (`"struct.Struct"`) also be covered? Those may take a different code path.
5. Is the reporter's intersphinx mapping for the Python docs confirmed? The issue lists the extension but not the `intersphinx_mapping` value.
6. Do `sphinx.ext.autosectionlabel`, `doctest` or `todo` (also enabled by the reporter) play any role? This is assumed not, but unverified.
7. Where are the relevant source modules and tests located, and what are the exact test/lint commands? These are unknown without repository access.