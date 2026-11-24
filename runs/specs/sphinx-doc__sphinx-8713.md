# Spec: `napoleon_use_param` applies to the "Other Parameters" section

## Objective

In `sphinx.ext.napoleon`, the **Other Parameters** section is always rendered in field-list style (`:Other Parameters: **y** (*float*)`). This happens even when `napoleon_use_param = True`. The **Parameters** section switches to docutils `:param:` / `:type:` fields when that option is set. The two sections describe the same kind of entity, so they should follow the same formatting rule.

**Who it's for:** Sphinx users who write NumPy- or Google-style docstrings with napoleon and enable `napoleon_use_param`. They want all parameter-like sections rendered consistently, for example so that `:type:` cross-referencing and theme styling apply to "other" parameters too.

**User story:** As a docs author with `napoleon_use_param = True`, I want my "Other Parameters" entries emitted as `:param name:` / `:type name:` fields, so they render and link the same way as regular parameters.

**Current behavior** (from the issue, Sphinx 1.8.1, Python 3.7):

```
NumpyDocstring("""\
Parameters
----------
x : int

Other parameters
----------------
y: float
""")
```
produces:
```
:param x:
:type x: int

:Other Parameters: **y** (*float*)
```

**Desired behavior** (from the issue, normalized; see Open Questions): when `napoleon_use_param` is True, the Other Parameters entries are emitted with `:param y:` / `:type y: float` field syntax, under some visible "Other Parameters" grouping or heading. When `napoleon_use_param` is False, the output stays exactly as it is today.

**Relevant code** (quoted in the issue; file path unknown, presumably the napoleon docstring module):

```python
def _parse_other_parameters_section(self, section):
    # type: (unicode) -> List[unicode]
    return self._format_fields(_('Other Parameters'), self._consume_fields())

def _parse_parameters_section(self, section):
    # type: (unicode) -> List[unicode]
    fields = self._consume_fields()
    if self._config.napoleon_use_param:
        return self._format_docutils_params(fields)
    else:
        return self._format_fields(_('Parameters'), fields)
```

## Assumptions

1. This change is controlled by the existing `napoleon_use_param` option. No new config value is introduced; the issue calls a separate option "a bit overkill".
2. The behavior applies to both `NumpyDocstring` and `GoogleDocstring`. The parsing method is shared, and `NumpyDocstring` appears to subclass `GoogleDocstring`; this is unverified.
3. With `napoleon_use_param = False`, the output must be byte-for-byte unchanged (backward compatibility).
4. The `:param: y` line in the issue's expected output is a typo for `:param y:`, which is the form that `_format_docutils_params` produces for `x`.
5. Section-header aliases that currently map to the Other Parameters parser (e.g. "Other parameters", "Other Parameters") all get the new behavior. The exact alias list is unknown.
6. Other parameter-like sections (e.g. Keyword Arguments, Attributes) are out of scope unless they already share this code path. Their current behavior is unknown.
7. The target is the current Sphinx main branch, not a 1.8.x backport.

## Tech Stack

- Python. The supported version range for the target branch is unknown; the issue's environment is Python 3.7.
- Sphinx, extension `sphinx.ext.napoleon`. Exact target version unknown; the issue reports 1.8.1.
- docutils field lists (`:param:`, `:type:`).

## Commands

Unknown. No repository access, so the build, test, and lint commands are not visible in the issue.

- Test: unknown (likely the project's pytest-based suite; exact invocation and flags unknown)
- Lint / type check: unknown
- Docs build: unknown

## Project Structure

Unknown beyond what the issue implies:

- Napoleon docstring parsing: module containing `_parse_other_parameters_section`, `_parse_parameters_section`, `_format_fields`, `_format_docutils_params`. Path unknown.
- Napoleon tests: location unknown.
- Napoleon config docs (`napoleon_use_param` description): location unknown.
- Changelog: location and format unknown.

## Code Style

Follow the existing style of the napoleon module. The only visible sample is the snippet above:

- Private `_parse_<section>_section(self, section)` methods return a `List[str]` of reST lines.
- The module uses type comments (`# type: (...) -> ...`) in the quoted version. Whether the current branch uses annotations or type comments is unknown.
- Section titles are wrapped in the translation function `_()`.
- Config is read via `self._config.napoleon_use_param`.

## Testing Strategy

- **Level:** unit tests on the docstring classes. Construct `NumpyDocstring` / `GoogleDocstring` with an explicit config and assert the rendered string. The framework and test file location are unknown.
- **Cases required:**
  1. NumPy style, `napoleon_use_param=True`, with Parameters + Other Parameters. Other Parameters entries render as `:param name:` / `:type name:`.
  2. NumPy style, `napoleon_use_param=False`. Output is identical to the current output (regression guard).
  3. Google style, equivalent cases for both config values.
  4. An Other Parameters section alone, with no Parameters section, under `napoleon_use_param=True`.
  5. Entries with a description, entries with no type, and multiple names on one line (e.g. `x1, x2 : int`), if supported for Parameters. These must behave the same as in the Parameters section.
- Existing napoleon tests must continue to pass. Any existing test that asserts the old Other Parameters rendering under `napoleon_use_param=True` must be updated, and that change called out in review.
- Coverage expectation: unknown project threshold. The new branch in `_parse_other_parameters_section` must be exercised for both config values.

## Boundaries

- **Always:**
  - Keep `napoleon_use_param=False` output unchanged.
  - Reuse the same formatting path that the Parameters section uses.
  - Add tests for both NumPy and Google styles.
  - Update the `napoleon_use_param` documentation to say it also affects Other Parameters.
  - Add a changelog entry.
- **Ask first:**
  - Introducing a new config option.
  - Changing the rendering of any section other than Other Parameters (e.g. Keyword Arguments).
  - Changing the shared `_format_docutils_params` behavior for the Parameters section.
  - Choosing a heading format that adds new markup or nodes.
- **Never:**
  - Change defaults of existing config values.
  - Remove or weaken existing tests without approval.
  - Merge Other Parameters entries silently into the main Parameters list so they become indistinguishable, unless that is explicitly approved (see Open Questions).

## Success Criteria

1. With `napoleon_use_param=True`, the issue's NumPy reproduction renders `y` as `:param y:` and `:type y: float` instead of `:Other Parameters: **y** (*float*)`.
2. With `napoleon_use_param=True`, the Google-style equivalent produces the same `:param` / `:type` form for Other Parameters.
3. With `napoleon_use_param=False`, the output for both styles is identical to the pre-change output.
4. Other Parameters entries follow exactly the same rules as Parameters entries under `napoleon_use_param=True`: type handling, description handling, missing type, and multiple names.
5. The rendered output still lets a reader tell which parameters are "other", via the approved heading or grouping, or the approved decision not to distinguish them.
6. All existing napoleon tests pass, plus the new tests listed under Testing Strategy.
7. The `napoleon_use_param` docs and the changelog reflect the change.

## Open Questions

1. **Heading / grouping.** Docutils `:param:` fields are typically merged by Sphinx into a single "Parameters" field in the output. How should "Other Parameters" stay visually distinct?
   - (a) Accept that they are merged with regular parameters.
   - (b) Emit a separate heading line before them, such as the `:Other Parameters:` the issue sketches. Note: an empty field may render oddly.
   - (c) Use another mechanism, such as a rubric or a custom field.
2. **Typo check.** Is the issue's expected `:param: y` indeed a typo for `:param y:`?
3. **Breaking-change policy.** Users with `napoleon_use_param=True` will see changed output for Other Parameters. Is this acceptable as a behavior change in a minor release, or does it require a new opt-in option despite the issue calling that overkill?
4. **Related sections.** Should Keyword Arguments, or other parameter-like sections, be aligned in the same change, or kept strictly out of scope?
5. **Target branch.** Which branch or version should this land on? This affects Python version support and the type-annotation style.
6. **Locations.** What are the test file location and the exact test/lint commands? Unknown without repository access.