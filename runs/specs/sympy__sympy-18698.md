# Spec: Consistent square-free decomposition in `sqf_list` / `sqf` for already-factored input

## Assumptions

1. This is the SymPy library. `sqf_list` and `sqf` are its public square-free factorization functions in the polys module. The issue does not name the project, but the API and output format match SymPy.
2. The typo `x*_2 - 5_x + 6` in the issue means `x**2 - 5*x + 6`, which equals `(x - 2)*(x - 3)`.
3. A square-free decomposition must have **at most one factor per multiplicity**. Each listed factor is the product of all irreducible factors with that multiplicity, so the multiplicities in the list are pairwise distinct.
4. The bug appears only when the input is passed as a product or power expression, not as an expanded polynomial. The second example in the issue (expanded input) is correct.
5. Root-cause hypothesis, not verified: when given a `Mul`, the expression-level code computes the square-free list of each top-level factor separately and concatenates the results. It never merges entries that share the same multiplicity. The domain-level algorithm, used on expanded input, already behaves correctly.
6. `factor_list` / `factor` are out of scope. They correctly return irreducible factors and must not change.
7. `sqf()` multiplies the factors back together, so its *value* is already mathematically correct. The visible inconsistency is in its *grouping* (e.g. `(x - 2)**3*(x - 3)**3` vs `(x**2 - 5*x + 6)**3`) and in `sqf_list`.

## Objective

Make `sqf_list` (and the structure of `sqf`) return a true square-free decomposition no matter how the input is written. Expanded and factored forms of the same polynomial must give equivalent results.

**User:** anyone calling `sqf_list`/`sqf` who expects the standard mathematical definition: `f = c · ∏ fᵢ^i`, where each `fᵢ` is square-free, the `fᵢ` are pairwise coprime, and there is one `fᵢ` per multiplicity `i`.

**Acceptance criteria (from the issue):**

- `sqf_list((x**2 + 1)*(x - 1)**2*(x - 2)**3*(x - 3)**3)` returns `(1, [(x**2 + 1, 1), (x - 1, 2), (x**2 - 5*x + 6, 3)])`, up to the library's canonical ordering.
- `sqf_list(x**5 - 2*x**4 - 2*x**3 + 4*x**2 + x - 2)` continues to return `(1, [(x - 2, 1), (x**2 - 1, 2)])`.
- `sqf_list(f)` and `sqf_list(expand(f))` return the same factors and multiplicities.

## Tech Stack

- Python, SymPy polys module. Exact version and branch: **unknown**.
- Affected public API: `sqf_list`, `sqf`, and possibly `Poly.sqf_list` and the expression-level helpers behind them. Internal function and file names: **unknown** (repository not visible).

## Commands

- Build: **unknown** (pure-Python library; likely none)
- Test: **unknown**. Probably the project's pytest-based runner on the polys test suite. The exact command and path must be confirmed.
- Lint: **unknown**
- Dev: **unknown**

## Project Structure

- Source location of `sqf_list` / `sqf`: **unknown** (expected somewhere in the polys package).
- Test location: **unknown** (expected alongside existing `sqf_list` tests in the polys test suite).
- Docs: **unknown**. Docstring examples for `sqf_list`/`sqf` may need their expected outputs checked.

## Code Style

- Follow the existing conventions of the surrounding polys code. There is no snippet available from the issue.
- Use the public API calls from the issue for illustration and as the basis for regression tests:

  ```python
  sqf_list((x**2 + 1)*(x - 1)**2*(x - 2)**3*(x - 3)**3)
  # expected: (1, [(x**2 + 1, 1), (x - 1, 2), (x**2 - 5*x + 6, 3)])
  ```

## Testing Strategy

- **Framework:** the project's existing test framework (assumed pytest-compatible; **unknown**).
- **Regression tests** (unit level, next to existing `sqf_list` tests):
  1. The failing example from the issue, in factored form, gives one factor of multiplicity 3.
  2. The correct example from the issue still passes unchanged.
  3. Equivalence: for several polynomials, `sqf_list(f) == sqf_list(expand(f))`, comparing factors as polynomials, not as raw expression forms.
  4. `sqf` of the factored input groups same-multiplicity factors, e.g. `(x**2 - 5*x + 6)**3`. Its value must equal the input when expanded.
- **Edge cases to cover:**
  - repeated identical factors written separately, e.g. `(x - 1)**2 * (x - 1)`
  - factors whose multiplicities only coincide after combination
  - a constant/content factor and a negative leading coefficient
  - multivariate input
  - rational functions (numerator/denominator)
  - non-polynomial or symbolic-exponent factors, if currently supported
  - the `frac` / `polys` / `include`-style options, if they exist
- **Non-regression:** the full existing polys test suite passes, and `factor_list` outputs are unchanged.
- Coverage target: **unknown**. At minimum, every new code path must be exercised by a test.

## Boundaries

- **Always:**
  - Keep `sqf_list` returning a valid square-free decomposition: square-free, pairwise coprime factors with distinct multiplicities.
  - Add regression tests reproducing the issue.
  - Run the polys test suite before committing.
  - Keep the return type and shape unchanged: `(coeff, [(factor, multiplicity), ...])`.
- **Ask first:**
  - Changing the ordering of returned factors.
  - Changing behavior of `Poly.sqf_list` / domain-level functions, or of `factor_list`.
  - Updating existing tests or docstrings whose expected output encodes the current (split) behavior.
  - Any public API or option change.
- **Never:**
  - Change `factor` / `factor_list` semantics.
  - Delete or weaken existing failing tests to make the suite pass.
  - Return factors whose product differs from the input.

## Success Criteria

1. `sqf_list((x**2 + 1)*(x - 1)**2*(x - 2)**3*(x - 3)**3)` yields exactly three factors, with multiplicities `{1, 2, 3}`. The multiplicity-3 factor equals `x**2 - 5*x + 6` as a polynomial.
2. For every tested `f`, `sqf_list(f)` and `sqf_list(expand(f))` agree on factors (as polynomials) and multiplicities.
3. In every `sqf_list` result, no two entries share a multiplicity.
4. `sqf(f)` expands to `f`, and same-multiplicity factors appear as a single base.
5. Existing polys tests pass, apart from tests explicitly approved for update because they encoded the buggy behavior.
6. `factor_list` output is unchanged for all existing tests.

## Open Questions

1. Should the fix be done by merging same-multiplicity entries in the expression-level path, or by converting the whole expression to a single `Poly` first? The second option changes behavior for non-polynomial and symbolic inputs.
2. What canonical ordering of factors is expected? The issue's example order (`(x - 3, 3), (x - 2, 3)`) suggests the current order is not strictly sorted.
3. Should the merged factor be returned expanded (`x**2 - 5*x + 6`) or as a product (`(x - 2)*(x - 3)`)? The issue implies expanded.
4. How should rational expressions be handled? Should numerator and denominator factors with equal multiplicity be combined separately (as numerator and denominator), or kept as distinct entries with negative multiplicities?
5. How should factors that are not polynomial in the generators (e.g. `exp(x)`, symbolic exponents `(x - 1)**n`) be treated when merging?
6. Are there existing tests or docstrings asserting the current split output that are considered correct and must be preserved?
7. Should `Poly.sqf_list` also be checked for the same inconsistency, or is the issue limited to the expression-level functions?
8. Which SymPy version/branch is the target, and what are the exact test command and test file location?