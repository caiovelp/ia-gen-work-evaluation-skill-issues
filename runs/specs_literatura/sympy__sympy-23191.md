## Summary
Pretty-printing `sympy.vector` objects with `pprint` in the terminal produces jumbled output. The unit vector (for example `i_C` or `k_C`) is inserted in the middle of the scalar coefficient's 2D layout instead of appearing as a separate factor.

## Steps to reproduce
1. Start a Python session in a terminal.
2. Import SymPy and `sympy.vector` (`CoordSys3D`, `Del`), then call `init_printing()`.
3. Create a coordinate system `C = CoordSys3D("C")` and a `Del()` operator.
4. Build a vector whose coefficient is a fraction containing trigonometric functions. For example, `Bx * C.i`, where `Bx = 2 * ten**(-4) * cos(ten**5 * t) * sin(ten**(-3) * C.y)` and `ten = symbols("10", positive=True)`.
5. Build a second vector containing an unevaluated `Integral` of the curl of the first vector.
6. Call `pprint` on the first vector, on the integral vector, and on the integral vector after `.doit()`.
7. Look at where the unit vector appears in each printed result.

The full script is under **Code example**.

## Observed behavior
The unit vector is placed inside the 2D layout of the coefficient, breaking up the expression:

- **`pprint(vecB)`:** `i_C` appears inside the numerator, between `2⋅sin(y_C/10^3)` and `cos(10^5⋅t)`. The bracket/fraction lines are also misaligned.
- **`pprint(vecE)`:** `k_C` appears on the second line, to the right of the large parenthesised expression, rather than aligned with it as a clear factor.
- **`pprint(vecE.doit())`:** `k_C` appears inside the numerator, after `cos(y_C/10^3)`. The bracket lines are again misaligned.

The full output is under **Stack trace / error output**.

## Expected behavior
The report does not state the expected output explicitly. It implies that the unit vector should not be inserted in the middle of the expression. The coefficient should render as an intact 2D expression, with the unit vector shown cleanly alongside it.

## Stack trace / error output
No exception is raised. The incorrect terminal output is:

```
⎛     ⎛y_C⎞    ⎛  5  ⎞⎞    
⎜2⋅sin⎜───⎟ i_C⋅cos⎝10 ⋅t⎠⎟
⎜     ⎜  3⎟           ⎟    
⎜     ⎝10 ⎠           ⎟    
⎜─────────────────────⎟    
⎜           4         ⎟    
⎝         10          ⎠    

⎛     ⌠                           ⎞    
⎜     ⎮       ⎛y_C⎞    ⎛  5  ⎞    ⎟ k_C
⎜     ⎮ -2⋅cos⎜───⎟⋅cos⎝10 ⋅t⎠    ⎟    
⎜     ⎮       ⎜  3⎟               ⎟    
⎜  11 ⎮       ⎝10 ⎠               ⎟    
⎜10  ⋅⎮ ─────────────────────── dt⎟    
⎜     ⎮             2             ⎟    
⎜     ⎮           10              ⎟    
⎜     ⌡                           ⎟    
⎜─────────────────────────────────⎟    
⎝               4⋅π               ⎠    

⎛   4    ⎛  5  ⎞    ⎛y_C⎞ ⎞    
⎜-10 ⋅sin⎝10 ⋅t⎠⋅cos⎜───⎟ k_C ⎟
⎜                   ⎜  3⎟ ⎟    
⎜                   ⎝10 ⎠ ⎟    
⎜─────────────────────────⎟    
⎝           2⋅π           ⎠    
```

## Test case
The original report contains no automated test case. This minimal reproduction is taken from the reporter's snippet and covers the first faulty output:

```python
from sympy import symbols, cos, sin, pprint
from sympy.vector import CoordSys3D

C = CoordSys3D("C")
t = symbols("t")
ten = symbols("10", positive=True)

Bx = 2 * ten**(-4) * cos(ten**5 * t) * sin(ten**(-3) * C.y)
pprint(Bx * C.i)  # i_C is printed in the middle of the coefficient
```

## Code example
```python
from sympy import *
from sympy.vector import CoordSys3D, Del

init_printing()

delop = Del()
CC_ = CoordSys3D("C")
x,    y,    z    = CC_.x, CC_.y, CC_.z
xhat, yhat, zhat = CC_.i, CC_.j, CC_.k

t = symbols("t")
ten = symbols("10", positive=True)
eps, mu = 4*pi*ten**(-11), ten**(-5)

Bx = 2 * ten**(-4) * cos(ten**5 * t) * sin(ten**(-3) * y)
vecB = Bx * xhat
vecE = (1/eps) * Integral(delop.cross(vecB/mu).doit(), t)

pprint(vecB)
print()
pprint(vecE)
print()
pprint(vecE.doit())
```

## Version and environment
- SymPy version: Not provided in the original report.
- Python version and OS: Not provided in the original report.
- Context given in the report: output printed in a terminal using `pprint` after `init_printing()`, with Unicode pretty printing as shown in the output.