# Spec: OneHotEncoder `handle_unknown='ignore'` with fixed-width string arrays

## Objective

Fix a bug in `sklearn.preprocessing.OneHotEncoder`. With `handle_unknown='ignore'`, `transform` can raise a spurious `ValueError` when the input is a NumPy fixed-width string array (for example `dtype '<U5'`).

**Root cause, as described in the issue:**
1. During `transform`, unknown entries are overwritten in place with a placeholder, `categories_[i][0]`. That is the first fitted category in sorted order.
2. The input array has a fixed-width string dtype. If the placeholder is longer than that width, NumPy silently truncates it.
3. The truncated value is not a known category, so the later label lookup raises `ValueError: y contains previously unseen labels: [...]`.

**Users:** anyone who one-hot encodes NumPy string arrays and relies on `handle_unknown='ignore'` to drop categories that were not seen during fit.

**User story:** As a user, I fit `OneHotEncoder(handle_unknown='ignore')` on string data. When I transform data that contains unseen strings, I expect all-zero indicator columns for those entries, no matter how long the strings in the fit and transform data are.

**Reproduction (from the issue):**
```python
import numpy as np
from sklearn.preprocessing import OneHotEncoder

train = np.array(['22', '333', '4444', '11111111']).reshape((-1, 1))
test  = np.array(['55555', '22']).reshape((-1, 1))

ohe = OneHotEncoder(dtype=bool, handle_unknown='ignore')
ohe.fit(train)
enc_test = ohe.transform(test)   # currently raises ValueError
```

**Expected result:** a 2×4 sparse matrix that is `False` everywhere except at (1, 1). Fitted categories sort as `['11111111', '22', '333', '4444']`, so `'22'` is column 1.

## Assumptions

1. The bug is in the shared transform path used by `OneHotEncoder` with `handle_unknown='ignore'`. The issue does not say which internal function, so the exact location is unknown.
2. The issue was reported against `sklearn 0.21.dev0` and Python 2.7. The fix must work on the Python and NumPy versions the codebase supports at the time it lands. The issue does not state those versions.
3. Lists of lists are not affected, because they become object arrays. The fix only needs to change behaviour for fixed-width string arrays: NumPy `U` dtype, and probably `S` (bytes) as well.
4. The caller's input array must not be modified as a side effect of `transform`. This is implied by "memory of the arrays is not handled safely".
5. The fitted `categories_` and the output for known categories must not change.
6. The reporter's suggested approach is to check element sizes and cast to `object` when needed. That is one acceptable direction, not a required design. A copy that is wide enough, or not writing placeholders into the input at all, would also be acceptable.
7. `OrdinalEncoder` may share the same code path. It is in scope only to the extent that it shares the fixed code. This needs confirmation (see Open Questions).

## Tech Stack

- Python, NumPy, SciPy (sparse output), scikit-learn. Exact supported versions are **unknown** from the issue.
- Reporter's environment: Python 2.7.12, NumPy 1.15.2, SciPy 0.18.1, sklearn 0.21.dev0.

## Commands

**Unknown.** The issue gives no build, test, or lint commands. They must be taken from the repository's contributor docs. Placeholders:
```
Build: <unknown>
Test:  <unknown — e.g. the project's test runner targeted at the preprocessing encoder tests>
Lint:  <unknown>
```

## Project Structure

**Unknown.** The issue only names the public module `sklearn.preprocessing`. The source file for `OneHotEncoder` and the location of its tests are not given and must be confirmed in the repository.

## Code Style

**Unknown** from the issue. Follow the existing conventions of the `sklearn.preprocessing` encoder code and its tests. No snippet is available to quote.

## Testing Strategy

- **Framework:** the project's existing test framework. Name and location are unknown.
- **Level:** unit tests on `OneHotEncoder.transform`.
- **Required regression cases:**
  1. The exact reproduction above. It must not raise, and it must return the expected 2×4 matrix with the single `True` at (1, 1).
  2. Fixed-width unicode input (`U` dtype) where the first sorted category is longer than the transform array's itemsize.
  3. The same scenario with bytes (`S` dtype), if bytes input is supported.
  4. The input array passed to `transform` is unchanged afterwards (values and dtype).
  5. Object-dtype and list-of-lists inputs give the same result as before (no regression).
  6. `handle_unknown='error'` still raises for unknown categories.
- **Coverage expectation:** every new branch, such as a dtype or itemsize check, is exercised by at least one test.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix and passes after it.
  - Keep `transform` side-effect free on the user's input.
  - Keep output shape, dtype, and sparsity unchanged for valid inputs.
- **Ask first:**
  - Changing public API or parameters.
  - Changing behaviour of `OrdinalEncoder` or other encoders beyond the shared fix.
  - Adding dependencies.
  - Introducing unconditional object casting that could noticeably affect performance on large numeric inputs.
- **Never:**
  - Change the order or contents of fitted `categories_`.
  - Silence the `ValueError` for `handle_unknown='error'`.
  - Remove or weaken existing encoder tests.

## Success Criteria

- [ ] The reproduction script runs without error. `ohe.transform(test).toarray()` equals `[[False, False, False, False], [False, True, False, False]]`.
- [ ] For any fixed-width string input, unknown entries with `handle_unknown='ignore'` produce all-zero rows in the corresponding feature block. This holds whatever the relative lengths of the fitted categories and the input strings.
- [ ] The array passed to `transform` is unmodified after the call.
- [ ] Results for object-dtype, list, and numeric inputs are unchanged.
- [ ] `handle_unknown='error'` behaviour is unchanged.
- [ ] All existing preprocessing tests pass.

## Open Questions

1. **Error message mismatch.** The reported error is `['111111']` (six characters). But the test array's dtype is `<U5`, so truncation should give `'11111'`. Was the message transcribed inaccurately, or is a different width involved? This affects how the regression test asserts the current failure.
2. **`OrdinalEncoder`.** Does it share the affected code path, and if so, should it be covered by tests in this change?
3. **Bytes input.** Should `S`-dtype bytes arrays be explicitly supported and tested?
4. **Preferred fix strategy.** The options are:
   - Cast to `object` only when the placeholder does not fit (the reporter's approach).
   - Always copy into a sufficiently wide dtype.
   - Avoid writing placeholders into the array altogether.

   Are there performance constraints that favour one of these?
5. **Reporter's patch.** The reporter says a fix already exists. Is there a linked PR to review against this spec?
6. **Versions.** Which Python and NumPy versions must the fix support? Python 2.7 compatibility in particular matters for the target release.
7. **Commands and paths.** What are the project's actual test, lint, and build commands, and where do the encoder source and tests live?