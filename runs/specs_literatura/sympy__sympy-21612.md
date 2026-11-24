## Summary

`parse_latex` drops the brackets around a fraction that is used as a denominator. For `\frac{\frac{a^3+b}{c}}{\frac{1}{c^2}}`, the result is `((a**3 + b)/c)/1/(c**2)`. Because of the missing brackets, this is mathematically different from the input, which is `((a**3 + b)/c)/(1/(c**2))`.

## Steps to reproduce

1. Start a Python 3 interpreter with SymPy installed.
2. Import the LaTeX parser: `from sympy.parsing.latex import parse_latex`
3. Parse a nested fraction whose denominator is itself a fraction:
   `parse_latex("\\frac{\\frac{a^3+b}{c}}{\\frac{1}{c^2}}")`
4. Look at the returned expression.

## Observed behavior

The expression is parsed as:

```
((a**3 + b)/c)/1/(c**2)
```

There are no brackets around the denominator `1/(c**2)`. Python evaluates `/` left to right, so the result is `((a**3 + b)/c) / 1 / c**2`. The input means `((a**3 + b)/c) / (1/c**2)`, so the parsed expression is wrong.

## Expected behavior

The expression should be parsed with the denominator fraction in brackets:

```
((a**3 + b)/c)/(1/(c**2))
```

## Stack trace / error output

Not provided in the original report. No exception is raised; the parser silently returns a wrong expression. The interpreter session from the report:

```
root@d31ef1c26093:/# python3
Python 3.6.9 (default, Jan 26 2021, 15:33:00)
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from sympy.parsing.latex import parse_latex
>>> parse_latex("\\frac{\\frac{a^3+b}{c}}{\\frac{1}{c^2}}")
((a**3 + b)/c)/1/(c**2)
```

## Test case

This minimal test is derived from the reproduction in the report. It checks that the parsed expression is mathematically equal to the expected one:

```python
from sympy import symbols, simplify
from sympy.parsing.latex import parse_latex

def test_parse_latex_nested_fraction_in_denominator():
    a, b, c = symbols('a b c')
    expr = parse_latex("\\frac{\\frac{a^3+b}{c}}{\\frac{1}{c^2}}")
    expected = ((a**3 + b)/c)/(1/(c**2))
    assert simplify(expr - expected) == 0
```

## Code example

```python
from sympy.parsing.latex import parse_latex
parse_latex("\\frac{\\frac{a^3+b}{c}}{\\frac{1}{c^2}}")
# returns: ((a**3 + b)/c)/1/(c**2)
# expected: ((a**3 + b)/c)/(1/(c**2))
```

## Version and environment

- SymPy versions tested: 1.8 and 1.6.2 (both affected)
- Python 3.6.9 (default, Jan 26 2021, 15:33:00), GCC 8.4.0
- OS: Linux (run as root inside what appears to be a container, host `d31ef1c26093`)