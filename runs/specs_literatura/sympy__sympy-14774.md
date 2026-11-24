## Summary
With `inv_trig_style="full"`, the LaTeX printer (`latex`) prints `asin` with its full name (`\arcsin`). It does not do the same for `acsc` and `asec`. For example, `acsc(x)` is printed as `\operatorname{acsc}` instead of `\operatorname{arccsc}`.

## Steps to reproduce
1. Call `latex(asin(x), inv_trig_style="full")` and note that the output uses the full name `\arcsin`.
2. Call `latex(acsc(x), inv_trig_style="full")`.
3. Compare the output with the expected full name `\operatorname{arccsc}`.
4. The title says `asec` has the same problem, so `latex(asec(x), inv_trig_style="full")` is affected too.

## Observed behavior
- `latex(asin(x), inv_trig_style="full")` returns `'\\arcsin{\\left (x \\right )}'`, which is correct.
- `latex(acsc(x), inv_trig_style="full")` returns `'\\operatorname{acsc}{\\left (x \\right )}'`. The abbreviated name is used.
- The title says `asec` is also not printed with its full name. The report does not include its exact output.

## Expected behavior
- `latex(acsc(x), inv_trig_style="full")` should return `'\\operatorname{arccsc}{\\left (x \\right )}'`.
- `asec` should also use its full inverse trig name with `inv_trig_style="full"`, as `asin` already does. The report does not give the exact expected string for `asec`.

## Stack trace / error output
Not provided in the original report. No error is raised; the output is wrong.

## Test case
```python
from sympy import symbols, asin, acsc, latex

x = symbols('x')

# Works as expected
assert latex(asin(x), inv_trig_style="full") == '\\arcsin{\\left (x \\right )}'

# Currently fails: returns '\\operatorname{acsc}{\\left (x \\right )}'
assert latex(acsc(x), inv_trig_style="full") == '\\operatorname{arccsc}{\\left (x \\right )}'
```

## Code example
```python
latex(asin(x), inv_trig_style="full")   # '\\arcsin{\\left (x \\right )}'
latex(acsc(x), inv_trig_style="full")   # '\\operatorname{acsc}{\\left (x \\right )}'
```

## Version and environment
Not provided in the original report.