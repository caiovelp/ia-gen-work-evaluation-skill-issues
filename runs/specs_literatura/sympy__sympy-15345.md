## Summary

`mathematica_code` produces invalid Mathematica code for `Max`. For `Max(x, 2)` it returns `'Max(2, x)'`, which uses parentheses instead of square brackets.

## Steps to reproduce

1. Define a symbol: `x = symbols('x')`
2. Call `mathematica_code(Max(x, 2))`
3. Inspect the returned string.

## Observed behavior

The output is:

```
'Max(2, x)'
```

This is not valid Mathematica code.

## Expected behavior

The output should be valid Mathematica code:

```
'Max[x,2]'
```

## Stack trace / error output

Not provided in the original report. No exception is raised; the function returns incorrect output.

## Test case

Minimal test derived from the reproduction snippet. The original report does not show the import statements.

```python
x = symbols('x')
assert mathematica_code(Max(x, 2)) == 'Max[x,2]'
```

## Code example

```python
x = symbols('x')
mathematica_code(Max(x,2))
```

## Version and environment

Not provided in the original report.