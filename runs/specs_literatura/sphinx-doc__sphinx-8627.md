## Summary

When `struct.Struct` appears in a type annotation of a function documented with `sphinx.ext.autodoc`, Sphinx cannot resolve the reference and reports `class reference target not found: Struct`. Other standard-library types in the same module, such as `pathlib.Path`, resolve correctly.

## Steps to reproduce

1. Create a module `helloworld.helloworld` (file `helloworld.py`) with the contents shown under **Code example**.
2. Create a minimal `index.rst` in `docs/`:
   ```rst
   Hello World
   ===========

   code docs
   =========

   .. automodule:: helloworld.helloworld
   ```
3. Enable these extensions in the Sphinx configuration: `sphinx.ext.autodoc`, `sphinx.ext.autosectionlabel`, `sphinx.ext.intersphinx`, `sphinx.ext.doctest`, `sphinx.ext.todo`.
4. Build the documentation:
   ```
   python3 -m sphinx -b html docs/ doc-out -nvWT
   ```
5. Observe the reported message about `Struct`.
6. For comparison, comment out the two functions annotated with `struct.Struct` (`consume_struct` and `make_struct`) and build again. `pathlib.Path` resolves and appears in the generated documentation.

## Observed behavior

The build reports:

```
class reference target not found: Struct
```

The `struct.Struct` annotations are not resolved. The `pathlib.Path` annotation in the same module resolves without problems.

## Expected behavior

`struct.Struct` in type annotations should resolve the same way `pathlib.Path` does, without a "reference target not found" message.

## Stack trace / error output

```
class reference target not found: Struct
```

No further output or traceback was provided in the original report.

## Test case

A minimal reproduction based on the report:

`helloworld/helloworld.py`:
```python
import struct

def consume_struct(_: struct.Struct) -> None:
    pass
```

`docs/index.rst`:
```rst
.. automodule:: helloworld.helloworld
```

Build with `python3 -m sphinx -b html docs/ doc-out -nvWT`.

- **Expected:** no `class reference target not found: Struct` message.
- **Actual:** the message is reported.

## Code example

`helloworld.py` as given in the report:

```python
import struct
import pathlib

def consume_struct(_: struct.Struct) -> None:
    pass

def make_struct() -> struct.Struct:
    mystruct = struct.Struct('HH')
    return mystruct

def make_path() -> pathlib.Path:
    return pathlib.Path()
```

## Version and environment

- **OS:** Ubuntu 18.04, 20.04
- **Python:** 3.8.2
- **Sphinx:** 3.2.1
- **Sphinx extensions:** `sphinx.ext.autodoc`, `sphinx.ext.autosectionlabel`, `sphinx.ext.intersphinx`, `sphinx.ext.doctest`, `sphinx.ext.todo`
- **Build command:** `python3 -m sphinx -b html docs/ doc-out -nvWT`