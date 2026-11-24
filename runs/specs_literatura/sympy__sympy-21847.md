## Summary
`sympy.itermonomials` returns incomplete results when the optional `min_degrees` argument is used. It returns only the pure powers of each variable, such as `x1**3`, and leaves out mixed monomials, such as `x1*x2**2`, that have the same total degree. This contradicts the documented behavior.

## Steps to reproduce
1. Define three symbols: `x1, x2, x3 = sp.symbols('x1, x2, x3')`.
2. Call `sp.itermonomials([x1, x2, x3], 3, min_degrees=3)`.
3. Sort the result with `monomial_key('grlex', states)` and print it (see the code example below).
4. Optionally, repeat with `max_degrees` greater than `min_degrees`. The mixed monomials are still missing.

## Observed behavior
The output is:
```
[x3**3, x2**3, x1**3]
```
Only the pure cubes are returned. Mixed monomials of total degree 3, such as `x1*x2**2` and `x2*x3**2`, are missing. They are also missing when `max_degrees` is greater than `min_degrees`.

## Expected behavior
The result should contain every monomial whose total degree lies between `min_degrees` and `max_degrees`. With both set to 3, that includes mixed monomials such as `x1*x2**2` and `x2*x3**2`, not only `x1**3`, `x2**3` and `x3**3`.

The documentation states:
> A generator of all monomials `monom` is returned, such that either `min_degree <= total_degree(monom) <= max_degree`...

## Stack trace / error output
Not provided in the original report. No error is raised; the output is incorrect.

## Test case
Minimal test derived from the report's snippet:
```python
import sympy as sp

def test_itermonomials_min_degrees_includes_mixed_monomials():
    x1, x2, x3 = sp.symbols('x1, x2, x3')
    monomials = set(sp.itermonomials([x1, x2, x3], 3, min_degrees=3))
    # Pure powers (currently returned)
    assert {x1**3, x2**3, x3**3} <= monomials
    # Mixed monomials of total degree 3 (currently missing)
    assert x1*x2**2 in monomials
    assert x2*x3**2 in monomials
```

## Code example
```python
import sympy as sp
from sympy.polys.orderings import monomial_key

x1, x2, x3 = sp.symbols('x1, x2, x3')
states = [x1, x2, x3]
max_degrees = 3
min_degrees = 3
monomials = sorted(sp.itermonomials(states, max_degrees, min_degrees=min_degrees),
                   key=monomial_key('grlex', states))
print(monomials)
```

## Version and environment
Not provided in the original report.