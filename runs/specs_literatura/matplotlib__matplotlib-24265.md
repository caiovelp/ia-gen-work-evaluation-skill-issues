## Summary

Accessing the `seaborn-colorblind` entry in `matplotlib.pyplot.style.library` raises a `KeyError` on matplotlib 3.6.1. The same code works on matplotlib 3.4.3. This is a regression between those two versions. The failure happens when the reporter's code is imported, at the line `the_rc = plt.style.library["seaborn-colorblind"]`.

## Steps to reproduce

1. Install matplotlib 3.6.1 with pip, on Python 3.9.7.
2. Run the following code:
   ```python
   import matplotlib.pyplot as plt
   the_rc = plt.style.library["seaborn-colorblind"]
   ```
3. A `KeyError` is raised.
4. For comparison, run the same code with matplotlib 3.4.3. No error occurs.

## Observed behavior

On matplotlib 3.6.1, the lookup `plt.style.library["seaborn-colorblind"]` raises a `KeyError`, reporting `'seaborn-colorblind'` as a bad key. The behavior is the same on macOS and Ubuntu.

## Expected behavior

The lookup should succeed, as it does on matplotlib 3.4.3. The `seaborn-colorblind` style should be available from the style library so that the user can continue plotting with that style.

## Stack trace / error output

```
Traceback (most recent call last):
KeyError: 'seaborn-colorblind'
```

(The original report includes only these lines. The intermediate traceback frames were not provided.)

## Test case

A minimal test derived from the reproduction snippet. It passes on matplotlib 3.4.3 and fails on 3.6.1 according to the report:

```python
import matplotlib.pyplot as plt

def test_seaborn_colorblind_in_style_library():
    the_rc = plt.style.library["seaborn-colorblind"]  # raises KeyError on 3.6.1
```

## Code example

```python
import matplotlib.pyplot as plt
the_rc = plt.style.library["seaborn-colorblind"]
```

## Version and environment

- **Matplotlib version (affected):** 3.6.1
- **Matplotlib version (not affected):** 3.4.3
- **Python version:** 3.9.7
- **Operating system:** macOS (OS/X); the same behavior was also observed on Ubuntu
- **Backend:** MacOSX
- **Installation method:** pip
- **Jupyter version:** Not provided in the original report.