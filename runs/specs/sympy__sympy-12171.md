# Spec: Mathematica Code Printer — Correct Output for `Derivative` and Exponent-Form `Float`

## Assumptions

1. This is the SymPy project. "MCodePrinter" is SymPy's Mathematica code printer, reached through the public `mathematica_code(expr)` function. The file location is **unknown**; it is probably `sympy/printing/mathematica.py`, but this is unverified.
2. The scope check found one capability, so no capability map is needed. The capability is "the Mathematica printer emits valid Wolfram Language for two expression types." The two fixes share one consumer and one module.
3. The target is plain Mathematica / Wolfram Language input syntax:
   - `D[f, x]` is a derivative.
   - `D[f, {x, n}]` is an n-th derivative.
   - `D[f, x, y]` is a mixed partial derivative.
   - `m*^e` is scientific notation, meaning m × 10^e.
4. The issue's suggested patch is a starting point, not the agreed design:
   - `_print_Derivative` joins `expr.args` with `", "`. The internal argument shape of `Derivative` depends on the SymPy version and is **unknown**. It may be `(expr, t)` or `(expr, (t, 1))`. Joining the raw args could emit `(t, 1)` or `Tuple(t, 1)`, which is not valid Mathematica.
   - `_print_Float` uses `str(expr).replace('e', '*^')`. This depends on how SymPy's `str` formats a `Float`, which affects precision, digit count and exponent formatting. It also assumes no other `e` can appear in the string.
5. Function application already prints as `f[t]` in this printer. The issue's expected output `D[f[t],t]` implies this.
6. Exact precision or digit-count matching with Mathematica's own output is not required. Only syntactic validity and numeric value matter.
7. Commands, test framework details, the test file location and the code style are not visible in the issue. They are marked unknown below.

## Objective

Make the Mathematica code printer produce valid, semantically correct Wolfram Language for two cases it currently gets wrong.

1. **Derivatives.** For example, `Derivative(f(t), t)` currently prints as the SymPy-style `Derivative(f(t), t)`. It should print as `D[f[t], t]`.
2. **Floats in scientific notation.** For example, `1.0e-4` currently prints with an `e` exponent. Mathematica reads that as multiplication by the symbol `e`. It should print as `1.0*^-4` or an equivalent valid form.

**User:** someone who converts SymPy expressions to Mathematica source with `mathematica_code(...)` and pastes or evaluates the result in Mathematica.

**Success:** the printed strings evaluate in Mathematica to the same mathematical object as the SymPy input.

## Tech Stack

- Python, SymPy. The supported Python and SymPy versions are **unknown**.
- Component: the Mathematica code printer (`MCodePrinter`, `mathematica_code`). The file path is **unknown**.

## Commands

**Unknown.** The repository is not visible. These are placeholders to confirm:

- Test: **unknown**. The repository is assumed to use pytest or SymPy's own test runner on the Mathematica printer tests.
- Lint: **unknown**.
- Build: not applicable for a pure-Python change. This is unverified.

## Project Structure

**Unknown.** Expected, unverified:

- Printer source: a Mathematica printing module in SymPy's printing package.
- Tests: the existing test module for the Mathematica printer, alongside the other printing tests.

## Code Style

**Unknown.** Follow the conventions of the existing `_print_<ClassName>` methods in `MCodePrinter`. Use the printer's own helpers, such as `self._print` and `self.stringify`, rather than `str()`, so that nested sub-expressions are printed recursively with Mathematica syntax.

## Testing Strategy

- Add unit tests to the existing Mathematica printer test module (location **unknown**). Each test should assert exact output strings from `mathematica_code(...)`.
- Cover both the normal cases and the edge cases listed under Success Criteria.
- Verifying in a real Mathematica kernel is optional and manual. It is outside the scope of automated tests.

## Boundaries

- **Always:**
  - Print sub-expressions through the printer, using recursion and Mathematica syntax.
  - Add tests for every new output form.
  - Run the existing printer test suite.
- **Ask first:**
  - Changing the output of any expression type other than `Derivative` and `Float`.
  - Changing printer settings or the public `mathematica_code` signature.
  - Adding dependencies.
- **Never:**
  - Emit output that loses the numeric value of a `Float`.
  - Remove or loosen existing tests.
  - Change other printers (C, Fortran, LaTeX, etc.).

## Success Criteria

### Derivative

1. `mathematica_code(Derivative(f(t), t))` returns `D[f[t], t]`.
2. Higher-order derivatives use Mathematica's `{var, n}` form. Whether order 1 should also use `{t, 1}` is an open question.
   - `Derivative(f(t), t, t)`, also written `Derivative(f(t), (t, 2))`, returns `D[f[t], {t, 2}]`.
   - `D[f[t], t, t]` is an alternative, also valid form. The canonical choice is an open question.
3. A mixed partial `Derivative(f(x, y), x, y)` returns a valid `D[f[x, y], x, y]`.
4. The output never contains SymPy-internal forms such as `Tuple(`, `(t, 1)` or `Derivative(`.
5. Nested sub-expressions in the differentiated expression print in Mathematica syntax. For example, `Derivative(sin(t)*f(t), t)` prints its body as `Sin[t]*f[t]`.

### Float

6. `mathematica_code(Float('1.0e-4'))` returns a string containing `*^-4` with an equivalent mantissa, such as `1.0*^-4`. The exact mantissa digits are an open question.
7. Large exponents work: `Float('1.0e+20')` returns a valid `*^20` form, with no stray `+` issues. Mathematica's acceptance of `*^+20` is still to be confirmed.
8. Floats with no exponent are unchanged. For example, `Float(0.5)` returns `0.5` or the current output for that value.
9. Negative floats print correctly. For example, `Float('-2.5e-3')` returns `-2.5*^-3`.
10. The printed value has the same numeric value as the input, up to the precision the printer currently emits.

### General

11. All existing Mathematica printer tests still pass.

## Open Questions

1. **Canonical derivative form.**
   - Should first-order derivatives print as `D[f[t], t]` (assumed) or `D[f[t], {t, 1}]`?
   - Should repeated differentiation print as `{t, 2}` or as `t, t`?
2. **Alternative representation.** Should derivatives of applied undefined functions use `Derivative[1][f][t]` instead of `D[...]`? `Derivative[1][f][t]` is how Mathematica represents an unevaluated derivative internally. The issue asks for `D[...]`, but this is worth confirming.
3. **Float precision.**
   - Should the printer keep the `Float`'s full precision, for example `1.00000000000000*^-4` as `str` may produce?
   - Or should it emit minimal digits, such as `1.0*^-4`?
   - Should it emit Mathematica precision markers such as `` ` ``?
4. **Exponent threshold.** Should the printer only rewrite floats that `str()` already shows in exponent form? Or should it choose its own threshold for switching to scientific notation?
5. **Special float values.** How should `inf`, `-inf` and `nan` be handled, if any reach `_print_Float`? A naive `'e' → '*^'` replace would not cover them. They may already be separate SymPy classes; this is **unknown**.
6. **Version constraints.** Which SymPy and Python versions must be supported? This determines the internal argument shape of `Derivative` (variable/count tuples).
7. **Commands and paths.** What are the exact test command and the file locations for the printer and its tests?
8. **Related types.** Are related types in scope for this change, or tracked separately? Examples are `Subs`, `Integral` and `Rational` printing.