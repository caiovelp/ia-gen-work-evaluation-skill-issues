# Spec: Restore Label Input Handling in Clustering Metrics (`mutual_info_score` regression)

## Objective

**Problem.** Since a version after scikit-learn 0.21.1, `sklearn.metrics.cluster.mutual_info_score` rejects or warns on valid categorical label arrays.

- `x = np.random.choice(['a', 'b'], size=20).astype(object)` → `mutual_info_score(x, x)` raises `ValueError: could not convert string to float: 'b'`.
- `x = np.random.choice(['a', 'b'], size=20)`, a NumPy unicode string array, works but emits a warning.
- In 0.21.1 both cases worked with no warning. The reporter and the maintainer edit both treat that as the correct behavior.

**Why it matters.** Cluster labels are categorical identifiers, not numeric quantities. Users often pass string labels, for example from pandas `object` columns. A metric that crashes on them, or warns about them, breaks existing code and is a regression.

**Users.** Anyone computing clustering metrics with non-numeric labels. Examples are ground-truth class names or cluster ids stored as strings or Python objects.

**What we're building.** A fix to label input validation for clustering metrics. Label arrays of any dtype that NumPy can treat as hashable categories must be accepted without dtype conversion and without spurious warnings. Numeric-label behavior stays unchanged.

**Acceptance criteria (user-facing):**

1. `mutual_info_score(x, x)` with `x` an `object`-dtype array of strings returns a finite float and raises no exception.
2. `mutual_info_score(x, x)` with `x` a NumPy unicode (`<U…`) string array returns a finite float and emits no warning.
3. Results for string labels equal the results for an equivalent integer encoding of the same labels.
4. Existing behavior for integer and other numeric labels is unchanged: same values, no new warnings.
5. Invalid inputs that were rejected before are still rejected. Examples are 2-D label arrays and length mismatches between `labels_true` and `labels_pred`.

## Assumptions

1. The regression comes from a change in the shared label-checking path used by clustering metrics. It is suspected to be a call to a generic array validator that defaults to a numeric dtype, or that warns on non-numeric dtype. This is not verified; I cannot see the source.
2. The warning in the unicode-string case is a dtype or conversion-related warning. Its exact text and class are not given in the issue.
3. The same validation helper is used by other clustering metrics that take two label arrays, such as adjusted/normalized mutual info, (adjusted) Rand index, homogeneity/completeness/V-measure, Fowlkes–Mallows, and the contingency matrix. They are probably affected too. This is unverified.
4. 0.21.1 behavior is the reference for "correct": no conversion, no warning for string or object labels.
5. Object arrays containing mixed or unorderable types are out of scope unless they also worked in 0.21.1 (see Open Questions).
6. `mutual_info_score`'s `contingency` argument path is not part of this regression.
7. The fix should not change public function signatures.

## Tech Stack

- Python, NumPy, scikit-learn (`sklearn.metrics.cluster`).
- Reference good version: 0.21.1. The first bad version and the exact affected version are **unknown**; the issue does not state them.
- Supported Python and NumPy versions: **unknown**.

## Commands

All commands are **unknown**, because the repository is not visible. Fill these in from the project's contributor docs:

```
Build:       <unknown>
Test:        <unknown>  (expected to target the clustering metrics test module)
Lint:        <unknown>
Reproduce:   python -c "import numpy as np; from sklearn.metrics.cluster import mutual_info_score; x=np.random.choice(['a','b'],size=20).astype(object); print(mutual_info_score(x,x))"
```

## Project Structure

Known from the issue:

- Public import path: `sklearn.metrics.cluster` (`mutual_info_score`).

Unknown (to be confirmed):

- File defining the supervised clustering metrics and their shared label-checking helper.
- Location of the corresponding test module.
- Location of the changelog / what's-new entry for bug fixes.

## Code Style

Unknown from the issue. Follow the existing conventions of the module being changed. No example snippet is available beyond the reproduction:

```python
from sklearn.metrics.cluster import mutual_info_score
import numpy as np

x = np.random.choice(['a', 'b'], size=20).astype(object)
mutual_info_score(x, x)  # must not raise
```

## Testing Strategy

- **Framework:** unknown. pytest is likely, but this is not verified.
- **Regression tests**, added to the existing clustering-metrics test module:
  - **Object-dtype strings:** `mutual_info_score` returns a value and raises no exception.
  - **Unicode strings:** `mutual_info_score` returns a value and emits no warnings. Assert this with a "no warnings raised" check.
  - **Equivalence:** the score for string labels equals the score for an integer encoding of the same labels.
  - **Other metrics:** a parametrized test over the other two-label clustering metrics that share the validation path, if Assumption 3 is confirmed. Each gets the same object and unicode inputs.
- **Non-regression:** the existing test suite for clustering metrics passes unchanged.
- **Coverage expectation:** unknown. At minimum, both code paths in the issue are covered.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix.
  - Keep numeric-label results bit-identical.
  - Keep existing shape and length validation.
  - Add a changelog entry if the project requires one.
- **Ask first:**
  - Changing a shared, library-wide validation utility rather than the clustering-specific label check.
  - Altering warning behavior for other metric families.
  - Deciding the policy for mixed-type object arrays.
- **Never:**
  - Silently convert labels to float.
  - Suppress warnings globally to hide the symptom.
  - Change public signatures.
  - Remove or weaken existing tests.

## Success Criteria

- [ ] The reproduction with an `object`-dtype string array returns a finite float without exception.
- [ ] The reproduction with a unicode string array returns a finite float and emits zero warnings.
- [ ] String-label results equal integer-encoded results for the same partition (`mutual_info_score(x, x)` equals the entropy of `x`).
- [ ] All other clustering metrics sharing the label-validation path accept object and unicode string labels without errors or warnings, or a documented decision limits scope to `mutual_info_score`.
- [ ] Existing clustering metric tests pass with no new warnings.
- [ ] 2-D inputs and length-mismatched inputs are still rejected with an error.

## Open Questions

1. Which version introduced the regression, and which change caused it? Is there a specific PR to reference or partially revert?
2. What is the exact warning emitted for unicode string arrays (class and message)? Is it a deliberate deprecation in a shared validator that should be kept for other estimators but bypassed for clustering labels?
3. Should the fix cover all supervised clustering metrics and the contingency-matrix helper, or only `mutual_info_score`? Does the fix target a patch release?
4. What should happen with object arrays of mixed or unorderable types (e.g. `['a', 1, None]`)? Did 0.21.1 accept them?
5. Should NaN or `None` in object label arrays be treated as a valid category, or rejected?
6. Are there other label-like inputs (e.g. pandas categorical, lists of tuples) that must be explicitly supported?
7. What are the project's test, lint, and changelog commands and file locations?