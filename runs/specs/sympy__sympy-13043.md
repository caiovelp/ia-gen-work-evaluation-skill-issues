# Spec: Deterministic output for `decompose(..., separate=True)` in `intpoly`

## Objective

`decompose()` in the `intpoly` module returns `list(poly_dict.values())` when called with `separate=True`. The order of that list comes from dictionary and hashing internals. It is not part of any defined contract, so it can change when unrelated core code changes. The issue reporter is already seeing test failures after core changes because of this.

**Goal:** give `decompose(..., separate=True)` a well-defined result that does not depend on hashing, dictionary insertion order or core internals. Callers and tests should not break when those internals change.

**Users:**
- Internal callers of `decompose` in `intpoly`, such as the polytope integration routines. These are assumed and need to be confirmed.
- Developers changing the core, who need the `intpoly` tests to stay stable.
- Any external users who call `decompose` directly.

**Acceptance criteria (user-story form):**
- As a core developer, I can change hashing or ordering internals without `intpoly` tests failing because of element order.
- As a caller of `decompose(expr, separate=True)`, I get either:
  - a result whose order is documented and reproducible, or
  - a result type that does not imply any order.

  The docstring states which one.
- As a maintainer, every test of `separate=True` asserts against the documented contract and does not rely on incidental order.

## Assumptions

1. The module is SymPy's polytope integration module. Its exact path is believed to be `sympy/integrals/intpoly.py`, but this is **unverified**.
2. With `separate=False`, `decompose` returns a dict mapping degree to the homogeneous component of that degree. That behavior is not in question and stays unchanged.
3. With `separate=True`, `decompose` returns the individual constituent terms or monomials, which are the values of an internal dict.
4. The internal callers of `separate=True` only iterate over the result. Either they sum per-term contributions, so order does not matter for correctness, or they use it in ways that must be confirmed.
5. The test failures come from order comparisons of the form `assert decompose(...) == [a, b, c]`, not from wrong mathematical content.
6. Removing or renaming `decompose` is out of scope. Only the return contract of `separate=True` is being fixed.

## Tech Stack

- Python, as part of SymPy. The supported Python and SymPy versions are **unknown**.
- Candidate ordering utilities (for example SymPy's canonical sort key or degree-based ordering) are available in the codebase. Which one to use is an open question.

## Commands

The exact commands are **unknown**; the issue does not specify them. Placeholders:

```
Test (intpoly only): UNKNOWN — likely the project's standard test runner targeted at the intpoly test file
Full test suite:      UNKNOWN
Lint / code quality:  UNKNOWN
Doctests:             UNKNOWN — decompose's docstring examples must also pass
```

## Project Structure

**Unknown.** The issue only names "intpoly". Expected locations, not verified:

```
<intpoly module>            → contains decompose() and its internal callers
<intpoly test module>       → tests for decompose / polytope integration
```

## Code Style

**Unknown.** Follow the existing conventions of the `intpoly` module and of SymPy in general.

Requirements on the change itself:
- Keep the public signature `decompose(expr, separate=False)` unchanged. The argument names should be confirmed against the source.
- Update the docstring to state the ordering or type contract of the `separate=True` return value explicitly.
- Docstring examples must show output that is stable under the new contract.

## Testing Strategy

- **Unit tests:**
  - Assert the `separate=True` result according to the chosen contract:
    - **If ordered:** compare against an explicitly ordered expected list, for inputs whose order is non-trivial (mixed degrees, several terms of the same degree, multiple variables).
    - **If unordered (set):** compare as sets, and assert the return type.
  - Tests must not depend on incidental dict or hash order.
- **Regression:** existing polytope integration tests that use `decompose` internally must still produce the same numerical or symbolic integrals.
- **Order-independence check:** if feasible, run the relevant tests under different hash seeds or with varied input term order, and confirm identical results.
- **Doctests:** the `decompose` docstring examples pass.
- **Coverage expectation:** **unknown**. At minimum, every branch of `separate=True` is exercised.

## Boundaries

- **Always:**
  - Keep `separate=False` behavior unchanged.
  - Keep integration results mathematically unchanged.
  - Document the return contract in the docstring.
  - Run the `intpoly` tests and doctests before committing.
- **Ask first:**
  - Changing the return type of `separate=True` (list → set, or any other type), since it may break external callers.
  - Adding a deprecation path.
  - Changing any internal caller beyond what the new contract requires.
- **Never:**
  - "Fix" tests by matching whatever order the current core happens to produce.
  - Remove failing tests without approval.
  - Change core hashing or ordering to satisfy `intpoly`.

## Success Criteria

1. The result of `decompose(expr, separate=True)` is either:
   - a sequence with a documented, deterministic order, identical across runs, hash seeds and Python versions; or
   - an unordered collection (e.g. a set) whose type makes the lack of order explicit.
2. The `decompose` docstring states which of these holds and gives an example consistent with it.
3. All `intpoly` tests and doctests pass, and none assert on incidental ordering.
4. Polytope integration results are unchanged for the existing test inputs.
5. The test failures reported after the core changes no longer occur because of `decompose` ordering. This needs verification by the reporter or against their branch, which is unknown.
6. `separate=False` output is unchanged.

## Open Questions

1. **What is `separate=True` used for?** Which internal callers and known external users depend on it, and does any of them depend on element order?
2. **Ordered list or set?**
   - Option A: sort the list by a defined key. Candidates:
     - total degree, then a canonical tie-breaker;
     - SymPy's default sort key;
     - lexicographic monomial order with a defined generator order.
   - Option B: return a set, which is a return-type change and needs a compatibility decision.
   - Option C: drop `separate=True` and have callers use the dict's values from `separate=False`. This raises the question of whether `separate=True` returns individual monomials rather than per-degree components, in which case C is not equivalent.
3. **Backward compatibility:** if the return type changes, is a deprecation cycle needed, or is `decompose` considered internal or private?
4. **Ordering key details**, if ordering is chosen:
   - How should terms of equal degree be ordered?
   - Should the generator order follow the expression's free symbols, sorted by name, or be passed in?
5. **Coefficients:** for inputs where a monomial has a numeric coefficient, are coefficients kept in the returned elements? This matters for sort-key and set semantics, since duplicates would collapse in a set.
6. **The reporter's failing tests:** which tests fail after the core change, and on which branch or PR? This is needed to confirm success criterion 5.
7. **Project commands and paths:** what are the exact test commands, test file location and supported Python/SymPy versions?
8. **Maintainer preference:** do the CC'd maintainers (@ArifAhmed1995, @certik) prefer a particular contract?