## Summary
`lambdify` fails with a `SyntaxError` when it is given a `MatrixSymbol` whose name contains curly braces (e.g. `"{v}"`). This happens even with `dummify=True`. Curly braces in an ordinary scalar symbol name work, and a `MatrixSymbol` with a plain name works. Only the combination fails.

## Steps to reproduce
1. Import SymPy: `import sympy as sy`.
2. Create a scalar symbol with curly braces in its name: `curlyx = sy.symbols("{x}")`.
3. Create a `MatrixSymbol` with a plain name: `v = sy.MatrixSymbol("v", 2, 1)`.
4. Create a `MatrixSymbol` with curly braces in its name: `curlyv = sy.MatrixSymbol("{v}", 2, 1)`.
5. Call `sy.lambdify(curlyx, curlyx)`. This works.
6. Call `sy.lambdify(v, v)`. This works.
7. Call `sy.lambdify(curlyv, curlyv)`. This raises a `SyntaxError`.
8. Call `sy.lambdify(curlyv, curlyv, dummify=True)`. This also raises a `SyntaxError`.

## Observed behavior
- `sy.lambdify(curlyx, curlyx)` works (scalar symbol with curly braces).
- `sy.lambdify(v, v)` works (`MatrixSymbol` with a plain name).
- `sy.lambdify(curlyv, curlyv)` raises a `SyntaxError`.
- `sy.lambdify(curlyv, curlyv, dummify=True)` also raises a `SyntaxError`.

## Expected behavior
`lambdify` should handle a `MatrixSymbol` with curly braces in its name, as it already does for scalar symbols with such names. At minimum, `dummify=True` should let these names be lambdified without a `SyntaxError`.

## Stack trace / error output
The report only says that a `SyntaxError` is raised. The full traceback and error message are not provided in the original report.

## Test case
```python
import sympy as sy

def test_lambdify_curly_matrixsymbol():
    curlyx = sy.symbols("{x}")
    v = sy.MatrixSymbol("v", 2, 1)
    curlyv = sy.MatrixSymbol("{v}", 2, 1)

    # These currently work
    sy.lambdify(curlyx, curlyx)
    sy.lambdify(v, v)

    # These currently raise SyntaxError
    sy.lambdify(curlyv, curlyv)
    sy.lambdify(curlyv, curlyv, dummify=True)
```

## Code example
```python
import sympy as sy

curlyx = sy.symbols("{x}")
v = sy.MatrixSymbol("v", 2, 1)
curlyv = sy.MatrixSymbol("{v}", 2, 1)

# Work:
curlyScalarId = sy.lambdify(curlyx, curlyx)
vectorId = sy.lambdify(v, v)

# Raise SyntaxError:
curlyVectorId = sy.lambdify(curlyv, curlyv)
curlyVectorIdDummified = sy.lambdify(curlyv, curlyv, dummify=True)
```

## Version and environment
Not provided in the original report.