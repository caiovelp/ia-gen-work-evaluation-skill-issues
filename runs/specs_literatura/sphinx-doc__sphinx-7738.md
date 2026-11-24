## Summary
With `sphinx.ext.napoleon`, an attribute named with a trailing underscore (`hello_`) in a NumPy-style `Attributes` section is over-escaped. It renders as `hello\_` in the HTML output, with a visible backslash. The reporter says older versions such as Sphinx 2.4.3 render it correctly.

## Steps to reproduce
1. Create an empty `__init__.py`.
2. Create `a.py` with the content shown under "Code example" below.
3. Run `sphinx-quickstart`.
4. In `conf.py`, add `'sphinx.ext.autodoc'` and `'sphinx.ext.napoleon'` to `extensions`.
5. Add the following to `index.rst`:
   ```rst
   .. autoclass:: a.A
   ```
6. Build the docs:
   ```sh
   PYTHONPATH=. make clean html
   ```
7. Open `_build/html/index.html` in a web browser.

## Observed behavior
The attribute name appears as `hello\_` in the rendered HTML, with a visible backslash before the trailing underscore.

## Expected behavior
There should be no backslash. The attribute name should render as `hello_`, similar to the output of this hand-written reST:

```rst
    .. attribute:: hello_
        :type: int

        hi
```

(The reporter notes that the type is also displayed differently, but that is not what this report is about.)

Older versions such as Sphinx 2.4.3 render the name without the backslash.

## Stack trace / error output
Not provided in the original report.

## Test case
Not provided in the original report.

A minimal test case based on the reproduction: document class `A` from the code example below with `autoclass` while `sphinx.ext.autodoc` and `sphinx.ext.napoleon` are enabled. Then check that the attribute name in the generated HTML is `hello_`, not `hello\_`.

## Code example
`a.py`:
```python
class A:
    """
    Attributes
    ----------
    hello_: int
        hi
    """
    pass
```

## Version and environment
- OS: Linux Debian testing
- Python version: 3.8.3
- Sphinx version: 3.0.4 (the reporter says older versions such as 2.4.3 behave correctly)
- Sphinx extensions: `sphinx.ext.autodoc`, `sphinx.ext.napoleon`
- Extra tools: Not provided in the original report.