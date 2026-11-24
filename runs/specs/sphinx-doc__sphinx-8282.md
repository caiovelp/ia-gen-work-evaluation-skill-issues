# Spec: Respect `autodoc_typehints` for overloaded callables

## Objective

`sphinx.ext.autodoc` ignores the `autodoc_typehints` setting when it renders signatures of callables decorated with `typing.overload`. With `autodoc_typehints = 'none'`, overload signatures still show parameter and return annotations, such as `foo(x: int) -> int`.

**Goal:** Every overload signature that autodoc emits follows `autodoc_typehints` in the same way that non-overloaded signatures already do.

**Users:** Sphinx users who document modules containing `@overload`-decorated callables with autodoc.

**User stories / acceptance criteria:**
- With `autodoc_typehints = 'none'`, overloaded functions render with no annotations: `foo(x)`, twice, once per overload.
- With `autodoc_typehints = 'signature'` (assumed default), overload signatures keep their annotations, as they do today.
- With `autodoc_typehints = 'description'`, overload signatures do not show annotations in the signature line. The behaviour for the description field list is an open question (see below).
- Non-overloaded callables behave exactly as they do today.

## Assumptions

1. The reported behaviour reproduces on the Sphinx 3.1.0dev line with Python 3.8. The bug is not platform-specific, although it was reported on macOS.
2. The accepted `autodoc_typehints` values are `'signature'`, `'description'` and `'none'`, with `'signature'` as the default. The issue only shows `'none'`.
3. "Overloaded callables" covers module-level functions (the reported case). It also covers methods and class constructors (`__init__` / `__new__` overloads) wherever autodoc renders overload signatures. Confirm under Open Questions.
4. Overload signatures come from source analysis of `@overload` definitions, not from runtime introspection of the final implementation. This is why they bypass the existing typehint handling.
5. The implementation function's own signature (`def foo(x)`) is not shown separately when overloads exist. This spec does not change that behaviour.
6. `'none'` is expected to strip both parameter annotations and the return annotation. Default values are kept.
7. Annotations given as strings (forward references) are treated the same as evaluated annotations.

## Tech Stack

- Python (issue reports 3.8.2; minimum supported version unknown)
- Sphinx 3.1.0dev, extension `sphinx.ext.autodoc`
- `typing.overload`
- Other dependencies and versions: unknown

## Commands

Not visible in the issue; all unknown.
- Build: unknown
- Test: unknown
- Lint: unknown
- Reproduce: a Sphinx build of a project with the `conf.py` / `index.rst` / `example.py` from the issue. The exact `sphinx-build` invocation is unknown.

## Project Structure

Unknown; no repository access.
- Location of autodoc documenters and signature formatting: unknown
- Location of autodoc tests and test fixture roots: unknown
- Location of changelog: unknown

## Code Style

Unknown; no source visible. Follow the existing conventions of the autodoc module. The only code available is the reproduction from the issue:

```python
from typing import overload

@overload
def foo(x: int) -> int:
    ...

@overload
def foo(x: float) -> float:
    ...

def foo(x):
    return x
```

## Testing Strategy

- Framework and test locations: unknown (follow the existing autodoc test suite).
- Add a regression test fixture that contains overloaded:
  - module-level functions
  - methods
  - constructors, if in scope
- For each `autodoc_typehints` value, assert on the generated autodoc output (directive signature lines):
  - `'none'`: `.. py:function:: foo(x)` appears once per overload, with no `: int`, `: float` or `-> ...`.
  - `'signature'`: the annotated overload signatures are unchanged from current output.
  - `'description'`: behaviour as decided in Open Questions.
- Run the existing autodoc tests to confirm no regressions for non-overloaded callables.
- Edge cases to cover:
  - overloads with default values
  - keyword-only and `*args`/`**kwargs` parameters
  - return-only annotations
  - string or forward-reference annotations

## Boundaries

- **Always:**
  - Keep the default (`'signature'`) output byte-for-byte identical for overloads.
  - Add regression tests.
  - Run the full autodoc test suite.
  - Add a changelog entry if the project keeps one.
- **Ask first:**
  - Changing how overloads are discovered or parsed.
  - Changing what `'description'` mode emits.
  - Adding new config options.
  - Altering the public documenter API.
  - Showing or hiding the implementation signature.
- **Never:**
  - Change the semantics of `autodoc_typehints` for non-overloaded callables.
  - Remove or loosen existing tests.
  - Add new runtime dependencies.

## Success Criteria

1. Building the issue's reproduction project with `autodoc_typehints = 'none'` produces two `foo` signatures, both rendered as `foo(x)` with no type annotations.
2. The same project with `autodoc_typehints = 'signature'` produces `foo(x: int) -> int` and `foo(x: float) -> float`, as today.
3. Equivalent results hold for overloaded methods (and constructors, if in scope).
4. `'description'` mode behaves as agreed in Open Questions, and a test covers it.
5. New regression tests fail before the fix and pass after it. All existing autodoc tests pass.

## Open Questions

1. **`'description'` mode:**
   - Should annotations be removed from overload signature lines?
   - If so, should overload types appear in the description field list? If they should, how are several overloads with conflicting types for the same parameter represented: merged, or listed per overload?
   - Or is `'description'` out of scope for this fix?
2. **Scope:** Should the fix cover methods, classmethods/staticmethods and class constructors (`__init__`/`__new__` overloads), or only module-level functions?
3. **Default values:** Should defaults on overload signatures be preserved under `'none'`? (Assumed yes.)
4. **Target version:** Which release line should receive the fix, 3.1.x or the next minor?
5. **Related settings:** Should other typehint-related settings, if any exist in this version (unknown), also be applied to overloads as part of this issue?
6. **Project layout:** Test commands, test locations and changelog location are unknown and need confirming from the repository.