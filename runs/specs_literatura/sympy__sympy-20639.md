## Summary

The pretty printer renders `pi**(1/E)` incorrectly. It displays it as a root expression with `-1` as the root index (roughly "the −1th root of π") instead of π raised to the power e⁻¹. The LaTeX and `str` printers handle the same expression correctly. The reporter did not find an existing report of this bug among other `printing.pretty` issues.

## Steps to reproduce

1. Start an interactive session (the report shows IPython-style `In`/`Out` prompts) with SymPy's pretty printing active for output.
2. Evaluate `pi**(1/E)`.
3. Look at the pretty-printed output.
4. For comparison, evaluate `print(latex(pi**(1/E)))` and `str(pi**(1/E))`.

## Observed behavior

The pretty-printed output is:

```
-1___
╲╱ π 
```

This reads as a root of π with index `-1`, which does not represent π^(e⁻¹).

The other printers give correct output:
- `latex(pi**(1/E))` gives `\pi^{e^{-1}}`
- `str(pi**(1/E))` gives `'pi**exp(-1)'`

## Expected behavior

The pretty printer should render the expression as π raised to the power e⁻¹ (i.e. `exp(-1)`), consistent with the LaTeX (`\pi^{e^{-1}}`) and `str` (`pi**exp(-1)`) output. It should not render it as a root with index `-1`.

## Stack trace / error output

Not provided in the original report. No exception is raised; the problem is incorrect rendered output.

## Test case

Minimal test derived from the report's reproduction. It checks that the pretty output is not the incorrect root rendering shown above, and that the LaTeX and `str` output match what the report observed:

```python
from sympy import pi, E, latex, pretty

def test_pretty_pi_pow_one_over_E():
    expr = pi**(1/E)
    # Observed incorrect rendering from the report
    assert pretty(expr, use_unicode=True) != "-1___\n╲╱ π "
    # These printers are reported to be correct
    assert latex(expr) == r"\pi^{e^{-1}}"
    assert str(expr) == "pi**exp(-1)"
```

## Code example

From the original report:

```
In [52]: pi**(1/E)
Out[52]:
-1___
╲╱ π 

In [53]: print(latex(pi**(1/E)))
\pi^{e^{-1}}

In [54]: str(pi**(1/E))
Out[54]: 'pi**exp(-1)'
```

## Version and environment

- SymPy version reported as `1.5.dev`. The reporter had just merged from the project master branch.
- Interactive session with IPython-style prompts and Unicode pretty printing.
- OS and Python version: Not provided in the original report.