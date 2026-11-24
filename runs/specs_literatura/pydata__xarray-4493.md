## Summary

Wrapping a dask-backed (chunked) `DataArray` in a `(dims, data)` tuple, either in `Dataset.update` or in the `Dataset` constructor, makes xarray compute the dask array eagerly. The resulting variable holds a `numpy.ndarray` instead of a dask array, so it is no longer chunked. This report merges two issues that show the same behavior:

1. `Dataset.update` with a `{"name": (dims, chunked_DataArray)}` mapping loses chunking.
2. `xr.Dataset(dict(a=(dims, chunked_DataArray)))` loses chunking. The reporter asks whether this is intentional, e.g. why `xr.Dataset(dict(a=('d0', xr.DataArray(da.random.random(10)))))` causes the dask array to compute.

Passing the chunked `DataArray` directly, without a `(dims, ...)` tuple, keeps it lazy.

## Steps to reproduce

**Scenario A: `Dataset.update`**

1. Create a chunked DataArray: `foo = xr.DataArray(np.random.randn(3, 3), dims=("x", "y")).chunk()`.
2. Build a Dataset from it: `ds = xr.Dataset({"foo": foo, "bar": ("x", [1, 2, 3])})`. Inspect `ds`. `foo` is chunked.
3. Build an update mapping that uses tuples: `update_dict = {"foo": (("x", "y"), ds.foo[1:, :]), "bar": ("x", ds.bar[1:])}`. `update_dict["foo"][1]` is still chunked.
4. Call `ds.update(update_dict)`.
5. Inspect `ds`. `foo` is no longer chunked.

**Scenario B: `Dataset` constructor**

1. Create a dask array: `x = da.random.randint(1, 10, size=(100, 25))`.
2. Build a Dataset by passing the DataArray directly: `ds = xr.Dataset(dict(a=xr.DataArray(x, dims=('x', 'y'))))`. `type(ds.a.data)` is `dask.array.core.Array`.
3. Build a second Dataset from the same DataArray, wrapped in a tuple that redefines the dimensions: `ds2 = xr.Dataset(dict(a=(('x', 'y'), ds.a)))`.
4. Check `type(ds2.a.data)`. It is `numpy.ndarray`.

## Observed behavior

- Scenario A: after `ds.update(update_dict)`, `ds.foo` is no longer chunked. Its dask values have been evaluated eagerly.
- Scenario B: `type(ds2.a.data)` is `numpy.ndarray`. The dask array was computed when the Dataset was constructed.

## Expected behavior

- Scenario A: `ds.foo` should still be chunked (dask-backed) after `Dataset.update`.
- Scenario B: `ds2.a.data` should still be a dask array, as it is for `ds.a.data`. Constructing a Dataset should not trigger computation.

## Stack trace / error output

Not provided in the original report. No error is raised. The problem is silent eager computation. Output from the report:

```
>>> type(ds.a.data)
dask.array.core.Array
>>> type(ds2.a.data)
numpy.ndarray
```

## Test case

Minimal checks derived from the report's snippets (imports added for completeness):

```python
import numpy as np
import dask.array as da
import xarray as xr


def test_update_preserves_chunks():
    foo = xr.DataArray(np.random.randn(3, 3), dims=("x", "y")).chunk()
    ds = xr.Dataset({"foo": foo, "bar": ("x", [1, 2, 3])})
    assert isinstance(ds.foo.data, da.Array)

    update_dict = {"foo": (("x", "y"), ds.foo[1:, :]), "bar": ("x", ds.bar[1:])}
    assert isinstance(update_dict["foo"][1].data, da.Array)

    ds.update(update_dict)
    assert isinstance(ds.foo.data, da.Array)  # fails: foo is no longer chunked


def test_constructor_with_dims_tuple_preserves_dask():
    x = da.random.randint(1, 10, size=(100, 25))
    ds = xr.Dataset(dict(a=xr.DataArray(x, dims=("x", "y"))))
    assert isinstance(ds.a.data, da.Array)

    ds2 = xr.Dataset(dict(a=(("x", "y"), ds.a)))
    assert isinstance(ds2.a.data, da.Array)  # fails: data is numpy.ndarray
```

## Code example

Scenario A, from the report:

```python
foo = xr.DataArray(np.random.randn(3, 3), dims=("x", "y")).chunk()  # foo is chunked
ds = xr.Dataset({"foo": foo, "bar": ("x", [1, 2, 3])})  # foo is still chunked here
ds  # you can verify that foo is chunked

update_dict = {"foo": (("x", "y"), ds.foo[1:, :]), "bar": ("x", ds.bar[1:])}
update_dict["foo"][1]  # foo is still chunked

ds.update(update_dict)
ds  # now foo is no longer chunked
```

Scenario B, from the report:

```python
import dask.array as da
import xarray as xr
x = da.random.randint(1, 10, size=(100, 25))
ds = xr.Dataset(dict(a=xr.DataArray(x, dims=('x', 'y'))))
type(ds.a.data)
# dask.array.core.Array

# Recreate the dataset with the same array, but also redefine the dimensions
ds2 = xr.Dataset(dict(a=(('x', 'y'), ds.a)))
type(ds2.a.data)
# numpy.ndarray
```

One-liner from the report: `xr.Dataset(dict(a=('d0', xr.DataArray(da.random.random(10)))))` causes the dask array to compute.

## Version and environment

Scenario A (from `xr.show_versions()`):

- xarray: 0.16.0
- dask: 2.20.0
- distributed: 2.20.0
- numpy: 1.18.5
- pandas: 1.0.5
- scipy: 1.5.0
- h5py: 2.10.0
- matplotlib: 3.2.2
- setuptools: 49.2.0.post20200714
- pip: 20.1.1
- pytest: 5.4.3
- IPython: 7.16.1
- python: 3.8.3 (default, Jul 2 2020, 11:26:31) [Clang 10.0.0], 64-bit
- OS: Darwin, OS-release 19.6.0, machine x86_64, processor i386
- LANG / LOCALE: en_US.UTF-8
- libhdf5: 1.10.6
- netCDF4, h5netcdf, zarr, cftime, bottleneck, pint, etc.: None

Scenario B: Not provided in the original report.