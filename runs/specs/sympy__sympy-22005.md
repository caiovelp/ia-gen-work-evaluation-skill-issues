# Spec: Detect Positive-Dimensional (Infinite-Solution) Systems in `solve_poly_system`

## Objective

`solve_poly_system` only supports **zero-dimensional** polynomial systems, meaning systems with a finite number of solutions. When given a system with infinitely many solutions, it should raise `NotImplementedError`. It does this for some inputs but not others:

```python
>>> solve_poly_system((x - 1,), x, y)
NotImplementedError: only zero-dimensional systems supported (finite number of solutions)   # correct

>>> solve_poly_system((y - 1,), x, y)
[(1,)]                                                                                       # WRONG
```

In the second case `x` is unconstrained, so the solution set is infinite. The function silently returns a wrong, truncated answer: a 1-tuple even though two generators were requested.

**Who is affected:** SymPy users, and other SymPy code such as `solve`, that call `solve_poly_system` or `_solve_reduced_system`.

**What success looks like:**
- Every positive-dimensional input raises `NotImplementedError`. This holds no matter which generator is left free or where it sits in the generator order.
- Every zero-dimensional input is solved exactly as it is today.

### Acceptance criteria
1. `solve_poly_system((x - 1,), x, y)` raises `NotImplementedError` (behaviour unchanged).
2. `solve_poly_system((y - 1,), x, y)` raises `NotImplementedError`.
3. `solve_poly_system(Poly(x - 1, x, y), (x, y))` raises `NotImplementedError`.
4. `solve_poly_system(Poly(y - 1, x, y), (x, y))` raises `NotImplementedError`.
5. All existing passing tests in `sympy/solvers/tests/test_polysys.py` still pass. This includes the multivariate zero-dimensional systems such as `[x*y - 2*y, 2*y**2 - x**2]` solved over `x, y`.
6. When the function does return solutions, every solution tuple has length equal to `len(gens)`.

## Assumptions

1. The error type stays `NotImplementedError`. The message stays the existing "only zero-dimensional systems supported (finite number of solutions)". No new exception class is introduced.
2. The defect is in `_solve_reduced_system` in `sympy/solvers/polysys.py`. This comes from the diff in the issue. The bug is that the branch picking a univariate polynomial (`if len(univariate) == 1:`) does not check whether the system is zero-dimensional when other generators remain unconstrained.
3. Raising on positive-dimensional systems is the intended contract. Returning a parametric solution is out of scope.
4. The diff in the issue is a **candidate** fix, not an approved one. It changes the condition to `len(univariate) == 1 and len(gens) == 1`. Its correctness must be verified against the existing multivariate tests (see Open Questions).
5. Other entry points that go through this code path (`solve`, `solve_generic`, `solve_biquadratic`) should benefit from the fix. Their public behaviour should not change for zero-dimensional inputs.

## Tech Stack

- Python, as part of the SymPy codebase. The supported Python version and SymPy version/branch are **unknown**.
- Relevant internals: Groebner basis computation and `Poly`, both used by `polysys.py`. Exact functions beyond those visible in the diff are **unknown**.

## Commands

The exact commands are **unknown** because they cannot be seen from the issue. To be confirmed:
- Run targeted tests: **unknown** (likely a pytest or `bin/test` invocation on `sympy/solvers/tests/test_polysys.py`; needs confirmation)
- Run the wider solvers test suite: **unknown**
- Lint/style check: **unknown**
- Doctests for `polysys.py`: **unknown**

## Project Structure

Only these paths are known from the issue:

```
sympy/solvers/polysys.py               → solve_poly_system, _solve_reduced_system (code under change)
sympy/solvers/tests/test_polysys.py    → test_solve_poly_system, test_solve_biquadratic, ...
```

Everything else about the layout is **unknown**.

## Code Style

These conventions can be seen in the issue; everything else should follow existing SymPy conventions, which are **unknown** beyond this:
- Error messages are built with `filldedent('''...''')`.
- Tests use `raises(ExcType, lambda: ...)` inside the existing `test_*` functions.

```python
raises(NotImplementedError, lambda: solve_poly_system(
    Poly(y - 1, x, y), (x, y)))
```

## Testing Strategy

- **Framework:** SymPy's test suite, using the `raises` helper. The exact runner is **unknown**.
- **Location:** `sympy/solvers/tests/test_polysys.py`, extending `test_solve_poly_system`.
- **Required regression tests:**
  - Acceptance criteria 1–4, with both tuple-of-expressions input and `Poly` input.
  - Free-generator variants: free generator first, free generator last, and more than two generators (e.g. `(z - 1,)` over `x, y, z`).
  - Systems where some equations are multivariate but one generator is still free (e.g. `(x*y - 1, )` style cases). The intended outcome for each case must be confirmed.
- **Non-regression:** all existing tests in `test_polysys.py` must pass. The multivariate zero-dimensional cases are the key guard against the candidate fix's `len(gens) == 1` condition. Callers in other solver test modules should also be run; the module list is **unknown**.
- **Coverage expectation:** **unknown**. At minimum, each new condition branch should be exercised.

## Boundaries

- **Always:**
  - Add a failing regression test for the `(y - 1,)` case before changing code.
  - Run the full `test_polysys.py` and related solver tests.
  - Keep the existing exception type and message.
- **Ask first:**
  - Changing the public signature or return format of `solve_poly_system`.
  - Changing the error message text.
  - Altering behaviour of `solve()` for inputs other than positive-dimensional polynomial systems.
  - Adopting the issue's diff as-is if it breaks any existing test.
- **Never:**
  - Delete or weaken existing tests to make the change pass.
  - Return partial-length solution tuples.
  - Add parametric or infinite-solution support as part of this change.

## Success Criteria

- [ ] Acceptance criteria 1–6 hold and are covered by tests.
- [ ] No existing test in `sympy/solvers/tests/test_polysys.py` regresses.
- [ ] No regressions in other test modules that call `solve_poly_system` (module list **unknown**).
- [ ] The detection works no matter which generator is unconstrained and how many generators there are.

## Open Questions

1. **Is the proposed condition `len(univariate) == 1 and len(gens) == 1` correct?**
   - `_solve_reduced_system` recurses with fewer generators. For a normal zero-dimensional multivariate system (e.g. `[x - y, y - 1]` over `x, y`), the top-level call has `len(gens) == 2` and exactly one univariate polynomial.
   - That suggests the candidate condition might wrongly raise for valid systems.
   - Should detection instead be based on a dimensionality check? One option is comparing the number of basis elements to the number of generators: a lex Groebner basis of a zero-dimensional ideal has at least `len(gens)` elements. Another option is a check that every generator appears constrained.
   - This needs a decision and test verification before implementation.
2. Should the check run once at the top level (`entry=True`), or at every recursion level?
3. Is there a cheaper or canonical "is zero-dimensional" helper already available in SymPy's polys module that should be reused? This is **unknown**.
4. Should `solve()` keep raising `NotImplementedError` for these inputs, or catch it and fall back to another strategy (e.g. a parametric answer)? This determines whether higher-level behaviour changes are expected.
5. Should the function behave the same for symbolic or domain-coefficient variations of these inputs (e.g. `(y - a,)` over `x, y`)?
6. Which commands, Python versions, and SymPy branch apply to this change? See the **unknown** entries under Commands.