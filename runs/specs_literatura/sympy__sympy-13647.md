## Summary

`Matrix.col_insert()` returns an incorrect matrix in SymPy 1.1.1. When columns are inserted into the middle of a 6×6 identity matrix, the original columns to the right of the insertion point are placed in the wrong rows. The 3×3 identity block that should be in the bottom three rows appears in the top three rows. The reporter asks whether this is related to the recent matrix refactor (cc @siefkenj).

## Steps to reproduce

1. Import SymPy: `import sympy as sm`
2. Create a 6×6 identity matrix: `M = sm.eye(6)`
3. Create a 6×2 matrix of twos: `V = 2 * sm.ones(6, 2)`
4. Insert `V` before column index 3 of `M`: `M.col_insert(3, V)`
5. Inspect the resulting 6×8 matrix.

## Observed behavior

The result is:

```
⎡1  0  0  2  2  1  0  0⎤
⎢                      ⎥
⎢0  1  0  2  2  0  1  0⎥
⎢                      ⎥
⎢0  0  1  2  2  0  0  1⎥
⎢                      ⎥
⎢0  0  0  2  2  0  0  0⎥
⎢                      ⎥
⎢0  0  0  2  2  0  0  0⎥
⎢                      ⎥
⎣0  0  0  2  2  0  0  0⎦
```

The 3×3 identity block to the right of the columns of twos is in the top three rows (rows 0–2).

## Expected behavior

The original columns 3–5 of `eye(6)` should keep their row positions after the two inserted columns of twos. The 3×3 identity block on the right should therefore be in the bottom three rows:

```
⎡1  0  0  2  2  0  0  0⎤
⎢0  1  0  2  2  0  0  0⎥
⎢0  0  1  2  2  0  0  0⎥
⎢0  0  0  2  2  1  0  0⎥
⎢0  0  0  2  2  0  1  0⎥
⎣0  0  0  2  2  0  0  1⎦
```

(This matrix follows from the report's statement that the block "is shifted from the bottom three rows to the top three rows". The report does not show it explicitly.)

## Stack trace / error output

Not provided in the original report. No exception is raised; the method returns a wrong result.

## Test case

Minimal test built from the reproduction in the report:

```python
import sympy as sm

def test_col_insert_middle_of_identity():
    M = sm.eye(6)
    V = 2 * sm.ones(6, 2)
    result = M.col_insert(3, V)
    expected = sm.Matrix([
        [1, 0, 0, 2, 2, 0, 0, 0],
        [0, 1, 0, 2, 2, 0, 0, 0],
        [0, 0, 1, 2, 2, 0, 0, 0],
        [0, 0, 0, 2, 2, 1, 0, 0],
        [0, 0, 0, 2, 2, 0, 1, 0],
        [0, 0, 0, 2, 2, 0, 0, 1],
    ])
    assert result == expected
```

## Code example

From the original report (IPython session):

```python
import sympy as sm

M = sm.eye(6)
V = 2 * sm.ones(6, 2)
M.col_insert(3, V)
```

## Version and environment

- SymPy version: `1.1.1` (from `sm.__version__`)
- Run in IPython
- Python version, OS and other environment details: Not provided in the original report.