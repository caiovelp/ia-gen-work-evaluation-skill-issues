## Summary

autodoc treats an annotation-only member defined in a superclass as "undocumented". It is left out when the subclass is documented with `:members:` and `:inherited-members:`, even though the member has a `#:` doc comment.

## Steps to reproduce

1. Create `example.py`:

   ```python
   # example.py
   class Foo:
       """docstring"""
       attr1: int  #: docstring


   class Bar(Foo):
       """docstring"""
       attr2: str  #: docstring
   ```

2. Create `index.rst`:

   ```rst
   .. autoclass:: example.Bar
      :members:
      :inherited-members:
   ```

3. Build the documentation with the `sphinx.ext.autodoc` extension enabled.
4. Look for the inherited attribute `Bar.attr1` in the generated output.
5. Optional: add the `:undoc-members:` option to the `autoclass` directive and build again.

## Observed behavior

- `Bar.attr1`, which is inherited from `Foo` and documented with a `#: docstring` comment, does not appear in the output.
- `Bar.attr1` does appear when `:undoc-members:` is added to the `autoclass` directive. This suggests autodoc treats the inherited annotation-only attribute as undocumented.

## Expected behavior

`Bar.attr1` should be shown when `:members:` and `:inherited-members:` are used, without needing `:undoc-members:`, because it has a doc comment (`#: docstring`) in the superclass.

## Stack trace / error output

Not provided in the original report.

## Test case

A minimal test case built from the reproduction in the report:

- Input module `example.py` and `index.rst` exactly as shown in *Steps to reproduce*.
- Directive under test: `.. autoclass:: example.Bar` with `:members:` and `:inherited-members:`.
- Assertion: the generated output includes the attribute `attr1` with its docstring.
- Control: the same directive with `:undoc-members:` added already shows `attr1`, as described in the report.

## Code example

```python
# example.py
class Foo:
    """docstring"""
    attr1: int  #: docstring


class Bar(Foo):
    """docstring"""
    attr2: str  #: docstring
```

```rst
.. index.rst
.. autoclass:: example.Bar
   :members:
   :inherited-members:
```

## Version and environment

- OS: Mac
- Python version: 3.9.1
- Sphinx version: HEAD of 3.x
- Sphinx extensions: `sphinx.ext.autodoc`
- Extra tools: none