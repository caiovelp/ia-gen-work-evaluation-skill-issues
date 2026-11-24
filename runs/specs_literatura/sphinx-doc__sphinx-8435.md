## Summary

`autodoc_type_aliases` has no effect on the type annotations of module-level variables or class attributes documented by `sphinx.ext.autodoc`.

## Steps to reproduce

1. Create a module `example.py` that uses postponed evaluation of annotations. Annotate a module-level variable and a class attribute with the alias name `String`:

   ```python
   # example.py
   from __future__ import annotations


   #: blah blah blah
   var: String


   class MyString:
       "mystring"

       #: blah blah blah
       var: String
   ```

2. In `conf.py`, enable `sphinx.ext.autodoc` and define the type alias:

   ```python
   # conf.py
   autodoc_type_aliases = {
       'String': 'example.MyString'
   }
   ```

3. In `index.rst`, document the module:

   ```rst
   .. automodule:: example
      :members:
      :undoc-members:
   ```

4. Build the documentation.
5. Look at the rendered type annotations of `example.var` and `example.MyString.var`.

## Observed behavior

`autodoc_type_aliases` is not applied to the variable `example.var` or the attribute `example.MyString.var`. The report does not show the exact rendered output.

## Expected behavior

`autodoc_type_aliases` should be applied to `example.var` and `example.MyString.var`, so that `String` resolves to `example.MyString`.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report. The three files in "Steps to reproduce" (`example.py`, `conf.py`, `index.rst`) form a minimal reproduction project. Build it and check whether the annotations of `example.var` and `example.MyString.var` use the alias `example.MyString`.

## Code example

```python
# example.py
from __future__ import annotations


#: blah blah blah
var: String


class MyString:
    "mystring"

    #: blah blah blah
    var: String
```

```rst
# index.rst
.. automodule:: example
   :members:
   :undoc-members:
```

```python
# conf.py
autodoc_type_aliases = {
    'String': 'example.MyString'
}
```

## Version and environment

- OS: Mac
- Python version: 3.9.0
- Sphinx version: HEAD of 3.x branch
- Sphinx extensions: `sphinx.ext.autodoc`
- Extra tools: none