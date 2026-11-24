# Spec: Correct pretty-printing of `sympy.vector` expressions with multi-line coefficients

## Objective

`pprint` (and `init_printing()` terminal output) garbles `sympy.vector` expressions whose scalar coefficient renders over more than one line, such as fractions, integrals, or nested functions with exponents.

The issue shows three symptoms:

1. **Basis vector inserted inside the coefficient.** In `pprint(vecB)`, `i_C` appears in the middle of the numerator (`2⋅sin⎜───⎟ i_C⋅cos⎝10 ⋅t⎠`). This displaces the following text and breaks the right-hand parenthesis column.
2. **Basis vector at the wrong row.** In `pprint(vecE)`, `k_C` sits on the second line of a tall integral expression. It is not at the expression's baseline or centre.
3. **Basis vector inside the enclosing parentheses.** In `pprint(vecE.doit())`, `k_C` is printed inside the coefficient's parentheses (`... k_C ⎟`). The parenthesis column is misaligned on the remaining rows.

**Users:** SymPy users who work with `sympy.vector` (`CoordSys3D`, `Del`, basis vectors `i/j/k`) and view results in a terminal through `pprint` or `init_printing()`. The problem appears both with and without Unicode box-drawing characters.

**Desired outcome:** The pretty form of a vector term is a well-formed 2D block in three parts:

- the coefficient, rendered intact and parenthesized if needed;
- the basis-vector symbol, placed outside and after the coefficient;
- vertical alignment consistent with how SymPy aligns other binary products (baseline alignment).

Multi-term vectors (`a*i + b*j + c*k`) must keep each basis vector attached to its own coefficient. The `+` separators must align on a common baseline.

### User stories

- As a user, when I `pprint` a vector with a fractional coefficient, I see the full fraction followed by the basis vector, and no characters are interleaved into the fraction.
- As a user, when I `pprint` an unevaluated `Integral` times a basis vector, the basis vector appears once, beside the integral expression, at the baseline.
- As a user, when I `pprint` a multi-component vector with multi-line coefficients, each component is readable and the columns stay aligned.

## Tech Stack

- Python and SymPy. The affected version is **unknown**; the issue does not state it.
- Components involved: the SymPy pretty printer (`pprint`, `init_printing`) and the `sympy.vector` module (`CoordSys3D`, `Del`, vector `Integral`/`doit`).
- Exact source files or functions: **unknown**. They are not visible from the issue.

## Commands

All of the following are **unknown**, because the issue gives no repository access:

- Build: unknown
- Test: unknown. A pytest-based suite is expected, but the exact command is unverified.
- Lint: unknown
- Reproduce: run the script from the issue with `python` (exact invocation unknown).

## Project Structure

**Unknown.** The locations of the pretty-printer source, the vector module, and their tests are not visible in the issue.

## Code Style

**Unknown.** Follow the existing conventions of the surrounding pretty-printer and vector code. No snippet is available from the issue.

## Testing Strategy

The framework and test locations are **unknown**. The intended levels are:

- **Unit tests (pretty printer)**: assert exact string output of `pretty(...)` for vector expressions in both Unicode and ASCII modes. Cover:
  - a single basis vector with a multi-line fraction coefficient containing a function call. This is the `vecB` case: `2*10**-4*cos(10**5*t)*sin(10**-3*y) * i`.
  - a basis vector times an unevaluated `Integral` coefficient (the `vecE` case).
  - a basis vector with a negative fraction coefficient containing several function factors (the `vecE.doit()` case).
  - a multi-component vector where each component has a multi-line coefficient.
  - regression cases: single-line coefficients (`3*i`, `x*i + y*j`), a coefficient of `1` or `-1`, and the zero vector. These must render exactly as they do today.
- **Regression**: existing pretty-printing tests for vectors and dyadics must still pass. Dyadics are an open question; see below.
- Expected output strings should be agreed (see Open Questions) before they are hard-coded.

## Boundaries

- **Always:**
  - Keep single-line vector output byte-identical to current behaviour unless agreed otherwise.
  - Test both Unicode and ASCII pretty modes.
  - Include the issue's reproduction as a test.
- **Ask first:**
  - Changing the visual format of vector output, for example parenthesization rules or basis-vector position, beyond fixing the corruption.
  - Changing how other printers (LaTeX, str, MathML) render vectors.
  - Changing shared 2D layout utilities used by non-vector printing.
- **Never:**
  - Alter the mathematical value or structure of vector objects to work around printing.
  - Remove or weaken existing printing tests.
  - Change printing of non-vector expressions as a side effect.

## Success Criteria

1. `pprint(vecB)` from the issue produces a block where:
   - the fraction numerator reads contiguously as `2⋅sin(y_C/10³)⋅cos(10⁵⋅t)` in 2D form, with no `i_C` inside it;
   - `i_C` appears exactly once, to the right of the closing parenthesis;
   - every row of the parenthesized coefficient has its right parenthesis in the same column.
2. `pprint(vecE)` shows `k_C` exactly once, to the right of the full parenthesized integral expression, on the baseline row (the fraction-bar row). It must not be on row 2.
3. `pprint(vecE.doit())` shows `k_C` exactly once, outside the closing parenthesis. The parenthesis column is consistent on all rows.
4. For every line of output, line widths are consistent: there is no trailing ragged characters between parenthesis segments.
5. The same three cases render correctly with `use_unicode=False`.
6. Multi-component vectors with multi-line coefficients render each basis vector after its own coefficient, with `+` aligned on the baseline.
7. All pre-existing vector pretty-printing tests pass unchanged, or any intentional changes are explicitly approved.

## Assumptions

1. The intended layout is `(<coefficient>) <basis>`. The basis vector is placed to the right of the parenthesized coefficient and aligned on the coefficient's baseline, consistent with how SymPy aligns other products.
2. The bug is in the pretty printer's rendering of vector (basis-dependent) expressions. It is not in the `sympy.vector` arithmetic: the expressions themselves are mathematically correct, and only display is affected.
3. The defect is triggered by coefficients whose pretty form spans multiple lines, especially when they contain function applications with parentheses. Single-line coefficients are currently correct.
4. The same layout logic may also be used for dyadics or other basis-dependent objects, so they may share the bug.
5. `symbols("10", positive=True)` is just a user trick to keep `10` unevaluated. It is not part of the bug.
6. Terminal width is sufficient. Line-wrapping is out of scope.

## Open Questions

1. **Placement:** Should the basis vector be aligned on the baseline (fraction-bar row), the vertical centre, or the bottom row of the coefficient?
2. **Parenthesization:** Should multi-line coefficients always be wrapped in parentheses, as today? Or should parentheses be dropped when the coefficient is a single fraction?
3. **Dyadics and other types:** Are dyadics and other basis-dependent types in scope for this fix? Should they get the same tests?
4. **Affected versions:** Which SymPy version(s) exhibit the bug? Is the fix to be backported?
5. **Output changes:** Is any change to existing approved test output acceptable, for example if the current tests encode the buggy layout?
6. **Other printers:** Should the LaTeX, string, and Jupyter rich display be checked for analogous problems, or is this strictly limited to the 2D terminal pretty printer?
7. **Repository details:** What are the exact test command, test file location, and pretty-printer source location? All are unknown from the issue.