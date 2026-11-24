# Spec: Napoleon over-escapes the trailing underscore in attribute names

## Objective

**Problem.** With `sphinx.ext.autodoc` and `sphinx.ext.napoleon` enabled, an attribute named `hello_` in a NumPy-style `Attributes` section renders in HTML as `hello\_`, with a visible backslash. The reporter says Sphinx 2.4.3 rendered it correctly and 3.0.4 does not, so this is a regression.

**Reproducer (from the issue):**

```python
class A:
    """
    Attributes
    ----------
    hello_: int
        hi
    """
    pass
```

- `conf.py` has `extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']`.
- `index.rst` contains `.. autoclass:: a.A`.
- The docs are built with `PYTHONPATH=. make clean html`.

**Expected.** The attribute name shows as `hello_` with no backslash. The output should match hand-written reST:

```rst
.. attribute:: hello_
   :type: int

   hi
```

How the type is displayed is out of scope. The reporter states it renders differently but "that's not the point here".

**User.** Sphinx users who document Python classes with napoleon (NumPy-style, and possibly Google-style) docstrings. Their attribute names end with an underscore, which is a common convention, for example fitted attributes in scikit-learn-style APIs.

**Acceptance criteria.**

- AC1: A NumPy-style `Attributes` entry named `hello_` renders as `hello_` in HTML, with no visible backslash.
- AC2: The reST napoleon generates for that entry names the attribute `hello_` in the `attribute` directive argument, not `hello\_`.
- AC3: Contexts that genuinely need escaping keep their current correct rendering, with no regression. Examples are parameter names such as `*args` and `**kwargs`, and names rendered as inline reST text.
- AC4: The behavior matches Sphinx 2.4.3 for this case.

## Assumptions

1. The backslash comes from napoleon escaping names for inline reST and then applying that same escaping to text used as a directive argument (`.. attribute:: <name>`). Directive arguments are not parsed as inline markup, so the backslash appears literally. This is inferred from the symptom and has not been verified in the code.
2. The regression was introduced between Sphinx 2.4.3 and 3.0.4. The issue does not identify the exact commit.
3. Only the `Attributes` section is affected in the reported form. Other sections may be affected too; see Open Questions.
4. The fix belongs in `sphinx.ext.napoleon`, not in autodoc or the Python domain, because hand-written `.. attribute:: hello_` renders correctly.
5. Python 3.8.3 on Linux is not relevant to the bug.
6. Google-style docstrings likely share the same code path and should get the same fix. The issue only demonstrates NumPy style.

## Tech Stack

- Python (the reporter used 3.8.3). The supported range is unknown.
- Sphinx (bug seen on 3.0.4, fine on 2.4.3).
- Extensions involved: `sphinx.ext.napoleon` and `sphinx.ext.autodoc`.
- Other dependency versions are unknown.

## Commands

The issue does not show any of these, and I have no repository access.

- Build: unknown
- Test: unknown
- Lint: unknown
- Docs build for manual reproduction: `PYTHONPATH=. make clean html`, run in a `sphinx-quickstart`-generated project (from the issue)

## Project Structure

Unknown, because I have no repository access.

- The module implementing napoleon's docstring conversion is unknown. Presumably it lives under the `sphinx.ext.napoleon` package.
- The location of the napoleon tests is unknown.

## Code Style

Unknown. Follow the existing conventions of the napoleon module and its tests once they are visible.

## Testing Strategy

- Framework and test locations are unknown.
- **Unit level:** convert the reproducer docstring (NumPy style, and Google style if it shares the path) with napoleon. Assert that the generated reST contains `.. attribute:: hello_` and does not contain `hello\_`.
- **Regression guard:** keep or add assertions that escaping still applies where it is needed, such as `*args` and `**kwargs` in parameter lists. Cover any other context identified under Open Questions.
- **Manual / integration:** build the reproducer project and confirm the HTML shows `hello_` with no backslash.

## Boundaries

- **Always:**
  - Add a test that fails on current behavior and passes after the fix.
  - Run the existing napoleon test suite.
  - Limit the change to how napoleon escapes names.
- **Ask first:**
  - Changing escaping behavior in sections other than `Attributes`.
  - Changing napoleon config options or their defaults.
  - Touching autodoc or the Python domain.
  - Changing how the attribute type is rendered.
- **Never:**
  - Remove escaping globally in a way that breaks `*args`/`**kwargs` or inline-text contexts.
  - Delete or weaken existing tests without approval.
  - Bundle in the unrelated type-display difference.

## Success Criteria

- [ ] For the reproducer, napoleon's output for the `Attributes` entry uses `hello_` as the `attribute` directive argument, with no backslash.
- [ ] The HTML for the reproducer shows `hello_` with no visible `\`.
- [ ] Existing napoleon tests pass, including any that cover escaping of `*args` and `**kwargs`.
- [ ] A new automated test covers the trailing-underscore attribute case in NumPy style, and in Google style if that style is affected.
- [ ] Rendering of trailing-underscore names in contexts that need escaping (to be determined; see Open Questions) is unchanged or verified correct.

## Open Questions

1. Is the Google-style `Attributes` section also affected? Should it be fixed in the same change?
2. Which other napoleon outputs put a name in a directive argument or a field name rather than inline text? Candidates include `Methods`, `:ivar:` output when `napoleon_use_ivar = True`, and `:param:` when `napoleon_use_param = True`. Should they also stop escaping?
3. Where must a trailing underscore still be escaped, so that it is not read as a reST reference such as inline names in field bodies? The fix needs to preserve escaping there.
4. Which commit between 2.4.3 and 3.0.4 introduced the escaping? Knowing what it was meant to fix helps avoid re-breaking that case.
5. Should the fix be backported to a 3.0.x bugfix release, or only land on the current development branch?
6. What are the test, lint, and build commands, and where are the napoleon tests located?
7. Is the type-rendering difference the reporter mentioned (`:type: int` vs napoleon's output) worth tracking in a separate issue?