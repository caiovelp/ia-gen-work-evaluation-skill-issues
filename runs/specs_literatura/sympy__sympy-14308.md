## Summary

Pretty printing of a `sympy.vector` expression is broken when a vector basis element is multiplied by a power expression such as `(x/y)**t`. The basis vector name (`e_j`) is printed twice: once inside the expression and once outside it, and the layout is malformed. The report also notes a separate problem: even when such expressions print correctly, the baseline is wrong. It should be centered.

## Steps to reproduce

1. Start an interactive session (the report uses IPython).
2. Run `from sympy.vector import *`.
3. Create a Cartesian coordinate system: `e = CoordSysCartesian('e')`.
4. Evaluate `(x/y)**t*e.j` and view the pretty-printed output.

Note: the report does not show how `x`, `y` and `t` are defined. They appear to be SymPy symbols.

## Observed behavior

The output is malformed. `e_j` appears twice, once embedded in the parenthesized power and once trailing on the first line:

```
Out[3]:
⎛   t⎞ e_j
⎜⎛x⎞ e_j ⎟
⎜⎜─⎟ ⎟
⎝⎝y⎠ ⎠
```

Additionally, according to the reporter, when vector expressions do print correctly, the baseline is wrong (not centered). No example output is given for this case.

## Expected behavior

- The expression `(x/y)**t*e.j` should pretty print correctly, with the basis vector `e_j` appearing once alongside the power expression `(x/y)**t`.
- The baseline of the printed vector expression should be centered.

## Stack trace / error output

Not provided in the original report. No exception is raised; the problem is incorrect output.

## Test case

The following minimal check is derived from the report's reproduction. It assumes `x`, `y` and `t` are plain SymPy symbols, which the report does not show.

```py
from sympy import symbols, pretty
from sympy.vector import CoordSysCartesian

x, y, t = symbols('x y t')
e = CoordSysCartesian('e')

out = pretty((x/y)**t*e.j)
print(out)
# The basis vector should appear only once in the output
assert out.count('e_j') == 1
```

## Code example

From the original report:

```py
In [1]: from sympy.vector import *

In [2]: e = CoordSysCartesian('e')

In [3]: (x/y)**t*e.j
Out[3]:
⎛   t⎞ e_j
⎜⎛x⎞ e_j ⎟
⎜⎜─⎟ ⎟
⎝⎝y⎠ ⎠
```

## Version and environment

Not provided in the original report. The reproduction uses an IPython session, the `sympy.vector` module, and `CoordSysCartesian`.