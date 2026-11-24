## Summary
The pretty printer misaligns the summand of a `Sum` with an expression added to it. For `Sum(x, (x, 1, oo)) + 3`, the summand `x` and the `+ 3` end up on different lines when they should share one baseline.

## Steps to reproduce
1. In an interactive session with `pprint`, `Sum`, `x` and `oo` available, run:
   ```python
   >>> pprint(Sum(x, (x, 1, oo)) + 3)
   ```
2. Compare the line holding the summand `x` with the line holding `+ 3`.

## Observed behavior
The summand `x` is printed one line above the `+ 3`:
```
  ∞
 ___
 ╲
  ╲   x
  ╱     + 3
 ╱
 ‾‾‾
x = 1
```

## Expected behavior
The summand `x` and the `+ 3` should be vertically aligned on the same line. The reporter is not sure whether the `x` should move down or the `+ 3` should move up.

## Stack trace / error output
Not provided in the original report. No error is raised; the problem is the formatting of the output.

## Test case
Minimal reproduction based on the report:
```python
pprint(Sum(x, (x, 1, oo)) + 3)
```
In the output, the summand `x` and the `+ 3` should appear on the same line.

## Code example
```python
>>> pprint(Sum(x, (x, 1, oo)) + 3)
```

## Version and environment
Not provided in the original report.