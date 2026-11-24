# Spec: Passing `constrained_layout=False` should not trigger layout-engine incompatibility warnings

## Objective

In Matplotlib 3.6.0, creating a figure with an explicit `constrained_layout=False` triggers a `UserWarning` when the user later calls `plt.subplots_adjust(...)`. The issue also reports this for `bbox_inches='tight'`. The warning says:

> UserWarning: This figure was using a layout engine that is incompatible with subplots_adjust and/or tight_layout; not calling subplots_adjust.

The reporter says the plot still renders as expected. However, the warning text says `subplots_adjust` is not being called, so the requested spacing may also be silently ignored. Both need to be checked.

**Who is affected:** Users who pass `constrained_layout=False` explicitly, for example to override an rcParam default, to be explicit, or because a variable holds the value. They expect it to behave the same as omitting the argument.

**Expected behavior:** An explicit `constrained_layout=False` is equivalent to not requesting constrained layout:
- No layout-engine incompatibility warning is emitted.
- `subplots_adjust` and `tight_layout` take effect normally.

**Reproduction (from the issue):**
```python
import matplotlib.pyplot as plt
import numpy as np
a = np.linspace(0,2*np.pi,100)
b = np.sin(a)
c = np.cos(a)
fig,ax = plt.subplots(1,2,figsize=(8,2),constrained_layout=False)
ax[0].plot(a,b)
ax[1].plot(a,c)
plt.subplots_adjust(wspace=0)   # emits UserWarning in 3.6.0
```

The warning does not appear when the `constrained_layout=False` argument is removed. The reporter says previous versions did not warn.

### User stories / acceptance criteria
- As a user, when I pass `constrained_layout=False`, I can call `subplots_adjust` without a warning, and the subplot parameters are applied.
- As a user, when I pass `constrained_layout=False`, I can save with `bbox_inches='tight'` without a layout-engine warning.
- As a user, when I pass `constrained_layout=True`, I still get the incompatibility warning on `subplots_adjust`. That behavior is intentional and must be preserved.

## Assumptions
1. The root cause is in how the figure-creation path interprets an explicit falsy `constrained_layout` value. The likely mechanism is that the argument is checked with "is not None" rather than for truthiness, so a constrained-layout (or similar incompatible) layout engine is attached even when the value is `False`. This is unverified; I have no access to the source.
2. The analogous keyword `tight_layout=False` may have the same defect, and should be covered under the same criteria.
3. The `bbox_inches='tight'` symptom shares the same root cause as the `subplots_adjust` symptom. The issue gives no separate reproduction for it.
4. This is a regression introduced in 3.6.0, when the layout-engine mechanism was introduced. The exact "previous version" is not stated in the issue.
5. Explicit `False` should also not attach any engine that blocks later user-chosen layouts. The figure should behave like the default, no-argument case.
6. The fix should not change behavior for `constrained_layout=True`, `layout="constrained"`, `layout="tight"`, or the default `None`.

## Tech Stack
- Python library: Matplotlib (reported against 3.6.0, installed via conda, OS X).
- Test framework: **unknown**. Presumably pytest, but this is not confirmed from the issue.
- Python version and backend: not specified in the issue. The bug appears to be backend-independent.

## Commands
- Build: **unknown**
- Test: **unknown**
- Lint: **unknown**
- Run reproduction: `python repro.py`, using the snippet above saved locally. Run it with warnings turned into errors, e.g. `python -W error::UserWarning repro.py`.

## Project Structure
**Unknown.** The repository is not visible. The relevant code is the figure construction path that handles the `constrained_layout` / `tight_layout` / `layout` keyword arguments. It is reached via `plt.subplots` → figure creation, and also `plt.figure` and direct `Figure(...)` construction. Exact file locations are unknown.

## Code Style
**Unknown.** Follow the existing conventions of the Matplotlib codebase, which are not visible here. No new public API should be introduced.

## Testing Strategy
- **Level:** Unit/regression tests at the figure API level. No image-comparison tests should be needed.
- **Regression tests to add (behavioral, framework TBD):**
  - Create a figure with `constrained_layout=False`, call `fig.subplots_adjust(wspace=0)`. Assert:
    - no `UserWarning` is raised;
    - the figure's subplot parameters reflect `wspace == 0`.
  - The same check via `plt.subplots(..., constrained_layout=False)` followed by `plt.subplots_adjust(...)`.
  - The same check with `tight_layout=False` (see Assumption 2).
  - With `constrained_layout=False`, call `fig.tight_layout()` and save with `bbox_inches='tight'` to an in-memory buffer. Assert no layout-engine incompatibility warning is raised.
  - Control case: `constrained_layout=True` followed by `subplots_adjust` still emits the incompatibility warning.
  - Control case: omitting the argument behaves identically to `constrained_layout=False`. Compare the layout engine state and the subplot params.
- **Coverage expectation:** All new branches in the keyword-handling logic are exercised. The specific threshold is unknown.

## Boundaries
- **Always:**
  - Preserve existing behavior for truthy values and for the `layout=` keyword.
  - Add regression tests that fail on 3.6.0 behavior.
  - Run the existing figure/layout test suites before committing.
- **Ask first:**
  - Changing the warning text.
  - Changing what happens when *both* `layout=` and `constrained_layout=`/`tight_layout=` are passed.
  - Changing behavior for non-bool falsy values (e.g. `{}` used as a constrained-layout kwargs dict).
  - Adding deprecations.
- **Never:**
  - Suppress or remove the incompatibility warning globally to hide the symptom.
  - Make `subplots_adjust` silently succeed when constrained layout *is* active.
  - Remove or loosen existing tests.

## Success Criteria
1. Running the reproduction snippet with `-W error::UserWarning` completes without error.
2. With `constrained_layout=False`, `subplots_adjust(wspace=0)` actually changes the figure's `wspace` to 0.
3. With `constrained_layout=False`, `tight_layout()` and `savefig(..., bbox_inches='tight')` produce no layout-engine incompatibility warning.
4. With `constrained_layout=True`, `subplots_adjust` still warns, as it does today.
5. A figure created with `constrained_layout=False` is behaviorally indistinguishable, in layout-engine terms, from one created without the argument.
6. All existing tests pass, and the new regression tests pass.

## Open Questions
1. Should `tight_layout=False` be fixed in the same change? Is it confirmed to have the same defect?
2. What should a figure created with `constrained_layout=False` report as its layout engine? Should it be no engine at all (identical to the default), or some neutral placeholder that remains compatible with `subplots_adjust` / `tight_layout`?
3. How should non-bool values be treated? A dict of constrained-layout parameters presumably enables constrained layout; what about an empty dict? Does "falsy" mean only `False`/`None`, or Python truthiness?
4. Is `bbox_inches='tight'` really affected by this bug, or does it emit a different warning? A separate reproduction for that path would confirm it.
5. Which release is the "previous version" that didn't warn? Is this targeted as a 3.6.x bugfix backport?
6. Is `subplots_adjust` actually being skipped, so the requested spacing is lost, as the warning text implies? Or is the reporter right that the output is unaffected? This determines whether the bug is a spurious warning or a functional regression.
7. Where are the relevant source and test files, and what are the project's test/lint commands? All unknown without repository access.