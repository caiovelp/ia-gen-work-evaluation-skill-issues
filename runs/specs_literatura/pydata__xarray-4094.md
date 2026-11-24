## Summary

`DataArray.to_unstacked_dataset` fails with a `MergeError` when the stacked variables have only a single dimension. Stacking with `Dataset.to_stacked_array` and then unstacking with `to_unstacked_dataset` does not round-trip in this case. The reporter needs to stack several variables and later unstack them again, which does not work if the variables have only one dimension.

## Steps to reproduce

1. Create a one-dimensional `DataArray` with values `np.arange(3)` and coordinate `x = [0, 1, 2]`.
2. Build a `Dataset` with two variables, `a` and `b`, both set to that array.
3. Stack the dataset with `data.to_stacked_array('y', sample_dims=['x'])`.
4. Unstack the result with `stacked.to_unstacked_dataset('y')`.
5. Observe that a `MergeError` is raised.

## Observed behavior

`to_unstacked_dataset('y')` raises a `MergeError` saying there are conflicting values for variable `'y'`, instead of returning a Dataset.

## Expected behavior

The stack/unstack round trip works: `to_unstacked_dataset('y')` returns the original Dataset with variables `a` and `b`.

## Stack trace / error output

```
MergeError: conflicting values for variable 'y' on objects to be combined. You can skip this check by specifying compat='override'.
```

(Only the error message was provided. The full traceback is not in the original report.)

## Test case

Minimal round-trip test derived from the reporter's example:

```python
import numpy as np
import xarray as xr


def test_to_unstacked_dataset_roundtrip_single_dim():
    arr = xr.DataArray(
        np.arange(3),
        coords=[("x", [0, 1, 2])],
    )
    data = xr.Dataset({"a": arr, "b": arr})
    stacked = data.to_stacked_array("y", sample_dims=["x"])
    unstacked = stacked.to_unstacked_dataset("y")  # currently raises MergeError
    assert unstacked.identical(data)
```

## Code example

```python
import numpy as np
import xarray as xr

arr = xr.DataArray(
    np.arange(3),
    coords=[("x", [0, 1, 2])],
)
data = xr.Dataset({"a": arr, "b": arr})
stacked = data.to_stacked_array('y', sample_dims=['x'])
unstacked = stacked.to_unstacked_dataset('y')
# MergeError: conflicting values for variable 'y' on objects to be combined. You can skip this check by specifying compat='override'.
```

## Version and environment

Output of `xr.show_versions()`:

- **xarray:** 0.15.1
- **pandas:** 1.0.3
- **numpy:** 1.17.3
- **python:** 3.7.3 (default, Mar 27 2019, 22:11:17) [GCC 7.3.0], 64-bit
- **OS:** Linux, release 4.15.0-96-generic, x86_64, little endian
- **LANG / LOCALE:** en_GB.UTF-8 (LC_ALL: None)
- **libhdf5:** 1.10.4
- **libnetcdf:** 4.6.2

Other packages: scipy 1.3.1, netCDF4 1.4.2, h5py 2.10.0, cftime 1.0.4.2, dask 2.10.1, distributed 2.10.0, matplotlib 3.1.1, seaborn 0.10.0, setuptools 41.0.0, pip 19.0.3, conda 4.8.3, pytest 5.3.5, IPython 7.9.0.

Not installed (None): pydap, h5netcdf, Nio, zarr, nc_time_axis, PseudoNetCDF, rasterio, cfgrib, iris, bottleneck, cartopy, numbagg, sphinx.