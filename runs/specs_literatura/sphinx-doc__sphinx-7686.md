## Summary
In `sphinx.ext.autosummary`, the `members` template variable for a module template includes imported members, such as `os`, even when `autosummary_imported_members = False`.

## Steps to reproduce
1. Create a Sphinx project with `sphinx.ext.autosummary` enabled.
2. Add the custom module template `_templates/autosummary/module.rst`, the module `example.py`, and the `index.rst` and `conf.py` content shown under **Code example**.
3. In `conf.py`, set `autosummary_generate = True` and `autosummary_imported_members = False`.
4. Build the documentation.
5. Open the generated file `generated/example.rst`.

## Observed behavior
The `members` variable lists the imported module `os`, along with module attributes such as `__builtins__` and `__doc__`. The generated `generated/example.rst` is:

```
example
=======

.. automodule:: example

   .. autosummary::

      __builtins__
      __cached__
      __doc__
      __file__
      __loader__
      __name__
      __package__
      __spec__
      os
```

## Expected behavior
When `autosummary_imported_members` is `False`, the template variable `members` should not contain imported members. In this example, `os` should not appear in `generated/example.rst`.

## Stack trace / error output
Not provided in the original report. No error is raised; the problem is incorrect generated output.

## Test case
A minimal test case based on the reproduction in the report:

- **Setup:** Use the four files under **Code example**, with `autosummary_generate = True` and `autosummary_imported_members = False`.
- **Action:** Build the documentation so that autosummary generates `generated/example.rst`.
- **Assertion:** The `autosummary` list in `generated/example.rst` does not contain `os`, which is the member imported by `example.py`.

## Code example
`_templates/autosummary/module.rst`:
```
{{ fullname | escape | underline }}

.. automodule:: {{ fullname }}

   .. autosummary::
   {% for item in members %}
      {{ item }}
   {%- endfor %}
```

`example.py`:
```python
import os
```

`index.rst`:
```
.. autosummary::
   :toctree: generated

   example
```

`conf.py`:
```python
autosummary_generate = True
autosummary_imported_members = False
```

## Version and environment
- OS: Mac
- Python version: 3.8.2
- Sphinx version: 3.1.0dev
- Sphinx extensions: `sphinx.ext.autosummary`
- Extra tools: None