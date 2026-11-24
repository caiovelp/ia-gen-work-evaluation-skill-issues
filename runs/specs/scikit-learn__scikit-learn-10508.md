# Spec: LabelEncoder.transform returns an empty array for empty input regardless of fitted label dtype

## Objective

`sklearn.preprocessing.LabelEncoder.transform([])` behaves differently depending on the data used in `fit`:

- Fitted on integers (`[1, 2]`): returns `array([], dtype=int64)`.
- Fitted on strings (`["a", "b"]`): raises `TypeError: Cannot cast array data from dtype('float64') to dtype('<U32') according to the rule 'safe'`.

The traceback shows the error is raised from `np.searchsorted(self.classes_, y)` in `transform` (`sklearn/preprocessing/label.py`, line 134 in 0.19.1). An empty Python list becomes a `float64` array, and NumPy will not safely cast it to the string dtype of `classes_`.

**Goal:** transforming an empty input always returns an empty integer array, whatever dtype `classes_` has.

**User:** anyone calling `LabelEncoder.transform` on data that may be empty, such as filtered batches, empty splits, or pipeline edge cases.

**User story:** As a user, after I fit a `LabelEncoder` on any supported label type, I can call `transform([])` and get an empty array of encoded labels instead of an exception.

## Assumptions

1. The expected result is the one the numeric case already produces: a 1-D empty array of integer dtype (`int64` in the report), not one that depends on the dtype of `classes_`.
2. Only empty input is in scope. Behavior for non-empty input, including the error raised for unseen labels, must not change.
3. "Empty list" also covers other empty 1-D array-likes, such as `np.array([])` and an empty tuple.
4. Calling `transform` on an unfitted encoder must still raise the existing "not fitted" error, even when the input is empty.
5. The defect also affects other string-like and object `classes_` dtypes (for example, object arrays of mixed or `str` values), not only `<U…` unicode.
6. The fix belongs in the library code of `LabelEncoder` (the traceback points to `sklearn/preprocessing/label.py`). It must not require a change to NumPy.
7. The fix must work with the Python and NumPy versions the project currently supports. The report used Python 3.6.3 and scikit-learn 0.19.1, and the exact supported range is unknown.

## Tech Stack

- Python (report: 3.6.3; supported range unknown)
- scikit-learn (report: 0.19.1; target branch unknown)
- NumPy (version unknown; the failure involves `np.searchsorted` casting rules)

## Commands

- Build: unknown
- Test: unknown (the project's test runner and invocation are not visible in the issue)
- Lint: unknown
- Reproduce (from the issue):
  ```python
  from sklearn.preprocessing import LabelEncoder
  le = LabelEncoder()
  le.fit(["a", "b"])
  le.transform([])  # currently raises TypeError
  ```

## Project Structure

- `sklearn/preprocessing/label.py`: contains `LabelEncoder.transform` (taken from the traceback).
- Test file location for `LabelEncoder`: unknown.
- Changelog or what's-new location: unknown.

## Code Style

Unknown. The fix should follow the existing conventions in `sklearn/preprocessing/label.py`. No snippet is available from the issue.

## Testing Strategy

- Unit tests sit next to the existing `LabelEncoder` tests (location and framework unknown).
- Required test cases:
  - Fit on `[1, 2]`, then check that `transform([])` returns an empty integer array. This is a regression guard for the case that already works.
  - Fit on `["a", "b"]`, then check that `transform([])` returns an empty integer array. This is the case that currently fails.
  - Fit on an object-dtype array of strings, then check that `transform([])` returns an empty integer array.
  - Check that `transform(np.array([]))` returns an empty integer array for both numeric and string fits.
  - Check that `transform([])` on an unfitted encoder raises the existing not-fitted error.
  - Check that non-empty `transform` results and the error for unseen labels are unchanged.
- If `inverse_transform` and `fit_transform` are brought into scope (see Open Questions), add the matching empty-input tests for them.

## Boundaries

- **Always:**
  - Add regression tests that reproduce the issue.
  - Keep existing non-empty behavior and error messages unchanged.
  - Run the existing preprocessing test suite.
- **Ask first:**
  - Changing the return dtype of `transform`.
  - Changing `inverse_transform` or `fit_transform` behavior.
  - Changing input validation for non-empty inputs.
  - Adding dependencies or raising minimum NumPy or Python versions.
- **Never:**
  - Suppress the `TypeError` with a broad `try/except` that could hide real errors on non-empty input.
  - Change the dtype of `classes_`.
  - Modify vendored or external code.

## Success Criteria

1. After `le.fit(["a", "b"])`, `le.transform([])` returns an array with `shape == (0,)` and an integer dtype, and raises no exception.
2. After `le.fit([1, 2])`, `le.transform([])` still returns an array with `shape == (0,)` and an integer dtype.
3. The return dtype for empty input is the same whatever the fitted label dtype is (numeric, unicode string, or object).
4. `np.array([])` as input gives the same result as `[]`.
5. An unfitted encoder still raises the not-fitted error on empty input.
6. All existing `LabelEncoder` tests pass without modification.
7. The new regression tests fail on the current code and pass after the fix.

## Open Questions

1. Should the empty-result dtype be exactly `int64`, or the platform's default integer (`np.intp`)? For example, Windows with older NumPy may give `int32`.
2. Should `inverse_transform([])` also be guaranteed to return an empty array, and with what dtype: that of `classes_`, or something else?
3. Should `fit_transform([])` and `fit([])` (an empty fit) be addressed here, or stay out of scope?
4. Which input shapes count as "empty"? For example, should a 2-D empty input such as `[[]]` be rejected by the existing column-or-1-D validation?
5. Are other encoders in the same module affected and in scope for this issue, for example `LabelBinarizer` and `MultiLabelBinarizer` on empty input after a string fit?
6. Which branch or version should the fix target, and does it need a changelog entry?
7. What are the project's test, lint, and build commands, and where do the `LabelEncoder` tests live?