## Summary

Calling `sympify` (`sp.S`) on the string `'Point2D(Integer(1),Integer(2))'` inside a `with sp.evaluate(False):` block raises `ValueError: Imaginary coordinates are not permitted.` The same call works without the context manager, and also works when `evaluate=False` is passed directly to `sp.S`.

## Steps to reproduce

1. Import SymPy: `import sympy as sp`.
2. Enter the global evaluation-disabled context: `with sp.evaluate(False):`.
3. Inside that block, call `sp.S('Point2D(Integer(1),Integer(2))')`.
4. Observe that a `ValueError` is raised.

For comparison, run each of these outside the `with` block. Both work:
- `sp.S('Point2D(Integer(1),Integer(2))')`
- `sp.S('Point2D(Integer(1),Integer(2))', evaluate=False)`

## Observed behavior

Inside `with sp.evaluate(False):`, the call fails with:

```
ValueError: Imaginary coordinates are not permitted.
```

The coordinates `Integer(1)` and `Integer(2)` are real, yet the error says they are imaginary.

## Expected behavior

`sp.S('Point2D(Integer(1),Integer(2))')` inside `with sp.evaluate(False):` should not raise an error. It should behave the same way as the two working calls, in particular `sp.S('Point2D(Integer(1),Integer(2))', evaluate=False)`.

## Stack trace / error output

```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/avinash/.local/lib/python3.8/site-packages/sympy/core/sympify.py", line 472, in sympify
    expr = parse_expr(a, local_dict=locals, transformations=transformations, evaluate=evaluate)
  File "/home/avinash/.local/lib/python3.8/site-packages/sympy/parsing/sympy_parser.py", line 1026, in parse_expr
    raise e from ValueError(f"Error from parse_expr with transformed code: {code!r}")
  File "/home/avinash/.local/lib/python3.8/site-packages/sympy/parsing/sympy_parser.py", line 1017, in parse_expr
    rv = eval_expr(code, local_dict, global_dict)
  File "/home/avinash/.local/lib/python3.8/site-packages/sympy/parsing/sympy_parser.py", line 911, in eval_expr
    expr = eval(
  File "<string>", line 1, in <module>
  File "/home/avinash/.local/lib/python3.8/site-packages/sympy/geometry/point.py", line 912, in __new__
    args = Point(*args, **kwargs)
  File "/home/avinash/.local/lib/python3.8/site-packages/sympy/geometry/point.py", line 153, in __new__
    raise ValueError('Imaginary coordinates are not permitted.')
ValueError: Imaginary coordinates are not permitted.
```

## Test case

A minimal test case built from the reproduction in the report:

```python
import sympy as sp

def test_sympify_point2d_under_evaluate_false():
    # Both of these work according to the report
    sp.S('Point2D(Integer(1),Integer(2))')
    sp.S('Point2D(Integer(1),Integer(2))', evaluate=False)

    # This currently raises ValueError: Imaginary coordinates are not permitted.
    with sp.evaluate(False):
        sp.S('Point2D(Integer(1),Integer(2))')
```

## Code example

Failing:

```python
import sympy as sp
with sp.evaluate(False):
  sp.S('Point2D(Integer(1),Integer(2))')
```

Working:

```python
sp.S('Point2D(Integer(1),Integer(2))')
sp.S('Point2D(Integer(1),Integer(2))', evaluate=False)
```

## Version and environment

- Python 3.8, based on the paths in the traceback (`/home/avinash/.local/lib/python3.8/site-packages/sympy/...`).
- SymPy is installed in the user site-packages. The SymPy version is not provided in the original report.
- The operating system is not stated explicitly. The `/home/...` paths suggest a Unix-like system.