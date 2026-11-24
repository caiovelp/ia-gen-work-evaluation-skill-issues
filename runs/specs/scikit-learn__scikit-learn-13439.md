# Spec: `Pipeline.__len__` support

## Assumptions

1. The target is scikit-learn's `sklearn.pipeline.Pipeline`, at development version `0.21.dev0` per the issue's version report.
2. "The new indexing support" means `Pipeline.__getitem__` already exists. It accepts at least integer indices and slices, and a slice returns a new `Pipeline` made of the selected steps. I cannot see the code to confirm this.
3. The length of a pipeline is the number of entries in its `steps` list. Steps set to `None` or `'passthrough'` count toward that number.
4. The fix only adds `__len__`. It does not change how `__getitem__` behaves.
5. `FeatureUnion` and other meta-estimators are out of scope unless a maintainer decides otherwise. See Open Questions.
6. Python 3 only, consistent with the reported Python 3.6.7 environment.
7. The repository's standard test framework is used. I believe it is pytest, but I cannot see the repo to confirm it.

## Objective

Users who slice a pipeline need to know how long it is, so they can write `pipe[:len(pipe)]` or `pipe[:len(pipe) - 1]`. Today `len(pipe)` raises an error (presumably a `TypeError`, since the object has no `__len__`). This makes length-based slicing unusable even though indexing is supported.

**User:** a scikit-learn user who builds and inspects `Pipeline` objects, for example to get every step except the final estimator.

**User stories / acceptance criteria**

- As a user, I can call `len(pipe)` on a `Pipeline` and get the number of steps.
- As a user, I can write `pipe[:len(pipe)]` without an error, and the result holds all steps.
- As a user, I can write `pipe[:len(pipe) - 1]` to get the pipeline without its final step.

**Success looks like:** the reproduction script in the issue runs without error and `len(pipe)` returns `2`.

## Tech Stack

- Language: Python (issue environment: 3.6.7)
- Library: scikit-learn `0.21.dev0`
- Dependencies in the issue environment: numpy 1.16.2, scipy 1.2.1, Cython 0.29.6, pandas 0.24.1
- No new dependencies are expected.

## Commands

The issue does not show them, and I have no repository access.

- Build: **unknown**
- Test: **unknown**. The likely runner is pytest, but the exact invocation is not confirmed.
- Lint: **unknown**
- Dev / install: **unknown**

## Project Structure

**Unknown.** I have no repository access. The only known location is the public import path `sklearn.pipeline.Pipeline`. The module file and its test file are not visible in the issue.

## Code Style

**Unknown.** No code snippets from the repo are visible. Follow the conventions already used in the module that defines `Pipeline`, especially the existing `__getitem__` implementation. Any new public method should include a docstring that matches the style around it.

## Testing Strategy

- **Framework:** the project's existing unit test framework. Assumed pytest; command unknown.
- **Location:** alongside the existing `Pipeline` tests. The path is unknown.
- **Test level:** unit tests only. This is a pure in-memory behaviour with no I/O.
- **Cases to cover:**
  - `len()` of a pipeline with 2 steps returns 2.
  - `len()` of a pipeline with 1 step returns 1.
  - `len()` counts steps set to `None` or `'passthrough'`, if those are allowed in this version.
  - `pipe[:len(pipe)]` succeeds and has the same number of steps as `pipe`.
  - `pipe[:len(pipe) - 1]` has `len(pipe) - 1` steps.
  - After changing `pipe.steps` (for example with `set_params`, replacing a step), `len()` still matches `len(pipe.steps)`.
  - Regression: the exact reproduction script from the issue runs without error.
- **Coverage expectation:** the new method is fully covered. Existing pipeline tests still pass.

## Boundaries

- **Always:**
  - Run the existing pipeline test suite before committing.
  - Derive the length from the pipeline's `steps` so it never goes stale.
  - Add a regression test based on the issue's reproduction.
  - Follow the project's changelog or what's-new convention if one exists (location unknown).
- **Ask first:**
  - Changing `__getitem__` semantics.
  - Adding `__len__` to other meta-estimators such as `FeatureUnion`.
  - Any change that affects truthiness of `Pipeline` objects (see Open Questions).
  - Adding dependencies.
- **Never:**
  - Change the public constructor signature or the `steps` attribute format.
  - Remove or weaken existing tests.
  - Commit unrelated refactors with this change.

## Success Criteria

1. `len(Pipeline([('anova', SelectKBest(...)), ('svc', SVC(...))]))` returns `2`.
2. For any valid pipeline `pipe`, `len(pipe) == len(pipe.steps)`.
3. `pipe[:len(pipe)]` raises no error and returns a pipeline with `len(pipe)` steps.
4. `pipe[:len(pipe) - 1]` returns a pipeline with `len(pipe) - 1` steps.
5. The reproduction script from the issue runs to completion without error.
6. All existing `Pipeline` tests pass unchanged.
7. New unit tests for the cases above exist and pass.

## Open Questions

1. **Truthiness side effect.** Defining `__len__` makes `bool(pipe)` depend on its length. Can a `Pipeline` with zero steps exist, and does any code rely on `if pipe:` or `if estimator:` being always true? If so, should `__bool__` be defined explicitly?
2. **Scope.** Should `FeatureUnion`, or other step-based composites that gained or will gain indexing, also get `__len__` for consistency?
3. **`None` / `'passthrough'` steps.** Should these count toward length? This spec assumes yes, since they occupy an index.
4. **Changelog.** Does this change need a what's-new or changelog entry, and where does it go?
5. **Commands and paths.** What are the build, test, and lint commands and file locations? None are visible from the issue.
6. **Documentation.** Should the user guide section on pipeline indexing (if one exists) mention `len(pipe)`?