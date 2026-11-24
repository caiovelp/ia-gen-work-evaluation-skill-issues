# Spec: Combine Like Terms with Numerically Equal Float Exponents in `simplify`

## Objective

**Problem.** Two expressions that are mathematically identical do not cancel after `evalf` and `simplify`:

```python
import sympy
from sympy import *
x=Symbol('x')
expr1 = S(1)/2*x**2.5
expr2 = S(1)*x**(S(5)/2)/2
res = expr1-expr2
res= simplify(res.evalf(5))
print res
```

Observed output: `-0.5*x**2.5 + 0.5*x**2.5`
Expected output: `0`

**Who is affected.** SymPy users who mix Python float literals (`x**2.5`) with exact rationals (`x**(S(5)/2)`) and then evaluate numerically. They expect `simplify` to cancel terms that print identically.

**Likely mechanism (hypothesis, not yet verified).**
- `x**2.5` creates a `Float` exponent at default precision (about 15 digits).
- `evalf(5)` turns `Rational(5, 2)` into a `Float` at 5-digit precision.
- The two exponents print the same (`2.5`), but they may differ in precision or in internal representation (mpf tuple, hash, `==`).
- If so, `Add` and `Mul` will not collect them as like terms, and `simplify` cannot cancel them.

This must be confirmed before the scope of the fix is chosen. See Open Questions.

**What success means.** One of these, depending on how the open questions are resolved:
- (a) The given snippet simplifies to `0`, or
- (b) the behavior is documented as intended, and a supported way to get `0` is identified and documented, such as `nsimplify`, avoiding float literals, or a specific `simplify` option.

## Assumptions

1. The issue is against SymPy. The `print res` syntax means the reporter ran Python 2, so the SymPy version is likely old. Current versions may already behave differently.
2. The root cause is that two `Float` exponents of equal value are treated as non-identical because their precision differs, not that the values differ.
3. Changing how `Float` equality and hashing treat precision is a core, wide-impact change. It is out of scope unless maintainers approve it. A fix inside `simplify` or term collection is preferred.
4. The fix must not merge floats whose values are actually different, for example `2.5` and `2.50001`.
5. Exact (non-float) expressions are unaffected and must stay unaffected.

## Tech Stack

- Python. The reporter used Python 2; the versions currently supported are unknown.
- SymPy. The affected version is unknown.
- mpmath, as SymPy's `Float` backend. The version is unknown.

## Commands

The project's commands could not be seen. All of these are unknown:

- Build: unknown (pure Python, likely none)
- Test: unknown
- Lint: unknown
- Reproduce: run the snippet above. The interpreter or version needed is unknown.

## Project Structure

Not visible from the issue, so all locations are unknown. Areas that are probably relevant:
- The core `Float`, `Pow` and `Add` term collection.
- The `simplify` module.

Exact paths are unknown.

## Code Style

Unknown; follow the existing SymPy conventions. No code from the repository is visible.

## Testing Strategy

The framework and test locations are unknown. Tests should cover:

**Regression test (unit).** The reporter's snippet: `simplify((S(1)/2*x**2.5 - x**(S(5)/2)/2).evalf(5))` should yield `0`, or the documented alternative should yield `0`.

**Precision variants.**
- Exponents produced at different `evalf` precisions, such as 5, 15 and 30, are handled as specified.
- Floats that genuinely differ in value must not be combined.

**Non-regression.**
- Existing tests for `simplify`, `Float` and `Add` still pass.
- Purely exact expressions are unchanged.

**Characterization (do first).**
- Record what `Float(2.5) == Float(2.5, 5)` returns, and whether their hashes match, in the target version.
- Record the srepr of both exponents after `evalf(5)`.

## Boundaries

**Always:**
- Reproduce the issue on the current development version before changing anything.
- Add a regression test.
- Run the full test suite for the core and simplify areas.

**Ask first:**
- Any change to `Float.__eq__`, `Float.__hash__`, or how precision takes part in structural equality.
- Changing what `evalf` returns.
- Adding new `simplify` keyword arguments.

**Never:**
- Combine floats whose values differ.
- Silently convert user floats to rationals inside `simplify` unless that is the agreed behavior.
- Weaken or remove existing tests.

## Success Criteria

1. The root cause is identified and recorded: whether the exponents differ in precision, in value, or in some other attribute.
2. Depending on the decision made under Open Questions, one of these holds:
   - The snippet's result prints `0`, or
   - the documentation explains the behavior and names a working approach, verified by a test that produces `0`.
3. Floats with different values are never merged. This is covered by a test.
4. No existing tests regress.

## Open Questions

1. Does this still reproduce on the current SymPy release? The report uses Python 2 syntax.
2. Is this a bug or expected behavior? Should Floats with equal value but different precision count as the same term?
3. Where should a fix live? The options are:
   - `Float` equality and hashing (core, high impact),
   - `Add` and `Mul` term collection,
   - a step inside `simplify`, such as rationalizing or normalizing float exponents,
   - documentation only, recommending `nsimplify`, exact rationals, or calling `simplify` before `evalf`.
4. If floats are normalized, what tolerance or precision rule decides that two Floats are "equal enough"?
5. Should `simplify` with default options handle this, or only an opt-in such as `rational=True`?
6. Which Python and SymPy versions must the fix support?