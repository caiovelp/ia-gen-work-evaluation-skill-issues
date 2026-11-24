## Summary
`simplify()` does not simplify `sin`/`cos` expressions with `Rational` arguments. The same trigonometric form with real symbols simplifies to `cos(x - y)`, but with `Rational(1, 50)` and `Rational(1, 25)` the expression is returned unchanged. This happens whether the expression is built directly or from a `Matrix` dot product, and also when it is wrapped in `acos`.

## Steps to reproduce
1. Import SymPy: `from sympy import *`.
2. Check that the symbolic case works:
   - Define `x, y = symbols('x, y', real=True)`.
   - Build `r = sin(x)*sin(y) + cos(x)*cos(y)` and call `r.simplify()`.
3. Check that rational arithmetic works: `(Rational(1, 50) - Rational(1, 25)).simplify()`.
4. Build the same trigonometric expression with rational arguments in two ways:
   - Use the dot product of `Matrix([sin(Rational(1, 50)), cos(Rational(1, 50)), 0])` and `Matrix([sin(Rational(1, 25)), cos(Rational(1, 25)), 0])`.
   - Write it directly as `sin(Rational(1, 50))*sin(Rational(1, 25)) + cos(Rational(1, 50))*cos(Rational(1, 25))`.
5. Call `.simplify()` on each result.
6. Call `acos(r)` and `acos(r).simplify()` on the direct expression.

## Observed behavior
- Symbolic case: `sin(x)*sin(y) + cos(x)*cos(y)` simplifies to `cos(x - y)`.
- Rational case: `Rational(1, 50) - Rational(1, 25)` gives `-1/50`.
- Rational trig arguments: `simplify()` leaves the expression unchanged, both for the `Matrix` dot product and for the directly written expression: `sin(1/50)*sin(1/25) + cos(1/50)*cos(1/25)`.
- `acos(r).simplify()` is also unchanged: `acos(sin(1/50)*sin(1/25) + cos(1/50)*cos(1/25))`.

## Expected behavior
The reporter expects the rational-argument expression to simplify the same way the symbolic one does, i.e. to `cos(1/50 - 1/25)`. The `acos(...)` expression should then simplify accordingly.

## Stack trace / error output
Not provided in the original report. No exception is raised. The full printed output is:

Symbolic and rational cases (work):
```
sin(x)*sin(y) + cos(x)*cos(y)
cos(x - y)

-1/50
-1/50
```

Rational trig arguments (not simplified):
```
sin(1/50)*sin(1/25) + cos(1/50)*cos(1/25)
sin(1/50)*sin(1/25) + cos(1/50)*cos(1/25)

sin(1/50)*sin(1/25) + cos(1/50)*cos(1/25)
sin(1/50)*sin(1/25) + cos(1/50)*cos(1/25)

acos(sin(1/50)*sin(1/25) + cos(1/50)*cos(1/25))
acos(sin(1/50)*sin(1/25) + cos(1/50)*cos(1/25))
```

## Test case
Minimal test derived from the report's snippet:
```python
from sympy import sin, cos, Rational, symbols, simplify

def test_simplify_trig_rational_args():
    x, y = symbols('x, y', real=True)
    # works for symbols
    assert simplify(sin(x)*sin(y) + cos(x)*cos(y)) == cos(x - y)

    # same identity with Rational arguments
    a, b = Rational(1, 50), Rational(1, 25)
    r = sin(a)*sin(b) + cos(a)*cos(b)
    assert simplify(r) == cos(a - b)  # fails: r is returned unchanged
```

## Code example
```python
from sympy import *

x, y = symbols('x, y', real=True)
r = sin(x)*sin(y) + cos(x)*cos(y)
print(r)
print(r.simplify())
print()

r = Rational(1, 50) - Rational(1, 25)
print(r)
print(r.simplify())
print()

t1 = Matrix([sin(Rational(1, 50)), cos(Rational(1, 50)), 0])
t2 = Matrix([sin(Rational(1, 25)), cos(Rational(1, 25)), 0])
r = t1.dot(t2)
print(r)
print(r.simplify())
print()

r = sin(Rational(1, 50))*sin(Rational(1, 25)) + cos(Rational(1, 50))*cos(Rational(1, 25))
print(r)
print(r.simplify())
print()

print(acos(r))
print(acos(r).simplify())
print()
```

## Version and environment
- SymPy: latest cloned version (no exact version or commit given)
- Python 3 (exact version not given)
- OS: Windows