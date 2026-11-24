## Summary

When `autowrap` is used with the Cython backend, the generated code is wrong if an array argument (for example a `MatrixSymbol`) is listed in `args` but does not appear in the wrapped expression. The C function is generated with a scalar parameter (`double x`) instead of a pointer (`double *x`). Calling the wrapped function with a NumPy array then raises a `TypeError`.

The problem does not occur when the expression depends on every argument. Supporting unused arguments matters when interfacing with external libraries, such as numerical integration routines, which require functions with a fixed signature whether or not each argument contributes to the output. The reporter believes the problem is in `codegen`.

## Steps to reproduce

1. Import `autowrap`, `MatrixSymbol` and NumPy.
2. Create a matrix symbol: `x = MatrixSymbol('x', 2, 1)`.
3. Define an expression that does not depend on `x`: `expr = 1.0`.
4. Wrap it with the Cython backend, passing `x` as an argument: `f = autowrap(expr, args=(x,), backend='cython')`.
5. Call the wrapped function with a NumPy array: `f(np.array([[1.0, 2.0]]))`.

## Observed behavior

The call fails with `TypeError: only size-1 arrays can be converted to Python scalars`.

The generated C function has the wrong signature. `x` is declared as `double` rather than `double *`:

```C
double autofunc(double x) {

   double autofunc_result;
   autofunc_result = 1.0;
   return autofunc_result;

}
```

If the expression depends on the argument (for example `expr = x[0,0]`), the wrapped function works correctly.

## Expected behavior

The call `f(np.array([[1.0, 2.0]]))` should return `1.0`. The array argument `x` should be generated as `double *` in the C function signature, even though it does not appear in the expression.

## Stack trace / error output

```
TypeError: only size-1 arrays can be converted to Python scalars
```

The original report does not include a full stack trace.

## Test case

Minimal test derived from the reproduction snippet:

```python
from sympy.utilities.autowrap import autowrap
from sympy import MatrixSymbol
import numpy as np

def test_cython_autowrap_unused_array_argument():
    x = MatrixSymbol('x', 2, 1)
    expr = 1.0
    f = autowrap(expr, args=(x,), backend='cython')
    assert f(np.array([[1.0, 2.0]])) == 1.0
```

## Code example

Failing example:

```python
from sympy.utilities.autowrap import autowrap
from sympy import MatrixSymbol
import numpy as np

x = MatrixSymbol('x', 2, 1)
expr = 1.0
f = autowrap(expr, args=(x,), backend='cython')

f(np.array([[1.0, 2.0]]))
```

Working variant, where the expression depends on `x`:

```python
from sympy.utilities.autowrap import autowrap
from sympy import MatrixSymbol
import numpy as np

x = MatrixSymbol('x', 2, 1)
# now output depends on x
expr = x[0,0]
f = autowrap(expr, args=(x,), backend='cython')

# returns 1.0 as expected, without failure
f(np.array([[1.0, 2.0]]))
```

## Version and environment

Not provided in the original report. The only details given are that the problem involves SymPy's `sympy.utilities.autowrap` with `backend='cython'` and NumPy.