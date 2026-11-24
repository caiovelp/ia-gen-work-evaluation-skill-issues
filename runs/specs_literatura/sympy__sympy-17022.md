## Summary

`lambdify` mistranslates expressions that contain an identity matrix. The generated code prints `Identity(n)` as `I`, and the lambdified function's globals bind `I` to Python's complex number `1j`. As a result, adding `Identity(n)` to a matrix argument adds `1j` to every element instead of adding the identity matrix.

## Steps to reproduce

1. Import NumPy and SymPy (`symbols`, `MatrixSymbol`, `Identity`, `lambdify`).
2. Define an integer symbol `n = symbols('n', integer=True)`.
3. Define a square matrix symbol `A = MatrixSymbol("A", n, n)`.
4. Create a NumPy array `a = np.array([[1, 2], [3, 4]])`.
5. Lambdify the expression `A + Identity(n)` with `A` as the argument: `f = lambdify(A, A + Identity(n))`.
6. Call `f(a)` and look at the result.
7. Optionally, inspect the generated source with `inspect.getsource(f)` and the value of `f.__globals__['I']`.

## Observed behavior

`f(a)` returns `1j` added to every element:

```python
array([[1.+1.j, 2.+1.j],
       [3.+1.j, 4.+1.j]])
```

The generated source shows that `Identity(n)` was printed as `I`:

```python
def _lambdifygenerated(A):
    return (I + A)
```

In the function's globals, `I` is the complex number `1j`:

```python
>>> f.__globals__['I']
1j
```

## Expected behavior

`f(a)` should add the identity matrix to the array and return:

```python
array([[2, 2], [3, 5]])
```

The reporter also states that the code printer should support identity matrices. For unsupported expressions that could be misinterpreted, it should raise an error instead of silently producing wrong code.

## Stack trace / error output

Not provided in the original report. No error is raised; the function silently returns a wrong result.

## Test case

Minimal test based on the reproduction in the report. The SymPy import line is not shown in the report and is assumed here.

```python
import numpy as np
from sympy import symbols, MatrixSymbol, Identity, lambdify

n = symbols('n', integer=True)
A = MatrixSymbol("A", n, n)
a = np.array([[1, 2], [3, 4]])

f = lambdify(A, A + Identity(n))

# Expected per the report: array([[2, 2], [3, 5]])
assert (f(a) == np.array([[2, 2], [3, 5]])).all()
```

## Code example

From the original report:

```python
>>> import numpy as np
>>> n = symbols('n', integer=True)
>>> A = MatrixSymbol("A", n, n)
>>> a = np.array([[1, 2], [3, 4]])
>>> f = lambdify(A, A + Identity(n))
>>> f(a)
array([[1.+1.j, 2.+1.j],
       [3.+1.j, 4.+1.j]])
```

```python
>>> import inspect
>>> print(inspect.getsource(f))
def _lambdifygenerated(A):
    return (I + A)
>>> f.__globals__['I']
1j
```

## Version and environment

Not provided in the original report. The report shows the code uses SymPy (`lambdify`, `MatrixSymbol`, `Identity`) with NumPy.