## Summary

`sympify(...).simplify()` on an expression containing `ceiling` gives different results depending on whether `sympify` is called with `evaluate=False` or `evaluate=True`. In SymPy 1.5.1 both calls return `4*ceiling(x/4 - 3/4)`. In SymPy 1.6.2, the `evaluate=False` call returns `4*ceiling(x/4) - 3`, while the `evaluate=True` call still returns `4*ceiling(x/4 - 3/4)`.

## Steps to reproduce

1. Install SymPy 1.6.2.
2. In a Python/IPython session, run `sympy.sympify('4*ceiling(x/4 - 3/4)', evaluate=False).simplify()`.
3. Run `sympy.sympify('4*ceiling(x/4 - 3/4)', evaluate=True).simplify()`.
4. Compare the two results.
5. Optionally, repeat steps 2–4 with SymPy 1.5.1, where both results are the same.

## Observed behavior

In SymPy 1.6.2:
- With `evaluate=False`: `4*ceiling(x/4) - 3`
- With `evaluate=True`: `4*ceiling(x/4 - 3/4)`

The two results differ.

In SymPy 1.5.1, both calls return `4*ceiling(x/4 - 3/4)`.

## Expected behavior

`simplify()` should return the same result whether the expression was parsed with `evaluate=False` or `evaluate=True`. In SymPy 1.5.1, both calls returned `4*ceiling(x/4 - 3/4)`.

The reporter asks whether there is a way to keep the behavior consistent when `evaluate=False` is used during parsing.

## Stack trace / error output

No exception is raised. The output from the report, for SymPy 1.6.2:

```
In [16]: sympy.sympify('4*ceiling(x/4 - 3/4)', evaluate=False).simplify()
Out[16]: 4*ceiling(x/4) - 3

In [17]: sympy.sympify('4*ceiling(x/4 - 3/4)', evaluate=True).simplify()
Out[17]: 4*ceiling(x/4 - 3/4)
```

## Test case

This test is built from the snippet in the report. It fails on SymPy 1.6.2 and passes on SymPy 1.5.1, based on the outputs shown in the report.

```python
import sympy

def test_sympify_simplify_ceiling_consistent_with_evaluate():
    s = '4*ceiling(x/4 - 3/4)'
    unevaluated = sympy.sympify(s, evaluate=False).simplify()
    evaluated = sympy.sympify(s, evaluate=True).simplify()
    assert unevaluated == evaluated
```

## Code example

```python
import sympy

sympy.sympify('4*ceiling(x/4 - 3/4)', evaluate=False).simplify()
sympy.sympify('4*ceiling(x/4 - 3/4)', evaluate=True).simplify()
```

## Version and environment

- SymPy 1.6.2: the results are inconsistent.
- SymPy 1.5.1: the results are consistent.
- The report was run in an IPython session.
- The Python version and operating system are not provided in the original report.