# Spec: Correct pretty-printing of `pi**(1/E)` (`pi**exp(-1)`)

## Objective

SymPy's pretty printer renders `pi**(1/E)` incorrectly. The user is on version 1.5.dev, merged from the project master.

**Observed (pretty printer):**
```
In [52]: pi**(1/E)
Out[52]:
-1___
╲╱ π
```
This reads as a "−1-th root of π", which is `π**(-1)`. That is mathematically wrong.

**Reference outputs (correct, per the issue):**
```
In [53]: print(latex(pi**(1/E)))
\pi^{e^{-1}}

In [54]: str(pi**(1/E))
Out[54]: 'pi**exp(-1)'
```

**Goal:** the pretty printer must render this expression in a form that is mathematically equivalent to `pi**exp(-1)`, consistent with what `latex` and `str` produce. No other expressions may regress.

**User:** SymPy users reading pretty-printed output in interactive sessions (IPython / terminal), with both Unicode and ASCII output.

**Acceptance criteria:**
- `pretty(pi**(1/E))` shows π raised to the exponent `e^(-1)`, or an equivalent unambiguous form. For example:
  ```
   ⎛ -1⎞
   ⎝ℯ  ⎠
  π
  ```
  The exact layout follows existing printer conventions and is an open question.
- The output must not use root notation unless the exponent really is a reciprocal suitable for root notation (see Open Questions).
- Existing root renderings such as `sqrt(x)`, `x**(1/3)` and `x**(1/n)` behave as they do today, unless a related bug is deliberately fixed and documented.

## Assumptions

1. The bug is in SymPy's pretty printer (`printing.pretty`, as the reporter mentions). The handling of `Pow` decides when to use root (radical) notation, and that decision misclassifies an exponent of `exp(-1)`.
2. Hypothesis, not verified: the root-notation check splits the exponent into numerator and denominator (e.g. via a `fraction`-style helper). It treats `exp(-1)` as `1/E`, and the root index is then printed incorrectly as `-1`. The root cause must be confirmed by reading the code.
3. `latex` and `str` are correct and are the reference for mathematical meaning. Their exact layout does not need to match.
4. Both Unicode and ASCII pretty modes are affected, and both must be fixed. Not verified for ASCII.
5. The fix should be minimal and local to the pretty printer. No changes to how `1/E` is evaluated or represented (`exp(-1)`).
6. Similar exponents may be affected by the same issue and should be covered by tests. Examples: `x**exp(-1)`, `x**(1/exp(1))`, and possibly `x**(1/pi)` or other symbolic reciprocals.

## Tech Stack

- Python, SymPy (reported version 1.5.dev, master at time of report).
- Python version: unknown.
- Pretty printing module: `printing.pretty`. Exact file paths are unknown; the repository is not visible.

## Commands

All unknown; the repository is not visible.
- Build: unknown. SymPy is pure Python, so likely no build step.
- Test: unknown. Likely the project's test runner targeted at the pretty-printing tests.
- Lint/code quality: unknown.
- Reproduce:
  ```python
  from sympy import pi, E, pretty, latex
  print(pretty(pi**(1/E)))
  print(pretty(pi**(1/E), use_unicode=False))
  print(latex(pi**(1/E)))
  print(str(pi**(1/E)))
  ```

## Project Structure

Unknown beyond the module name in the issue.
- `printing/pretty/`: pretty printer implementation. The exact file is unknown.
- Pretty-printer tests: location unknown, presumably a `tests/` directory alongside the module.

## Code Style

Unknown. Follow the existing conventions of the pretty printer module and its tests: match surrounding code, and write tests in the existing style of expected-string assertions for both Unicode and ASCII.

## Testing Strategy

- **Regression tests** in the existing pretty-printer test suite:
  - `pi**(1/E)` in Unicode and ASCII, with the exact expected output.
  - Related cases: `x**exp(-1)`, `x**(1/E)`, and other non-rational symbolic exponents of the form `1/<expr>`, where the expected behavior is decided in Open Questions.
- **Non-regression:** existing root-notation tests (`sqrt`, `x**(1/3)`, `x**(1/n)`, `x**Rational(2,3)`, negative exponents) must still pass.
- **Consistency check:** the rendered output must be mathematically equivalent to `str(expr)`.
- Coverage target: unknown, so follow project norms.

## Boundaries

- **Always:** add regression tests for both Unicode and ASCII output; run the full pretty-printing test suite; keep `latex` and `str` output unchanged.
- **Ask first:**
  - Changing which expressions get root notation in general, e.g. dropping root notation for `x**(1/n)`.
  - Modifying shared helpers (such as fraction-splitting utilities) used outside the pretty printer.
  - Changing the automatic evaluation of `1/E`.
- **Never:** change existing expected outputs in unrelated tests to make them pass; add new dependencies; alter `str`/`latex` printers as part of this fix.

## Success Criteria

- `pretty(pi**(1/E))` no longer shows a root with index `-1`. It shows π with exponent `e^(-1)`, or another agreed form equivalent to `pi**exp(-1)`.
- Unicode and ASCII modes are both correct and covered by new tests.
- All existing pretty-printer tests pass without modifying their expectations, unless a change is explicitly approved.
- The root cause is identified and documented in the PR description.

## Open Questions

1. **Desired rendering.** Should `pi**exp(-1)` be shown as a power with exponent `e^(-1)`? Or as a root `∜`-style with index `e` (i.e. `ℯ√π`), which is also mathematically valid? The `latex` output suggests the power form.
2. **Rule for root notation.** Should root notation be used only for rational exponents `1/n`, or also for symbolic reciprocals like `x**(1/n)` with symbol `n`? What happens with `x**(1/pi)`, which currently may or may not use roots? This defines the scope of the fix.
3. **Root cause.** Is the `-1` index caused by how `exp(-1)` is split into numerator and denominator, or by how the root index is printed? This needs code inspection.
4. **Other affected expressions.** Are other `exp(-k)` exponents affected, e.g. `x**exp(-2)` or `x**(2/E)`? Should they be included in this fix or tracked separately?
5. **Supported versions.** Is the fix targeted only at master, or also at a maintenance branch?
6. **Test commands and file locations** for the pretty-printing tests in this repository.