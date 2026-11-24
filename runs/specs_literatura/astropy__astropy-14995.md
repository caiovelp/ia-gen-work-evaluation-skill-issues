## Summary

In astropy v5.3, `NDDataRef` arithmetic with `handle_mask=np.bitwise_or` raises a `TypeError` when one operand has a mask and the other does not. This happens whether the unmasked operand is a scalar constant or an `NDDataRef` without a mask. The same operations work without error in v5.2, so this is a regression.

The reporter suspects, from the error message, that the operand without a mask is treated as a mask of `None` values. `np.bitwise_or` then tries to combine an `int` with `None` and fails.

## Steps to reproduce

1. Install astropy v5.3.
2. Create a data array and an integer bitmask:
   ```python
   import numpy as np
   from astropy.nddata import NDDataRef

   array = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
   mask = np.array([[0, 1, 64], [8, 0, 1], [2, 1, 0]])
   ```
3. Create one `NDDataRef` without a mask and one with a mask:
   ```python
   nref_nomask = NDDataRef(array)
   nref_mask = NDDataRef(array, mask=mask)
   ```
4. Multiply the masked `NDDataRef` by a constant, using `handle_mask=np.bitwise_or`:
   ```python
   nref_mask.multiply(1., handle_mask=np.bitwise_or).mask
   ```
5. Multiply the masked `NDDataRef` by the unmasked one, using `handle_mask=np.bitwise_or`:
   ```python
   nref_mask.multiply(nref_nomask, handle_mask=np.bitwise_or).mask
   ```

## Observed behavior

The results of each combination in v5.3:

| Operation | Operands | Result |
|---|---|---|
| `nref_nomask.multiply(1., handle_mask=np.bitwise_or)` | no mask × constant | No mask returned (OK) |
| `nref_nomask.multiply(nref_nomask, handle_mask=np.bitwise_or)` | no mask × no mask | No mask returned (OK) |
| `nref_mask.multiply(nref_mask, handle_mask=np.bitwise_or)` | mask × mask | Returns the mask as expected (OK) |
| `nref_mask.multiply(1., handle_mask=np.bitwise_or)` | mask × constant | **`TypeError`** |
| `nref_mask.multiply(nref_nomask, handle_mask=np.bitwise_or)` | mask × no mask | **`TypeError`** |

In v5.2, none of these operations raise an error.

## Expected behavior

When only one operand has a mask, the existing mask should be copied to the output, as in v5.2. For both failing cases, the expected resulting mask is:

```
array([[ 0,  1, 64],
       [ 8,  0,  1],
       [ 2,  1,  0]])
```

## Stack trace / error output

The full traceback was not included in the original report (it was elided with `...`). Both failing cases end with this error:

```
TypeError: unsupported operand type(s) for |: 'int' and 'NoneType'
```

## Test case

This minimal test is derived from the reproduction in the report. It passes on v5.2 and fails on v5.3, according to the report.

```python
import numpy as np
from astropy.nddata import NDDataRef


def test_bitwise_or_mask_propagation_with_one_unmasked_operand():
    array = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    mask = np.array([[0, 1, 64], [8, 0, 1], [2, 1, 0]])

    nref_nomask = NDDataRef(array)
    nref_mask = NDDataRef(array, mask=mask)

    # no mask * constant -> no mask (works in v5.3)
    assert nref_nomask.multiply(1., handle_mask=np.bitwise_or).mask is None

    # no mask * no mask -> no mask (works in v5.3)
    assert nref_nomask.multiply(nref_nomask, handle_mask=np.bitwise_or).mask is None

    # mask * mask -> mask (works in v5.3)
    np.testing.assert_array_equal(
        nref_mask.multiply(nref_mask, handle_mask=np.bitwise_or).mask, mask
    )

    # mask * constant -> existing mask copied (raises TypeError in v5.3)
    np.testing.assert_array_equal(
        nref_mask.multiply(1., handle_mask=np.bitwise_or).mask, mask
    )

    # mask * no mask -> existing mask copied (raises TypeError in v5.3)
    np.testing.assert_array_equal(
        nref_mask.multiply(nref_nomask, handle_mask=np.bitwise_or).mask, mask
    )
```

## Code example

The original interactive session from the report:

```python
>>> import numpy as np
>>> from astropy.nddata import NDDataRef

>>> array = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
>>> mask = np.array([[0, 1, 64], [8, 0, 1], [2, 1, 0]])

>>> nref_nomask = NDDataRef(array)
>>> nref_mask = NDDataRef(array, mask=mask)

# multiply no mask by constant (no mask * no mask)
>>> nref_nomask.multiply(1., handle_mask=np.bitwise_or).mask   # returns nothing, no mask,  OK

# multiply no mask by itself (no mask * no mask)
>>> nref_nomask.multiply(nref_nomask, handle_mask=np.bitwise_or).mask # return nothing, no mask, OK

# multiply mask by constant (mask * no mask)
>>> nref_mask.multiply(1., handle_mask=np.bitwise_or).mask
...
TypeError: unsupported operand type(s) for |: 'int' and 'NoneType'

# multiply mask by itself (mask * mask)
>>> nref_mask.multiply(nref_mask, handle_mask=np.bitwise_or).mask
array([[ 0,  1, 64],
       [ 8,  0,  1],
       [ 2,  1,  0]])

# multiply mask by no mask (mask * no mask)
>>> nref_mask.multiply(nref_nomask, handle_mask=np.bitwise_or).mask
...
TypeError: unsupported operand type(s) for |: 'int' and 'NoneType'
```

## Version and environment

- **astropy:** 5.3 (affected); 5.2 reported as not affected
- **Python:** 3.10.11 | packaged by conda-forge | (main, May 10 2023, 19:07:22) [Clang 14.0.6]
- **NumPy:** 1.24.3
- **pyerfa:** 2.0.0.3
- **SciPy:** 1.10.1
- **Matplotlib:** 3.7.1
- **Operating system:** Not provided in the original report (the compiler string suggests a conda-forge build using Clang).