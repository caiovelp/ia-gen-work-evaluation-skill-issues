# Spec: `mathematica_code` should print `Max` (and likely `Min`) as valid Mathematica syntax

## Objective

`mathematica_code` converts SymPy expressions into Mathematica (Wolfram Language) source code. For `Max`, it currently emits function-call syntax with parentheses, which Mathematica cannot parse.

**Reported behavior:**

```python
x = symbols('x')
mathematica_code(Max(x, 2))
# actual:   'Max(2, x)'   (invalid Mathematica)
# expected: 'Max[x,2]'    (as written in the issue)
```

**Goal:** `mathematica_code` must print `Max` expressions using Mathematica bracket syntax, `Max[...]`, so the output is valid Wolfram Language code.

**User:** Anyone who uses SymPy to generate Mathematica code, such as code generation pipelines or people copying output into a Mathematica notebook.

**User story:** As a user, when I call `mathematica_code(Max(x, 2))`, I get a string I can paste into Mathematica and evaluate without a syntax error.

## Assumptions

1. The project is SymPy, and `mathematica_code` is SymPy's Mathematica code printer. The issue does not show the module path.
2. The root cause is that the Mathematica printer has no specific handling for `Max`. It probably falls back to a generic printer that emits `Name(args)` with parentheses.
3. `Min` behaves the same way and is in scope, because it is structurally identical to `Max`. This is unverified, so it is also listed under Open Questions.
4. The argument order in the output follows SymPy's canonical ordering of `Max`'s arguments. The reported `2, x` order comes from SymPy reordering the arguments, not from the printer. Getting exactly `x,2` (the order the user typed) is not a hard requirement. The real defect is the parentheses-versus-brackets syntax.
5. The separator between arguments follows whatever convention the Mathematica printer already uses for other functions, for example `", "`. The issue's `'Max[x,2]'` with no space is illustrative and not an exact formatting requirement.
6. Mathematica's `Max` and `Min` accept any number of arguments, so arguments map one-to-one with no change in semantics.
7. No public API changes. `mathematica_code`'s signature and settings stay as they are.

## Tech Stack

- Python (version unknown)
- SymPy (version unknown; the issue does not name the affected release)
- Component: SymPy's Mathematica code printer (exact module/file unknown)

## Commands

The issue does not specify these, so they are unknown:

- Build: unknown (likely none needed for a pure-Python change)
- Test: unknown (the SymPy test runner invocation is not given)
- Lint: unknown
- Dev: N/A

## Project Structure

Unknown; the issue does not provide it. These need confirming:

- Location of the Mathematica printer source: unknown
- Location of the Mathematica printer's tests: unknown

## Code Style

Unknown. Follow the existing conventions of the Mathematica printer, such as how it already prints other functions with `Name[args]` bracket syntax. No snippet is available from the issue.

## Testing Strategy

- **Level:** Unit tests on the Mathematica printer's string output.
- **Location:** The existing test file for the Mathematica printer (path unknown).
- **Cases to cover:**
  - `Max(x, 2)` produces bracket syntax `Max[...]` containing both `x` and `2`, with no parentheses call syntax.
  - `Max` with three or more arguments, e.g. `Max(x, y, z)`.
  - `Max` nested in a larger expression, e.g. `Max(x, 2) + 1` or `sin(Max(x, y))`.
  - `Min` with the same cases, if confirmed in scope.
  - Regression check: existing Mathematica printer tests still pass.
- **Coverage:** Every new or changed code path in the printer is exercised by at least one test.

## Boundaries

**Always:**
- Produce output that is syntactically valid Wolfram Language.
- Add regression tests that reproduce the reported case.
- Keep the change consistent with how the printer already handles other functions.

**Ask first:**
- Changing argument ordering behavior. This could mean preserving the user's input order, or changing SymPy's canonical ordering of `Max`/`Min`.
- Changing the argument separator format used across the printer.
- Expanding scope beyond `Max`/`Min` to other functions that may have the same fallback problem.

**Never:**
- Change the core `Max`/`Min` classes or their evaluation or canonicalization just to fix printing.
- Change the public signature of `mathematica_code`.
- Remove or weaken existing printer tests.

## Success Criteria

1. `mathematica_code(Max(x, 2))` returns a string of the form `Max[<args>]` using square brackets, with arguments `x` and `2` in SymPy's canonical order, joined by the printer's standard separator.
2. The output contains no `Max(` parentheses call syntax.
3. Multi-argument `Max(x, y, z)` prints as `Max[...]` with all three arguments.
4. `Max` nested inside other expressions prints correctly with brackets.
5. If `Min` is in scope, criteria 1–4 also hold for `Min`.
6. All pre-existing Mathematica printer tests continue to pass.
7. New regression tests covering the cases above are added and pass.

## Open Questions

1. **Argument order:** Is the canonical order `Max[2, x]` acceptable, or must the output preserve the order the user wrote, giving `Max[x, 2]`? The issue's expected output shows `x,2`, but SymPy reorders `Max` arguments when it builds the expression.
2. **Exact formatting:** Must the output be exactly `Max[x,2]` with no space, or is the printer's existing separator (likely `", "`) acceptable?
3. **Min scope:** Does `Min` have the same defect, and should it be fixed in the same change?
4. **Broader scope:** Are other SymPy functions also falling back to parentheses syntax in the Mathematica printer? Should they be audited here or tracked separately?
5. **Affected versions:** Which SymPy version(s) exhibit this? The issue does not say.
6. **Repository details:** What are the paths of the Mathematica printer and its tests, and what is the test command?