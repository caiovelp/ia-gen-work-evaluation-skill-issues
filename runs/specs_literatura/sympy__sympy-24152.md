## Summary

`TensorProduct.expand(tensorproduct=True)` returns an incompletely expanded result when the summands in the tensor product factors have commutative (scalar) coefficients. In the example below, only the first tensor factor is expanded and the second, `(U + V)`, is left unexpanded. Functions that rely on `.expand(tensorproduct=True)`, such as `qapply()`, are also affected.

The reporter traced the problem to `TensorProduct._eval_expand_tensorproduct()` in `quantum/tensorproduct.py`. That method checks whether a recursive expansion is needed. The check fails when the `TensorProduct` constructor pulls commutative (scalar) factors out front. In that case the constructor returns `Mul(c_factors, TensorProduct(...))` rather than a bare `TensorProduct`, so the recursive expansion is skipped.

## Steps to reproduce

1. Import `sympy` and `sympy.physics.quantum`.
2. Create two operators: `U = Operator('U')` and `V = Operator('V')`.
3. Build a tensor product whose factors contain scalar coefficients: `P = TensorProduct(2*U - V, U + V)`.
4. Call `P.expand(tensorproduct=True)` and print the result.

## Observed behavior

```
print(P)
# (2*U - V)x(U + V)
print(P.expand(tensorproduct=True))
# 2*Ux(U + V) - Vx(U + V)
```

The first tensor factor is expanded, but the second tensor factor `(U + V)` is not, so the expansion is incomplete.

The reporter notes that calling `.expand(tensorproduct=True)` repeatedly, once per tensor factor or until the result stops changing, eventually produces the complete expansion. This is only practical in interactive sessions, not inside algorithms.

## Expected behavior

A single call to `P.expand(tensorproduct=True)` should fully expand all tensor factors. The result should be equivalent to `2*UxU + 2*UxV - VxU - VxV`.

## Stack trace / error output

Not provided in the original report. No exception is raised; the result is incorrect.

## Test case

Minimal test case derived from the report's snippet:

```python
from sympy.physics.quantum import Operator, TensorProduct

def test_tensorproduct_expand_with_scalar_coefficients():
    U = Operator('U')
    V = Operator('V')
    P = TensorProduct(2*U - V, U + V)
    expected = (2*TensorProduct(U, U) + 2*TensorProduct(U, V)
                - TensorProduct(V, U) - TensorProduct(V, V))
    assert P.expand(tensorproduct=True) == expected
```

The reporter also notes a related case. The constructor returns `0` if a tensor factor is `0`, for example `TensorProduct(U - U, U + V)`, so the result of constructing a `TensorProduct` is not guaranteed to contain a `TensorProduct` object.

## Code example

```python
from sympy import *
from sympy.physics.quantum import *
U = Operator('U')
V = Operator('V')
P = TensorProduct(2*U - V, U + V)
print(P)
# (2*U - V)x(U + V)
print(P.expand(tensorproduct=True))
# result: 2*Ux(U + V) - Vx(U + V)  -- expansion has missed 2nd tensor factor and is incomplete
```

## Version and environment

Not provided in the original report.