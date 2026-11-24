# Spec: Apply `autodoc_type_aliases` to Module Variables and Class Attributes

## Objective

The `sphinx.ext.autodoc` configuration option `autodoc_type_aliases` is not applied to the type annotations of **module-level variables** or **class attributes**. The reporter expects the alias mapping to be honored for these members, as it already is (by implication) for other documented objects.

**User:** A Sphinx documentation author who uses `from __future__ import annotations` and defines `autodoc_type_aliases` in `conf.py` so that string annotations resolve to fully qualified, documented types.

**User story:** As a documentation author, when I annotate a module variable or class attribute with a name listed in `autodoc_type_aliases`, I want the rendered type to use the alias target, so that variable and attribute docs are consistent with function and method docs.

**Reproduction (from the issue):**

```python
# example.py
from __future__ import annotations


#: blah blah blah
var: String


class MyString:
    "mystring"

    #: blah blah blah
    var: String
```

```rst
.. index.rst
.. automodule:: example
   :members:
   :undoc-members:
```

```python
# conf.py
autodoc_type_aliases = {
    'String': 'example.MyString'
}
```

**Observed:** The alias is not applied to `example.var` or `example.MyString.var`. The issue does not show the exact rendered output.
**Expected:** The alias is applied to both `example.var` and `example.MyString.var`.

## Assumptions

1. "Does not effect" means the rendered `:type:` of the variable and attribute shows the raw annotation (`String`) instead of the aliased target (`example.MyString`). The issue does not include the actual output.
2. `autodoc_type_aliases` already works for function and method signatures. The bug is limited to the variable and attribute documenters.
3. The fix belongs to the Sphinx 3.x line, since the reporter tested against HEAD of the 3.x branch.
4. Both annotation sources in the example are in scope:
   - module-level annotations (`var: String`)
   - class-body annotations (`var: String` inside `MyString`)
5. Annotations here are strings because of `from __future__ import annotations` (PEP 563). Applying the alias to non-stringified annotations is desirable but secondary.
6. The alias value is emitted as the type text, and cross-referencing then follows normal Sphinx behavior. Whether `example.MyString` renders as a link is not part of this bug.
7. Behavior when `autodoc_type_aliases` is empty or unset must not change.
8. Unannotated variables and attributes, and annotations that don't match any alias key, must render exactly as before.

## Tech Stack

- Python (reporter: 3.9.0; minimum supported version for the 3.x branch: **unknown**)
- Sphinx, 3.x branch, with the `sphinx.ext.autodoc` extension
- Exact dependency versions: **unknown**

## Commands

The issue gives none, and the repository is not visible.

- Build: **unknown**
- Test: **unknown** (the project's test runner and invocation are not shown)
- Lint: **unknown**
- Reproduce: build docs for the example project above with `sphinx.ext.autodoc` enabled. The exact `sphinx-build` invocation is **unknown/not given**.

## Project Structure

Not visible from the issue.

- Location of the autodoc documenters for data/variables and attributes: **unknown**
- Location of the code that applies `autodoc_type_aliases` today: **unknown**
- Location of autodoc tests and test fixture roots: **unknown**

## Code Style

Unknown. Follow the existing conventions of the Sphinx codebase in the files being changed. The repository is not visible, so no style snippet can be given.

## Testing Strategy

- **Level:** Integration-style autodoc tests that generate directive output for a fixture module and assert on the rendered lines. The framework and fixture layout are **unknown** and must be matched to existing autodoc tests.
- **Fixture:** A module equivalent to `example.py` above, using `from __future__ import annotations`, with:
  - an annotated module variable
  - a class with an annotated attribute
  - both annotated with an alias key
- **Cases:**
  1. Module variable with an aliased annotation → the rendered type uses the alias target.
  2. Class attribute with an aliased annotation → the rendered type uses the alias target.
  3. Same fixture without `autodoc_type_aliases` → the rendered type is the raw annotation (regression guard).
  4. Annotation not present in the alias map → unchanged output.
  5. Existing tests for `autodoc_type_aliases` on functions and methods still pass.
- **Coverage expectation:** **unknown**. The new code paths for the variable and attribute documenters must be exercised by at least the cases above.

## Boundaries

- **Always:**
  - Keep existing behavior for functions and methods.
  - Keep output unchanged when no alias matches.
  - Add regression tests for both module variables and class attributes.
  - Run the existing autodoc test suite.
- **Ask first:**
  - Changing the semantics or documentation of the `autodoc_type_aliases` config option.
  - Altering how annotations are evaluated globally (for example, changes affecting `autodoc_typehints`).
  - Adding dependencies.
  - Backporting or forward-porting to branches other than 3.x.
- **Never:**
  - Remove or weaken existing tests.
  - Change the public config option name or type.
  - Introduce behavior that raises errors on annotations that can't be resolved; such annotations should fall back to their current rendering.

## Success Criteria

- [ ] With the reproduction project and `autodoc_type_aliases = {'String': 'example.MyString'}`, the documented type of `example.var` reflects `example.MyString`, not `String`.
- [ ] Under the same conditions, the documented type of `example.MyString.var` reflects `example.MyString`.
- [ ] Without `autodoc_type_aliases`, the output for both members is identical to the current output.
- [ ] Annotations that match no alias key render identically to the current output.
- [ ] Existing `autodoc_type_aliases` behavior for functions and methods is unchanged, and the existing tests pass.
- [ ] New automated tests cover cases 1–4 in the Testing Strategy and pass.

## Open Questions

1. **Observed output:** What exactly is rendered today for `example.var` and `example.MyString.var`? Is it `String`, no type at all, or an error or warning?
2. **Annotation styles in scope:** Should aliases also apply to:
   - annotations without `from __future__ import annotations`?
   - type comments (`# type: String`)?
   - attributes declared only in `__init__` (`self.var: String = ...`)?
3. **Other attribute-like members:** Should the fix also cover properties, slots, or instance attributes documented via other mechanisms, or only the two cases in the issue?
4. **Interaction with `autodoc_typehints`:** Should `autodoc_typehints` settings (e.g. `"none"` or `"description"`) affect how aliased types appear for variables and attributes?
5. **Partial matches:** Should an alias apply when the alias name appears inside a larger annotation, such as `List[String]` or `Optional[String]`, or only on exact whole-annotation matches?
6. **Target branch and versions:** Is the 3.x branch the only target? What is the minimum supported Python version?
7. **Docs:** Should the `autodoc_type_aliases` documentation be updated to state explicitly that it applies to variables and attributes?