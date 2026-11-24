## Summary

When a module defines an empty `__all__` (`__all__ = []`), `sphinx.ext.autodoc` ignores it. `.. automodule:: <module>` with `:members:` documents every public function in the module, even though the empty `__all__` means none should be documented.

## Steps to reproduce

1. Create a module `example.py`:
   ```python
   # example.py
   __all__ = []


   def foo():
       "docstring"


   def bar():
       "docstring"


   def baz():
       "docstring"
   ```
2. Create `index.rst` with the `automodule` directive and the `:members:` option:
   ```rst
   .. automodule:: example
      :members:
   ```
3. Enable the `sphinx.ext.autodoc` extension and build the documentation.
4. Look at the generated output for the `example` module.

## Observed behavior

The functions `foo`, `bar` and `baz` all appear in the generated documentation.

## Expected behavior

No members should be shown, because the module's `__all__` is empty.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report. A minimal test case can be built from the reproduction above: document the module `example` (with `__all__ = []` and the functions `foo`, `bar`, `baz`) using `automodule` with `:members:`. The test should assert that the output has no entries for `foo`, `bar` or `baz`.

## Code example

```python
# example.py
__all__ = []


def foo():
    "docstring"


def bar():
    "docstring"


def baz():
    "docstring"
```

```rst
.. index.rst
.. automodule:: example
   :members:
```

## Version and environment

- OS: Mac
- Python version: 3.9.1
- Sphinx version: HEAD of 3.x
- Sphinx extensions: `sphinx.ext.autodoc`
- Extra tools: None