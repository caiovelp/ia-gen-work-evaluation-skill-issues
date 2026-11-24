# Spec: Consistent, Detectable Results for Non-Converged Affinity Propagation

## Objective

When `AffinityPropagation` stops at `max_iter` without converging, the result looks like a valid clustering. Its behaviour also contradicts the documentation.

**Documented behaviour (quoted in the issue):**
> "When the algorithm does not converge, it returns an empty array as cluster_center_indices and -1 as label for each training sample."

**Observed behaviour (scikit-learn 0.20.3):**

```python
from sklearn.cluster import AffinityPropagation
import pandas as pd

data = pd.DataFrame([[1,0,0,0,0,0],[0,1,1,1,0,0],[0,0,1,0,0,1]])
af = AffinityPropagation(affinity='euclidean', verbose=True, copy=False, max_iter=2).fit(data)

print(af.cluster_centers_indices_)   # observed: [2]      expected per docs: []
print(af.labels_)                    # observed: [0 0 0]  expected per docs: [-1 -1 -1]
```

The only signal of non-convergence today is the `verbose=True` printout. The workaround of comparing `n_iter_ == max_iter` is unreliable because convergence can occur at exactly the last iteration.

**User:** A developer who calls `AffinityPropagation` inside a larger script or pipeline. They need to detect failed convergence programmatically, without reading stdout. They must not silently consume a meaningless clustering.

**Goal:** The documentation and the runtime behaviour agree. A non-converged fit can be detected programmatically and reliably.

**Acceptance criteria (pending answers to the Open Questions):**
1. For a fit that does not converge within `max_iter`, the returned values match whatever the documentation states. The doc-literal behaviour is `cluster_centers_indices_ == []` and `labels_ == [-1] * n_samples`.
2. A non-converged fit is detectable without `verbose=True`, through a warning, an attribute, or both (see Open Questions).
3. A fit that does converge, including one that converges exactly at the final allowed iteration, keeps its current results and is not reported as non-converged.
4. The public function form of the algorithm, if it exists separately from the estimator, behaves the same way as the estimator.

## Assumptions

1. The issue's reproduction is accurate. With `max_iter=2`, the example does not converge, and the verbose output confirms this.
2. The convergence criterion uses a stable-exemplar window. The parameter is presumably `convergence_iter`, and the issue's "15 iterations" matches its default. The exact parameter name and default have not been verified in the code.
3. The root cause is suspected to be that, after the iteration loop ends without convergence, the code still extracts exemplars from the final state. In that reading, the "empty / -1" result happens only when zero exemplars are found, not whenever convergence fails. This hypothesis has not been verified against source.
4. The fix belongs in scikit-learn's affinity propagation implementation, covering both estimator and function. It does not belong in user code.
5. Other scikit-learn estimators that fail to converge conventionally emit `sklearn.exceptions.ConvergenceWarning`. Following that convention is preferred.
6. The behaviour should be fixed on the current development branch, not on 0.20.3 specifically.

## Tech Stack

- Python, NumPy, SciPy; scikit-learn (reported on 0.20.3, numpy 1.15.4, scipy 1.2.0, pandas 0.23.4).
- Exact versions supported by the current development branch: **unknown**.

## Commands

All of these are **unknown**, because the repository was not visible.
- Build: unknown
- Test: unknown (presumably pytest-based; verify)
- Lint: unknown
- Docs build: unknown

## Project Structure

**Unknown.** The relevant locations still need to be identified:
- The source module containing the `AffinityPropagation` estimator and its function counterpart.
- The test module for affinity propagation.
- The docstrings and user-guide pages that contain the quoted sentence about non-convergence.
- The changelog or what's-new file for user-visible behaviour changes.

## Code Style

**Unknown.** Follow the existing conventions of the affinity propagation module and the project's estimator conventions:
- Fitted attributes end with `_`.
- Warnings use the project's exception classes.
- Docstrings use NumPy format.

No snippet is included because no source is visible.

## Testing Strategy

- **Framework:** unknown (expected to be the project's existing test runner).
- **Regression test:** Use the issue's 3-sample input with `max_iter=2`. Assert that the documented non-converged outputs are returned and that the chosen signal (warning and/or attribute) is raised or set.
- **Function-level test:** Apply the same assertions to the function form of the algorithm, if one exists.
- **Converged-case test:** A well-separated dataset that converges must produce unchanged centers and labels and no non-convergence signal.
- **Edge-case test:** Convergence occurring exactly at the last allowed iteration must be reported as converged. This is the reporter's stated concern about the `n_iter_ == max_iter` heuristic.
- **Predict-after-non-convergence test:** Define and verify what `predict` returns on a non-converged model, depending on the Open Questions.
- **Coverage:** No new branches in the non-convergence path are left untested.

## Boundaries

- **Always:**
  - Keep the documentation and behaviour consistent in the same change.
  - Add regression tests reproducing the issue.
  - Document the user-visible change in the changelog.
  - Use the project's standard convergence warning mechanism.
- **Ask first:**
  - Changing returned values for non-converged fits, since existing users may depend on them.
  - Adding new public attributes or parameters.
  - Changing the signature or return tuple of the public function.
  - Deciding the behaviour of `predict` on non-converged models.
  - Any deprecation cycle.
- **Never:**
  - Change results for fits that converge.
  - Rely on `verbose` output as the only failure signal.
  - Use `n_iter_ == max_iter` as the convergence test.
  - Remove or weaken existing tests without approval.

## Success Criteria

- [ ] Running the issue's example without `verbose` produces a programmatically detectable non-convergence signal.
- [ ] The returned `cluster_centers_indices_` and `labels_` for non-converged fits match the documentation exactly. Whether the code or the docs change is decided in Open Questions.
- [ ] Converged fits, including convergence at the last permitted iteration, are unchanged and raise no non-convergence signal.
- [ ] The estimator and the public function (if present) behave identically on non-convergence.
- [ ] `predict` behaviour on a non-converged model is defined, documented, and tested.
- [ ] Regression tests are added, and the full existing test suite for the module passes.
- [ ] A changelog entry describes the behaviour change.

## Open Questions

1. **Code or docs?** Should the implementation change to match the documentation (empty centers and all `-1` labels on non-convergence)? Or should the documentation change to describe the current "best-effort last state" output? The reporter prefers the former.
2. **Warning:** Should non-convergence emit a `ConvergenceWarning`, consistent with other estimators, independent of `verbose`?
3. **Attribute:** Should a public flag (e.g. a `converged_`-style attribute) be added? If so, under what name, and should the function form also return it?
4. **Backwards compatibility:** Changing outputs for non-converged fits is user-visible. Is a direct change acceptable as a bug fix, or is a deprecation period or opt-in parameter required?
5. **`predict` on non-converged models:** Should it return all `-1`, raise an error, or warn? What about `fit_predict`?
6. **Degenerate converged cases:** Is the current all-`-1` / empty output for "converged but zero exemplars" intended? Should it stay distinguishable from non-convergence?
7. **Root cause confirmation:** Is Assumption 3 correct, i.e. that exemplars are extracted from the final iteration state regardless of convergence? This needs verification in source before planning.
8. **Repository details:** What are the exact file paths, test commands, and changelog location? All are unknown here.