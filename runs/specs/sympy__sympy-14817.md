# Spec: Robust Pretty Printing of `MatAdd` (no `sympify` of matrix arguments)

## Assumptions

1. The project is SymPy and the affected code is `_print_MatAdd` in `sympy/printing/pretty/pretty.py`, around line 828 as the traceback shows. Line numbers may have drifted since the report.
2. The bug comes from `S(item.args[0])` (that is, `sympify`) being applied to the first argument of each `MatAdd` term.
   - For a bare `MatrixSymbol`, `args[0]` is the name string (`'y*'`).
   - That string gets parsed as code and fails.
3. The intent of the check seems to be this: when a term is a negated matrix expression such as `-x`, i.e. `MatMul(-1, x)`, print it as `x - y` instead of `x + -y`. When that term is not the first term, the printer leaves out the explicit `+` separator.
4. Other printers (str, LaTeX, possibly others) may contain similar logic for `MatAdd`. The issue only reports the pretty printer.
5. `MatrixSymbol` names may legitimately contain characters that are not valid Python or SymPy syntax, such as `*`, spaces or punctuation. Printers must treat names as opaque strings.
6. Python 3 is in use (the traceback shows exception chaining).

## Objective

Fix `pprint` / `pretty` so it prints any `MatAdd` correctly, and so it never fails on how the arguments of individual terms are represented internally.

**User problem:** `pprint(MatrixSymbol('x', n, n) + MatrixSymbol('y*', n, n))` raises `SympifyError`. Pretty printing should never raise for a valid expression.

**Root cause, as reported:**
- The printer calls `sympify` on `item.args[0]` to decide whether a term is "negative".
- This assumes every term's first argument is a numeric-like coefficient. That assumption is wrong:
  - For `MatrixSymbol`, `args[0]` is the name string.
  - For other matrix expressions (`Transpose`, `Inverse`, `MatPow`, …), `args[0]` is an arbitrary sub-expression.

**Desired behavior:**
- Terms are classified as negative using the structure of the term, such as a `MatMul` whose scalar coefficient is negative. No string parsing is involved, and terms whose structure doesn't match are not misclassified.
- A negative term after the first is printed with a `-` separator, without a redundant `+`.
- All other terms are printed with ` + ` separators.

**User stories:**
- As a user, I can pretty-print a sum of matrix symbols whose names contain arbitrary characters, and no exception is raised.
- As a user, `pprint(x - y)` for matrix symbols shows `x - y`, not `x + -y`, and doesn't drop the operator.
- As a maintainer, I can read `_print_MatAdd` and understand which terms count as negative and why.

## Tech Stack

- Python (supported version range: **unknown**, but must match what SymPy currently supports)
- SymPy internals involved:
  - `sympy.printing.pretty.pretty.PrettyPrinter._print_MatAdd`
  - `sympy.matrices.expressions` (`MatAdd`, `MatMul`, `MatrixSymbol`)
  - `sympy.core.sympify`, which is the call to remove from this code path

## Commands

All of these are **unknown**; the repository is not visible. Likely candidates need confirming:

- Test (targeted): unknown, possibly `bin/test sympy/printing/pretty` or `pytest sympy/printing/pretty/tests/test_pretty.py`
- Test (full printing suite): unknown
- Lint / code quality: unknown, possibly `bin/test sympy/utilities/tests/test_code_quality.py`
- Build: not applicable / unknown

## Project Structure

Known only from the traceback:

```
sympy/printing/pretty/pretty.py   → PrettyPrinter, including _print_MatAdd (bug site)
sympy/printing/printer.py         → Printer dispatch (_print)
sympy/core/sympify.py             → sympify / S (should not be called here)
sympy/parsing/sympy_parser.py     → parse_expr (reached via sympify of strings)
```

The pretty printer tests are probably in `sympy/printing/pretty/tests/test_pretty.py`, but the location is **unknown**. The location of the `MatAdd` / `MatMul` / `MatrixSymbol` classes is also **unknown**; it is likely under `sympy/matrices/expressions/`.

## Code Style

Unknown. Follow the existing conventions in `pretty.py`. Constraints that come from the issue:

- Printers must not call `sympify` or `S(...)` on arguments taken out of expression objects. Operate on the expression tree directly.
- Negativity detection should state its structural assumption explicitly, e.g. "term is a `MatMul` with a negative scalar coefficient", and not rely on positional `args[0]`.

## Testing Strategy

- **Framework:** SymPy's existing test runner and test style (exact command unknown).
- **Location:** the existing pretty-printer test module (path unknown, see above).
- **Regression tests** (pretty, ASCII and Unicode where the module covers both):
  1. `MatrixSymbol('x', n, n) + MatrixSymbol('y*', n, n)` prints without raising and shows both names joined by `+`.
  2. `x + y` for ordinary matrix symbols is unchanged from current correct output.
  3. `x - y` (i.e. `MatAdd(x, MatMul(-1, y))`) prints as `x - y`.
  4. `-x + y`, where the negative term may come first depending on argument ordering, prints with a leading `-` and the correct separator for the other term.
  5. A term with a negative non-unit coefficient (e.g. `x - 2*y`) prints with `-` and the coefficient. Whether it shows `2⋅y` or another form follows the existing `MatMul` conventions.
  6. Terms whose first argument is not a scalar (e.g. `Transpose`, `Inverse`, `MatPow`, or a matrix symbol named like a negative number such as `'-1'`) are not treated as negative and don't raise.
- **Consistency check:** run the existing str and LaTeX printer tests for `MatAdd` and make sure they still pass. Whether to fix those printers as well is an open question.

## Boundaries

- **Always:**
  - Keep the fix confined to `MatAdd` printing logic.
  - Add regression tests for the reported case.
  - Run the full pretty-printer test module before finishing.
- **Ask first:**
  - Changing str, LaTeX, MathML or other printers in the same change.
  - Changing `MatAdd` / `MatMul` canonical argument ordering or construction.
  - Changing existing expected output in tests.
  - Adding any helper to the public API (e.g. a shared "could extract minus sign" utility for matrix expressions).
- **Never:**
  - Call `sympify`/`S` on strings or arbitrary args inside printers.
  - Restrict or validate `MatrixSymbol` names as a workaround.
  - Swallow `SympifyError` with a try/except as the fix.
  - Remove or weaken existing tests.

## Success Criteria

1. `pprint(MatrixSymbol('x', n, n) + MatrixSymbol('y*', n, n))` prints the sum and raises no exception.
2. No code path in `_print_MatAdd` calls `sympify`/`S` on term arguments.
3. For matrix symbols `x`, `y`, the output of `x - y` contains exactly one operator between the terms, a minus, and no `+ -`.
4. Output of `x + y` and of all existing `MatAdd` pretty-printing tests is unchanged, unless explicitly approved.
5. Terms are classified as negative only through an explicit structural check that is documented in a code comment or docstring. Matrix symbols whose names look like negative numbers are not classified as negative.
6. The new regression tests pass under the project's test runner, and the existing printing test suite passes.

## Open Questions

1. **Scope across printers:** do the str printer, LaTeX printer and others have the same `S(item.args[0])` pattern? Should they be fixed in this change, or tracked separately?
2. **Definition of "negative term":** which terms should get a `-` separator? Options:
   - Only `MatMul` with a negative numeric coefficient.
   - Also negative symbolic coefficients (e.g. `-a*X` where `a` is a scalar symbol).
   - Anything for which `could_extract_minus_sign()` holds, if that is available on matrix expressions.
3. **Leading negative term:** when the first term is negative, should it print as `-x + y`? And should `_print_MatAdd` print the first term's sign itself, or delegate that to the `MatMul` printer?
4. **Ordering:** does `MatAdd` canonicalize argument order so that the negative term can come first? This affects expected output in tests.
5. **Shared helper:** should negative-term detection be factored into a shared utility so the pretty, str and LaTeX printers behave the same way? If yes, where should it live?
6. **Test runner and command:** what exact commands should be used to run the targeted and full test suites in this repository?