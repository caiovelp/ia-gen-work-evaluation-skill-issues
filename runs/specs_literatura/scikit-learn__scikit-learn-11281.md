## Summary
Give mixture models a clusterer-compatible interface

## Description
Mixture models currently behave differently from the other clustering estimators. Conceptually they are clusterers: they are probabilistic, and unlike many clusterers they can be applied to inductive problems. Their API, however, differs from that of clusterers:

- They use an `n_components` parameter, which serves exactly the same purpose as `n_clusters` in clusterers.
- They do not store the `labels_` of the training data.
- They do not provide a `fit_predict` method.

Their documentation is also almost entirely separate from the clustering documentation.

The request asks whether mixture models should be made more consistent with clusterers.

## Product version
Not provided in the original request.

## Rationale
Mixture models are essentially clusterers, but their API and documentation are inconsistent with those of other clusterers. Aligning them would make the interface uniform across estimators that perform the same kind of task.

## Use case or scenario
Not provided in the original request.

## Possible solution
The original request suggests making mixture models more like clusterers, based on the listed differences:

- Address the inconsistency between `n_components` and `n_clusters`.
- Store `labels_` for the training data.
- Add a `fit_predict` method.
- Integrate their documentation more closely with the clustering documentation.