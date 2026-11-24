# Spec: Honor `set_visible(False)` on 3D Axes (`projection="3d"`)

## Objective

**Problem.** In Matplotlib 3.4.2, calling `set_visible(False)` on an Axes created with `projection="3d"` does not hide it. The subplot is still drawn: its panes, axis lines, ticks, labels and scatter artists all appear. For regular 2D Axes, `set_visible(False)` hides the Axes as expected.

**Who is affected.** Users who build multi-panel figures with 3D subplots and want to hide individual panels without removing them from the layout. For example, they may want to toggle a panel's visibility interactively, or blank one cell of a grid.

**Reproduction (from the issue):**

```python
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, subplot_kw={'projection': '3d'})
ax1.scatter(1, 1, 1)
ax2.scatter(1, 1, 1, c='r')
ax1.set_visible(False)

plt.show()
```

- **Actual:** `ax1` is rendered.
- **Expected:** `ax1` is not rendered. `ax2` renders normally.

**What we're building.** A behavior fix so that 3D Axes respect the standard Artist visibility contract. When `get_visible()` is `False`, drawing the Axes produces no output: no panes, axis lines, ticks, labels, grid, title or child artists. The behavior must match 2D Axes.

### User stories / acceptance

- As a user, when I call `ax.set_visible(False)` on a 3D Axes, the figure renders without that Axes. This holds on interactive backends (e.g. Qt5Agg) and on file output (`savefig`).
- As a user, when I call `ax.set_visible(True)` again, the Axes renders exactly as it did before it was hidden.
- As a user, hiding one 3D Axes does not change the rendering of the other Axes in the same figure.

## Assumptions

1. The root cause is in the 3D Axes drawing path. The 3D Axes class overrides `draw()` and does not short-circuit when the Axes is invisible, unlike the 2D path. This is unverified because the repository is not visible.
2. The fix belongs in the 3D toolkit, `mpl_toolkits.mplot3d`. The base `Artist.set_visible` / `get_visible` API does not need to change. The exact file path is not seen and is unknown.
3. The bug is backend-independent: it reproduces on Agg, Qt5Agg, and PDF/SVG output. The issue only reports Qt5Agg, so this is an assumption.
4. The bug still exists on the current development branch, not only in 3.4.2.
5. "Not visible" means nothing is drawn in the Axes' region. The Axes still occupies its layout slot. Neither the 2D nor the 3D version removes the Axes from the figure or reflows the layout.
6. Interaction behavior on a hidden 3D Axes, such as mouse rotation and zoom, is out of scope unless the 2D behavior for hidden Axes says otherwise. Rendering is the primary concern.
7. The `GridSpec` import in the reproduction is unused and has nothing to do with the bug.

## Tech Stack

- Python. The issue reports 3.8.10; the supported range for the target branch is unknown.
- Matplotlib, including the `mpl_toolkits.mplot3d` 3D toolkit. The target branch and version are unknown; the bug was reported against 3.4.2.
- Test framework: assumed to be pytest, with Matplotlib's image-comparison helpers. Unverified.

## Commands

The exact commands are unknown because the repository is not visible. They need to be confirmed from the project's contributor docs and CI configuration.

```
Build:  UNKNOWN (e.g. editable install of matplotlib — confirm)
Test:   UNKNOWN (assumed pytest-based; confirm path selection for the mplot3d tests)
Lint:   UNKNOWN (confirm project linter, e.g. flake8 config)
Dev:    N/A
```

## Project Structure

The layout is unknown. The following is inferred from the package names in the issue and from public Matplotlib conventions, and must be verified:

```
lib/matplotlib/                 → core library (Artist, Axes, Figure)        [UNVERIFIED]
lib/mpl_toolkits/mplot3d/       → 3D Axes implementation (likely fix site)   [UNVERIFIED]
lib/mpl_toolkits/.../tests/     → mplot3d tests (likely test site)           [UNVERIFIED]
```

## Code Style

- Follow the existing Matplotlib conventions in the touched module. These are not visible here, so no snippet is provided.
- Keep the fix minimal and local to the 3D draw path.
- Mirror how 2D Axes handle invisibility rather than inventing a new mechanism.

## Testing Strategy

- **Regression test (required).** Create a figure with two 3D subplots and call `set_visible(False)` on one. Verify that the hidden Axes contributes nothing to the render. Two candidate approaches; the choice is an open question:
  - **Image comparison:** compare against a reference figure where only the visible 3D Axes exists in the same layout slot. Using Matplotlib's figure-equality comparison avoids a new baseline image, if that helper exists. Unverified.
  - **Non-image check:** confirm that drawing the figure does not invoke drawing of the hidden Axes' children. For example, check that the hidden Axes' artists are not rendered, or check renderer call counts.
- **Round-trip test:** call `set_visible(False)` and then `set_visible(True)`. The output must match a never-hidden 3D Axes.
- **Non-regression:** the existing 2D and 3D test suites still pass. The visible 3D Axes renders identically to before the change.
- **Level:** unit and image tests only. No end-to-end or GUI tests are needed, because the fix is backend-independent per Assumption 3.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix and passes after it.
  - Keep 3D visibility semantics consistent with 2D Axes.
  - Run the full mplot3d and Axes test suites.
- **Ask first:**
  - Changing the shared `Artist` or base `Axes` drawing logic, as opposed to the 3D-specific path.
  - Adding new baseline images.
  - Changing interaction behavior (rotation, zoom, picking) of hidden Axes.
  - Adding a changelog or "API changes" note, if the project requires one.
- **Never:**
  - Change the public signature or semantics of `set_visible` / `get_visible`.
  - Remove or loosen existing tests.
  - Make the fix backend-specific (e.g. Qt-only).

## Success Criteria

1. The reproduction script renders only `ax2` (the red point and its 3D Axes). Nothing from `ax1` appears: no panes, axis lines, ticks, tick labels, grid lines, title or the blue scatter point.
2. The same result holds for `fig.savefig(...)` to a raster format and to a vector format.
3. A hidden 3D Axes keeps its layout slot. The position and size of `ax2` are unchanged compared with the case where `ax1` is visible.
4. After `ax1.set_visible(True)` and a redraw, `ax1` renders identically to a 3D Axes that was never hidden.
5. A new automated regression test covers criteria 1 and 4. It fails on the unfixed code and passes on the fixed code.
6. All existing 2D and 3D tests pass unchanged.

## Open Questions

1. Which branch or version should the fix target: the current main branch only, or also a 3.4.x/3.5.x backport?
2. Should the test use image comparison, either figure-equality or a new baseline, or a non-image check such as renderer calls or artist draw counts? What is the project's preference for 3D regression tests?
3. When a 3D Axes is hidden, should mouse interaction (rotation, zoom, pan) and event handling also be disabled? Or should the change be limited to rendering, consistent with whatever 2D Axes currently do?
4. Are there other 3D-specific paths that bypass the visibility check and should be fixed in the same change? Candidates include 3D-specific children drawn outside the normal child loop, and tight-bbox or layout computations that query the hidden Axes.
5. Should invisible 3D Axes be excluded from tight-bbox and constrained-layout calculations, matching 2D behavior? Or is that a separate issue?
6. Does the project require a changelog or what's-new entry for this bug fix?
7. What are the exact build, test and lint commands, and where do the mplot3d tests live? These are unknown here.