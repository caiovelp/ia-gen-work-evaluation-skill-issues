## Summary
`refine()` does not simplify `arg()` of a variable under real-number assumptions (e.g. `Q.positive`), so expressions containing `arg(a)` stay unsimplified.

## Description
`refine()` does not recognize that complex-argument functions such as `arg()` simplify when the argument is known to be real, for example positive. It already handles `abs()` this way (`refine(abs(a), Q.positive(a))` returns `a`), but `refine(arg(a), Q.positive(a))` returns `arg(a)` unchanged.

As a result, refining a `Piecewise` result whose condition depends on `arg(a)` does not reduce it, even though the condition is clearly satisfied when `a` is positive.

Reproduction:

```python
>>> from sympy import *
>>> var('a,x')
>>> J = Integral(sin(x)*exp(-a*x),(x,0,oo))
>>> J.doit()
Piecewise((1/(a**2 + 1), 2*Abs(arg(a)) < pi), (Integral(exp(-a*x)*sin(x), (x, 0, oo)), True))
>>> refine(J.doit(),Q.positive(a))
Piecewise((1/(a**2 + 1), 2*Abs(arg(a)) < pi), (Integral(exp(-a*x)*sin(x), (x, 0, oo)), True))
>>> refine(abs(a),Q.positive(a))
a
>>> refine(arg(a),Q.positive(a))
arg(a)
```

**Expected:** with `Q.positive(a)`, `arg(a)` should simplify, so the `Piecewise` above reduces to `1/(a**2 + 1)`.
**Actual:** `arg(a)` and the `Piecewise` expression are returned unchanged.

The reporter found no open issue about this.

## Product version
Not provided in the original request.

## Rationale
The reporter expects to use `refine()` often. Without this simplification, results such as the `Piecewise` output of definite integrals cannot be reduced under suitable assumptions. This limits how useful `refine()` is in practice.

## Use case or scenario
A user computes the definite integral of `sin(x)*exp(-a*x)` from `0` to `oo`. `doit()` returns a conditional `Piecewise` result. The user then wants to call `refine(..., Q.positive(a))` to get the simple closed form `1/(a**2 + 1)` for positive `a`.

## Possible solution
The reporter says the issue should be "easy to fix" but does not describe a specific fix. Implied by the report: `refine()` should simplify `arg()` under real or positive assumptions, the way it already simplifies `abs()`.