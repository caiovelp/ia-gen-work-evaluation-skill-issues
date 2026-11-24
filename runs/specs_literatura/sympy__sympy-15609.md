## Summary

The LaTeX printer produces output that will not compile for an indexed matrix product such as `(M*N)[i, j]`. The summation dummy index appears as `_i_1` inside the subscripts, which creates a double subscript (`_`). LaTeX rejects the result and MathJax cannot render it.

## Steps to reproduce

1. Define the symbols `i`, `j`, `k`:
   `i, j, k = symbols("i j k")`
2. Define two square matrix symbols of size `k × k`:
   `M = MatrixSymbol("M", k, k)` and `N = MatrixSymbol("N", k, k)`
3. Print the indexed product to LaTeX:
   `latex((M*N)[i, j])`
4. Compile the resulting string with LaTeX, or render it with MathJax.

(The original report does not show the import statements.)

## Observed behavior

`latex((M*N)[i, j])` returns:

```
\sum_{i_{1}=0}^{k - 1} M_{i, _i_1} N_{_i_1, j}
```

In the subscripts of `M` and `N`, the dummy index is written as `_i_1`. The summation limit uses a different form, `i_{1}`. LaTeX reports a double subscript error on `_`, and MathJax does not render the expression.

## Expected behavior

The printer should return a valid LaTeX string that compiles without a double-subscript error and renders in MathJax.

## Stack trace / error output

No stack trace was provided. The report only says that "LaTeX complains about a double subscript `_`". The exact LaTeX error message is not provided in the original report.

## Test case

This minimal test case is built from the reproduction snippet. It checks that the dummy index does not appear in the malformed `_i_1` form that causes the double subscript:

```python
def test_latex_indexed_matrix_product_no_double_subscript():
    i, j, k = symbols("i j k")
    M = MatrixSymbol("M", k, k)
    N = MatrixSymbol("N", k, k)
    result = latex((M*N)[i, j])
    # Observed (broken) output: \sum_{i_{1}=0}^{k - 1} M_{i, _i_1} N_{_i_1, j}
    assert "_i_1" not in result
```

## Code example

```python
i, j, k = symbols("i j k")
M = MatrixSymbol("M", k, k)
N = MatrixSymbol("N", k, k)
latex((M*N)[i, j])
```

## Version and environment

Not provided in the original report.