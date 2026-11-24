## Summary

Pretty printing a `MatAdd` whose operands include a `MatrixSymbol` with a name such as `'y*'` raises `SympifyError`. In `_print_MatAdd` in `sympy/printing/pretty/pretty.py`, the printer calls `S(item.args[0])` to check whether each term is negative. For a `MatrixSymbol`, `args[0]` is the name string, so the printer tries to parse `'y*'` as an expression, which fails.

The reporter also questions this sign check. When a term is considered negative, the printer omits the `+`. This assumes the arguments of `MatAdd` have a particular form and always print a particular way when negative.

## Steps to reproduce

1. Open a Python session in a SymPy checkout and import `pprint` and `MatrixSymbol`. The report does not show the imports or how `n` is defined; it is used as the matrix dimension.
2. Create two matrix symbols, one with a name that is not a valid expression:
   `MatrixSymbol('x', n, n)` and `MatrixSymbol('y*', n, n)`.
3. Add them and pretty print the result:
   ```py
   >>> pprint(MatrixSymbol('x', n, n) + MatrixSymbol('y*', n, n))
   ```

## Observed behavior

`pprint` raises `sympy.core.sympify.SympifyError` instead of printing the expression. The error comes from `_print_MatAdd`, which calls `S(item.args[0]).is_negative`. For the `MatrixSymbol` `y*`, this tries to sympify the string `'y*'`. Parsing fails with `SyntaxError: unexpected EOF while parsing`, and that is re-raised as `SympifyError`.

## Expected behavior

The sum `x + y*` of the two matrix symbols should pretty print without an error. The printer should not treat a `MatrixSymbol`'s name string as an expression to parse.

The decision about whether to print or omit the `+` between terms should not rely on assumptions about the form of `MatAdd`'s arguments.

## Stack trace / error output

```
Traceback (most recent call last):
  File "./sympy/core/sympify.py", line 368, in sympify
    expr = parse_expr(a, local_dict=locals, transformations=transformations, evaluate=evaluate)
  File "./sympy/parsing/sympy_parser.py", line 950, in parse_expr
    return eval_expr(code, local_dict, global_dict)
  File "./sympy/parsing/sympy_parser.py", line 863, in eval_expr
    code, global_dict, local_dict)  # take local objects in preference
  File "<string>", line 1
    Symbol ('y' )*
                 ^
SyntaxError: unexpected EOF while parsing

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "./sympy/printing/pretty/pretty.py", line 2371, in pretty_print
    use_unicode_sqrt_char=use_unicode_sqrt_char))
  File "./sympy/printing/pretty/pretty.py", line 2331, in pretty
    return pp.doprint(expr)
  File "./sympy/printing/pretty/pretty.py", line 62, in doprint
    return self._print(expr).render(**self._settings)
  File "./sympy/printing/printer.py", line 274, in _print
    return getattr(self, printmethod)(expr, *args, **kwargs)
  File "./sympy/printing/pretty/pretty.py", line 828, in _print_MatAdd
    if S(item.args[0]).is_negative:
  File "./sympy/core/sympify.py", line 370, in sympify
    raise SympifyError('could not parse %r' % a, exc)
sympy.core.sympify.SympifyError: Sympify of expression 'could not parse 'y*'' failed, because of exception being raised:
SyntaxError: unexpected EOF while parsing (<string>, line 1)
```

## Test case

This minimal test case is derived from the reproduction snippet. The definition of `n` and the import locations are not given in the original report. The expected rendered output is also not given, so the test only checks that printing does not raise.

```py
# n: matrix dimension, as used in the original report
def test_pretty_MatAdd_with_non_parsable_MatrixSymbol_name():
    expr = MatrixSymbol('x', n, n) + MatrixSymbol('y*', n, n)
    pprint(expr)  # currently raises SympifyError
```

## Code example

The line in `_print_MatAdd` (`sympy/printing/pretty/pretty.py`, line 828) where the failure occurs, as shown in the traceback:

```py
if S(item.args[0]).is_negative:
```

## Version and environment

Not provided in the original report. The traceback shows the code was run from a local SymPy source tree (paths like `./sympy/...`) in an interactive Python session.