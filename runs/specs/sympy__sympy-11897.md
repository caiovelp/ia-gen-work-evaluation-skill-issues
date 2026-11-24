# Spec: LaTeX Printer Consistency with Pretty Printer (Products, Negative Exponents, Rational Coefficients)

## Objective

The issue reports that the LaTeX printer (`latex()`) gives output that differs in structure from the pretty printer (`pprint()`) for some expressions. The stated principle is:

> The LaTeX printer should always give the same output as the pretty printer, unless better output is possible from LaTeX.

**Users:** People who render symbolic expressions as LaTeX (documents, notebooks, MathJax) and expect it to show the same mathematical form they see in `pprint`/`str`.

**Reported inconsistencies:**

| # | Input | `latex()` (current) | `pprint()` (reference) | Problem |
|---|---|---|---|---|
| 1 | `exp(-x)*log(x)`, with `x` declared `positive=True` | `\frac{1}{e^{x}} \log{\left (x \right )}` | `ℯ^(-x)⋅log(x)` | LaTeX rewrites `e^{-x}` as `1/e^{x}`. The pretty printer keeps the negative exponent. |
| 2 | `1/(x + y)/2` | `\frac{1}{2 x + 2 y}` | `1 / (2⋅(x + y))` | LaTeX distributes the `2` into the sum in the denominator. The pretty printer keeps `2⋅(x + y)`. |

**Secondary concern from the reporter:** Symbol assumptions such as `positive=True` should not change how an expression prints.

**User stories:**
- As a user, when I call `latex(expr)`, I see the same structural form as `pprint(expr)`. This covers things like negative exponents vs. fractions, and factored vs. expanded denominators.
- As a user, adding or removing assumptions on a symbol does not change the printed form of an expression whose structure is otherwise identical.

**Acceptance criteria (to be confirmed):**
1. For `exp(-x)*log(x)`, `latex()` shows `e^{-x}` times the log term. It does not show `\frac{1}{e^{x}}`.
2. For `1/(x + y)/2`, `latex()` shows a fraction whose denominator is `2 \left(x + y\right)`. It does not show `2 x + 2 y`.
3. Cases 1 and 2 print the same with and without assumptions on `x`/`y`. This applies to `positive=True` at minimum.
4. LaTeX output that is currently correct and consistent stays unchanged.

## Assumptions

1. This is the SymPy project. `latex`, `pprint`, `var` and `exp`/`log` are SymPy's public API.
2. The pretty printer is the reference behavior. We change the LaTeX printer to match it, not the other way round.
3. The exact LaTeX strings in this spec, such as `e^{- x}` vs `e^{-x}` or `\left(x + y\right)`, describe intent only. The precise target strings must follow the LaTeX printer's existing conventions. The output shown in the issue (`\left (x \right )`) comes from an older version, and current formatting may differ.
4. The differences probably come from how the LaTeX printer splits a `Mul` into numerator and denominator. It seems to call a generic helper like `fraction`/`together`, which rewrites `exp(-x)` as `1/exp(x)` and distributes the coefficient. The pretty printer may not do this. This is unverified.
5. Assumption-dependent printing (case 1) most likely comes from automatic simplification that depends on assumptions. Examples are `exp(-x)` being treated as a power with negative exponent, or `Mul`/`Pow` canonicalization when `x` is positive. It is not intended printer logic. This is unverified.
6. In case 2, `1/(x + y)/2` is stored as `Mul(1/2, 1/(x+y))` and not as an expanded `Add`. The distribution happens at print time, not during construction. This is unverified.
7. "Better output is possible from LaTeX" lets LaTeX use real typesetting features such as `\frac` and proper sub/superscripts. It does not allow algebraic rewrites like turning `e^{-x}` into `1/e^{x}` or expanding denominators.
8. The scope is limited to the two reported patterns and their direct generalizations:
   - negative-exponent `exp` inside products
   - numeric coefficients multiplying a sum in the denominator

   This work is not a full audit of LaTeX/pretty consistency.

## Tech Stack

- Language: Python. The version is unknown.
- Library: SymPy. The version is unknown, and the issue's output suggests an older release.
- Components involved, by name only:
  - the LaTeX printer (`latex`)
  - the pretty printer (`pprint`)
  - the expression classes `exp`, `log`, `Mul`, `Pow`, `Add`
  - symbol assumptions (`positive=True`)
- Dependencies: none new expected.

## Commands

The commands are unknown because the repository is not visible. The following are needed:

- Build/install: *unknown*
- Run full test suite: *unknown*
- Run printing tests only: *unknown*
- Lint/code-quality checks: *unknown*
- Doctests: *unknown*

## Project Structure

Unknown because the repository is not visible. To be confirmed:

- Location of the LaTeX printer source: *unknown*
- Location of the pretty printer source: *unknown*
- Location of LaTeX printer tests: *unknown*
- Location of pretty printer tests: *unknown*

## Code Style

Unknown because no project source is visible. Follow the existing style of the LaTeX printer module. This includes naming, how `_print_<Class>` style methods are structured if that is the pattern, and how tests assert exact output strings.

## Testing Strategy

- **Framework:** *unknown*. Use whatever the project's printing tests already use.
- **Regression tests:** These are required and cover the issue's exact examples.
  - `latex(exp(-x)*log(x))` with plain `x` and with `x` declared `positive=True`. Both must produce the same expected string, which keeps `e^{-x}` as a power.
  - `latex(1/(x + y)/2)` produces a denominator `2 (x + y)` in the project's paren style, not `2 x + 2 y`.
- **Consistency checks:** For each new LaTeX test case, also assert or document the matching `pprint`/pretty output, so that the two printers are tested on the same inputs.
- **Assumption-invariance tests:** The same expression built with assumption-free symbols and with `positive=True` symbols must print identically in LaTeX.
- **Non-regression:** The existing LaTeX printer test suite must keep passing. Any changed expected strings in existing tests must be listed and justified as consistency fixes, not changed silently.
- **Coverage expectations:** *unknown*.

## Boundaries

- **Always:**
  - Add regression tests for both reported examples.
  - Keep `latex()` output structurally consistent with `pprint()` for the cases in scope.
  - Run the full printing test suite before proposing the change.
  - List every existing test expectation that changes.
- **Ask first:**
  - Changing the pretty printer's output.
  - Changing expression construction or canonicalization in core classes (`Mul`, `Pow`, `exp`) instead of the printer. This matters if the assumption-dependence comes from core behavior and not from printing.
  - Changing printer settings or defaults that users can see. Examples are fraction-style options and `fold_*` style settings, if they exist.
  - Widening scope beyond the two reported patterns.
- **Never:**
  - Delete or weaken existing printing tests just to make new behavior pass.
  - Make printing depend on symbol assumptions.
  - Introduce new dependencies.

## Success Criteria

1. `latex(exp(-x)*log(x))` contains `e^{-x}`, in the project's spacing convention, followed by the log term. It contains no `\frac{1}{e^{x}}`.
2. Criterion 1 holds whether `x` is plain or declared with `positive=True`, and both outputs are identical strings.
3. `latex(1/(x + y)/2)` produces a single fraction with numerator `1` and denominator `2 (x + y)` in the project's paren style. The output does not contain `2 x + 2 y`.
4. New regression tests for criteria 1–3 exist and pass.
5. All existing LaTeX and pretty printer tests pass. Any changed expected outputs are explicitly listed and justified.
6. `pprint` output for these expressions is unchanged.

## Open Questions

1. **Exact target strings:** What are the exact expected LaTeX strings, given the current printer's conventions? For example, `e^{- x}` vs `e^{-x}`, and `\left(x + y\right)` vs `\left (x + y \right )`.
2. **Root cause of assumption-dependence:** Does `positive=True` change the expression tree itself, for example through `exp(-x)` canonicalizing differently? Or does it only change a branch in the LaTeX printer? If it changes the tree, fixing it may need a core change and not a printer change. Is that in scope?
3. **Generalization:** Should the fix cover every case where the LaTeX printer splits a `Mul` into a fraction differently from the pretty printer? Or only the two reported patterns? Examples of other cases:
   - other functions with negative exponents
   - `x**-n` symbols
   - rational coefficients over products
4. **When is `\frac` "better"?** If the pretty printer shows `ℯ^(-x)` as a power but a user might prefer `\frac{1}{e^{x}}` in LaTeX, which form is correct? The issue suggests matching pretty, but should there be a printer setting to choose?
5. **Rational coefficients:** For `1/(x + y)/2`, should LaTeX print `\frac{1}{2 \left(x + y\right)}` to match pretty? Or is `\frac{1}{2} \cdot \frac{1}{x + y}`, or another form, acceptable?
6. **Existing test expectations:** If current tests encode the old behavior (`\frac{1}{e^{x}}`, expanded denominators), may those expectations be updated?
7. **Version/environment:** Which SymPy version and branch is targeted? Does the issue still reproduce on it?
8. **Commands and paths:** What are the build, test, and lint commands, and where are the LaTeX and pretty printer sources and tests? All of these are currently unknown.