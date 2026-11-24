## Summary
Show the units of coordinates and data variables in the `xarray.Dataset` repr.

## Description
The `Dataset` overview (repr) currently lists coordinates and data variables with their names, dimensions, dtypes and values, but not their units. The request is to include the units of each coordinate and data variable in this overview.

Current output for a hypothetical dataset:

```
<xarray.Dataset>
Dimensions:  (time: 3, x: 988, y: 822)
Coordinates:
  * x         (x) float64 ...
  * y         (y) float64 ...
  * time      (time) datetime64[ns] ...
Data variables:
    rainfall  (time, y, x) float32 ...
    max_temp  (time, y, x) float32 ...
```

## Product version
Not provided in the original request.

## Rationale
The original request says only that showing units in the repr "would be really nice." It gives no further reason why the feature is needed.

## Use case or scenario
A user inspects a dataset with spatial coordinates `x` and `y` in metres, a `time` coordinate, and data variables `rainfall` in mm and `max_temp` in deg C. The user wants to see the units of each coordinate and variable directly in the `Dataset` repr.

## Possible solution
The request suggests appending the unit to each name in the repr, in the form `<name>, in <unit>`, and aligning the remaining columns:

```
<xarray.Dataset>
Dimensions:  (time: 3, x: 988, y: 822)
Coordinates:
  * x, in metres         (x)            float64 ...
  * y, in metres         (y)            float64 ...
  * time                 (time)         datetime64[ns] ...
Data variables:
    rainfall, in mm      (time, y, x)   float32 ...
    max_temp, in deg C   (time, y, x)   float32 ...
```

In this example, entries without a unit, such as `time`, are shown without the `, in <unit>` suffix.