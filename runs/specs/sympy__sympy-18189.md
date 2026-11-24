# Spec: `diophantine` returns complete solution set regardless of `syms` order when `permute=True`

## Objective

`diophantine(eq, syms=..., permute=True)` gives different answers depending on the order of symbols passed in `syms`:

```
In [10]: diophantine(n**4 + m**4 - 2**4 - 3**4, syms=(m,n), permute=True)
Out[10]: {(-3, -2), (-3, 2), (-2, -3), (-2, 3), (2, -3), (2, 3), (3, -2), (3, 2)}

In [11]: diophantine(n**4 + m**4 - 2**4 - 3**4, syms=(n,m), permute=True)
Out[11]: {(3, 2)}
```

The second call is wrong. It returns only the base solution and drops the permuted and sign-changed solutions. Because the equation is symmetric in `m` and `n`, both calls should return the same set of 8 tuples. In general, the result should be the same solution set with each tuple's elements reordered to match `syms`.

**Who is affected:** Users of SymPy's Diophantine solver who pass `syms` in an order that differs from the solver's default (sorted) symbol order. They silently get incomplete results, which is a correctness bug.

**What success looks like:** The `syms` argument only controls the order of components in each solution tuple. It never changes which solutions are returned. All other keyword arguments, `permute` in particular, are honored the same way whatever order is chosen.

## Assumptions

1. The project is SymPy and the function is `sympy.solvers.diophantine.diophantine` (exact module path unknown, since the repository is not visible).
2. With the default symbol ordering (`syms=(m, n)` here, i.e. sorted order), `permute=True` already behaves correctly. Output `[10]` is the reference behavior.
3. The bug is in how `diophantine` handles a `syms` order that differs from its internal variable order. Hypothesis, not verified: on that code path, other options such as `permute` are not passed along, so the result is computed as if `permute=False`.
4. The intended semantics of `syms`: it sets the tuple element order of the output, and every solution must be remapped to that order.
5. The fix should not change behavior for calls that omit `syms` or that pass `syms` already in default order.
6. The same problem may affect other keyword arguments on the same path. If so, they are in scope (see Open Questions).

## Tech Stack

- Python, SymPy. Versions are unknown and not given in the issue.
- Test framework: unknown. Presumably SymPy's standard test suite (pytest-compatible `test_*.py` functions), but this is not confirmed from the repo.

## Commands

Unknown, since the repository is not visible. Expected categories:

- Run the relevant tests: *unknown*, e.g. the SymPy test runner targeted at the diophantine test module.
- Full test suite: *unknown*
- Lint / code quality: *unknown*

## Project Structure

Unknown, since the repository is not visible. Expected locations to confirm:

- Diophantine solver source: *unknown* (likely under `sympy/solvers/`)
- Diophantine tests: *unknown* (likely a `tests/` directory next to the solver module)

## Code Style

Unknown from the issue. Follow existing SymPy conventions in the surrounding module. Regression tests should take the form of the reproduction above, written as an equality assertion on the returned set.

## Testing Strategy

- **Level:** Unit tests on the public `diophantine` function.
- **Regression test (required):** For `eq = n**4 + m**4 - 2**4 - 3**4`:
  - `diophantine(eq, syms=(m, n), permute=True)` equals the 8-element set shown in `[10]`.
  - `diophantine(eq, syms=(n, m), permute=True)` equals the same 8-element set. The set is equal because it is symmetric.
- **Generalized property:** For an asymmetric equation, the result with reversed `syms` equals the default-order result with each tuple reversed. Example: an equation where `m` and `n` have different coefficients, with `permute=True`.
- **Non-regression:**
  - `permute=False` results stay the same for both `syms` orders, apart from tuple reordering.
  - Calls without `syms` are unchanged.
  - Existing diophantine tests still pass.
- **Coverage expectation:** Cover the code path where `syms` differs from the default variable order, with `permute=True` and with `permute=False`.

## Boundaries

- **Always:**
  - Add a regression test that reproduces the issue before or alongside the fix.
  - Keep `syms` semantics limited to output ordering.
  - Run the existing diophantine tests.
- **Ask first:**
  - Changing the public signature of `diophantine`.
  - Changing results for calls that don't pass `syms`.
  - Changing how `permute` decides which permutations and sign changes apply to which equation types.
- **Never:**
  - Weaken or delete existing tests to make the change pass.
  - Special-case the specific example equation.
  - Introduce new dependencies.

## Success Criteria

1. `diophantine(n**4 + m**4 - 2**4 - 3**4, syms=(n, m), permute=True)` returns `{(-3, -2), (-3, 2), (-2, -3), (-2, 3), (2, -3), (2, 3), (3, -2), (3, 2)}`.
2. For any equation `eq` and any permutation `s` of its free symbols, `diophantine(eq, syms=s, permute=P)` equals `diophantine(eq, permute=P)` with each tuple's elements reordered from the default order to `s`. This holds for both `P=True` and `P=False`.
3. All keyword options given to `diophantine` affect the result identically whether or not `syms` reordering is needed.
4. The new regression tests pass, and all existing diophantine tests still pass.

## Open Questions

1. Do other keyword arguments besides `permute` get dropped on the same `syms`-reordering path? If so, should they be fixed in this change or tracked separately?
2. What should happen when `syms` contains symbols not present in `eq`, or omits some of the free symbols? Is the current behavior intended, and is it in scope here?
3. Which SymPy version or branch is the target, and what are the exact commands to run the diophantine tests?
4. Where exactly do the diophantine solver and its tests live in the repository?
5. Should a changelog or release note entry be added for this correctness fix?