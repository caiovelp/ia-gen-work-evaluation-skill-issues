# Spec: Fix `itermonomials` dropping mixed monomials when `min_degrees` is given

## Objective

`sympy.itermonomials(variables, max_degrees, min_degrees=...)` returns too few monomials when `min_degrees` is given as an integer (a total-degree bound). It returns only pure powers such as `x1**3` and leaves out mixed-term monomials such as `x1*x2**2`, even though their total degree falls within the requested range.

The documentation says:

> A generator of all monomials `monom` is returned, such that either `min_degree <= total_degree(monom) <= max_degree`...

**Users:** SymPy users who build polynomial bases, for example for state-space, sum-of-squares or regression models, and need every monomial within a total-degree window.

**Reproduction (from the issue):**

```python
import sympy as sp
from sympy.polys.orderings import monomial_key

x1, x2, x3 = sp.symbols('x1, x2, x3')
states = [x1, x2, x3]
monomials = sorted(sp.itermonomials(states, 3, min_degrees=3),
                   key=monomial_key('grlex', states))
print(monomials)
```

- **Actual:** `[x3**3, x2**3, x1**3]`
- **Expected:** all 10 monomials of total degree exactly 3 in `x1, x2, x3`. This includes `x1*x2**2`, `x2*x3**2`, `x1*x2*x3` and so on.
- The defect also appears when `max_degrees > min_degrees`. Mixed monomials are missing at every degree in the range.

**Success means:** in the total-degree mode, the output exactly matches the documented set: every monomial `m` with `min_degree <= total_degree(m) <= max_degree`, each appearing exactly once.

## Assumptions

1. The bug is limited to the **total-degree mode**, where `max_degrees` and `min_degrees` are integers. The per-variable mode, where both are lists, is not reported as broken and is out of scope. It must still keep its current behaviour.
2. The documented contract quoted above is correct, and the implementation is what is wrong. The documentation does not change, except perhaps to add an example.
3. "Total degree" means the sum of the exponents of all variables.
4. The default `min_degrees` (presumably `None`/`0`) must keep producing the same set of monomials as today, all monomials up to `max_degree`. The issue implies this path works correctly.
5. `itermonomials` accepts both commutative and non-commutative variables. The documented docstring covers both, so the fix must give correct results for both. For non-commutative variables, different orderings of the same factors are distinct monomials.
6. The order in which the generator yields monomials is not part of the contract. Callers sort the results themselves, as the issue example does. Tests should compare sets or sorted lists.
7. Each monomial must be yielded once, with no duplicates.
8. The return type stays the same: a generator or iterable of SymPy expressions, with `S.One` included when `min_degree == 0`.

## Tech Stack

- Python, SymPy. Exact supported Python and SymPy versions: **unknown**.
- Affected public API: `sympy.itermonomials`. The defining module is not stated in the issue, so its **path is unknown**. It is presumably in the `sympy.polys` package, since the example imports `sympy.polys.orderings.monomial_key`.

## Commands

All **unknown** from the issue. The project's actual build, test and lint commands must be confirmed.

```
Build: unknown
Test:  unknown (SymPy's test runner / pytest invocation for the polys monomials tests not given)
Lint:  unknown
```

## Project Structure

**Unknown.** The issue does not reveal where `itermonomials` or its tests live. Expected layout, to be confirmed:

```
<module defining itermonomials>      → implementation (path unknown)
<corresponding tests module>         → regression tests (path unknown)
```

## Code Style

Follow the existing SymPy conventions in the module that defines `itermonomials`. No snippet is available from the issue. Style is **unknown** beyond the public API usage shown in the reproduction.

## Testing Strategy

- **Level:** unit tests for `itermonomials` in the existing test module for monomials (location unknown).
- **Framework:** whatever SymPy's test suite uses (unknown; to be confirmed).
- **Regression tests to add:**
  1. The exact reproduction from the issue, with 3 variables, `max=3` and `min=3`. Expect exactly the 10 degree-3 monomials.
  2. `max_degrees > min_degrees`, for example 3 variables with `max=4` and `min=3`. Expect exactly the 10 + 15 = 25 monomials of degree 3 or 4.
  3. Edge cases:
     - `min == max == 0`, which yields `{1}`
     - `min == 0`, which yields the same set as omitting `min_degrees`
     - `min > max`, where the behaviour must match whatever is currently documented or defined (see Open Questions)
     - a single variable
     - two variables
  4. Non-commutative variables with an integer min degree. The output contains all words of each length in the range, for example 2 symbols with `min=max=2` give 4 distinct products.
  5. A cross-check that, for small cases, the result equals a brute-force filter: all monomials up to `max` (the default path) whose total degree is at least `min`.
  6. A guard that per-variable (list) mode outputs are unchanged.
  7. A no-duplicates check: `len(list(result)) == len(set(result))`.
- **Coverage:** every branch of the total-degree code path, both commutative and non-commutative, is exercised with a non-zero `min_degrees`.

## Boundaries

- **Always:**
  - Keep the public signature of `itermonomials` unchanged.
  - Add regression tests that reproduce the issue.
  - Run the existing polys test suite before finishing.
- **Ask first:**
  - Changing the order in which monomials are yielded, if any existing tests or doctests depend on it.
  - Changing behaviour for invalid inputs such as `min > max` or negative degrees.
  - Editing documentation beyond adding or correcting examples.
  - Touching the per-variable (list) mode.
- **Never:**
  - Change the documented contract to match the buggy output.
  - Remove or weaken existing tests.
  - Add new dependencies.

## Success Criteria

- [ ] The issue's example returns all 10 monomials of total degree 3 in `x1, x2, x3`.
- [ ] For `max_degrees=4, min_degrees=3` over 3 commutative variables, exactly 25 monomials are returned, with no duplicates.
- [ ] For any integer `0 <= min <= max` and commutative variables, the result set equals {monomials `m` : `min <= total_degree(m) <= max`}. The count equals the sum over d = min..max of C(n+d-1, d).
- [ ] For non-commutative variables, the result set equals all distinct products of length in [min, max].
- [ ] Calls without `min_degrees` produce the same set as before the change.
- [ ] Per-variable (list) mode produces the same results as before the change.
- [ ] All existing tests and doctests for `itermonomials` pass.

## Open Questions

1. Where do `itermonomials` and its tests live, and what are the exact test and lint commands?
2. What is the intended behaviour when `min_degrees > max_degrees` (empty result or error) and for negative degrees? Is it already defined somewhere?
3. Do any doctests or downstream callers rely on the current yield order? If so, must that order be kept for the default (no `min_degrees`) path?
4. Is the non-commutative variable path affected by the same bug? The issue only shows commutative symbols. It should be verified and covered either way.
5. Should the docstring gain an example with `min_degrees` to prevent regressions in the documentation as well?
6. Are mixed calls in scope, such as integer `max_degrees` with list `min_degrees` or the reverse? What is their expected behaviour?