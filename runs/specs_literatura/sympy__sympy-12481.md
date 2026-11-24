## Summary
Allow the `Permutation` constructor to accept non-disjoint cycles.

## Description
Right now, calling the `Permutation` constructor with non-disjoint cycles raises a `ValueError`. For example:

```
Permutation([[0,1],[0,1]])
```

This raises a `ValueError`. The expected result is the identity permutation.

Requested behavior: when the cycles are non-disjoint, the constructor should apply them in left-to-right order and return the resulting permutation.

## Product version
Not provided in the original request.

## Rationale
The reporter sees no reason to forbid non-disjoint cycles. The resulting permutation should also be easy to compute.

## Use case or scenario
A user builds a permutation from cycles that share elements, such as `[[0,1],[0,1]]`. The user expects to get the composed permutation (here the identity), not an error.

## Possible solution
Do not raise a `ValueError` when the cycles are non-disjoint. Instead, apply the cycles in left-to-right order and return the resulting permutation.