# Spec: Replace the Mignotte bound with the Knuth-Cohen bound in `sympy.polys.factortools`

## Objective

Replace the coefficient bound used by integer polynomial factorization in `sympy.polys.factortools` with a tighter one:

- **`dup_zz_mignotte_bound(f, K)`** (univariate) should compute the **Knuth-Cohen bound** instead of the classical Mignotte bound.
- **`dmp_zz_mignotte_bound(f, u, K)`** (multivariate) should be "replaced appropriately" with a Knuth-Cohen-based equivalent.

**Why.** The issue reports research with Prof. A. G. Akritas. It compared several bounds on dozens of polynomials of varying degree, density and coefficient range. The Knuth-Cohen bound was significantly better. Kalevi Suominen gave feedback and agreed with the proposal.

A tighter bound on the coefficients of factors means fewer lifting steps or a smaller modulus during factorization. That should mean less work.

**Users.**
- SymPy users who factor integer polynomials, indirectly.
- Code that calls these two functions directly.

**What success looks like.**
- The bounds are smaller than or equal to the current ones on typical inputs.
- They remain valid upper bounds.
- Every factorization result is unchanged.

## Assumptions

1. The new bound must still be a **valid upper bound** on the absolute values of the coefficients of any integer factor of `f`, as callers need it. Correctness takes priority over tightness.
2. The bound is consumed by the Zassenhaus/Hensel-lifting factorization path in `factortools`. Its exact callers are not shown in the issue.
3. The public names and signatures `dup_zz_mignotte_bound(f, K)` and `dmp_zz_mignotte_bound(f, u, K)` are kept, so callers do not change. Only the returned value changes.
4. The return value stays an element of the ground domain `K`, an integer type, as it is today.
5. The source is in the file backing the `sympy.polys.factortools` module. The exact path is inferred from the module name and has not been verified.
6. The Knuth-Cohen bound means the bound from Knuth (TAOCP vol. 2) as refined by Cohen (*A Course in Computational Algebraic Number Theory*). It combines:
   - binomial coefficients that depend on the degree,
   - the Euclidean (L2) norm of `f`,
   - the absolute value of its leading coefficient.

   The exact formula and its variant are not given in the issue (see Open Questions).
7. The comparison data mentioned in the issue is not available. Improvement will be checked with new tests and benchmarks rather than by reproducing that study.
8. No new third-party dependencies are needed. Binomial coefficients and integer square roots or ceilings are available inside SymPy.

## Tech Stack

- Python, SymPy (`sympy.polys` low-level dense polynomial representation: `dup_*` univariate, `dmp_*` multivariate).
- Versions: **unknown** (not stated in the issue).

## Commands

All unknown. No repository access, and the issue states none.

| Purpose | Command |
|---|---|
| Build | unknown (likely none for pure Python) |
| Test (targeted) | unknown — presumably the test module for `sympy.polys.factortools` |
| Test (full polys suite) | unknown |
| Lint / code quality | unknown |
| Benchmarks | unknown |

## Project Structure

Only what the issue implies:

```
sympy/polys/factortools  → module containing dup_zz_mignotte_bound / dmp_zz_mignotte_bound (exact file path unverified)
<tests for factortools>  → location unknown
<benchmarks>             → location unknown
```

## Code Style

- Follow the existing conventions of `sympy.polys.factortools`.
  - `dup_`/`dmp_` prefixes.
  - Arguments `(f, K)` / `(f, u, K)`.
  - Arithmetic is done through the domain object `K`.
- No existing code snippet is visible, so a concrete style example is **unknown**.
- Docstrings should name the bound (Knuth-Cohen) and cite the reference(s).

## Testing Strategy

- **Framework:** unknown (SymPy's existing test runner).
- **Unit tests for the univariate bound:**
  - Known polynomials with hand-computed expected Knuth-Cohen values.
  - Edge cases: degree 0, degree 1, a monic polynomial, a negative leading coefficient, a sparse polynomial, a polynomial with large coefficients.
- **Unit tests for the multivariate bound:** the same categories applied to multivariate inputs.
- **Validity (property) checks:** for polynomials with known factorizations, every coefficient of every true factor is at most the bound in absolute value.
- **Regression:** the existing factorization tests in `sympy.polys` must pass unchanged, since factorization output must not change.
- **Comparison:** on a sample set, the new bound is ≤ the old Mignotte bound, or any cases where it is larger are documented.
- **Coverage expectations:** unknown.

## Boundaries

- **Always:**
  - Keep the bound mathematically valid for its callers.
  - Keep the function signatures.
  - Run the polys factorization test suite.
  - Cite the source of the formula in the docstring.
- **Ask first:**
  - Renaming the functions or adding new public functions, e.g. keeping the old Mignotte bound under a new name.
  - Changing callers in the factorization algorithm.
  - Adding dependencies.
  - Changing the return type.
- **Never:**
  - Ship a bound that can underestimate factor coefficients.
  - Change factorization results.
  - Delete or weaken existing tests to make the change pass.

## Success Criteria

1. `dup_zz_mignotte_bound(f, K)` returns the Knuth-Cohen bound for `f`. It matches hand-computed values on the specified test polynomials.
2. `dmp_zz_mignotte_bound(f, u, K)` returns a Knuth-Cohen-based bound for multivariate `f`. The construction is documented and agreed (see Open Questions).
3. For every test polynomial with known factors, all factor coefficients are ≤ the returned bound in absolute value, for both functions.
4. On the comparison sample, the new bound is ≤ the old Mignotte bound for the cases claimed in the issue. Any exceptions are documented.
5. All existing `sympy.polys` factorization tests pass with no changes to expected outputs.
6. Docstrings describe the new bound and its reference.
7. Optional: a benchmark shows no slowdown in factorization, and ideally a speedup, on representative inputs.

## Open Questions

1. **Exact formula.** Which variant of the Knuth-Cohen bound is intended? Possibilities:
   - a bound on a single coefficient of a factor of degree *k*, maximized over coefficients and degrees;
   - the degree-halved form used for Zassenhaus.

   Can the authors provide the formula and reference used in the Akritas study?
2. **Rounding.** How should non-integer intermediate values be made into a domain integer? The Euclidean norm involves a square root, so ceiling, integer square root rounding up, or another method. The bound must remain valid after rounding.
3. **Multivariate generalization.** What does "replaced appropriately" mean for `dmp_zz_mignotte_bound`? Which norm should be used, and what degree measure: total degree, or the sum or max of degrees per variable? Is there a reference proving validity in the multivariate case?
4. **Caller assumptions.** Do callers depend on any specific property of the current Mignotte bound? For example: it is for factors of any degree versus only factors of degree ≤ n/2, or it includes the leading coefficient factor. Replacing it must not break that assumption.
5. **Keep the old bound?** Should the classical Mignotte bound stay available, e.g. as a separate function, for comparison or backward compatibility? Or is a straight replacement intended?
6. **Naming.** Should the functions keep the name `mignotte_bound` even though they no longer compute the Mignotte bound? Or should they be renamed or aliased, with deprecation?
7. **Evidence.** Can the comparison data or polynomial set from the study be shared, to use as test and benchmark fixtures?
8. **Commands and paths.** What are the exact test, lint and benchmark commands, and where are the tests and benchmark files for `factortools`?