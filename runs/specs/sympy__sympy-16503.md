# Spec: Vertical alignment of `Sum` summand with surrounding terms in pretty printing

## Objective

When a `Sum` is pretty-printed as part of a larger expression, such as `Sum(x, (x, 1, oo)) + 3`, the summand and the neighbouring terms are drawn on different rows. In the reported case the summand `x` sits one row above `+ 3`:

```
>>> pprint(Sum(x, (x, 1, oo)) + 3)
  ∞
 ___
 ╲
  ╲   x
  ╱     + 3
 ╱
 ‾‾‾
x = 1
```

**Goal:** the summand of a pretty-printed `Sum` must share a baseline with the operators and terms it is combined with. Here, `x` and `+ 3` must be on the same row.

**Users:** anyone using `pprint` or `pretty` (Unicode, and presumably ASCII) on expressions that contain `Sum`. Examples include interactive sessions, notebooks and documentation output.

**Success looks like:** `pprint(Sum(x, (x, 1, oo)) + 3)` renders `x` and `+ 3` on one row. The sum sign, upper limit and lower limit stay intact and readable.

## Assumptions

1. The bug is in the pretty printer's vertical baseline for `Sum`. It is not in `Add` printing, because `Add` simply aligns its terms on each term's baseline.
2. The summand is currently placed at a vertical offset that differs from the baseline the `Sum` pretty form reports to its parent. That mismatch is why `+ 3` lands one row below `x`.
3. ASCII mode (`use_unicode=False`) likely has the same or an analogous misalignment. It should be fixed and verified too.
4. The fix should also hold for:
   - multi-line summands, such as fractions
   - summands of different heights
   - nested sums
   - multiple limits (`Sum(f, (x, ...), (y, ...))`)
   - `Sum` appearing on either side of an `Add`, `Mul` or `Relational`
5. Related constructs that share the same drawing logic, such as `Product`, are out of scope unless they share the same code path. This needs to be confirmed; see Open Questions.
6. Existing pretty-printing tests that encode the current, misaligned output will need their expected strings updated. Changing those expectations is acceptable.
7. The sum symbol's shape (`╲ ╱`, `___`, `‾‾‾`) and the placement of the limits should not change. Only the vertical alignment should change.

## Tech Stack

- Python, SymPy (the version is unknown; it is not stated in the issue).
- The component is SymPy's pretty printer (`pprint` / `pretty`). The exact module and function are unknown from the issue.

## Commands

- Build: unknown; not given in the issue.
- Test: unknown; not given in the issue. The project's pretty-printing test suite is the expected target.
- Lint: unknown.
- Reproduce, taken from the issue:
  ```python
  from sympy import Sum, oo, pprint
  from sympy.abc import x
  pprint(Sum(x, (x, 1, oo)) + 3)
  ```

## Project Structure

Unknown. The issue does not show it. The location of the `Sum` pretty-printing logic and of its tests must be confirmed in the repository.

## Code Style

Unknown from the issue. Follow the existing conventions of the pretty-printing module and its tests. The expected output in tests should be written as literal multi-line strings that match the exact rendered output, consistent with however existing pretty-print tests are written.

## Testing Strategy

- Add regression tests for `pprint(Sum(x, (x, 1, oo)) + 3)` in both Unicode and ASCII modes, asserting the exact rendered string.
- Add tests for alignment in these variants:
  - A summand taller than one line, e.g. `Sum(1/x, (x, 1, oo)) + 3` or `Sum(x**2, ...)`.
  - A `Sum` as the right-hand operand, e.g. `3 + Sum(...)` and `y + Sum(...)` where ordering puts the `Sum` last.
  - A `Sum` multiplied by another factor, and a `Sum` inside an equation such as `Eq(Sum(...), 3)`.
  - Nested sums and sums with multiple limits.
  - Sums with tall upper or lower limits, e.g. a fraction in the limit.
- Run the full existing pretty-printing test suite, plus any other suites that compare pretty output (e.g. doctests). Review every changed expectation to confirm that it is an alignment-only change.
- Test levels: unit tests on rendered strings are sufficient. No integration or e2e testing applies.

## Boundaries

- **Always:**
  - Assert exact rendered output in tests.
  - Check both Unicode and ASCII modes.
  - Keep the sum sign's glyphs and the layout of its limits unchanged.
  - Review every existing test expectation that changes.
- **Ask first:**
  - Changing the rendering of other big operators (`Product`, `Integral`, etc.).
  - Changing the shape or size of the sum symbol.
  - Changing the public API of the pretty printer or the semantics of its baseline.
- **Never:**
  - Delete or weaken failing pretty-printing tests just to make the suite pass.
  - Special-case only the literal example `Sum(x, (x, 1, oo)) + 3` instead of fixing the general alignment.

## Success Criteria

1. In `pprint(Sum(x, (x, 1, oo)) + 3)`, the summand `x` and `+ 3` are on the same output row, in both Unicode and ASCII modes.
2. For any single-line summand, the summand's row equals the row on which adjacent `Add`, `Mul` and `Relational` operators are drawn.
3. For multi-line summands, the summand's own baseline (e.g. a fraction bar) aligns with the adjacent operators.
4. The sum sign, upper limit and lower limit render as before; only their vertical offset relative to neighbouring terms may change.
5. Nested sums and multi-limit sums remain correctly aligned with neighbouring terms.
6. Every existing pretty-printing test either passes unchanged or has an updated expectation whose only difference is the corrected vertical alignment.

## Open Questions

1. **Which way should alignment go?** Should the summand move down, so that `+ 3` stays where it is, or should the baseline move up, so that `+ 3` rises to the summand's row? The issue author is unsure. This decides the final rendered shape and every updated test expectation.
2. **Where should the baseline sit for even-height signs?** For a sum sign with an even number of rows, which row counts as the "middle": the upper middle or the lower middle? Should it depend on the summand's height?
3. **Should the same fix apply to related operators?** Should `Product` (and any other operator sharing the `Sum` drawing logic) get the same alignment fix in this change, or in a separate one?
4. **Is ASCII mode affected?** Is ASCII output confirmed to have the same misalignment, and must it be fixed in the same change?
5. **How should multi-line summands align?** For multi-line summands (fractions, matrices, nested sums), should alignment follow the summand's own baseline, or the vertical centre of the sum sign?
6. **What SymPy version and test layout apply?** Which SymPy version or branch is targeted, and what are the exact test commands and file locations for the pretty-printing tests? These are currently unknown.