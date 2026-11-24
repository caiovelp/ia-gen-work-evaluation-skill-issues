## Summary

`simplify((-a)**x * a**(-x))` returns `(-1)**x` both when `a` is a positive integer Symbol and when `a` is the concrete integer `2`. When `x = -10/3` is substituted, the two cases behave differently:

- **Symbolic `a`:** the original and simplified expressions evaluate to the same value.
- **`a = 2`:** they evaluate to different values. The simplified result is not numerically equivalent to the original expression.

## Steps to reproduce

**Case 1: `a` is a positive integer Symbol (consistent)**

1. Define `a = Symbol('a', integer=True, positive=True)`. `x` is used as a symbol; its definition is not shown in the original report.
2. Build `e = (-a)**x * a**(-x)`.
3. Compute `f = simplify(e)`.
4. Set `t = -S(10)/3`.
5. Compute `n1 = e.subs(x, t)` and `n2 = f.subs(x, t)`.
6. Print `N(n1)` and `N(n2)`.

**Case 2: `a = S(2)` (inconsistent)**

1. Define `a = S(2)`.
2. Repeat steps 2–6 from Case 1.

## Observed behavior

**Case 1 (`a` symbolic, positive integer):**
- `print(e)` gives `a**(-x)*(-a)**x`
- `print(f)` gives `(-1)**x`
- `N(n1)` gives `-0.5 + 0.866025403784439*I`
- `N(n2)` gives `-0.5 + 0.866025403784439*I`
- The two values match.

**Case 2 (`a = 2`):**
- `print(e)` gives `(-2)**x*2**(-x)`
- `print(f)` gives `(-1)**x`
- `N(n1)` gives `0.5 - 0.866025403784439*I`
- `N(n2)` gives `-0.5 + 0.866025403784439*I`
- The two values differ. The original expression and its simplified form give different numerical results.

## Expected behavior

`simplify` should return an expression equivalent to its input. After substituting `x = -10/3`, the original and simplified expressions should give the same numerical value in both cases (symbolic positive integer `a` and `a = 2`). The original report does not say which of the two values is the correct one.

## Stack trace / error output

Not provided in the original report. No exception is raised; the issue is an incorrect or inconsistent result.

## Test case

Minimal test derived from the report (Case 2, the failing case):

```python
a = S(2)
e = (-a)**x * a**(-x)
f = simplify(e)
t = -S(10)/3
n1 = e.subs(x, t)
n2 = f.subs(x, t)
# Expected: N(n1) and N(n2) are equal
# Observed: N(n1) == 0.5 - 0.866025403784439*I
#           N(n2) == -0.5 + 0.866025403784439*I
```

For comparison, the same steps with `a = Symbol('a', integer=True, positive=True)` give matching values (`-0.5 + 0.866025403784439*I` for both).

## Code example

Case 1 (symbolic `a`, consistent):

```
>>> a = Symbol('a', integer=True, positive=True)
>>> e = (-a)**x * a**(-x)
>>> f = simplify(e)
>>> print(e)
a**(-x)*(-a)**x
>>> print(f)
(-1)**x
>>> t = -S(10)/3
>>> n1 = e.subs(x,t)
>>> n2 = f.subs(x,t)
>>> print(N(n1))
-0.5 + 0.866025403784439*I
>>> print(N(n2))
-0.5 + 0.866025403784439*I
```

Case 2 (`a = 2`, inconsistent):

```
>>> a = S(2)
>>> e = (-a)**x * a**(-x)
>>> f = simplify(e)
>>> print(e)
(-2)**x*2**(-x)
>>> print(f)
(-1)**x
>>> t = -S(10)/3
>>> n1 = e.subs(x,t)
>>> n2 = f.subs(x,t)
>>> print(N(n1))
0.5 - 0.866025403784439*I
>>> print(N(n2))
-0.5 + 0.866025403784439*I
```

## Version and environment

Not provided in the original report.