## Summary

`parse_mathematica` in `sympy.parsing.mathematica` cannot parse Greek characters such as `λ`, and possibly other non-ASCII characters. It raises `SyntaxError: unable to create a single AST for the expression`. The deprecated `mathematica` function in the same module parses the same input without error. Since SymPy 1.11, `parse_mathematica` replaces `mathematica`, so this is a regression for users who migrate.

## Steps to reproduce

1. Install SymPy 1.11.
2. Run the following in Python:
   ```python
   from sympy.parsing.mathematica import parse_mathematica
   parse_mathematica('λ')
   ```
3. For comparison, run the deprecated parser on the same input:
   ```python
   from sympy.parsing.mathematica import mathematica
   mathematica('λ')
   ```

## Observed behavior

- `parse_mathematica('λ')` raises `SyntaxError: unable to create a single AST for the expression`.
- `mathematica('λ')` (deprecated) returns `λ`.

## Expected behavior

`parse_mathematica('λ')` should parse the Greek character successfully and return `λ`, as the deprecated `mathematica('λ')` does.

## Stack trace / error output

From the report (the traceback was truncated by the reporter):
```
Traceback (most recent call last):
...
File "<string>", line unknown
SyntaxError: unable to create a single AST for the expression
```

Output of the deprecated parser for the same input:
```
Out[]: 
λ
```

## Test case

Minimal test derived from the reproduction snippet. It checks that the new parser accepts the input and agrees with the deprecated parser:
```python
from sympy.parsing.mathematica import mathematica, parse_mathematica

def test_parse_mathematica_greek_character():
    # Currently raises SyntaxError: unable to create a single AST for the expression
    assert parse_mathematica('λ') == mathematica('λ')
```

## Code example

Deprecated parser (works):
```python
from sympy.parsing.mathematica import mathematica
mathematica('λ')
# λ
```

New parser (fails):
```python
from sympy.parsing.mathematica import parse_mathematica
parse_mathematica('λ')
# SyntaxError: unable to create a single AST for the expression
```

## Version and environment

- SymPy 1.11 (the version in which `mathematica` was deprecated in favor of `parse_mathematica`)
- Python version, OS and other environment details: Not provided in the original report.