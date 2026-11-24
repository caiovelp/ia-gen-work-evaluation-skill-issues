## Summary

The matrix multiplication operator `@` (`__matmul__`) on `Matrix` accepts a scalar operand. It currently behaves exactly like `*` (`__mul__`), so `2 @ B` performs scalar multiplication. `@` should only work when the operation is a real matrix multiplication, meaning both operands are matrices. It should fail if either operand is not a matrix. NumPy behaves this way.

## Steps to reproduce

1. Create two matrices:
   ```python
   A = Matrix([[1, 2], [3, 4]])
   B = Matrix([[2, 3], [1, 2]])
   ```
2. Evaluate `A @ B`. This is a matrix-matrix product and works as expected.
3. Evaluate `2 @ B`, where the left operand is a scalar.

## Observed behavior

`A @ B` correctly returns the matrix product:

```
>>> A@B
Matrix([
[ 4,  7],
[10, 17]])
```

`2 @ B` does not fail. It returns the scalar multiple of `B`, the same result as `2 * B`:

```
>>> 2@B
Matrix([
[4, 6],
[2, 4]])
```

The report says that `__matmul__` currently just copies `__mul__`.

## Expected behavior

`@` should only succeed when both operands are matrices. Using `@` with a scalar operand, such as `2 @ B`, should raise an error. Scalar multiplication should still be available through `*`.

NumPy shows the expected behavior. `*` with a scalar works, and `@` with a scalar raises an error:

```
>>> import numpy as np
>>> a = np.array([[1, 2], [3, 4]])
>>> 2*a
array([[2, 4],
       [6, 8]])
>>> 2@a
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: Scalar operands are not allowed, use '*' instead
```

The report does not say which exception type or message `Matrix` should use.

## Stack trace / error output

`Matrix` produces no error, which is the bug. The only traceback in the report is NumPy's reference behavior, shown above under Expected behavior.

## Test case

This minimal test is derived from the reproduction snippet. The report does not specify the exact exception type, so the test checks only that an error is raised.

```python
A = Matrix([[1, 2], [3, 4]])
B = Matrix([[2, 3], [1, 2]])

# Matrix @ Matrix should keep working
assert A @ B == Matrix([[4, 7], [10, 17]])

# Scalar * Matrix should keep working
assert 2 * B == Matrix([[4, 6], [2, 4]])

# Scalar @ Matrix should fail (currently returns Matrix([[4, 6], [2, 4]]))
try:
    2 @ B
except Exception:
    pass
else:
    raise AssertionError("2 @ B should raise an error, but it succeeded")
```

## Code example

```python
>>> A = Matrix([[1, 2], [3, 4]])
>>> B = Matrix([[2, 3], [1, 2]])
>>> A@B
Matrix([
[ 4,  7],
[10, 17]])
>>> 2@B
Matrix([
[4, 6],
[2, 4]])
```

## Version and environment

Not provided in the original report.