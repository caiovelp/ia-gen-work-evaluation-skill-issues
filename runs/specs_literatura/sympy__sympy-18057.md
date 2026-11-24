## Summary

`sympy.Symbol.__eq__` (in `Expr.__eq__`) calls `sympify` on the other operand. For an unknown object, `sympify` passes the object's `repr()` string to `parse_expr`, which `eval`s it. Comparing a SymPy expression with an arbitrary object therefore evaluates code taken from that object's `__repr__`. The reporter calls this **very bad**, especially because a plain equality check triggers it.

There are two visible consequences:
1. If the repr evaluates to something invalid, an equality comparison raises an exception (e.g. `AttributeError`).
2. If an unknown object's repr is `x`, it compares as equal to `sympy.Symbol('x')`.

## Steps to reproduce

**Case 1: exception during equality check**
1. Define a class whose `__repr__` returns `'x.y'`.
2. Compare `sympy.Symbol('x')` with an instance of that class using `==`.
3. An `AttributeError` is raised.

**Case 2: false equality**
1. Define a class whose `__repr__` returns `'x'`.
2. Evaluate `sympy.Symbol('x') != C()`.
3. The result is `False`: the object compares equal to the symbol.

## Observed behavior

- **Case 1:** The comparison raises `AttributeError: 'Symbol' object has no attribute 'y'`. The repr string is parsed and `eval`ed inside `eval_expr` in `sympy/parsing/sympy_parser.py`. The evaluated code is:
  ```
  Symbol ('x' ).y
  ```
  It is evaluated on this line:
  ```
      expr = eval(
          code, global_dict, local_dict)  # take local objects in preference
  ```
- **Case 2:** An unknown object whose repr is `x` compares equal to `sympy.Symbol('x')`, so `assert sympy.Symbol('x') != C()` fails.

## Expected behavior

- An equality check should never `eval` strings produced by the `repr()` of unknown objects.
- Comparing a SymPy expression with an unrelated object should not raise an exception. In Case 1, the comparison should simply complete.
- An unrelated object should not compare equal to a SymPy symbol just because its repr matches the symbol's name. `sympy.Symbol('x') != C()` should be `True`.

## Stack trace / error output

```
FAILED                   [100%]
        class C:
            def __repr__(self):
                return 'x.y'
    
>       _ = sympy.Symbol('x') == C()

_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
sympy/core/expr.py:124: in __eq__
    other = sympify(other)
sympy/core/sympify.py:385: in sympify
    expr = parse_expr(a, local_dict=locals, transformations=transformations, evaluate=evaluate)
sympy/parsing/sympy_parser.py:1011: in parse_expr
    return eval_expr(code, local_dict, global_dict)
sympy/parsing/sympy_parser.py:906: in eval_expr
    code, global_dict, local_dict)  # take local objects in preference
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

>   ???
E   AttributeError: 'Symbol' object has no attribute 'y'

<string>:1: AttributeError
```

## Test case

The following minimal tests are derived from the reproduction snippets in the report:

```python
import sympy

def test_eq_does_not_eval_repr_of_unknown_object():
    class C:
        def __repr__(self):
            return 'x.y'
    _ = sympy.Symbol('x') == C()  # currently raises AttributeError

def test_unknown_object_with_matching_repr_not_equal():
    class C:
        def __repr__(self):
            return 'x'
    assert sympy.Symbol('x') != C()  # currently fails
```

## Code example

Repro code from the report:

```python
import sympy
class C:
    def __repr__(self):
        return 'x.y'
_ = sympy.Symbol('x') == C()
```

Related case:

```python
    class C:
        def __repr__(self):
            return 'x'

    assert sympy.Symbol('x') != C()  # fails
```

## Version and environment

Not provided in the original report. The traceback references `sympy/core/expr.py:124`, `sympy/core/sympify.py:385`, and `sympy/parsing/sympy_parser.py:1011` and `:906`. The output appears to come from pytest.