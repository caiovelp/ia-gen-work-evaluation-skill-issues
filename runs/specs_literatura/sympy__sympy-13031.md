## Summary

`Matrix.hstack` returns a different shape in SymPy 1.1 than in SymPy 1.0 when stacking matrices that have zero rows. In SymPy 1.0, horizontally stacking zero-row matrices with 0, 1, 2 and 3 columns gives shape `(0, 6)`. In SymPy 1.1 the same call gives `(0, 3)`. With one row, the same column counts give `(1, 6)` in SymPy 1.1. The title says `vstack` behavior also changed, but the report only shows an example for `hstack`.

## Steps to reproduce

1. Install SymPy 1.1.
2. Create four zero-row matrices with 0, 1, 2 and 3 columns:
   ```python
   import sympy as sy
   M1 = sy.Matrix.zeros(0, 0)
   M2 = sy.Matrix.zeros(0, 1)
   M3 = sy.Matrix.zeros(0, 2)
   M4 = sy.Matrix.zeros(0, 3)
   ```
3. Stack them horizontally and check the shape:
   ```python
   sy.Matrix.hstack(M1, M2, M3, M4).shape
   ```
4. For comparison, repeat steps 2–3 with one-row matrices (`zeros(1, 0)`, `zeros(1, 1)`, `zeros(1, 2)`, `zeros(1, 3)`).
5. Optionally, run step 3 again on SymPy 1.0.

## Observed behavior

| SymPy version | Input matrices | `hstack(...).shape` |
|---|---|---|
| 1.0 | `zeros(0,0)`, `zeros(0,1)`, `zeros(0,2)`, `zeros(0,3)` | `(0, 6)` |
| 1.1 | `zeros(0,0)`, `zeros(0,1)`, `zeros(0,2)`, `zeros(0,3)` | `(0, 3)` |
| 1.1 | `zeros(1,0)`, `zeros(1,1)`, `zeros(1,2)`, `zeros(1,3)` | `(1, 6)` |

In SymPy 1.1, the zero-row case returns only 3 columns instead of the total of 6.

## Expected behavior

`sy.Matrix.hstack(M1, M2, M3, M4).shape` should be `(0, 6)` for the zero-row matrices. That matches SymPy 1.0, and it matches the one-row case in SymPy 1.1, where the column counts (0 + 1 + 2 + 3 = 6) add up.

## Stack trace / error output

Not provided in the original report. No exception is raised; only the resulting shape is wrong.

## Test case

```python
import sympy as sy

def test_hstack_zero_rows_shape():
    M1 = sy.Matrix.zeros(0, 0)
    M2 = sy.Matrix.zeros(0, 1)
    M3 = sy.Matrix.zeros(0, 2)
    M4 = sy.Matrix.zeros(0, 3)
    assert sy.Matrix.hstack(M1, M2, M3, M4).shape == (0, 6)  # SymPy 1.1 gives (0, 3)

def test_hstack_one_row_shape():
    M1 = sy.Matrix.zeros(1, 0)
    M2 = sy.Matrix.zeros(1, 1)
    M3 = sy.Matrix.zeros(1, 2)
    M4 = sy.Matrix.zeros(1, 3)
    assert sy.Matrix.hstack(M1, M2, M3, M4).shape == (1, 6)  # passes in SymPy 1.1
```

## Code example

```python
import sympy as sy

# Zero rows: (0, 6) in SymPy 1.0, (0, 3) in SymPy 1.1
M1 = sy.Matrix.zeros(0, 0)
M2 = sy.Matrix.zeros(0, 1)
M3 = sy.Matrix.zeros(0, 2)
M4 = sy.Matrix.zeros(0, 3)
print(sy.Matrix.hstack(M1, M2, M3, M4).shape)

# One row: (1, 6) in SymPy 1.1
M1 = sy.Matrix.zeros(1, 0)
M2 = sy.Matrix.zeros(1, 1)
M3 = sy.Matrix.zeros(1, 2)
M4 = sy.Matrix.zeros(1, 3)
print(sy.Matrix.hstack(M1, M2, M3, M4).shape)
```

## Version and environment

- SymPy 1.0: behaves as expected (`(0, 6)`)
- SymPy 1.1: affected (`(0, 3)`)
- Python version, OS and other environment details: Not provided in the original report.