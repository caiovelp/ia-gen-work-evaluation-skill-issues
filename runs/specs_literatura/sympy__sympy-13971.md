## Summary
In Jupyter, the rendered output of `SeqFormula()` backslash-escapes its square brackets (`\left\[ ... \right\]`). When this output is copied into a Markdown cell, it does not render properly. The same content with unescaped brackets renders correctly.

## Steps to reproduce
1. Open a Jupyter notebook.
2. Run the following in a code cell:
   ```python
   import sympy as sp
   k, m, n = sp.symbols('k m n', integer=True)
   sp.init_printing()

   sp.SeqFormula(n**2, (n,0,sp.oo))
   ```
3. Look at the rendered output. Its LaTeX source is `\left\[0, 1, 4, 9, \ldots\right\]`.
4. Copy this output into a Markdown cell and render the cell.

## Observed behavior
The Jupyter rendering produces backslash-escaped square brackets:

`\left\[0, 1, 4, 9, \ldots\right\]`

When this output is pasted into a Markdown cell, it does not render properly.

## Expected behavior
The sequence output should render properly when copied into a Markdown cell. For comparison, the following renders correctly in a Markdown cell:

`[0, 1, 4, 9, \ldots ]`

The reporter suggests that either sequence output should not backslash-escape square brackets, or `\]` should render correctly. The report does not say which is intended.

## Stack trace / error output
Not provided in the original report. No error is raised; the problem is incorrect rendering. The problematic output is:

`\left\[0, 1, 4, 9, \ldots\right\]`

## Test case
Not provided in the original report. The following minimal reproduction comes from the report's snippet:

```python
import sympy as sp
k, m, n = sp.symbols('k m n', integer=True)
sp.init_printing()

sp.SeqFormula(n**2, (n,0,sp.oo))
# Observed rendered output: \left\[0, 1, 4, 9, \ldots\right\]
# Copied into a Markdown cell, this does not render properly.
# By contrast, [0, 1, 4, 9, \ldots ] renders fine in a Markdown cell.
```

## Code example
```python
import sympy as sp
k, m, n = sp.symbols('k m n', integer=True)
sp.init_printing()

sp.SeqFormula(n**2, (n,0,sp.oo))
```

## Version and environment
- Environment: Jupyter notebook, with output rendered via `sp.init_printing()` and pasted into a Markdown cell.
- SymPy version, Python version, Jupyter version and OS: Not provided in the original report.