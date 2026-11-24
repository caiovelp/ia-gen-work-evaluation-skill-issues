## Summary

When printing a `Poly`, the `str` and `pretty` printers order monomials logically, from highest to lowest degree. The LaTeX printer (`latex`) does not. Its output uses a different order, so it does not match the other printers.

## Steps to reproduce

1. In an interactive session (SymPy, implied by the API used), declare the symbols: `var('a b c x')`.
2. Create a polynomial: `p = Poly([a, 1, b, 2, c, 3], x)`.
3. Print `p` with `str` (by evaluating `p`), with `pretty(p)` and with `latex(p)`.
4. Compare the order of the monomials in the three outputs.

## Observed behavior

`str` and `pretty` list the monomials from highest to lowest degree:

```
a*x**5 + x**4 + b*x**3 + 2*x**2 + c*x + 3
```

`latex` lists them in a different order. The terms with symbolic coefficients come first, followed by the remaining terms:

```
a x^{5} + b x^{3} + c x + x^{4} + 2 x^{2} + 3
```

## Expected behavior

`latex(p)` should use the same monomial order as `str` and `pretty`, from highest to lowest degree:

```
a x^{5} + x^{4} + b x^{3} + 2 x^{2} + c x + 3
```

## Stack trace / error output

Not provided in the original report. No error is raised; the issue is the order of terms in the output.

Full output from the original report:

```
>>> p
Poly(a*x**5 + x**4 + b*x**3 + 2*x**2 + c*x + 3, x, domain='ZZ[a,b,c]')
>>> pretty(p)
"Poly(a*x**5 + x**4 + b*x**3 + 2*x**2 + c*x + 3, x, domain='ZZ[a,b,c]')"
>>> latex(p)
'\\operatorname{Poly}{\\left( a x^{5} + b x^{3} + c x + x^{4} + 2 x^{2} + 3, x, domain=\\mathbb{Z}\\left[a, b, c\\right] \\right)}'
```

## Test case

Minimal test derived from the reproduction snippet. It checks only the order of the monomials in the LaTeX output:

```python
from sympy import var, Poly, latex

def test_latex_poly_monomial_order():
    a, b, c, x = var('a b c x')
    p = Poly([a, 1, b, 2, c, 3], x)
    s = latex(p)
    terms = ["a x^{5}", "x^{4}", "b x^{3}", "2 x^{2}", "c x", "3"]
    positions = [s.index(t) for t in terms]
    # Monomials should appear from highest to lowest degree, as in str/pretty
    assert positions == sorted(positions)
```

## Code example

```python
>>> var('a b c x')
>>> p = Poly([a, 1, b, 2, c, 3], x)
>>> p
Poly(a*x**5 + x**4 + b*x**3 + 2*x**2 + c*x + 3, x, domain='ZZ[a,b,c]')
>>> pretty(p)
"Poly(a*x**5 + x**4 + b*x**3 + 2*x**2 + c*x + 3, x, domain='ZZ[a,b,c]')"
>>> latex(p)
'\\operatorname{Poly}{\\left( a x^{5} + b x^{3} + c x + x^{4} + 2 x^{2} + 3, x, domain=\\mathbb{Z}\\left[a, b, c\\right] \\right)}'
```

## Version and environment

Not provided in the original report.