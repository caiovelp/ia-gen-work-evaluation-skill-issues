## Summary

The LaTeX printer (`latex()`) gives output that is inconsistent with the pretty printer (`pprint()`) for some expressions. The LaTeX printer should always give the same output as the pretty printer unless LaTeX allows better output. Two examples:

1. `exp(-x)*log(x)` with `x` positive: LaTeX prints `\frac{1}{e^{x}} \log{\left (x \right )}`, but the pretty printer shows `ℯ^(-x)⋅log(x)`.
2. `1/(x + y)/2`: LaTeX prints `\frac{1}{2 x + 2 y}`, but the pretty printer shows `1/(2⋅(x + y))`, with the factor 2 kept outside the parenthesized sum.

The reporter also thinks that assumptions on symbols, such as `positive=True`, should not affect printing.

## Steps to reproduce

**Example 1: `exp(-x)*log(x)` with a positive symbol**

1. Create a positive symbol: `var('x', positive=True)`
2. Run `latex(exp(-x)*log(x))`
3. Run `pprint(exp(-x)*log(x))`
4. Compare the two outputs.

**Example 2: `1/(x + y)/2`**

1. Create symbols: `var('x y')`
2. Run `latex(1/(x + y)/2)`
3. Run `pprint(1/(x + y)/2)`
4. Compare the two outputs.

## Observed behavior

**Example 1:**

```py
In [9]: var('x', positive=True)
Out[9]: x

In [10]: latex(exp(-x)*log(x))
Out[10]: '\\frac{1}{e^{x}} \\log{\\left (x \\right )}'

In [11]: pprint(exp(-x)*log(x))
 -x
ℯ  ⋅log(x)
```

The LaTeX output writes `exp(-x)` as a fraction `1/e^x`. The pretty printer writes it as `ℯ` raised to `-x`.

**Example 2:**

```py
In [14]: var('x y')
Out[14]: (x, y)

In [15]: latex(1/(x + y)/2)
Out[15]: '\\frac{1}{2 x + 2 y}'

In [16]: pprint(1/(x + y)/2)
    1
─────────
2⋅(x + y)
```

The LaTeX output distributes the 2 into the denominator (`2 x + 2 y`). The pretty printer keeps it as `2⋅(x + y)`.

## Expected behavior

The LaTeX output should match the pretty printer's output, unless LaTeX can produce better output:

- Example 1: the LaTeX output should show `e` raised to `-x`, multiplied by `log(x)`, as the pretty printer does. It should not show `1/e^{x}`.
- Example 2: the LaTeX output should show `1` over `2(x + y)`, as the pretty printer does. It should not show `1` over `2 x + 2 y`.

Assumptions on symbols (for example `positive=True`) should not affect how an expression is printed.

## Stack trace / error output

Not provided in the original report. No error is raised; the problem is inconsistent output.

## Test case

The following minimal test is derived from the report's snippets. It only checks that the observed inconsistent output is no longer produced. The exact expected LaTeX strings are not given in the original report.

```py
from sympy import var, exp, log, latex

def test_latex_consistent_with_pprint_exp_log():
    x = var('x', positive=True)
    # pprint shows: ℯ^(-x)⋅log(x)
    assert latex(exp(-x)*log(x)) != '\\frac{1}{e^{x}} \\log{\\left (x \\right )}'

def test_latex_consistent_with_pprint_rational_factor():
    x, y = var('x y')
    # pprint shows: 1/(2⋅(x + y))
    assert latex(1/(x + y)/2) != '\\frac{1}{2 x + 2 y}'
```

## Code example

```py
var('x', positive=True)
latex(exp(-x)*log(x))
pprint(exp(-x)*log(x))

var('x y')
latex(1/(x + y)/2)
pprint(1/(x + y)/2)
```

## Version and environment

Not provided in the original report. The examples were run in an interactive IPython-style session.