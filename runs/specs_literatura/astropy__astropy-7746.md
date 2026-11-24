## Summary

Passing empty lists/arrays to WCS transformation methods such as `WCS.wcs_pix2world` raises `InconsistentAxisTypesError` from wcslib. The call should succeed and return empty lists/arrays.

## Steps to reproduce

1. Create a `WCS` object from a FITS file (the reporter used `2MASS_h.fits`):
   ```python
   from astropy.wcs import WCS
   wcs = WCS('2MASS_h.fits')
   ```
2. Call a pixel-to-world transformation with an empty list for each axis and origin `0`:
   ```python
   wcs.wcs_pix2world([], [], 0)
   ```

## Observed behavior

The call raises `InconsistentAxisTypesError` from wcslib's `wcsp2s()`:

```
ncoord and/or nelem inconsistent with the wcsprm.
```

## Expected behavior

The call should not fail. It should return empty lists/arrays, one per world axis.

## Stack trace / error output

```
---------------------------------------------------------------------------
InconsistentAxisTypesError                Traceback (most recent call last)
<ipython-input-3-e2cc0e97941a> in <module>()
----> 1 wcs.wcs_pix2world([], [], 0)

~/Dropbox/Code/Astropy/astropy/astropy/wcs/wcs.py in wcs_pix2world(self, *args, **kwargs)
   1352         return self._array_converter(
   1353             lambda xy, o: self.wcs.p2s(xy, o)['world'],
-> 1354             'output', *args, **kwargs)
   1355     wcs_pix2world.__doc__ = """
   1356         Transforms pixel coordinates to world coordinates by doing

~/Dropbox/Code/Astropy/astropy/astropy/wcs/wcs.py in _array_converter(self, func, sky, ra_dec_order, *args)
   1267                     "a 1-D array for each axis, followed by an origin.")
   1268 
-> 1269             return _return_list_of_arrays(axes, origin)
   1270 
   1271         raise TypeError(

~/Dropbox/Code/Astropy/astropy/astropy/wcs/wcs.py in _return_list_of_arrays(axes, origin)
   1223             if ra_dec_order and sky == 'input':
   1224                 xy = self._denormalize_sky(xy)
-> 1225             output = func(xy, origin)
   1226             if ra_dec_order and sky == 'output':
   1227                 output = self._normalize_sky(output)

~/Dropbox/Code/Astropy/astropy/astropy/wcs/wcs.py in <lambda>(xy, o)
   1351             raise ValueError("No basic WCS settings were created.")
   1352         return self._array_converter(
-> 1353             lambda xy, o: self.wcs.p2s(xy, o)['world'],
   1354             'output', *args, **kwargs)
   1355     wcs_pix2world.__doc__ = """

InconsistentAxisTypesError: ERROR 4 in wcsp2s() at line 2646 of file cextern/wcslib/C/wcs.c:
ncoord and/or nelem inconsistent with the wcsprm.
```

## Test case

Minimal test derived from the reproduction above. It uses the same FITS file as the reporter.

```python
from astropy.wcs import WCS

def test_wcs_pix2world_empty_input():
    wcs = WCS('2MASS_h.fits')
    result = wcs.wcs_pix2world([], [], 0)
    # Expected: no exception, and an empty list/array returned for each axis
    for axis in result:
        assert len(axis) == 0
```

## Code example

```python
from astropy.wcs import WCS

wcs = WCS('2MASS_h.fits')
wcs.wcs_pix2world([], [], 0)  # raises InconsistentAxisTypesError
```

## Version and environment

- **Astropy version:** Not provided in the original report. The traceback shows the reporter was running astropy from a local source checkout.
- **wcslib version:** Not provided in the original report.
- **Python version / OS:** Not provided in the original report.
- **Interface:** The reproduction was run in an IPython session.