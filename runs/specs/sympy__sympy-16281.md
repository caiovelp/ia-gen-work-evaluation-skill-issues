# Spec: Improve Pretty-Printing of `Product`

## Objective

Make the 2D pretty-printed form of `Product` more compact and better proportioned, in both Unicode and ASCII modes.

**Who benefits:** anyone who views `Product` expressions through `pprint` or a similar pretty-print entry point.

**Problems reported in the issue:**

1. **Empty bottom row.** The ∏ symbol always ends with an empty row below the function body. This makes the bottom look asymmetric and makes the symbol taller than it needs to be.
2. **Too wide.** The ∏ is "too fat". From the samples, its interior width grows with the body's height rather than its width:
   - body height 1 → interior width 3
   - body height 3 → interior width 6
   - body height 4 → interior width 8
3. **Top bar (tentative).** The reporter thinks the top bar might look better if it extended one column past each vertical leg. The reporter says they are unsure about this.

**Target shape proposed in the issue** (Unicode, `Product(1/n**2, (n, 1, oo))`):

```
    ∞
─┬─────┬─
 │     │  1
 │     │  ──
 │     │   2
 │     │  n
  n = 1
```

The reporter adds a constraint: making the symbol much skinnier than this "starts to look bad". The result may still be roughly twice as wide as the equivalent `Sum`.

**Success looks like:**
- Product output is shorter (no trailing empty row) and narrower than today.
- Product output stays readable and symmetric.
- Product output stays correctly aligned when embedded in larger expressions.

## Assumptions

1. This issue is about SymPy's pretty printer (`pprint`, `Product`, `oo`, `use_unicode=False`). The actual file and function that render `Product` are not visible in the issue and are **unknown**.
2. The change is limited to the visual layout of `Product`. `Sum`, `Integral` and other operators are out of scope, apart from not regressing.
3. Both Unicode and ASCII (`use_unicode=False`) output must change consistently. The issue shows a target only for Unicode, so the ASCII target is inferred (see Open Questions).
4. The issue's mockup is a guide, not an exact specification. Small deviations, such as the exact width formula, are acceptable if they meet the criteria below.
5. Existing tests that hard-code the current `Product` output will need their expected strings updated. That counts as an intended behavior change, not a regression.
6. The rules for placing the limits stay as they are now:
   - The upper limit is centered above the symbol.
   - The lower limit (`n = 1`) is centered below it.
7. The baseline and vertical centering of the function body relative to surrounding terms must keep working, for example in `Product(...) * x` and in nested products.
8. Behavior for multiple limits is assumed to apply the new shape to each factor. The issue's examples show only single-limit products.

## Tech Stack

- Python, SymPy pretty-printing subsystem.
- Versions: **unknown**.

## Commands

- Build: **unknown** (not shown in the issue)
- Test: **unknown**. Presumably the project's standard test runner, targeted at the pretty-printing tests, but the exact command and path are not visible.
- Doctests: **unknown**
- Lint: **unknown**

## Project Structure

**Unknown.** The issue does not show the location of:
- the `Product` pretty-printing implementation;
- the pretty-printing tests;
- any documentation or doctests that embed `Product` output.

All three need to be located before planning.

## Code Style

Unknown. Follow the existing conventions of the pretty-printing module. No code is shown in the issue.

## Testing Strategy

- **Unit tests (pretty printer).** Assert the exact Unicode and ASCII output strings for at least these cases, which are the issue's own examples:
  - `Product(1, (n, 1, oo))`
  - `Product(1/n, (n, 1, oo))`
  - `Product(1/n**2, (n, 1, oo))`
- **Edge cases to cover:**
  - a symbolic upper limit wider than the symbol, e.g. `Product(1, (n, 1, k + 10))`;
  - a long lower-limit expression;
  - multiple limits, e.g. `Product(f, (n, 1, oo), (m, 1, oo))`;
  - a nested `Product`;
  - `Product` as a factor or term in a larger expression, e.g. `Product(...) * x` and `x + Product(...)`, to check baseline alignment.
- **Regression.** The existing pretty-printing test suite and doctests must pass. The only allowed changes are updated expected strings for `Product` output.
- **Coverage expectations:** unknown.

## Boundaries

**Always:**
- Update Unicode and ASCII rendering together.
- Update every hard-coded expected `Product` output in tests and doctests.
- Keep the upper and lower limits centered relative to the symbol.

**Ask first:**
- Adopting the extended top bar (`─┬─…─┬─`), since the reporter is unsure about it.
- Changing the shared helpers used by other operators, such as `Sum`.
- Changing the baseline semantics of the printed form.

**Never:**
- Change how `Sum`, `Integral`, etc. render as a side effect.
- Change the mathematical content or the order of printed limits.
- Delete failing tests instead of updating their expected output.

## Success Criteria

**1. No trailing empty row.** The last row of the vertical legs is level with the last row of the function body. For example, `Product(1/n**2, (n, 1, oo))` has 4 leg rows, not 5.

**2. Narrower symbol.** The interior width between the legs is strictly smaller than today for each example:

| Expression | Interior width today | Target in issue mockup |
|---|---|---|
| `Product(1, (n, 1, oo))` | 3 | — |
| `Product(1/n, (n, 1, oo))` | 6 | — |
| `Product(1/n**2, (n, 1, oo))` | 8 | 5 |

The final width rule must be documented in the tests.

**3. Readable proportions.** The symbol is not made "much skinnier" than the mockup. A reviewer judges this visually against the issue's mockup.

**4. Top bar.** Implemented with the extension or without it, depending on the decision in Open Questions. Either way, it is consistent between Unicode and ASCII.

**5. Unicode matches the mockup.** For `Product(1/n**2, (n, 1, oo))`, the Unicode output matches the issue's mockup, or a variant that has been agreed.

**6. ASCII follows the same rules.** ASCII output has no trailing empty row and the same narrower width.

**7. Alignment preserved.**
- Limits stay centered.
- The body stays vertically aligned with adjacent terms in compound expressions.
- Wide limits still widen the layout correctly.

**8. No regressions.** All existing tests pass, apart from intended updates to expected `Product` strings.

## Open Questions

1. **Top bar.** Should the top bar extend past the legs (`─┬─────┬─`)? The reporter is unsure. Who makes the final call?
2. **Width formula.** What exact width rule is wanted? Candidates:
   - a fixed small padding around the body;
   - a smaller height-proportional ratio;
   - the mockup's width of 5 for a body of height 4, generalized somehow.
   What is the minimum width for a height-1 body such as `Product(1, …)`?
3. **ASCII target.** The issue gives no target for ASCII. Should the top bar be `_` characters, extended past the legs like `_|_` / `__`? Or should it keep today's style, just narrower and without the empty row?
4. **Gap before the body.** In the mockup, the body starts two columns after the right leg. Today it starts one column after. Is the extra column intended?
5. **Sum consistency.** Should `Sum` change to match? For example, should both use the same padding or the same position for the limits? Or is this strictly `Product`-only?
6. **Multiple limits.** For products with multiple limits, should each ∏ get the new shape independently? Should adjacent symbols share spacing?
7. **Baseline.** With the trailing row removed, where should the baseline sit? This affects alignment with neighboring terms and should be confirmed against current behavior.
8. **Documentation impact.** Do documentation pages or tutorials outside the test suite embed `Product` pretty output that also needs updating? Their locations are unknown.