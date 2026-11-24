## Summary

`apart` gives a wrong result for a rational expression that has a symbolic coefficient `a`. `bug.apart(t)` returns `-a*t`. Substituting `a = 1` first and then calling `apart` returns `-t + 1/2 - 1/(2*(2*t - 1))`. The two results disagree, which suggests the decomposition with `a` present loses terms.

## Steps to reproduce

1. Define the symbols:
   - `a = symbols('a', real=True)`
   - `t = symbols('t', real=True, negative=False)`
2. Build the expression `bug = a * (-t + (-t + 1) * (2 * t - 1)) / (2 * t - 1)`.
3. Call `bug.subs(a, 1).apart()` and `bug.subs(a, 1).apart(t)`. Note the results.
4. Call `bug.apart(t)` and compare it with the results from step 3.

## Observed behavior

- `bug.subs(a, 1)` → `(-t + (-t + 1)*(2*t - 1))/(2*t - 1)`
- `bug.subs(a, 1).apart()` → `-t + 1/2 - 1/(2*(2*t - 1))`
- `bug.subs(a, 1).apart(t)` → `-t + 1/2 - 1/(2*(2*t - 1))`
- `bug.apart(t)` → `-a*t`

The result with `a` present is missing the `1/2` and `-1/(2*(2*t - 1))` terms. It is not consistent with the result for `a = 1`.

## Expected behavior

The report says only "Wrong result with apart". From the outputs shown, `bug.apart(t)` should agree with the `a = 1` result multiplied by `a`, that is, an expression equivalent to `a*(-t + 1/2 - 1/(2*(2*t - 1)))`. It should not be `-a*t`.

## Stack trace / error output

Not provided in the original report. No exception is raised; the result is mathematically wrong.

## Test case

A minimal test derived from the reproduction session in the report:

```python
from sympy import symbols, simplify

def test_apart_with_symbolic_coefficient():
    a = symbols('a', real=True)
    t = symbols('t', real=True, negative=False)
    bug = a * (-t + (-t + 1) * (2 * t - 1)) / (2 * t - 1)

    # Partial fraction decomposition must not change the value of the expression
    assert simplify(bug.apart(t) - bug) == 0

    # Result with a present must be consistent with the result for a = 1
    assert simplify(bug.apart(t).subs(a, 1) - bug.subs(a, 1).apart(t)) == 0
```

## Code example

```python
from sympy import symbols

a = symbols('a', real=True)
t = symbols('t', real=True, negative=False)
bug = a * (-t + (-t + 1) * (2 * t - 1)) / (2 * t - 1)

bug.subs(a, 1)            # (-t + (-t + 1)*(2*t - 1))/(2*t - 1)
bug.subs(a, 1).apart()    # -t + 1/2 - 1/(2*(2*t - 1))
bug.subs(a, 1).apart(t)   # -t + 1/2 - 1/(2*(2*t - 1))
bug.apart(t)              # -a*t   <-- wrong
```

## Version and environment

- SymPy 1.0
- Python 3.6.0 (Continuum Analytics, Inc. / Anaconda build, Dec 23 2016)
- IPython 5.1.0
- Operating system: not provided in the original report.