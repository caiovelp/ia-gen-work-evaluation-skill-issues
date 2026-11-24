## Summary

`VotingClassifier.fit` raises an `AttributeError` when `sample_weight` is passed and one of the estimators has been set to `None`, for example with `set_params(lr=None)`. According to the reporter, the `sample_weight` support code does not check whether an estimator is `None`.

## Steps to reproduce

1. Load the iris dataset with `load_iris(return_X_y=True)`.
2. Create a `VotingClassifier` with two estimators: `('lr', LogisticRegression())` and `('rf', RandomForestClassifier())`.
3. Call `fit(X, y, sample_weight=np.ones(y.shape))`. This first fit succeeds.
4. Set one estimator to `None` with `voter.set_params(lr=None)`.
5. Call `fit(X, y, sample_weight=np.ones(y.shape))` again.

## Observed behavior

The second call to `fit` (step 5) fails with an `AttributeError`, because the code tries to call `fit` on the `None` estimator.

## Expected behavior

The report implies that `fit` should not fail when an estimator has been set to `None` and `sample_weight` is passed.

## Stack trace / error output

```
AttributeError: 'NoneType' object has no attribute 'fit'
```

The full traceback was not provided in the original report.

## Test case

This is the reproduction snippet from the report. The imports (`load_iris`, `VotingClassifier`, `LogisticRegression`, `RandomForestClassifier`, `np`) are not shown in the original report.

```python
X, y = load_iris(return_X_y=True)
voter = VotingClassifier(
    estimators=[('lr', LogisticRegression()),
                ('rf', RandomForestClassifier())]
)
voter.fit(X, y, sample_weight=np.ones(y.shape))
voter.set_params(lr=None)
voter.fit(X, y, sample_weight=np.ones(y.shape))  # raises AttributeError
```

## Code example

See the test case above. The original report contains no other code.

## Version and environment

Not provided in the original report.