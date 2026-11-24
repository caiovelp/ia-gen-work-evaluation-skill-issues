## Summary
Allow `sign` to be rewritten in terms of `Abs` in SymPy.

## Description
SymPy defines the `sign` function as:

```
    sign(z)  :=  z / Abs(z)
```

for all complex non-zero `z`. There is currently no way to rewrite `sign` in terms of `Abs`. The requested behavior is:

```
>>> sign(x).rewrite(Abs)
 x 
───
│x│
```

It is unclear how to handle the case where the argument is zero. The current behavior is inconsistent with the definition:

```
>>> sign(0)
0
>>> 0 / Abs(0)
nan
```

## Product version
Not provided in the original request.

## Rationale
`sign(z)` is defined as `z / Abs(z)`, so users should be able to express `sign` in terms of `Abs` through the standard `rewrite` mechanism.

## Use case or scenario
A user has an expression containing `sign(x)` and wants to rewrite it as `x/Abs(x)` by calling `sign(x).rewrite(Abs)`.

## Possible solution
- Implement `sign(x).rewrite(Abs)` so it returns `x/Abs(x)`.
- Handle the zero-argument case in one of two ways suggested in the request:
  1. Change `sign(0)` to return `nan`, so it is consistent with `0 / Abs(0)`; or
  2. Keep `sign(0) == 0` and have the rewrite account for the argument possibly being zero. The request notes that this would make the rewrite fail in most cases.