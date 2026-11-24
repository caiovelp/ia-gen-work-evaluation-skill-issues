# Spec: Deterministic Output Signs for `KernelPCA` (rbf kernel)

## Objective

**Problem.** A user runs `KernelPCA(n_components=7, kernel='rbf', copy_X=False, n_jobs=-1).fit_transform(X)` several times on the same dataset (scikit-learn 0.18.1). The absolute values match across runs, but the signs of individual components differ. Each component flips on its own, as the three reported runs show:

| Run | c1 | c2 | c3 | c4 | c5 | c6 | c7 |
|---|---|---|---|---|---|---|---|
| 1 | − | − | − | + | − | − | + |
| 2 | + | + | + | − | − | − | − |
| 3 | − | − | + | + | + | + | + |

**Background.** An eigenvector is only defined up to sign, so `v` and `−v` are both valid kernel principal components. Both answers are mathematically correct. The problem is that the output is not reproducible. Downstream users expect repeated calls on identical input to return identical output. This matters for pipelines, caching, model comparison and tests.

**Goal.** Make the signs of `KernelPCA` components deterministic for identical input and identical parameters. Do this through a deterministic sign convention, by documenting the behaviour, or both. Which of these is in scope is an open question.

**Users.** scikit-learn users who use `KernelPCA` for dimensionality reduction and need reproducible embeddings.

**User stories**
- As a user, when I call `fit_transform(X)` repeatedly on the same `X` with the same parameters, I get identical output, signs included.
- As a user, if sign indeterminacy is inherent to the method, the documentation tells me so and tells me how to get reproducible results (for example by setting a seed or choosing a solver, if applicable).

## Assumptions

1. The variation comes from the eigen-decomposition step. One likely source is an iterative solver started from a random vector. The other is the eigenvector sign ambiguity itself. Neither has been checked in code; the code is not visible.
2. The rbf kernel is not special. Any kernel whose eigenproblem goes through the same solver path is probably affected. The issue only demonstrates rbf.
3. `n_jobs=-1` and `copy_X=False` are not the cause. They should not affect eigenvector signs. Unverified.
4. The user did not pass a random seed. Whether `KernelPCA` in 0.18.1 accepts one, and what it controls, is unknown from the issue.
5. Any fix will target the current development version, not 0.18.1.
6. The fix must not change the magnitudes or ordering of components, or the subspace they span. Only the signs may become canonical.
7. A sign convention similar to the one used elsewhere in the library for SVD-based decompositions is acceptable, if one exists. Not verified.

## Tech Stack

- Python, scikit-learn (reported version 0.18.1). The target version for the fix is unknown.
- NumPy/SciPy eigen-solvers, assumed. The exact solvers used by `KernelPCA` are unknown from the issue.

## Commands

- Build: unknown
- Test: unknown
- Lint: unknown
- Reproduce: unknown as a runnable command. The issue gives only this snippet, and `X` is not provided:
  ```python
  pca = KernelPCA(n_components=7, kernel='rbf', copy_X=False, n_jobs=-1)
  pca.fit_transform(X)
  ```

## Project Structure

Unknown. The location of the `KernelPCA` implementation, its tests and its documentation is not visible in the issue.

## Code Style

Unknown. Follow the existing conventions of the module that contains `KernelPCA`. No code snippet is available.

## Testing Strategy

- **Framework:** unknown. Use the project's existing test framework and layout.
- **Regression test (required):**
  - Fit `KernelPCA` with `kernel='rbf'` and `n_components=7` several times on the same fixed dataset.
  - Assert that the outputs are exactly or numerically equal, signs included.
  - Cover every eigen-solver option that `KernelPCA` exposes, including the automatic choice.
  - Cover dataset sizes that trigger each solver path. The thresholds are unknown.
- **Invariance test:** compare outputs from different solvers on the same data. They should agree up to numerical tolerance after any sign convention is applied, if that is in scope.
- **Non-regression:**
  - Absolute values of transformed data are unchanged by the fix.
  - Explained eigenvalues are unchanged.
  - `transform` on new data stays consistent with `fit_transform`.
  - `inverse_transform` still works, if applicable.
- **Coverage expectations:** unknown.

## Boundaries

- **Always:**
  - Keep the component subspace, eigenvalues and ordering unchanged.
  - Add a regression test that reproduces the sign flip.
  - Make `fit_transform` and `fit(...).transform(...)` use the same sign convention.
- **Ask first:**
  - Introducing or changing a public parameter, such as a random seed or a solver default.
  - Changing results for existing users. A canonical sign convention will flip signs relative to some current outputs, which is a behaviour change that needs a changelog note.
  - Changing behaviour of other decomposition estimators.
- **Never:**
  - Change magnitudes or the selection of components.
  - Remove or weaken existing tests to accommodate the change.
  - Claim that the issue is fixed if signs can still vary across solver paths without documentation saying so.

## Success Criteria

1. On a fixed dataset, repeated `KernelPCA(n_components=7, kernel='rbf').fit_transform(X)` calls return identical output (`np.allclose`, signs included) in the same environment, for every solver path.
2. Repeated `fit(X).transform(X)` calls are equally deterministic and match `fit_transform(X)`.
3. Absolute values of the output and the fitted eigenvalues are numerically equal to pre-fix values.
4. The sign behaviour is documented in the `KernelPCA` docstring: either the deterministic convention that is applied, or the inherent indeterminacy and how to control it.
5. A regression test exists that fails on the current code and passes after the change.
6. A changelog entry notes that output signs may differ from previous versions, if a canonical sign convention is adopted.

## Open Questions

1. **Resolution type.** Should this be fixed in code (deterministic sign convention), handled in documentation only ("signs are arbitrary"), or both?
2. **Root cause.** Is the run-to-run variation caused by a randomly initialised iterative eigen-solver? Or does it also occur with the dense or exact solver? This affects whether seeding alone is sufficient.
3. **Determinism scope.** Is determinism required only across repeated runs in the same environment, or also across eigen-solvers, platforms and BLAS/LAPACK backends?
4. **Sign convention.** If a convention is adopted, which one? For example, the largest-absolute-value entry of each eigenvector is positive. Should it match an existing convention used by other decomposition estimators in the library?
5. **Random seed.** Does `KernelPCA` already expose a random seed parameter for its solver? If not, is adding one acceptable?
6. **Reproduction data.** Can the reporter provide `X` (or its shape and dtype) and confirm which solver was used? This determines which code path to test.
7. **Backward compatibility.** Is a one-time change of output signs for existing users acceptable, and does it need a deprecation period or only a changelog note?
8. **Other kernels and estimators.** Should the fix cover all kernels, and possibly other estimators that share the same eigen-decomposition code? Or only `KernelPCA`?
9. **Target version.** Which release or branch should receive the fix? 0.18.1 itself is assumed to be out of scope.