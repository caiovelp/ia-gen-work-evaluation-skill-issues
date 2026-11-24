# Spec: Correct grouping when parsing nested LaTeX fractions (`\frac{…}{\frac{…}{…}}`)

## Objective

`parse_latex` from `sympy.parsing.latex` appears to return a wrong expression when the denominator of a `\frac` is itself a fraction.

**Reproduction (from the issue, SymPy 1.8 and 1.6.2, Python 3.6.9):**

```python
>>> from sympy.parsing.latex import parse_latex
>>> parse_latex("\\frac{\\frac{a^3+b}{c}}{\\frac{1}{c^2}}")
((a**3 + b)/c)/1/(c**2)
```

**Expected:** `((a**3 + b)/c)/(1/(c**2))`, which is mathematically `c*(a**3 + b)`.

**Observed:** `((a**3 + b)/c)/1/(c**2)`. Read left to right, this means `(a**3 + b)/c**3`, which is a different value.

**Who is affected:** Users who turn LaTeX into SymPy expressions, for example from Jupyter notebooks or from OCR or handwriting pipelines. They need the result to mean the same thing as the LaTeX. They also need its printed form to read back correctly.

**What success looks like:**
- Any nesting of `\frac` inside the numerator or denominator of another `\frac` gives an expression that is mathematically equal to the LaTeX.
- The string form of that expression, read back as SymPy/Python, gives the same value.

Two defects could explain the report, and the cause is not yet known:

- **(a) Parser defect.** The parser builds the wrong expression tree.
- **(b) Printer defect.** The tree is correct, but `str()` drops the parentheses around an unevaluated product in the denominator.

The spec covers whichever turns out to be the cause (see Open Questions).

### Acceptance criteria
1. `parse_latex("\\frac{\\frac{a^3+b}{c}}{\\frac{1}{c^2}}")` satisfies both of these:
   - It simplifies to `c*(a**3 + b)`, checked by `simplify(result - c*(a**3+b)) == 0`.
   - Its `str()` output, re-parsed with `sympify`/`parse_expr`, also simplifies to `c*(a**3 + b)`.
2. The printed form of the reproducer contains explicit grouping around the denominator, for example `((a**3 + b)/c)/(1/(c**2))`. The exact formatting is to be confirmed.
3. These related forms behave correctly under criterion 1:
   - `\frac{a}{\frac{b}{c}}` → `a*c/b`
   - `\frac{\frac{a}{b}}{\frac{c}{d}}` → `a*d/(b*c)`
   - `\frac{1}{\frac{1}{x}}` → `x`
   - `\frac{a}{\frac{b}{\frac{c}{d}}}` → `a*c/(b*d)`
   - `\frac{a}{b c}` → `a/(b*c)`
4. Existing results for flat fractions are unchanged, for example `\frac{a}{b}` and `\frac{a+b}{c}`. The existing LaTeX parsing test suite still passes.
5. If the cause is in the string printer, any other unevaluated `Mul`/`Pow` combination that has the same denominator-grouping problem also prints with correct parentheses. This must not add redundant parentheses to ordinary evaluated expressions such as `a/(b*c)` and `x/y`.

## Assumptions
1. The bug is still present on current SymPy `master`/latest release. It was only reported on 1.8 and 1.6.2.
2. `parse_latex` builds `\frac` results as unevaluated products and powers (`evaluate=False`). That is why the result keeps a nested structure instead of collapsing to `c*(a**3+b)`. This is unverified.
3. Defect (b) is at least as likely as (a). An unevaluated `Mul(1, Pow(c**2, -1))` inside `Pow(…, -1)` may be printed without parentheses even though the tree is correct.
4. The fix should keep `\frac` results unevaluated (the structure is preserved). The goal is correct meaning and printing, not auto-simplification.
5. The ANTLR-based LaTeX backend is the one in scope. Grammar changes are not expected, because the parse tree for nested `\frac` is presumably unambiguous.
6. Python versions supported by current SymPy are the target. Python 3.6 from the report is not a requirement.

## Tech Stack
- Python. The minimum version is whatever current SymPy supports (unknown here).
- SymPy core (`Mul`, `Pow`, `Add`), `sympy.parsing.latex.parse_latex`, and SymPy's string printer.
- ANTLR4 Python runtime, which `parse_latex` needs. The required version is unknown.

## Commands
Unknown. The repository is not visible. These are needed:
- How to run the LaTeX parsing tests (test file location and runner command): **unknown**
- How to run the string printer tests: **unknown**
- Full test suite / lint commands used by SymPy CI: **unknown**
- Whether the ANTLR runtime must be installed separately to run the parser tests: **unknown**

## Project Structure
Unknown. The repository is not visible. Things to locate:
- The module that converts the ANTLR parse tree to SymPy objects, in particular the `\frac` handling: **unknown path**
- The string printer's handling of `Mul` with negative-power factors: **unknown path**
- The existing test files for the LaTeX parser and the str printer: **unknown paths**

## Code Style
Follow the existing SymPy conventions in the touched modules. No snippet is shown because no source is visible. Constraints that apply either way:
- Do not change the public signature of `parse_latex`.
- Tests are regression tests that name the issue they cover.

## Testing Strategy
- **Regression tests** for the reproducer and the related nested forms in acceptance criterion 3. Each test checks three things:
  - **Structure:** the expression is mathematically equal to the expected value, using `simplify(diff) == 0` or an equality check after `doit()`.
  - **Round-trip:** `str()` output, re-parsed, is equal to the expected value.
  - **Numeric:** substituting concrete values matches hand-computed results. For example, with `a=1, b=1, c=2` the reproducer must give `4`. The buggy reading gives `0.25`.
- **Printer unit tests**, if the root cause is (b). Build the unevaluated expression directly, for example `Mul(x, Pow(Mul(1, Pow(y, -1), evaluate=False), -1), evaluate=False)`, and assert that the printed output is grouped correctly.
- **No-regression:** run the full existing LaTeX parser and printer test suites. Printer changes may alter the output of many doctests, so the whole doctest suite must pass.
- Coverage target: **unknown**. Follow the project's existing practice.

## Boundaries
- **Always:**
  - Find the root cause first. Check whether the expression tree is wrong or only its string form. Do this before changing any code.
  - Add regression tests that fail before the fix.
  - Keep `\frac` results mathematically faithful to the LaTeX.
- **Ask first:**
  - Changing the str printer's general parenthesization rules, since this affects output across all of SymPy.
  - Changing `\frac` from unevaluated to evaluated construction.
  - Modifying the ANTLR grammar or regenerating parser files.
  - Changing the printed format of existing, non-nested expressions.
- **Never:**
  - Special-case only the exact reproducer string.
  - Update existing expected outputs in tests or doctests to hide a behavior change without approval.
  - Add new dependencies.

## Success Criteria
- The reproducer gives an expression that equals `c*(a**3 + b)`, and its printed form round-trips to the same value.
- All nested-fraction cases in acceptance criterion 3 pass the structural, round-trip, and numeric checks.
- The existing LaTeX parser, printer, and doctest suites pass unchanged, or any changes are explicitly approved.
- The root cause, parser or printer, is documented in the PR or issue.

## Open Questions
1. **Where is the bug: parser or printer?** Is the returned expression tree actually wrong? Check this with `.args`/`srepr` and numeric substitution. Or is only `str()` dropping parentheses around an unevaluated denominator? This decides which component the fix belongs in.
2. If the cause is the printer, should the fix live in the general str printer, which also affects unevaluated expressions built outside `parse_latex`? Or should `parse_latex` build `\frac` differently, for example as a true division node, so that the printer issue never arises?
3. What exact printed form is wanted: `((a**3 + b)/c)/(1/(c**2))`, or something equivalent such as `((a**3 + b)/c)/(1/c**2)`? Are tests allowed to assert on exact strings, or only on equivalence?
4. Do other printers (`latex()`, `pretty()`, `repr`/`srepr`, code printers) mishandle the same unevaluated structure? Are they in scope?
5. Should `\frac` results stay unevaluated at all? Users may expect `parse_latex` to return `c*(a**3 + b)` directly.
6. Do other division-like LaTeX constructs have the same problem, and are they in scope? Examples are `a / \frac{b}{c}`, `\dfrac`, `\tfrac`, and `\frac` inside exponents.
7. Does the bug reproduce on the current development branch, and is any change being made to the LaTeX backend (for example an alternative non-ANTLR parser) that this fix needs to cover?
8. Repository details are unknown: test commands, file locations for the parser conversion code and the printer, and the required ANTLR runtime version.