# Spec: Consistent, value-preserving `simplify()` for `ceiling` expressions parsed with `evaluate=False`

## Objective

`simplify()` returns a different result for the same expression depending on whether it was built with `sympify(..., evaluate=False)` or `evaluate=True`. The issue reports this for SymPy 1.6.2. It was not present in 1.5.1.

```python
sympify('4*ceiling(x/4 - 3/4)', evaluate=False).simplify()  # 1.6.2 → 4*ceiling(x/4) - 3
sympify('4*ceiling(x/4 - 3/4)', evaluate=True).simplify()   # 1.6.2 → 4*ceiling(x/4 - 3/4)
```

This is a **correctness bug**, not just a style difference. The two results are not mathematically equal:

- At `x = 0`, the original is `4*ceiling(-3/4) = 0`.
- At `x = 0`, the "simplified" form is `4*ceiling(0) - 3 = -3`.

So `simplify()` changes the value of the expression on the `evaluate=False` path.

**Users:** SymPy users who parse strings with `evaluate=False` (for example, to keep the user's input form) and then call `simplify()`.

**Success looks like:**
1. `simplify()` never returns an expression that differs in value from its input. This applies to `ceiling` and `floor` with non-integer offsets.
2. For this input, the `evaluate=False` and `evaluate=True` paths give the same simplified result, as they did in 1.5.1.

## Assumptions

1. The expected output for both paths is `4*ceiling(x/4 - 3/4)`, matching 1.5.1 and the current `evaluate=True` result. Any other value-equivalent form is acceptable only if both paths agree.
2. `x` is a plain `Symbol` with no assumptions: not integer, may be complex or real.
3. Root-cause hypothesis, not verified because the repository is not available:
   - With `evaluate=False`, the argument `x/4 - 3/4` stays as an unevaluated tree. For example, `-3/4` may be held as `Mul(-3, Pow(4, -1))` rather than `Rational(-3, 4)`.
   - Somewhere in the 1.6 code path, the integer part `-3/4` is then wrongly pulled out of the ceiling, or the term is wrongly judged to be an integer. Candidates are an integrality check, `ceiling` argument handling, or `Mul` distribution inside `simplify`.
   - The defect most likely lives in core or functions code, not in the parser.
4. The fix belongs in the SymPy library itself. A user-side workaround is a secondary deliverable.
5. Correctness wins over uniformity: if the paths cannot be made identical, both must at least be value-equivalent to the input.

## Tech Stack

- Python, SymPy. Affected version: 1.6.2. Last known-good version: 1.5.1.
- Exact supported Python versions for the target branch: **unknown**.

## Commands

Unknown, because the repository is not visible. The project's standard test runner (e.g. a `pytest` or `bin/test` invocation) must be confirmed.

- Build: unknown
- Test: unknown
- Lint: unknown

## Project Structure

Unknown. The relevant areas are likely the following, all **to be confirmed**:

- The `ceiling`/`floor` implementation (integer-part functions).
- Core `Mul`/`Add` integrality assumptions.
- `simplify`.
- `sympify`/parser handling of `evaluate=False`.

## Code Style

Follow the existing SymPy conventions. No snippet is available from the issue.

## Testing Strategy

- Add regression tests next to the existing tests for the module where the root cause is found. The location is unknown.

**Required cases:**
- `sympify('4*ceiling(x/4 - 3/4)', evaluate=False).simplify()` equals `sympify('4*ceiling(x/4 - 3/4)', evaluate=True).simplify()`.
- The simplified result is numerically equal to the input at sample points, for example `x ∈ {0, 1, 2, 3, 4, -1, 5/2}`.
- The same checks for `floor(x/4 - 3/4)`.
- The same checks with other non-integer offsets, for example `ceiling(x/3 + 1/3)`.

**Guard cases** (existing correct behavior must not regress):
- `ceiling(x + 1)` still becomes `ceiling(x) + 1`, because an integer offset may legitimately be extracted.
- The same with `x` declared `integer=True`.

**General requirements:**
- The tests must fail on the current code and pass after the fix.
- The full existing test suite must keep passing.

## Boundaries

**Always:**
- Add regression tests that reproduce the issue.
- Verify value-equivalence of every simplification.
- Run the full test suite for the touched modules.

**Ask first:**
- Changing what `evaluate=False` means for parsing in general.
- Changing the public `simplify` output for expressions other than the integer-part functions.
- Changing integrality assumptions in core `Mul`/`Add`, which has a wide blast radius.

**Never:**
- Paper over the bug by special-casing the string in `sympify`.
- Weaken or remove existing tests.
- Accept a "consistent" result that is mathematically wrong.

## Success Criteria

- [ ] Both `evaluate=False` and `evaluate=True` give `4*ceiling(x/4 - 3/4)` for the reported input, or the same value-equivalent expression on both paths.
- [ ] No `simplify()` result for `ceiling`/`floor` with a non-integer constant offset differs in value from its input at the tested points.
- [ ] Integer offsets are still extracted where valid, e.g. `ceiling(x + 1) → ceiling(x) + 1`.
- [ ] The root cause is identified and fixed at its source, not only at the `sympify` entry point.
- [ ] All existing tests pass.

## Open Questions

1. Where exactly does the 1.6 change come from? A `git bisect` between 1.5.1 and 1.6.2 should identify the commit. Is it a bad integrality check on unevaluated `Mul`/`Pow`, or `ceiling`/`floor` argument splitting?
2. What should the canonical simplified form be: the original unchanged form, or another equivalent form? Must the output be structurally identical across both paths, or only value-equivalent?
3. Does the bug reproduce without `simplify`? For example, with `expand`, or with direct construction such as `Mul(4, ceiling(Add(Mul(x, Pow(4,-1)), Mul(-3, Pow(4,-1), evaluate=False), evaluate=False)), evaluate=False)`.
4. Are `floor`, `frac`, and other integer-part functions affected the same way?
5. Which branch or version should the fix target? Is a backport to the 1.6.x series expected?
6. Should the reply to the reporter include an interim workaround, such as re-sympifying with `evaluate=True` before `simplify()`? Is that workaround safe in general?