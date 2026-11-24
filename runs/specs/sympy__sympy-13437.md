# Spec: `bell(oo)` evaluates to `oo`

## Objective

`bell(n).limit(n, oo)` currently returns `bell(oo)` unevaluated. It should return `oo`.

The Bell numbers B(n) count the partitions of a set of size n. They are positive integers that grow strictly and without bound for n ≥ 1, so B(n) → ∞ as n → ∞. Two outcomes are wanted:

1. `bell(oo)` evaluates directly to `oo`.
2. As a result, `bell(n).limit(n, oo)` returns `oo`.

The issue says this follows recent fixes to the same limit for the Fibonacci and Lucas numbers. Those fixes are the reference pattern.

**Users:** SymPy users who compute limits or evaluate combinatorial functions at infinity.

**User story:** As a SymPy user, when I evaluate `bell(n).limit(n, oo)`, I get `oo` instead of an unevaluated `bell(oo)`.

## Assumptions

1. The Fibonacci and Lucas fixes made `fibonacci(oo)` and `lucas(oo)` evaluate to `oo` inside the function's own evaluation logic, and did not change the limit algorithm. This is unverified; the issue does not show those changes.
2. The right place for the fix is `bell`'s own automatic evaluation, so that `bell(oo)` itself returns `oo`. The limit result then follows. The issue's wording ("`bell(oo)` should be able to be evaluated") supports this.
3. Only the single-argument form `bell(n)` is in scope. The multi-argument forms are out of scope unless the Open Questions decide otherwise. These are the Bell polynomial `bell(n, x)` and the incomplete Bell polynomial `bell(n, k, symbols)`.
4. `bell(-oo)`, `bell(zoo)`, and other non-finite arguments are out of scope. They keep their current behavior.
5. Existing behavior for integer, symbolic, and other finite arguments must stay the same.
6. The issue reporter intends to implement the fix. This spec only defines what is to be built.

## Tech Stack

- Python, SymPy (this repository).
- Exact SymPy version and supported Python versions: **unknown**, as the issue does not state them.

## Commands

Not visible in the issue. All of these are **unknown**:

- Build: unknown (pure-Python package; likely none needed)
- Test: unknown. The project's test runner and the exact invocation for the combinatorial-functions and limits test modules are not given.
- Lint / code-quality checks: unknown
- Dev: unknown

## Project Structure

Not visible in the issue. All of these are **unknown**:

- Location of the `bell` function definition: unknown. It presumably sits alongside `fibonacci` and `lucas` in SymPy's combinatorial-numbers functions module.
- Location of the existing tests for `bell`, `fibonacci`, and `lucas`: unknown.
- Location of the limit tests: unknown.

## Code Style

- Follow the existing conventions of the module that defines `bell`.
- Mirror the Fibonacci/Lucas fix as closely as possible, so the three functions handle infinity the same way.
- No code snippet is available from the issue. The concrete style example is **unknown**.

## Testing Strategy

- **Framework:** unknown. Use SymPy's existing test framework and conventions.
- **Unit tests** go next to the existing `bell` tests. They should cover:
  - `bell(oo)` returns `oo`.
  - `bell(n).limit(n, oo)` returns `oo`, with `n = symbols('n')` as in the issue.
  - Regression: existing finite-argument results are unchanged, e.g. `bell(0)`, `bell(5)`, symbolic `bell(n)` staying unevaluated, and the polynomial forms.
- If the Fibonacci/Lucas fixes added limit tests, add a matching test for `bell` in the same place, for consistency.
- **Coverage expectation:** every new code path, meaning the `oo` branch, is exercised by at least one test.

## Boundaries

- **Always:**
  - Run the existing `bell` tests and limit tests before submitting.
  - Add regression tests for the new behavior.
  - Keep the handling consistent with `fibonacci` and `lucas`.
- **Ask first:**
  - Changing the general limit algorithm instead of `bell`'s own evaluation.
  - Defining behavior for the polynomial or incomplete forms at infinity.
  - Changing behavior for `-oo` or complex infinity.
  - Changing `bell`'s public signature.
- **Never:**
  - Change results for finite arguments.
  - Remove or weaken existing tests.
  - Add new dependencies.

## Success Criteria

1. `bell(oo)` returns `oo`, i.e. `S.Infinity`.
2. `bell(n).limit(n, oo)` returns `oo` for `n = symbols('n')`, matching the issue's reproduction.
3. All existing tests for `bell`, the other combinatorial number functions, and limits still pass.
4. New tests for criteria 1 and 2 exist and pass.
5. Infinity is handled the same way for `bell`, `fibonacci`, and `lucas`.

## Open Questions

1. Should the Bell polynomial `bell(oo, x)` also be evaluated? Its limit depends on `x` (for example, at `x = 0` the value is 0 for n ≥ 1), so a blanket `oo` would be wrong.
2. Should the incomplete Bell polynomial form with infinite `n` be handled at all?
3. Should `bell(-oo)` or `bell(zoo)` raise an error, return `nan`, or stay unevaluated? Or is that left alone?
4. Where exactly were the Fibonacci and Lucas fixes made: in each function's evaluation, or in the limit machinery? They are referenced but not linked, and this fix should mirror them.
5. What are the exact test commands and test file locations for the `bell` and limit tests?
6. Should other unbounded combinatorial sequences with the same problem be fixed together, or tracked separately? Examples might include Catalan numbers or partition numbers. This spec assumes they are tracked separately.