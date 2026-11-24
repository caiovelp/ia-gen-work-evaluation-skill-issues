# Spec: Intersection Must Give Duplicate-Invariant Results (SymPy `Intersection`)

## Assumptions

1. This is the SymPy library. `Intersection`, `FiniteSet`, `S.EmptySet`, `Piecewise`, and `Eq` are the SymPy objects the issue refers to.
2. In the issue, `{1}` and `{x}` mean `FiniteSet(1)` and `FiniteSet(x)`. `x` is a plain `Symbol` with no assumptions, so `x` may or may not equal `1`.
3. The bug lives in the evaluation path of `Intersection` (construction or simplification). It is not in `FiniteSet` itself. I cannot confirm the exact function because I have no access to the code.
4. Mathematically, intersection is idempotent and commutative: `A ∩ A = A`, and argument order does not matter. The result must not depend on repeated arguments or on the order of arguments.
5. Both outcomes the reporter offers count as correct. One is `Piecewise((FiniteSet(1), Eq(x, 1)), (S.EmptySet, True))`. The other is an unevaluated `Intersection`. The firm requirement is that the result is never wrong (`EmptySet`) and is the same whether or not duplicates are present.
6. The reporter suggests removing duplicates and ordering the arguments canonically at instantiation. I record this as a proposed approach, not a settled design.
7. Public API signatures will not change.

## Objective

Make `Intersection` return a correct result that does not change when duplicate arguments are present.

**Current (incorrect) behavior, as reported:**
```python
>>> Intersection({1}, {1}, {x})
EmptySet()          # wrong: if x == 1 the true answer is {1}
>>> Intersection({1}, {x})
{1}                 # also questionable: if x != 1 the true answer is EmptySet
```

The two calls describe the same mathematical set, yet they return different results. Neither result is correct for every value of `x`.

**Desired behavior:**
- `Intersection({1}, {1}, {x})` and `Intersection({1}, {x})` return the same result.
- That result is either `Piecewise((FiniteSet(1), Eq(x, 1)), (S.EmptySet, True))` or an unevaluated `Intersection(FiniteSet(1), FiniteSet(x))`.
- Results do not depend on the order of the arguments.

**Users:** SymPy users who work with symbolic sets, and downstream SymPy code (solvers, `solveset`, set simplification) that relies on `Intersection` giving correct results.

## Tech Stack

- Python, SymPy. The supported Python and SymPy versions are unknown and not given in the issue.
- Relevant objects: `Intersection`, `FiniteSet`, `EmptySet`, `Piecewise`, `Eq`.

## Commands

All commands are unknown because no repository is available. Placeholders to confirm:
```
Test (targeted): unknown (likely a pytest/sympy test runner invocation on the sets tests)
Test (full):     unknown
Lint:            unknown
Build:           unknown / not applicable
```

## Project Structure

Unknown; the issue does not show it. Expected locations to confirm:
- The source of `Intersection` and its simplification/evaluation logic: unknown path (probably a sets module).
- Tests for sets: unknown path.

## Code Style

Follow existing SymPy conventions in the sets module. I cannot see the code, so I give no snippet. Expected behavior in doctest form, taken from the issue:

```python
>>> Intersection({1}, {1}, {x}) == Intersection({1}, {x})
True
```

## Testing Strategy

- **Framework:** SymPy's existing test suite. The exact runner is unknown.
- **Level:** Unit tests in the existing sets tests, plus doctests if the docstring is updated.
- **Cases to cover:**
  1. `Intersection({1}, {1}, {x})` is neither `EmptySet` nor `{1}`. It is the agreed `Piecewise` or the unevaluated form.
  2. `Intersection({1}, {x})` gives the same result as case 1.
  3. Argument order does not matter: `Intersection({x}, {1})`, `Intersection({x}, {1}, {1})`, and `Intersection({1}, {x}, {1})` all give the same result.
  4. Fully numeric cases still evaluate correctly:
     - `Intersection({1}, {1})` gives `{1}`.
     - `Intersection({1}, {2})` gives `EmptySet`.
     - `Intersection({1, 2}, {2, 3}, {2, 3})` gives `{2}`.
  5. Duplicate non-finite arguments do not change results. For example, `Intersection(Interval(0, 1), Interval(0, 1), {x})` equals `Intersection(Interval(0, 1), {x})`.
  6. Regression: the existing sets and solveset tests still pass.

## Boundaries

- **Always:**
  - Keep results mathematically correct.
  - Prefer leaving an expression unevaluated over returning a wrong answer.
  - Add regression tests for the reported examples.
  - Run the existing sets tests.
- **Ask first:**
  - Changing the public output form of existing `Intersection` results that are currently correct.
  - Choosing `Piecewise` over the unevaluated form as the canonical output.
  - Changing how `Union` or other set operations canonicalize their arguments.
- **Never:**
  - Change public signatures.
  - Delete or weaken existing tests to make them pass.
  - Return a result that is wrong for some value of a free symbol.

## Success Criteria

- [ ] `Intersection({1}, {1}, {x})` no longer returns `EmptySet()`.
- [ ] `Intersection({1}, {x})` no longer returns `{1}` unconditionally.
- [ ] Both return the same object: the agreed `Piecewise` or the unevaluated `Intersection`.
- [ ] The result is invariant under duplicate arguments and under permutations of the arguments.
- [ ] Numeric-only intersections still produce the same results as before.
- [ ] New regression tests cover the reported cases. The existing sets test suite passes.

## Open Questions

1. **Output form:** Which is the preferred canonical result for `Intersection({1}, {x})`: `Piecewise((FiniteSet(1), Eq(x, 1)), (S.EmptySet, True))` or an unevaluated `Intersection`? Do other parts of SymPy, such as `solveset`, expect one form over the other?
2. **Scope:** Should we fix only duplicate invariance? Or should we also fix the separate bug that `Intersection({1}, {x})` returns `{1}` even with no duplicates?
3. **Approach:** Should duplicate removal and canonical ordering happen at instantiation, as the reporter suggests? Or should they happen inside the simplification routine? Does any caller pass `evaluate=False` and depend on duplicates being kept?
4. **Ordering key:** If arguments are sorted, which canonical ordering should we use (for example, SymPy's default sort key)? Could a different order change the results of other simplification rules?
5. **Symbol assumptions:** Should behavior differ when `x` carries assumptions, such as `integer=True` or a known value?
6. **Related operations:** Do `Union` or `Complement` show the same duplicate or order sensitivity, and should they be in scope?
7. Which SymPy version is affected, and what are the exact test and lint commands and file paths?