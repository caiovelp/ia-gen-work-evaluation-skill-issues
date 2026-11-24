## Summary

With `autodoc_typehints = "description"`, autodoc duplicates `*args` and `**kwargs` in the "Parameters" list of an `__init__` method that documents them as `:param *args:` and `:param **kwargs:`. One set of entries has the description but no type. The other has the type but no description and loses the `*`/`**` prefix. The class-level "Parameters" list also shows `args` and `kwargs` without their `*`/`**` prefix.

## Steps to reproduce

1. Enable the Sphinx autodoc extension and set `autodoc_typehints = "description"`.
2. Define the class shown in **Code example**. Its `__init__` has type hints for `x`, `*args` and `**kwargs` and documents them as `:param x:`, `:param *args:` and `:param **kwargs:`.
3. Document the class with autodoc and build the documentation.
4. Look at the "Parameters" sections for the class and for `__init__`.

## Observed behavior

With Sphinx 4.2.0, the output is:

```
Class docstring.

   Parameters:
      * **x** (*int*) --

      * **args** (*int*) --

      * **kwargs** (*int*) --

   Return type:
      None

   __init__(x, *args, **kwargs)

      Init docstring.

      Parameters:
         * **x** (*int*) -- Some integer

         * ***args** --

           Some integer

         * ****kwargs** --

           Some integer

         * **args** (*int*) --

         * **kwargs** (*int*) --

      Return type:
         None
```

- In the `__init__` section, `*args` and `**kwargs` each appear twice. The `*args`/`**kwargs` entries have the description but no type. The `args`/`kwargs` entries have the type `(int)` but no description and no `*`/`**` prefix.
- In the class section, the parameters appear as `args` and `kwargs`, without the `*`/`**` prefix.

## Expected behavior

Each of `*args` and `**kwargs` should appear once, with its `*`/`**` prefix, its type and its description:

```
  Class docstring.

   Parameters:
      * **x** (*int*) --

      * ***args** (*int*) --

      * ****kwargs** (*int*) --

   Return type:
      None

   __init__(x, *args, **kwargs)

      Init docstring.

      Parameters:
         * **x** (*int*) -- Some integer

         * ***args** (*int*) --

           Some integer

         * ****kwargs** (*int*) --

           Some integer

      Return type:
         None
```

## Stack trace / error output

Not provided in the original report. No error is raised; the problem is in the rendered output.

## Test case

Not provided in the original report. The class in **Code example** plus the setting `autodoc_typehints = "description"` is the minimal reproduction input. The expected rendered output is shown under **Expected behavior**.

## Code example

```python
class _ClassWithDocumentedInitAndStarArgs:
    """Class docstring."""

    def __init__(self, x: int, *args: int, **kwargs: int) -> None:
        """Init docstring.

        :param x: Some integer
        :param *args: Some integer
        :param **kwargs: Some integer
        """
```

Configuration:

```python
autodoc_typehints = "description"
```

## Version and environment

- Sphinx 4.2.0
- Extension: `sphinx.ext.autodoc` with `autodoc_typehints = "description"`
- Python version, OS and other environment details: Not provided in the original report.