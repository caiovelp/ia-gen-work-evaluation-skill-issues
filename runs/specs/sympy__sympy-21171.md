# Spec: LaTeX printing of a power of `SingularityFunction`

## Objective

LaTeX printing in SymPy crashes when an expression contains a `SingularityFunction` raised to a power. The issue reproduces this with `Beam.shear_force()` from `sympy.physics.continuum_mechanics`: the result contains such a power in a denominator, and Jupyter's LaTeX display hook fails with:

```
TypeError: _print_SingularityFunction() got an unexpected keyword argument 'exp'
```

**Root cause, from the traceback:**
- `LatexPrinter._print_Pow` in `sympy/printing/latex.py` handles a power whose base is a Function by calling `self._print(expr.base, exp=self._print(expr.exp))`.
- `_print_SingularityFunction` does not accept the `exp` keyword argument, so the call fails.

**Users:**
- SymPy users who display beam or continuum-mechanics results in Jupyter, IPython or any LaTeX output.
- Anyone who calls `latex()` on an expression containing `SingularityFunction(...)**n`.

**Goal:** `latex()` returns valid LaTeX for any expression containing a `SingularityFunction` raised to a power. Expressions that print correctly today must print exactly the same.

**Acceptance criteria:**
1. The issue's reproduction script, followed by `b2.shear_force()`, renders in Jupyter without an exception.
2. `latex(SingularityFunction(x, a, n)**p)` returns a string and does not raise. This holds for symbolic and numeric `p`, including negative powers such as `-1` and `-2`, which appear in denominators.
3. The output makes the exponent mathematically unambiguous. The exponent `p` must be visually distinct from the singularity order `n`.
4. The LaTeX for a bare `SingularityFunction(x, a, n)` is unchanged.

## Tech Stack

- Python and SymPy. The traceback shows Python 3.8 under `/usr/local/lib/python3.8/dist-packages`. The exact SymPy version is **unknown**.
- Component: `sympy/printing/latex.py`, which contains `LatexPrinter._print_Pow` and `LatexPrinter._print_SingularityFunction`.
- Also involved: `sympy/printing/printer.py` (dispatch through `Printer._print`) and `sympy/interactive/printing.py` (the Jupyter hook).
- Trigger: `sympy.physics.continuum_mechanics.Beam`.

## Commands

- Build: **unknown.** SymPy is pure Python, so there is likely no build step. Not confirmed.
- Test: **unknown.** The project's test runner and the exact invocation were not provided.
- Lint: **unknown.**
- Reproduce: run the issue's script in Jupyter, or call `latex(b2.shear_force())` in plain Python.

## Project Structure

Only these paths are known, all from the traceback:

```
sympy/printing/latex.py           → LatexPrinter, including _print_Pow and _print_SingularityFunction
sympy/printing/printer.py         → Printer._print dispatch (passes **kwargs to _print_<Class>)
sympy/interactive/printing.py     → Jupyter/IPython LaTeX display hook
sympy/physics/continuum_mechanics → Beam class (source of the triggering expression)
```

The test file location for the LaTeX printer is **unknown**. It is likely a `tests/` directory under `sympy/printing/`, but this is not confirmed.

## Code Style

- Follow the existing conventions in `sympy/printing/latex.py`.
- Other `_print_<Function>` methods in the same file apparently accept an optional `exp=None` argument, since `_print_Pow` relies on that pattern. A fix should match how those methods handle `exp`.
- No snippet is available from the issue, so no concrete style example is included.

## Testing Strategy

Add regression tests next to the existing LaTeX printer tests (exact location unknown). They should cover:

- `latex(SingularityFunction(x, a, n)**2)`
- `latex(SingularityFunction(x, a, n)**-1)`
- `latex(SingularityFunction(x, a, n)**p)` with a symbolic `p`
- A `Mul` or `Add` that has a powered `SingularityFunction` in the denominator, mirroring the beam case
- An unchanged-output assertion for bare `SingularityFunction(x, a, n)`
- Optionally, an end-to-end check that `latex(b2.shear_force())` from the issue scenario does not raise

Test level: unit tests on `latex()` output. A Jupyter or IPython test is not required, because the failure reproduces in `latex()` directly.

## Boundaries

- **Always:**
  - Keep existing LaTeX output for non-powered expressions byte-identical.
  - Add a regression test for the reported failure.
  - Run the printing test suite before committing.
- **Ask first:**
  - Changing the generic `Function` branch of `_print_Pow`, since that affects all function printers.
  - Changing the visual notation of `SingularityFunction`.
  - Fixing other printers (pretty, str, MathML) in the same change.
- **Never:**
  - Swallow the exception or fall back silently to a non-LaTeX representation.
  - Change `Beam` so that it avoids producing such expressions.
  - Remove or loosen existing tests.

## Assumptions

1. The bug lies only in the LaTeX printer: `_print_SingularityFunction` lacks the `exp` parameter. The `Beam` computation is mathematically correct.
2. The fix belongs in `_print_SingularityFunction`, by accepting an optional `exp` argument. The `_print_Pow` dispatch logic stays as it is.
3. A powered singularity function should print with the bracket wrapped in parentheses and then raised to the power, for example `\left(\langle x - a \rangle^{n}\right)^{p}`. Writing `\langle x - a \rangle^{n p}` or stacking superscripts would be ambiguous or wrong.
4. Other SymPy printers (str, pretty, MathML) are out of scope unless they are shown to fail.
5. The bug is present on the current main branch, not only in the reporter's version.

## Success Criteria

- [ ] The issue's reproduction followed by `b2.shear_force()` displays in Jupyter without error.
- [ ] `latex(SingularityFunction(x, a, n)**p)` succeeds for `p ∈ {2, -1, -2, symbol}` and produces parenthesized, unambiguous output.
- [ ] `latex(SingularityFunction(x, a, n))` output is unchanged.
- [ ] New regression tests fail before the fix and pass after it.
- [ ] The existing LaTeX printer test suite passes.

## Open Questions

1. What is the preferred LaTeX form for `SingularityFunction(x, a, n)**p`? Is `\left(\langle x - a \rangle^{n}\right)^{p}` acceptable?
2. Which SymPy version did the reporter use, and does the bug still reproduce on main?
3. Do other `_print_<Function>` methods in `latex.py` also lack the `exp` keyword? If so, should they be audited and fixed in this change or tracked separately?
4. Should the pretty printer and the MathML printer be checked for the same powered-`SingularityFunction` case?
5. Where do the LaTeX printer tests live, and what command runs them?
6. Is it expected that `Beam.shear_force()` produces a `SingularityFunction` raised to a power in a denominator? This could point to a separate simplification issue, which would be out of scope here.