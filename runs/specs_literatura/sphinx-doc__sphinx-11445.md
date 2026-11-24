## Summary

When `rst_prolog` is set in `conf.py`, a document whose first (top-level) heading contains a domain role (e.g. ``:mod:`mypackage2` ``) does not render that heading correctly, and the heading is not included in the toctree. The heading renders correctly if it is plain text (e.g. `mypackage2`) or if `rst_prolog` is not set. The reporter can also reproduce this in Sphinx v4.0.0, so it has been present for some time.

## Steps to reproduce

1. Create a new project:
   ```bash
   sphinx-quickstart --no-sep --project mypackage --author me -v 0.1.0 --release 0.1.0 --language en docs
   ```
2. Write `docs/index.rst`:
   ```bash
   echo -e 'Welcome\n=======\n\n.. toctree::\n\n   mypackage\n' > docs/index.rst
   ```
3. Write `docs/mypackage.rst`, whose top-level heading uses the `:mod:` role:
   ```bash
   echo -e ':mod:`mypackage2`\n=================\n\nContent\n\nSubheading\n----------\n' > docs/mypackage.rst
   ```
4. Add an `rst_prolog` to `docs/conf.py`:
   ```bash
   echo -e 'rst_prolog = """\n.. |psf| replace:: Python Software Foundation\n"""\n' >> docs/conf.py
   ```
5. Build the HTML output:
   ```bash
   sphinx-build -b html . _build
   ```
6. Check whether the heading appears in the generated index page:
   ```bash
   grep 'mypackage2' docs/_build/index.html
   ```

Note: The commands are given exactly as in the original report. The build command in step 5 uses `.` and `_build`, while step 6 reads `docs/_build/index.html`. This implies that the build is run from inside `docs/`.

## Observed behavior

- The top-level heading ``:mod:`mypackage2` `` in `mypackage.rst` does not render correctly.
- The heading is not included in the toctree. `grep 'mypackage2'` on the built `index.html` does not find it.

## Expected behavior

The heading ``:mod:`mypackage2` `` should render correctly and appear in the toctree of `index.html`. This is what happens when:
- the heading is plain text (`mypackage2` instead of ``:mod:`mypackage2` ``), or
- `rst_prolog` is not set.

## Stack trace / error output

Not provided in the original report.

## Test case

A minimal test case derived from the reproduction:

- `conf.py`:
  ```python
  rst_prolog = """
  .. |psf| replace:: Python Software Foundation
  """
  ```
- `index.rst`:
  ```rst
  Welcome
  =======

  .. toctree::

     mypackage
  ```
- `mypackage.rst`:
  ```rst
  :mod:`mypackage2`
  =================

  Content

  Subheading
  ----------
  ```
- Build with the `html` builder and check that `_build/index.html` contains `mypackage2`.
  - **Expected:** the string is present.
  - **Currently:** the string is absent.

## Code example

`docs/index.rst`:

```rst
Welcome
=======

.. toctree::

   mypackage
```

`docs/mypackage.rst`:

```rst
:mod:`mypackage2`
=================

Content

Subheading
----------
```

Addition to `docs/conf.py`:

```python
rst_prolog = """
.. |psf| replace:: Python Software Foundation
"""
```

## Version and environment

```text
Platform:              linux; (Linux-6.3.2-arch1-1-x86_64-with-glibc2.37)
Python version:        3.11.3 (main, Apr  5 2023, 15:52:25) [GCC 12.2.1 20230201])
Python implementation: CPython
Sphinx version:        7.1.0+/d3c91f951
Docutils version:      0.20.1
Jinja2 version:        3.1.2
Pygments version:      2.15.1
```

- Sphinx extensions: none (`[]`)
- Also reproducible in Sphinx v4.0.0, according to the reporter.