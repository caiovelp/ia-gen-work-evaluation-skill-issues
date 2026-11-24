## Summary

Running `KernelPCA` with the `rbf` kernel several times on the same dataset gives results that differ in sign. The absolute values match across runs, but the signs of some or all components flip from run to run.

## Steps to reproduce

1. Take a dataset `X`. The dataset is not provided in the original report.
2. Create a `KernelPCA` instance that reduces to 7 dimensions with the `rbf` kernel:
   `KernelPCA(n_components=7, kernel='rbf', copy_X=False, n_jobs=-1)`
3. Call `fit_transform(X)`.
4. Repeat steps 2–3 on the same dataset and compare the outputs.

## Observed behavior

The outputs have the same absolute values but different signs. Three runs gave these results for the same row:

```
[[-0.44457617 -0.18155886 -0.10873474  0.13548386 -0.1437174  -0.057469    0.18124364]]

[[ 0.44457617  0.18155886  0.10873474 -0.13548386 -0.1437174  -0.057469   -0.18124364]]

[[-0.44457617 -0.18155886  0.10873474  0.13548386  0.1437174   0.057469    0.18124364]]
```

Different components flip sign in different runs. Compared with the first run:
- In the second run, components 1, 2, 3, 4 and 7 have the opposite sign.
- In the third run, components 3, 5 and 6 have the opposite sign.

## Expected behavior

Running `fit_transform` on the same dataset with the same parameters should give the same result, including signs.

## Stack trace / error output

Not provided in the original report. No error is raised; the problem is inconsistent output.

## Test case

Not provided in the original report. A minimal check based on the reporter's snippet (the dataset `X` is not provided):

```python
pca1 = KernelPCA(n_components=7, kernel='rbf', copy_X=False, n_jobs=-1)
r1 = pca1.fit_transform(X)

pca2 = KernelPCA(n_components=7, kernel='rbf', copy_X=False, n_jobs=-1)
r2 = pca2.fit_transform(X)

# Expected: r1 and r2 are equal, including signs.
# Observed: values are equal in absolute value but signs differ.
```

## Code example

```python
pca = KernelPCA(n_components=7, kernel='rbf', copy_X=False, n_jobs=-1)
pca.fit_transform(X)
```

## Version and environment

- Version: 0.18.1 (the report does not name the package)
- OS, Python version and other environment details: Not provided in the original report.