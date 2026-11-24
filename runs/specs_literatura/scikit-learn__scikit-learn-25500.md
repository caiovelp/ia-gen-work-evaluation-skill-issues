## Summary

`CalibratedClassifierCV` with `method='isotonic'` fails at prediction time after `set_config(transform_output="pandas")` has been called. The reporter believes the fitted `IsotonicRegression` calibrator returns a pandas DataFrame instead of a 1-D array. In `_CalibratedClassifier.predict_proba`, the line `proba[:, class_idx] = calibrator.predict(this_pred)` then tries to assign that 2-D output into a 1-D column of a NumPy array, which raises a `ValueError` broadcast error.

## Steps to reproduce

1. Enable pandas output globally with `set_config(transform_output="pandas")`.
2. Create `CalibratedClassifierCV(SGDClassifier(), method='isotonic')`.
3. Fit it on numeric data, e.g. `X = np.arange(90).reshape(30, -1)` and `y = np.arange(30) % 2`.
4. Call `model.predict(X)`. Per the reporter, it crashes.

```python
import numpy as np
from sklearn import set_config
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import SGDClassifier

set_config(transform_output="pandas")
model = CalibratedClassifierCV(SGDClassifier(), method='isotonic')
model.fit(np.arange(90).reshape(30, -1), np.arange(30) % 2)
model.predict(np.arange(90).reshape(30, -1))
```

## Observed behavior

Prediction crashes with:

```
ValueError: could not broadcast input array from shape (20,1) into shape (20,)
```

The error is raised in `sklearn/calibration.py`, in `_CalibratedClassifier.predict_proba`, at `proba[:, class_idx] = calibrator.predict(this_pred)`. The calibrator's output is 2-D with shape `(n, 1)`, which the reporter attributes to `IsotonicRegression` returning a DataFrame. The target slice is 1-D with shape `(n,)`.

Note: the traceback below comes from the reporter's own project, where `CalibratedClassifierCV` is the last step of a `Pipeline` run through `cross_val_predict` (hence 20 test samples). It is not the output of the minimal snippet above. The report does not include the snippet's exact output.

## Expected behavior

`predict` (and `predict_proba`) on `CalibratedClassifierCV` with `method='isotonic'` should run without crashing when `transform_output="pandas"` is set.

## Stack trace / error output

```
../core/model_trainer.py:306: in train_model
    cv_predictions = cross_val_predict(pipeline,
.../site-packages/sklearn/model_selection/_validation.py:968: in cross_val_predict
    predictions = parallel(
.../site-packages/joblib/parallel.py:1085: in __call__
    if self.dispatch_one_batch(iterator):
.../site-packages/joblib/parallel.py:901: in dispatch_one_batch
    self._dispatch(tasks)
.../site-packages/joblib/parallel.py:819: in _dispatch
    job = self._backend.apply_async(batch, callback=cb)
.../site-packages/joblib/_parallel_backends.py:208: in apply_async
    result = ImmediateResult(func)
.../site-packages/joblib/_parallel_backends.py:597: in __init__
    self.results = batch()
.../site-packages/joblib/parallel.py:288: in __call__
    return [func(*args, **kwargs)
.../site-packages/joblib/parallel.py:288: in <listcomp>
    return [func(*args, **kwargs)
.../site-packages/sklearn/utils/fixes.py:117: in __call__
    return self.function(*args, **kwargs)
.../site-packages/sklearn/model_selection/_validation.py:1052: in _fit_and_predict
    predictions = func(X_test)
.../site-packages/sklearn/pipeline.py:548: in predict_proba
    return self.steps[-1][1].predict_proba(Xt, **predict_proba_params)
.../site-packages/sklearn/calibration.py:477: in predict_proba
    proba = calibrated_classifier.predict_proba(X)
.../site-packages/sklearn/calibration.py:764: in predict_proba
    proba[:, class_idx] = calibrator.predict(this_pred)
E   ValueError: could not broadcast input array from shape (20,1) into shape (20,)
```

(`...` = `../../../../.anaconda3/envs/strategy-training/lib/python3.9`)

## Test case

A minimal test derived from the reproduction snippet. The only expectation is that no exception is raised:

```python
import numpy as np
from sklearn import set_config
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import SGDClassifier


def test_calibrated_classifier_isotonic_with_pandas_output():
    X = np.arange(90).reshape(30, -1)
    y = np.arange(30) % 2

    set_config(transform_output="pandas")
    try:
        model = CalibratedClassifierCV(SGDClassifier(), method="isotonic")
        model.fit(X, y)
        model.predict(X)  # should not raise
    finally:
        set_config(transform_output="default")
```

## Code example

The relevant line identified by the reporter in `sklearn/calibration.py` (`_CalibratedClassifier.predict_proba`, line 764 in 1.2.0):

```python
proba[:, class_idx] = calibrator.predict(this_pred)
```

## Version and environment

- scikit-learn: 1.2.0
- Python: 3.9.15 (main, Nov 24 2022, 14:31:59) [GCC 11.2.0]
- OS: Linux-5.15.0-57-generic-x86_64-with-glibc2.31
- numpy 1.23.5, scipy 1.9.3, pandas 1.4.1, joblib 1.2.0, threadpoolctl 3.1.0, matplotlib 3.6.3, pip 22.2.2, setuptools 62.3.2, Cython: None
- Built with OpenMP: True. Threadpools: libgomp (OpenMP, 12 threads), OpenBLAS 0.3.20 (numpy) and 0.3.18 (scipy), Haswell, pthreads, 12 threads each
- Environment: Anaconda env `strategy-training`