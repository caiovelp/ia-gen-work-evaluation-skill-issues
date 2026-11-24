# Spec: autosummary — exclude imported members from the module template `members` variable when `autosummary_imported_members = False`

## Objective

When `sphinx.ext.autosummary` generates stub pages, it passes a `members` variable to the module template (`autosummary/module.rst`). Today that variable contains imported members (for example `os` after `import os`), even when `autosummary_imported_members = False`.

The fix should make `members` respect `autosummary_imported_members`:

- If it is `False`, `members` must not contain names whose objects were imported from another module.
- If it is `True`, imported members stay in `members`, as they do today.

**Users:** Sphinx documentation authors who use custom autosummary module templates that iterate over `{{ members }}`. They expect `members` to follow the same imported-members policy as the other template variables.

**Success looks like:** For the issue's reproduction, the generated `generated/example.rst` no longer lists `os` under `members` when `autosummary_imported_members = False`.

### Reproduction (from the issue)

```
# _templates/autosummary/module.rst
{{ fullname | escape | underline }}

.. automodule:: {{ fullname }}

   .. autosummary::
   {% for item in members %}
      {{ item }}
   {%- endfor %}
```
```
# example.py
import os
```
```
# index.rst
.. autosummary::
   :toctree: generated

   example
```
```
# conf.py
autosummary_generate = True
autosummary_imported_members = False
```

**Observed output.** `members` contains `__builtins__`, `__cached__`, `__doc__`, `__file__`, `__loader__`, `__name__`, `__package__`, `__spec__` and `os`.

**Expected output (per issue).** `members` does not contain imported members such as `os`.

## Assumptions

1. "Imported member" uses the same definition autosummary already applies to its type-specific template variables (`functions`, `classes`, `exceptions`): the object's defining module (`__module__`) differs from the documented module. *Unverified — I cannot see the source.*
2. The issue only targets imported members. Module dunder attributes (`__builtins__`, `__doc__`, `__name__`, etc.) are not imports. Whether they stay in `members` is a separate question; see Open Questions.
3. Objects without a reliable `__module__` (for example module objects like `os`, or plain data values) must still be classified somehow. Module objects bound in the namespace via `import` are treated as imported.
4. Only the module template's `members` variable is in scope. Class template `members` and the `autosummary_imported_members=True` behaviour stay unchanged.
5. The default value of `autosummary_imported_members` stays unchanged.
6. The issue was reported against Sphinx 3.1.0dev, Python 3.8.2, macOS. The fix is expected to be platform-independent.

## Tech Stack

- Python (reported: 3.8.2; supported range: **unknown**)
- Sphinx 3.1.0dev, extension `sphinx.ext.autosummary`
- Jinja2 templating for autosummary templates
- Test framework: **unknown** (presumably pytest, unverified)

## Commands

- Build: **unknown**
- Test: **unknown**
- Lint: **unknown**
- Docs build for reproduction: **unknown** (any `sphinx-build` invocation over the repro project above)

## Project Structure

**Unknown.** No repository access. The following locations need to be identified:

- The autosummary stub-generation code that builds the template context (`members`, `functions`, `classes`, ...).
- The existing autosummary tests and their test-root fixtures.
- The changelog file and the autosummary documentation for template variables.

## Code Style

Unknown. Follow the existing conventions of the autosummary module. No snippet is available from the issue.

## Testing Strategy

- **Regression test (required).** Use a test-root module that imports another module (e.g. `import os`) and also defines at least one local function or class. Generate the stub with `autosummary_imported_members = False` and assert that:
  - `os` is **not** in the module template's `members`;
  - locally defined members **are** in `members`.
- **Complementary test.** With `autosummary_imported_members = True`, assert that `os` (or an imported function or class) **is** in `members`.
- **Consistency check.** Under both settings, `members` filtering is consistent with the existing filtering of `functions`, `classes` and `exceptions`.
- **Level.** Unit or integration test at the stub-generation level, asserting on the template context or generated `.rst` content. The exact harness is unknown.
- **Suite.** The existing autosummary test suite must still pass.

## Boundaries

- **Always:**
  - Add a regression test reproducing the issue.
  - Keep behaviour unchanged when `autosummary_imported_members = True`.
  - Reuse the existing imported-member detection logic rather than introducing a divergent definition.
- **Ask first:**
  - Removing dunder or private attributes from `members`.
  - Changing class-template `members`.
  - Changing the default of `autosummary_imported_members`.
  - Adding new template variables.
  - Any change visible to existing custom templates beyond removing imported names.
- **Never:**
  - Change autosummary output for users who set `autosummary_imported_members = True`.
  - Delete or weaken existing tests.
  - Change unrelated autodoc behaviour.

## Success Criteria

1. With the issue's reproduction and `autosummary_imported_members = False`, `generated/example.rst` does not list `os`.
2. With `autosummary_imported_members = True`, `os` is still listed in `members`.
3. Members defined in the module itself (functions, classes, module-level variables) remain in `members` under both settings.
4. Under both settings, `members` filtering is consistent with the filtering already applied to `functions`, `classes` and `exceptions`.
5. A regression test covering criteria 1–3 is added and passes, and the existing autosummary tests pass.
6. A changelog entry describes the bug fix (exact file is unknown).

## Open Questions

1. **Dunder attributes.** Should `__builtins__`, `__cached__`, `__doc__`, `__file__`, `__loader__`, `__name__`, `__package__` and `__spec__` remain in `members`? They are not imported, so the issue's expected behaviour doesn't strictly cover them, but users may expect them gone.
2. **Classifying data members.** How should members without a meaningful `__module__` be classified (module-level constants, or values imported via `from x import CONST`)? Is it acceptable that imported plain data values may not be detectable as imported?
3. **Submodules of a package.** Should submodules bound on a package (`import pkg.sub` inside `pkg/__init__.py`) count as imported members of the package?
4. **Class templates.** Should the class template's `members` variable also be reviewed for consistency, or is it strictly out of scope?
5. **Compatibility of the fix.** Is this a backward-compatible bug fix for the next patch/minor release? Custom templates that relied on `members` including imports will see fewer entries.
6. **Documentation.** Does the autosummary template-variable documentation need updating to state that `members` honours `autosummary_imported_members`?