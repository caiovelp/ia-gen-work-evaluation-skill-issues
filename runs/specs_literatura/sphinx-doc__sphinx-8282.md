## Summary

The `autodoc_typehints` setting has no effect on overloaded callables (functions decorated with `typing.overload`). With `autodoc_typehints = 'none'`, the setting is not applied to the overloaded function's signatures.

## Steps to reproduce

1. In `conf.py`, enable `sphinx.ext.autodoc` and set:
   ```python
   autodoc_typehints = 'none'
   ```
2. Create `example.py` with an overloaded function:
   ```python
   from typing import overload


   @overload
   def foo(x: int) -> int:
       ...


   @overload
   def foo(x: float) -> float:
       ...


   def foo(x):
       return x
   ```
3. In `index.rst`, document the module:
   ```rst
   .. automodule:: example
      :members:
      :undoc-members:
   ```
4. Build the documentation.
5. Inspect the rendered signatures of `foo`.

## Observed behavior

The `autodoc_typehints` setting is not applied to the overloaded callable `foo`. The report does not include the actual rendered output.

## Expected behavior

All type hints of overloaded callables follow the `autodoc_typehints` setting. With `autodoc_typehints = 'none'`, the overload signatures of `foo` (`(x: int) -> int` and `(x: float) -> float`) should be rendered without type hints.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report. A minimal test case can be built from the reproduction files above: build `example.py` with `autodoc_typehints = 'none'` and check that no type hints appear in the documented signatures of the overloaded function `foo`.

## Code example

`conf.py`:
```python
autodoc_typehints = 'none'
```

`index.rst`:
```rst
.. automodule:: example
   :members:
   :undoc-members:
```

`example.py`:
```python
from typing import overload


@overload
def foo(x: int) -> int:
    ...


@overload
def foo(x: float) -> float:
    ...


def foo(x):
    return x
```

## Version and environment

- OS: Mac
- Python version: 3.8.2
- Sphinx version: 3.1.0dev
- Sphinx extensions: `sphinx.ext.autodoc`
- Extra tools: None