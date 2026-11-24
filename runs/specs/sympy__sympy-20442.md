# Spec: `convert_to` must not return a dimensionally different result when the target units cannot represent the expression

## Objective

**Problem.** `sympy.physics.units.convert_to` returns a dimensionally incorrect result when the target unit(s) cannot exactly express the dimension of the input expression. This was reported on SymPy 1.4.

```
>>> convert_to(joule*second, joule)
joule**(7/9)
```

- `joule*second` has dimension `mass·length²·time⁻¹`.
- `joule**(7/9)` has dimension `mass^(7/9)·length^(14/9)·time^(-14/9)`.

These are not the same physical quantity. The function silently produces an approximate (best-fit) combination of the target units instead of an exact conversion.

**Why it matters.** Users rely on `convert_to` for correct physics. A silently wrong dimension is worse than an error, because it propagates into later calculations unnoticed.

**User.** Anyone who uses `sympy.physics.units` to change the units of an expression.

**Core invariant to establish.** For any expression `expr` and target units `T`, `convert_to(expr, T)` must have the **same dimension** and the **same physical value** as `expr`. It must never return a result whose dimension differs from the input's.

**User stories / acceptance criteria**

1. **Inexpressible target.** Converting an expression to target units that cannot exactly represent its dimension must not return a dimensionally different result. The default assumed behavior is to return the expression unchanged; see Open Questions.
2. **Representable targets keep working.** Conversions whose target units *can* exactly represent the expression must keep producing the same results as today. This includes the three examples the reporter calls "sensible."
3. **Legitimate fractional exponents are still allowed.** Fractional exponents in a result remain valid when they are exact. For example, converting a quantity whose dimension is truly `length^(1/2)` to `meter` may still yield `meter**(1/2)`. Only *inexact* fits are forbidden.

## Assumptions

1. The function in question is `convert_to` from `sympy.physics.units`. Its exact source file is not visible in the issue and is **unknown**.
2. The bad result comes from the conversion choosing target-unit exponents that only *approximately* match the input's dimension, for example by a least-squares style solve. Nothing checks that the match is exact. This is a hypothesis; the implementation is not visible.
3. The chosen behavior for an inexpressible conversion is to **return the original expression unchanged**, not to raise. Reasons:
   - It is the first option the reporter lists.
   - It does not break callers that pass a list of units and expect a best-effort result.
   - This is subject to confirmation in Open Questions.
4. The bug still exists on current SymPy, not only on 1.4. The reporter could not test 1.5+.
5. The fix is limited to `convert_to` behavior. No public signature changes and no new dependencies.
6. In the third "sensible" example, `J`, `s`, `kg`, `m` and `mins` are the standard SymPy unit objects (`joule`, `second`, `kilogram`, `meter`, `minute`) or aliases for them. They are not user-defined symbols.

## Tech Stack

- Python, SymPy, module `sympy.physics.units`.
- Supported Python and SymPy versions for the fix: **unknown**. The issue only mentions SymPy 1.4.

## Commands

All commands below are **unknown**, because the repository is not visible.

```
Build: unknown
Test (units module): unknown
Test (single test): unknown
Lint: unknown
```

## Project Structure

**Unknown.** The issue shows no paths. To be determined:
- the file that defines `convert_to`
- the location of the existing unit tests for `convert_to`

## Code Style

**Unknown.** Follow the existing conventions of the units module and SymPy. No snippet can be shown without repository access.

## Testing Strategy

**Level.** Unit tests in the existing test suite for `sympy.physics.units`. The framework and location are unknown.

**Required regression cases.** Exact expected outputs depend on resolving Open Question 1.

| Input | Expected (assuming "return unchanged") |
|---|---|
| `convert_to(joule*second, joule)` | `joule*second` |
| `convert_to(joule*second, joule*second)` | `joule*second` (unchanged from today) |
| `convert_to(joule*second, kilogram*meter**2/second)` | `kilogram*meter**2/second` (unchanged from today) |
| `convert_to(joule*second, minute)` | Today: `joule*minute/60`; must be confirmed (see Open Question 3) |

**Property-style check.** For each test case, assert that the dimension of the result equals the dimension of the input. This guards the core invariant directly, not just specific outputs.

**Non-regression.** All existing `convert_to` tests must pass unmodified, unless a change is explicitly approved.

## Boundaries

- **Always:**
  - Preserve the dimension and physical value of the input.
  - Add regression tests for the reported case.
  - Run the existing units test suite before considering the work done.
- **Ask first:**
  - Raising an exception instead of returning the expression unchanged.
  - Changing the result of any currently passing conversion.
  - Changing the function signature, for example adding a `strict` flag.
  - Adding dependencies.
- **Never:**
  - Return a result with a different dimension than the input.
  - Delete or weaken existing tests to make the change pass.
  - Change unrelated unit definitions.

## Success Criteria

1. `convert_to(joule*second, joule)` no longer returns `joule**(7/9)` or any other result whose dimension differs from `joule*second`. Under the current assumption it returns `joule*second`.
2. The three examples marked "sensible" in the issue return the same results as before.
3. Conversions that genuinely need rational exponents, where the target units exactly span the input dimension, still succeed.
4. For every new and existing `convert_to` test, the result's dimension equals the input's dimension.
5. The full existing test suite for `sympy.physics.units` passes.

## Open Questions

1. **Desired behavior for inexpressible conversions.** The reporter offers three options:
   - return the expression unchanged;
   - return it in base units;
   - raise an error.

   Which one should SymPy adopt? This spec assumes "unchanged." Raising an error is stricter, but may break existing callers.
2. **Partial expressibility with multiple targets.** When `target_units` is a list and only part of the expression's dimension can be expressed, what should happen? Options are to convert nothing, or to convert what is possible and leave the remainder.
3. **The `minute` example.** The reporter calls `convert_to(J*s, mins) → J*mins/60` sensible, but `minute` alone cannot express `energy·time`, so this result is a *partial* conversion that keeps `joule`. Two things need confirming:
   - Was this observed with standard SymPy unit objects or with user-defined symbols?
   - Under the new rule, should this case stay as `joule*minute/60`, or return `joule*second` unchanged?
4. **Unit systems.** Should the exactness check use the dimension system of the active/default unit system (e.g. SI)? Are there unit systems where dimensions are related in ways that affect "exact" representability?
5. **Versions.** Does the bug reproduce on the current development version? Which SymPy versions should get the fix?
6. **Documentation.** Should the `convert_to` docstring be updated to state the behavior for inexpressible targets?