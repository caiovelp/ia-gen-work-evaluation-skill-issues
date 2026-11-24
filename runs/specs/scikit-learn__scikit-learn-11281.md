# Spec: Clusterer-Compatible Interface for Mixture Models

## Objective

Mixture models are effectively probabilistic clusterers and are often used inductively, meaning they predict on unseen data after fitting. Their public API and documentation differ from the library's clusterers in three ways:

1. They take an `n_components` parameter. It serves the same purpose as `n_clusters` on clusterers.
2. They do not store the training-data assignments as a `labels_` attribute.
3. They do not provide a `fit_predict` method.

They are also documented almost entirely separately from clustering.

**Goal:** Decide whether mixture models should expose a clusterer-compatible interface, and if so, define what that interface is. The aim is that users and generic code that work with clusterers can use mixture models the same way, without breaking existing users of the mixture-model API.

**Users:**
- Library users who swap between clustering estimators, for example comparing a clusterer against a mixture model in the same script.
- Generic or meta code that relies on the clusterer contract: `fit_predict`, `labels_`, and clustering metrics applied to `labels_`.
- Readers of the documentation looking for clustering methods.

**Candidate user stories (subject to the decision in Open Questions):**
- As a user, I can call `fit_predict(X)` on a mixture model and receive one hard cluster assignment per training sample. The result matches calling `fit(X)` followed by `predict(X)`, subject to the semantics decided in OQ2.
- As a user, after `fit(X)` I can read `labels_` on a mixture model to get the training-sample assignments, as I would with a clusterer.
- As a user, I can find mixture models in the clustering documentation, or cross-referenced from it, and understand how they relate to other clusterers.
- As an existing user, my current code that uses `n_components` and the current mixture-model methods keeps working unchanged. If anything is deprecated, I get a deprecation warning first.

## Assumptions

1. "Mixture models" refers to every estimator in the library's mixture-model family. The issue does not list them, so the exact set of classes is unknown.
2. "Clusterers" refers to the library's clustering estimators, which share a common clusterer interface or mixin providing `fit_predict` and `labels_`. The exact name and location of that mixin or base class is unknown.
3. Mixture models already provide `fit` and `predict` (hard assignment on new data). This is implied by "applied to inductive problems" but not stated outright.
4. Probabilistic outputs that mixture models already have, such as soft assignments and densities, stay as they are. This change only adds to the API or aligns it.
5. Backward compatibility is required. No existing public parameter, attribute, or method is removed without a deprecation cycle.
6. `labels_` for a mixture model would be the hard assignment (most probable component) of each training sample under the final fitted model.
7. The work covers both the code API and the documentation (user guide placement and cross-references).
8. A renamed or aliased parameter would follow the library's usual deprecation policy. The policy's details (number of releases, warning class) are unknown.

## Tech Stack

- Language: Python (inferred from attribute and method naming conventions).
- Framework, dependencies, and versions: **Unknown**, not stated in the issue.

## Commands

- Build: **Unknown**
- Test: **Unknown**
- Lint: **Unknown**
- Docs build: **Unknown**

## Project Structure

- Location of mixture-model source: **Unknown**
- Location of clustering source and the shared clusterer interface: **Unknown**
- Location of tests: **Unknown**
- Location of user-guide documentation for mixture models and clustering: **Unknown**

## Code Style

**Unknown.** No code was provided in the issue. Follow existing library conventions:
- Fitted attributes use a trailing underscore (e.g. `labels_`).
- Constructor parameters are stored unchanged.
- Public API changes go through deprecation.

## Testing Strategy

Framework and test locations are **unknown**. The levels of testing needed:

- **Unit tests per mixture-model class:**
  - `fit_predict(X)` returns an array with one integer label per sample, in the valid component range.
  - `fit_predict(X)` is consistent with `fit(X).predict(X)` under a fixed random state. The precise equality guarantee depends on OQ2.
  - After `fit(X)`, `labels_` exists, has length `n_samples`, and equals the training predictions under the agreed semantics.
  - Any new or aliased parameter (e.g. `n_clusters`, if adopted) behaves the same as `n_components`. Conflicting values are handled as decided, and deprecation warnings are raised where specified.
- **Common/API conformance tests:** If the library has generic checks for clusterers, mixture models pass them, or documented exceptions are recorded.
- **Regression tests:** Existing mixture-model tests pass unmodified, except for intentional deprecation warnings.
- **Documentation:** Docs build without errors, and any new cross-references resolve. The docs build command is unknown.

## Boundaries

- **Always:**
  - Preserve existing mixture-model behaviour and outputs.
  - Keep all existing public names working, or deprecate them with a warning.
  - Add tests for every new public method or attribute.
  - Document new API surface.
- **Ask first:**
  - Renaming or aliasing `n_components` / `n_clusters`.
  - Changing the inheritance of mixture models, such as adding a clusterer mixin.
  - Moving or restructuring user-guide sections.
  - Changing what `predict` returns.
  - Any change to shared clusterer base classes that affects other estimators.
- **Never:**
  - Remove or rename public parameters, attributes, or methods without a deprecation cycle.
  - Change the numerical results of fitting.
  - Drop the probabilistic API of mixture models.

## Success Criteria

These are conditional on the decision in OQ1 being "yes, align the API". Each item is subject to the corresponding open question.

1. Every mixture-model class provides `fit_predict(X)`, which returns one hard label per training sample.
2. Every mixture-model class sets `labels_` after `fit`, with length equal to the number of training samples.
3. The relationship between `fit_predict(X)`, `fit(X).predict(X)`, and `labels_` is documented and covered by tests.
4. The `n_components` / `n_clusters` question is resolved as decided in OQ3. Whether that means keeping `n_components` as is, adding an alias, or deprecating it, the resolution is implemented and tested, including any deprecation warnings.
5. Mixture models pass the library's generic clusterer conformance checks, if such checks exist, or the deviations are explicitly listed.
6. The clustering documentation mentions mixture models, links to their documentation, and explains the probabilistic/inductive distinction. The mixture-model docs link back to clustering.
7. All pre-existing mixture-model tests pass without modification, other than expected deprecation warnings.

If the decision in OQ1 is "no", the success criterion is instead a documented rationale and, optionally, documentation cross-links between clustering and mixture models.

## Open Questions

1. **Go/no-go:** Should mixture models adopt the clusterer interface at all? Is there any concern that doing so blurs the distinction between density estimators and clusterers?
2. **Semantics of `fit_predict` and `labels_`:** Must `fit_predict(X)` be exactly equal to `fit(X).predict(X)`? With multiple initializations or random restarts, the labels from the final E-step and from a separate `predict` call could differ. Should `labels_` come from the final model, from the last iteration's responsibilities, or something else?
3. **Parameter naming:** Should `n_components` stay as is, gain an `n_clusters` alias, or be deprecated in favour of `n_clusters`? For Bayesian or variational mixtures, `n_components` is an upper bound rather than the effective number of clusters. Does that make `n_clusters` misleading for those classes?
4. **Memory cost:** Is storing `labels_` (one integer per training sample) acceptable for large datasets? Should it be optional?
5. **Soft labels:** Should a probabilistic counterpart of `labels_` also be stored (e.g. training responsibilities)? Or is the existing method for soft assignments sufficient?
6. **Scope of classes:** Which exact mixture-model classes are in scope? Are any deprecated or legacy variants excluded?
7. **Inheritance:** Should mixture models inherit the shared clusterer mixin or base class, or implement the methods directly? Would inheriting the mixin change estimator-type detection, tags, or the behaviour of generic tools such as scoring or model selection?
8. **Documentation placement:** Should mixture models move into the clustering section of the user guide, stay separate with cross-references, or both?
9. **Deprecation policy:** What deprecation period and warning mechanism apply if any parameter is renamed?
10. **Repository specifics:** Build, test, lint, and docs commands, and the source, test, and doc file locations, are all unknown and need to be supplied.