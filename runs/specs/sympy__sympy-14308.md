# Spec: Correct pretty printing of `sympy.vector` expressions (layout and baseline)

## Objective

Pretty printing of `sympy.vector` expressions is broken when a basis vector is multiplied by a multi-line scalar coefficient.

Reported reproduction:

```py
In [1]: from sympy.vector import *
In [2]: e = CoordSysCartesian('e')
In [3]: (x/y)**t*e.j
Out[3]:
⎛   t⎞ e_j
⎜⎛x⎞ e_j ⎟
⎜⎜─⎟ ⎟
⎝⎝y⎠ ⎠
```

Observed defects:

1. **Corrupted layout.** The basis vector name `e_j` is placed inside the scalar's 2D picture. It appears once on the top line, outside the parentheses, and once on an inner line, inside the parentheses. The outer parentheses do not match their contents.
2. **Wrong baseline.** The reporter says that even when the layout is correct, the baseline of a printed vector is wrong. A vector term should be vertically centered so it lines up correctly with surrounding expressions.

**Goal:** Pretty printing (Unicode and ASCII) of vector expressions should produce well-formed 2D layouts:
- The scalar coefficient is rendered intact.
- The basis vector appears exactly once, outside and to the right of the coefficient.
- The baseline is consistent with how SymPy centers other multi-line expressions.

**Users:** SymPy users who display vector expressions with `pprint`, `pretty`, or interactive (IPython or Jupyter) output.

**Scope:**
- **In scope:** the pretty-printed form of vector expressions (basis vectors scaled by scalar coefficients, and sums of such terms) and their baseline.
- **Out of scope:** `str`, LaTeX and MathML output, unless the same root cause is found to affect them. Changes to vector semantics are also out of scope.

## Assumptions

1. `x`, `y`, `t` in the reproduction are ordinary SymPy `Symbol`s (e.g. from `sympy.abc` or `symbols`); the issue does not show their definition.
2. `CoordSysCartesian` is the coordinate-system class in the affected version. If the codebase has since renamed or replaced it (e.g. `CoordSys3D`), the fix applies to whichever class is current, and the old name is still covered if it remains supported.
3. The defect is in how the vector's pretty form is assembled from the coefficient's 2D picture, not in the pretty printing of `(x/y)**t` itself. A plain scalar `(x/y)**t` is assumed to print correctly.
4. The defect affects both Unicode and ASCII pretty printing.
5. "Centered baseline" means the same vertical-centering convention SymPy's pretty printer already uses for other multi-line products and fractions. It does not mean a new convention.
6. Expected rendering for the reported case looks roughly like the block below. The exact spacing follows existing pretty-printer conventions.
   ```
       t    
   ⎛x⎞     
   ⎜─⎟  e_j
   ⎝y⎠     
   ```
   The basis vector sits on the vertical center line of the coefficient, and the coefficient's internal structure is unchanged.
7. Single-line coefficients (e.g. `3*e.i`, `x*e.j`) already print acceptably. They must not change except for baseline corrections.

## Tech Stack

- Python, SymPy. Exact SymPy and Python versions: **unknown** (not stated in the issue).
- Relevant subsystems:
  - the `sympy.vector` module;
  - SymPy's pretty printer and 2D string-layout machinery.
- Exact file locations: **unknown** (not visible in the issue).

## Commands

- Build: **unknown**. This is a pure-Python library; no build step is shown.
- Test: **unknown**. The project's test runner and the invocation for vector and pretty-printing tests are not shown.
- Lint: **unknown**.
- Manual reproduction: run the snippet from the issue in IPython or a Python REPL after defining `x, y, t` as symbols.

## Project Structure

**Unknown.** The issue does not show the repository layout. To be determined:
- where vector pretty-printing logic lives (a printer method versus a method on the vector classes);
- where pretty-printing tests for vectors live.

## Code Style

**Unknown.** Follow the existing conventions of the surrounding pretty-printer and `sympy.vector` code. No snippet is available from the issue.

## Testing Strategy

- **Framework / location:** unknown. Use the project's existing test framework and add tests next to the existing vector pretty-printing tests.
- **Regression tests (required):**
  - The reported case `(x/y)**t*e.j`, Unicode and ASCII, compared against exact expected strings.
  - Other multi-line coefficients, for example:
    - a plain fraction `x/y*e.i`;
    - an integral or other tall expression times a basis vector;
    - a nested power.
  - Sums of vector terms where one or more terms has a multi-line coefficient, e.g. `(x/y)**t*e.j + e.i`.
  - Baseline checks: a vector embedded in a larger pretty-printed expression (e.g. inside a sum or alongside a fraction) must align on the expected center line.
  - Unchanged output for simple cases: `e.i`, `3*e.i`, `x*e.j`, the zero vector, and sums of simple terms. The only allowed difference is the intended baseline correction.
- **Coverage expectation:** every code path that builds a vector's pretty form (single term, multi-term sum, possibly dyadics if they share the logic) is covered by at least one test with a multi-line coefficient.

## Boundaries

**Always:**
- Add regression tests reproducing the exact issue before or with the fix.
- Run the existing pretty-printing and vector test suites.
- Preserve output for cases that currently render correctly, except for the intended baseline fix.

**Ask first:**
- Changing the expected output of existing tests.
- Changing the general pretty-printer layout utilities, rather than vector-specific code, in ways that could affect non-vector output.
- Extending the fix to dyadics or other vector-like objects if they need separate work.
- Changing `str`, LaTeX or MathML output.

**Never:**
- Change vector semantics or arithmetic to fix a display issue.
- Delete or weaken existing printing tests to make them pass.
- Special-case only the exact expression from the issue.

## Success Criteria

1. `pretty((x/y)**t*e.j)`, in both Unicode and ASCII:
   - renders the coefficient `(x/y)**t` exactly as it renders on its own (no injected text, matching parentheses);
   - shows `e_j` exactly once, to the right of the coefficient.
2. For any vector term whose coefficient's pretty form spans multiple lines:
   - the basis vector appears exactly once;
   - it never appears inside the coefficient's picture.
3. Multi-term vector sums with multi-line coefficients render each term correctly, with `+` signs and terms aligned on a common baseline.
4. The pretty form of a vector has its baseline at the vertical center, consistent with other multi-line SymPy expressions. A vector placed inside a larger pretty-printed expression aligns correctly.
5. Pretty output for single-line-coefficient vectors is unchanged, apart from any intended baseline adjustment.
6. All new regression tests pass, and existing pretty-printing and vector tests pass (or their changes are explicitly approved).

## Open Questions

1. Which SymPy version is affected? Is `CoordSysCartesian` still the current API, or should tests use its replacement (e.g. `CoordSys3D`)?
2. What exact layout is expected for the reported case? Specifically:
   - Should the basis vector be vertically centered on the coefficient, or aligned with the coefficient's baseline?
   - What exact spacing should separate the coefficient and the basis vector?
3. "When it does print correctly, the baseline is wrong (it should be centered)": which cases print correctly but with a wrong baseline? An example of current versus expected output would pin this down.
4. Are dyadics (and any other `sympy.vector` objects with custom pretty printing) affected, and should they be fixed in the same change?
5. Should ASCII mode (`use_unicode=False`) be held to the same expected layouts as Unicode?
6. Is `str`, LaTeX or MathML output of vectors also affected? Should that be tracked in this issue or separately?
7. Where do vector pretty-printing logic and tests live, and what commands run the relevant test suites?