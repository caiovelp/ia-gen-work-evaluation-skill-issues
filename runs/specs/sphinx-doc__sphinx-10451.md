# Spec: Fix duplicated `*args` / `**kwargs` entries with `autodoc_typehints = "description"`

## Objective

When Sphinx's autodoc extension runs with `autodoc_typehints = "description"`, parameters declared as `*args` and `**kwargs` show up twice in the generated "Parameters" field list, and both copies are incomplete:

- One entry comes from the docstring (`:param *args:`). It is rendered as `***args**` with the description but **no type**.
- The other entry is generated from the type hints. It is rendered as `**args**` (stars stripped) with the type but **no description**.

At the class level, where the class docstring is used and `__init__`'s type hints are merged in, the generated entries are rendered without the leading stars: `**args**` instead of `***args**`.

**Goal:** typehint-derived entries for variadic parameters must be matched to their docstring-documented counterparts and merged into one entry. The merged entry shows the star-prefixed name, the type, and the description, the same way regular parameters such as `x` are already handled.

**Users:** Sphinx users who document functions or classes with variadic parameters and use `autodoc_typehints = "description"`.

### Reproduction (from issue)

```python
class _ClassWithDocumentedInitAndStarArgs:
    """Class docstring."""

    def __init__(self, x: int, *args: int, **kwargs: int) -> None:
        """Init docstring.

        :param x: Some integer
        :param *args: Some integer
        :param **kwargs: Some integer
        """
```

Config: autodoc extension enabled, `autodoc_typehints = "description"`. Observed on Sphinx 4.2.0.

### Expected output (from issue)

```
Class docstring.

   Parameters:
      * **x** (*int*) --
      * ***args** (*int*) --
      * ****kwargs** (*int*) --

   Return type:
      None

   __init__(x, *args, **kwargs)

      Init docstring.

      Parameters:
         * **x** (*int*) -- Some integer
         * ***args** (*int*) --
           Some integer
         * ****kwargs** (*int*) --
           Some integer

      Return type:
         None
```

## Assumptions

1. The bug is in the autodoc typehints-to-description merging logic. That logic builds field entries from annotation names (`args`, `kwargs`) and compares them against docstring field names (`*args`, `**kwargs`), so the comparison fails. The exact module and function are not visible in the issue and are **unknown**.
2. The intended canonical display name for variadic parameters is the star-prefixed form (`*args`, `**kwargs`). The issue's expected output shows this form in both the class-level and method-level listings.
3. Documenting variadics in a docstring as `:param *args:` and `:param **kwargs:` is the convention to support. Whether to also support the star-less form `:param args:` is not stated; see Open Questions.
4. The fix should apply equally to:
   - plain functions
   - methods
   - class-level output where `__init__` hints are merged into the class description
5. The same mismatch probably affects `:type *args:` fields. If a docstring gives an explicit `:type *args:`, autodoc should not add a duplicate type annotation.
6. Behaviour of the other `autodoc_typehints` modes (`"signature"`, `"none"`, `"both"`) must not change.
7. `autodoc_typehints_description_target` (if it exists in the target version) should keep its current semantics: `"all"` versus `"documented"`. Under `"documented"`, a variadic documented as `:param *args:` counts as documented.

## Tech Stack

- Python, Sphinx (`sphinx.ext.autodoc`). Bug reported against 4.2.0.
- Exact supported Python and Sphinx versions on the target branch: **unknown**.

## Commands

All **unknown**, because the repository is not visible. To be filled in from the project's contributor docs (e.g. its test runner and lint invocations).

- Build: unknown
- Test: unknown
- Lint: unknown

## Project Structure

**Unknown.** These need to be located in the repository:

- the autodoc typehints-merging module
- the autodoc test suite and its test-root fixtures (where a target module such as the reproduction class would live)
- the changelog file

## Code Style

Follow the existing Sphinx code style and conventions; the specifics are unknown here. The fix should be a minimal, local change to the name-matching and merging logic.

## Testing Strategy

- **Level:** integration tests through the existing autodoc test harness. The tests build docs for a fixture module and assert on the rendered text or doctree output.
- **New cases:**
  1. A function with `x: int, *args: int, **kwargs: int`, where the docstring documents all three with `:param *args:` and `:param **kwargs:`. Assert there is a single entry per parameter, each with its type and description.
  2. A class whose `__init__` has the same signature, rendered via the class (the issue's reproduction). Assert that the class-level listing shows `*args` and `**kwargs` with stars and types, and has no duplicates.
  3. Variadics present in the signature but **not** documented in the docstring:
     - Under description target `"all"`, they appear once with the star-prefixed name and type.
     - Under `"documented"`, they are omitted.
  4. A docstring that supplies an explicit `:type *args:`. Assert that no extra typehint-derived type is added.
- **Regression:** the existing autodoc typehints tests must continue to pass unchanged, unless an expected output encoded the buggy star-less name. Any such change must be called out.
- Coverage target: unknown and project-defined.

## Boundaries

- **Always:**
  - Keep the change confined to the typehints description merging behaviour.
  - Add regression tests reproducing the issue.
  - Add a changelog entry if the project convention requires one.
- **Ask first:**
  - Changing how `:param args:` (without stars) is interpreted.
  - Changing output for modes other than `"description"`.
  - Any change to public config options.
- **Never:**
  - Alter the rendering of non-variadic parameters.
  - Remove or loosen existing tests to make them pass.
  - Introduce new dependencies.

## Success Criteria

1. With the reproduction and `autodoc_typehints = "description"`, the `__init__` Parameters list contains exactly three entries:
   - `x (int) -- Some integer`
   - `*args (int) -- Some integer`
   - `**kwargs (int) -- Some integer`

   There are no star-less `args` or `kwargs` duplicates.
2. The class-level Parameters list shows `x (int)`, `*args (int)` and `**kwargs (int)` with the star prefixes.
3. The return type is still rendered as `None` in both places.
4. The rendered output matches the issue's "expected output" structure.
5. Undocumented variadics appear exactly once, star-prefixed, under target `"all"`, and are absent under `"documented"`.
6. All pre-existing autodoc tests pass.

## Open Questions

1. Should `:param args:` (no stars) in a docstring also be recognised as documenting `*args`, and merged accordingly? Or is only the star-prefixed form supported?
2. When the docstring uses the star-less form, should the rendered name be normalised to the star-prefixed form?
3. Is the class-level star-less rendering (`**args**`) considered part of this bug, as the expected output implies? Or should it be split into a separate change?
4. Which branch or version is the fix targeting (a 4.x bugfix release or the main branch)? Does it require a changelog entry?
5. Should Napoleon-style (Google/NumPy) docstrings that document `*args` and `**kwargs` be covered by this fix, or only reST `:param:` fields?
6. Are there existing tests whose expected output currently encodes the star-less variadic names that would need updating?