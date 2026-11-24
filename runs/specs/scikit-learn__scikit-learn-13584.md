# Spec: Fix `print_changed_only=True` repr crash for array-valued parameters

## Objective

With `sklearn.set_config(print_changed_only=True)`, printing an estimator whose parameter value is a NumPy array raises an exception instead of producing a repr.

**Reproduction (from the issue):**

```python
import sklearn
import numpy as np
from sklearn.linear_model import LogisticRegressionCV
sklearn.set_config(print_changed_only=True)
print(LogisticRegressionCV(Cs=np.array([0.1, 1])))
```

**Observed:**
`ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()`

**Expected:** The estimator prints normally. `Cs` appears in the output because its value differs from the default (`Cs=10`), for example `LogisticRegressionCV(Cs=array([0.1, 1. ]))`. The exact formatting is an open question.

**Likely cause (hypothesis, not verified):** The "changed only" logic decides whether to show a parameter by comparing its current value with the constructor default, using something like `value != default` in a boolean context. When the value is a multi-element `ndarray`, that comparison returns an array, and evaluating it as a bool raises the error.

**Users:** Anyone using the new repr with `print_changed_only=True` who passes array-like hyperparameters, such as `Cs`, `alphas`, `class_weight` arrays or `priors`. This includes indirect cases like notebooks, logging, and `repr()` inside error messages.

**Success means:** Printing never crashes because of a parameter's type. Changed parameters are shown and unchanged ones are hidden, as `print_changed_only` intends.

## Assumptions

1. The bug lives in the shared estimator pretty-printing / "changed parameters" helper. It is not specific to `LogisticRegressionCV`, so any estimator with an array-valued parameter is affected.
2. The failing step is the comparison between the current parameter value and the `__init__` default signature value. Array formatting itself is not the problem.
3. With `print_changed_only=False`, the same estimator prints without error. This is not stated in the issue and needs to be confirmed.
4. An array-valued parameter should be treated as "changed" whenever it is not the default. The default for `Cs` is a scalar (`10`), so any array counts as changed.
5. The fix must not change repr output for estimators whose parameters are all scalars, strings, `None` or estimators.
6. NaN defaults, if the current logic handles them specially, must keep working.

## Tech Stack

- Python, NumPy, scikit-learn. Exact supported versions are **unknown** (not in the issue).
- Global configuration via `sklearn.set_config(print_changed_only=...)`.

## Commands

All are **unknown**; they are not visible in the issue. These are placeholders to be filled from the repository's contributor docs.

```
Build:     unknown
Test:      unknown (likely a pytest invocation; exact command/flags not confirmed)
Lint:      unknown
```

## Project Structure

**Unknown.** The file containing the pretty-printer / changed-params logic and its test file are not visible in the issue. They must be located in the repository before implementation.

## Code Style

Follow the existing scikit-learn conventions in the affected module. No code snippet is available from the issue. The style reference is **unknown** until the file is inspected.

## Testing Strategy

- **Level:** Unit tests next to the existing tests for the estimator repr / pretty-printer. The location is unknown.
- **Regression test:** Reproduce the issue exactly. With `print_changed_only=True`, `repr(LogisticRegressionCV(Cs=np.array([0.1, 1])))` must not raise, and its output must contain `Cs`.
- **Additional cases to cover:**
  - Array parameter whose default is a scalar. This is the issue case.
  - Array parameter whose default is `None`.
  - Single-element array, which does not raise today but may be compared wrongly.
  - An unchanged scalar default is still hidden.
  - NaN-valued parameters keep their current behavior.
  - The same estimator with `print_changed_only=False` still prints correctly.
- **Config isolation:** Tests must restore the global config afterward, for example with a config context manager if one exists. Leaking `print_changed_only=True` into other tests must be avoided.
- **Coverage expectation:** Every newly added branch in the comparison logic is exercised by at least one test.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix and passes after.
  - Keep repr output unchanged for scalar-only estimators.
  - Run the existing repr / pretty-print test suite.
- **Ask first:**
  - Changing the documented semantics of "changed", for example comparing arrays element-wise against array defaults versus treating any array as changed.
  - Changing how arrays are formatted in the repr.
  - Touching public API or `set_config` behavior.
- **Never:**
  - Silence the error with a blanket `try/except` that hides parameters or prints wrong output.
  - Special-case `LogisticRegressionCV` or `Cs` only.
  - Remove or loosen existing repr tests.

## Success Criteria

1. The issue's reproduction script prints without raising.
2. The output includes `Cs` with its array value.
3. With `print_changed_only=True`, any estimator with an `ndarray` parameter value whose default is not an equal array prints without error and shows that parameter.
4. Parameters equal to their defaults remain hidden, including the NaN-default case if currently supported.
5. All existing repr / pretty-printer tests pass unchanged.
6. A regression test for this issue exists in the test suite.

## Open Questions

1. **Array vs. array defaults:** If a default value is itself an array and the user passes an equal array, should the parameter be hidden (element-wise equality) or shown (treat arrays as always changed)? Which do maintainers prefer for simplicity?
2. **Other array-likes:** Should lists, tuples, sparse matrices and pandas objects be handled too, or only `ndarray`? Lists compare fine with `!=`, but sparse and pandas objects may have their own ambiguous-truth behavior.
3. **Output format:** What exact repr string is expected for the array, e.g. `Cs=array([0.1, 1. ])`? Should long arrays be truncated?
4. **Affected versions:** Which released versions include the new repr with `print_changed_only`? Does the fix need a changelog entry or a backport?
5. **Location:** Which module and test file own the changed-params logic? Not visible from the issue.
6. **Commands:** What are the project's test and lint commands for this area? Unknown.
7. **Scope check with @NicolasHug:** Should other places that compare parameter values to defaults get the same fix in this change, or in a separate one?