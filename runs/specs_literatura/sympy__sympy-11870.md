## Summary
`trigsimp` should rewrite exponential expressions that match trigonometric identities, e.g. simplify to `sin(k)` and `sinc(k)`.

## Description
At present, `trigsimp` does not turn an expression made of complex exponentials into the equivalent trigonometric function. For example:

```
f = 1 / 2 * (-I*exp(I*k) + I*exp(-I*k))
trigsimp(f)
```

Ideally this would return `sin(k)`. The reporter asks whether there is a way to get this result.

As an extension, the reporter would like this expression:

```
f = 1 / 2 / k* (-I*exp(I*k) + I*exp(-I*k))
trigsimp(f)
```

to return `sinc(k)`.

## Product version
Not provided in the original request.

## Rationale
Not provided in the original request. (The reporter only says it would be "awesome" if `sinc(k)` could also be recognized.)

## Use case or scenario
A user has an expression written with complex exponentials, such as `1/2 * (-I*exp(I*k) + I*exp(-I*k))`. The user calls `trigsimp` on it and wants the compact trigonometric form `sin(k)`. If the same expression is divided by `k`, the user wants `sinc(k)`.

## Possible solution
Not provided in the original request. The reporter states the desired result (`trigsimp` returning `sin(k)` and `sinc(k)` for these inputs) but suggests no implementation. They also ask whether some existing way to get this result already exists.