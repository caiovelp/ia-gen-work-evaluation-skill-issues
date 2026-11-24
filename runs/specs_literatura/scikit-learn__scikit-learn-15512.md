## Summary

`AffinityPropagation` does not return the documented values when it does not converge. The documentation says: "When the algorithm does not converge, it returns an empty array as cluster_center_indices and -1 as label for each training sample." In the example below the algorithm does not converge (`max_iter=2`), yet it returns a cluster center and non-negative labels. The only way the reporter has found to detect non-convergence is the `verbose` option, which is inconvenient in a larger script. Checking `max_iter == n_iter_` is unreliable. Without a reliable signal, a user may not know the clustering never converged. The reporter is unsure whether the behavior or the documentation is wrong.

## Steps to reproduce

1. Create a pandas DataFrame with three samples: `[[1,0,0,0,0,0],[0,1,1,1,0,0],[0,0,1,0,0,1]]`.
2. Fit `AffinityPropagation(affinity='euclidean', verbose=True, copy=False, max_iter=2)` on it. With `max_iter=2`, the algorithm does not converge.
3. Print `af.cluster_centers_indices_` and `af.labels_`.

## Observed behavior

- `cluster_centers_indices_` is `[2]`.
- `labels_` is `[0, 0, 0]`.

Nothing in the returned attributes shows that the clustering did not converge.

## Expected behavior

As documented for the non-converged case:

- `cluster_centers_indices_` is an empty array.
- `labels_` is `[-1, -1, -1]`.

## Stack trace / error output

Not provided in the original report. No exception is raised. The verbose output is not included in the report.

## Test case

Minimal test derived from the reporter's example and the documented behavior:

```python
from sklearn.cluster import AffinityPropagation
import pandas as pd

def test_affinity_propagation_non_convergence_return_values():
    data = pd.DataFrame([[1,0,0,0,0,0],[0,1,1,1,0,0],[0,0,1,0,0,1]])
    af = AffinityPropagation(affinity='euclidean', verbose=True, copy=False, max_iter=2).fit(data)

    # Documented: empty array of cluster center indices and -1 labels when not converged
    assert len(af.cluster_centers_indices_) == 0
    assert list(af.labels_) == [-1, -1, -1]
```

## Code example

```python
from sklearn.cluster import AffinityPropagation
import pandas as pd

data = pd.DataFrame([[1,0,0,0,0,0],[0,1,1,1,0,0],[0,0,1,0,0,1]])
af = AffinityPropagation(affinity='euclidean', verbose=True, copy=False, max_iter=2).fit(data)

print(af.cluster_centers_indices_)
print(af.labels_)
```

## Version and environment

- OS / machine: Linux-4.15.0-52-generic-x86_64-with-debian-stretch-sid
- Python: 3.6.7 | packaged by conda-forge | (default, Nov 21 2018, 02:32:25) [GCC 4.8.2 20140120 (Red Hat 4.8.2-15)]
- BLAS: MKL (`SCIPY_MKL_H=None, HAVE_CBLAS=None`; cblas_libs: `mkl_rt, pthread`)
- sklearn: 0.20.3
- numpy: 1.15.4
- scipy: 1.2.0
- pandas: 0.23.4
- Cython: 0.29.2
- pip: 18.1
- setuptools: 40.6.3