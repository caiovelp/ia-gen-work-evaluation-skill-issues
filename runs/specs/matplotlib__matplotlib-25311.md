# Spec: Pickling Figures with Draggable Legends and Annotations

## Objective

Make figures that contain a **draggable legend** or **draggable annotation** picklable. Today they raise `TypeError` when serialized.

**Users:** Matplotlib users who pickle figures, for example to save and restore interactive sessions, pass figures between processes, or cache them. Interactive backends such as QtAgg (`FigureCanvasQTAgg`) are a common case.

**Observed (Matplotlib 3.7.0, Python 3.10, Windows 10, pip install):**

```python
import matplotlib.pyplot as plt
import pickle

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot([0, 1, 2, 3, 4], [40, 43, 45, 47, 48], label="speed")
leg = ax.legend()
leg.set_draggable(True)   # pickling works without this line
pickle.dumps(fig)         # TypeError: cannot pickle 'FigureCanvasQTAgg' object
```

The reporter says the same error occurs for draggable annotations.

**Expected:** `pickle.dumps(fig)` succeeds. A figure with draggable artists pickles just like the same figure without them.

**User stories / acceptance:**
- As a user, I can call `set_draggable(True)` on a legend and still pickle the figure.
- As a user, I can make an annotation draggable and still pickle the figure.
- As a user, I can unpickle such a figure without errors. The legend or annotation appears in the same position and keeps its properties.

## Assumptions

1. **Root cause (hypothesis, not verified against source):** the helper object that implements dragging holds a direct reference to the figure canvas. It probably also holds canvas event-callback connection ids.
   - The figure already excludes its canvas when pickling.
   - This helper does not, so pickling it pulls in the GUI canvas, which cannot be pickled.
2. The failure is not specific to Qt. Any canvas object that cannot be pickled will trigger it. Even with Agg, a canvas reference held outside the figure is suspect.
3. Both draggable legends and draggable annotations share the same dragging machinery. One fix should therefore cover both.
4. **Drag behavior after unpickling.** This is not specified in the issue; see Open Questions. The baseline assumed here:
   - Pickling must not fail.
   - The draggable state should, ideally, be preserved after unpickling.
   - That state should reconnect to the new canvas once the figure is attached to one.
5. Pickle compatibility is only required within the same Matplotlib version. Matplotlib does not guarantee cross-version figure pickles.
6. The fix should not change the public API for `set_draggable` or for draggable annotations.

## Tech Stack

- Python (issue reports 3.10; the supported range for the target branch is **unknown**)
- Matplotlib (bug reported on 3.7.0; the target branch is **unknown**)
- Standard library `pickle`
- Backends: QtAgg reported. Others presumed affected.

## Commands

**Unknown.** The repository is not visible. The project's test runner is presumably pytest, but the exact commands and flags are not confirmed.

- Build: unknown
- Test: unknown (likely a pytest invocation targeting the pickling tests)
- Lint: unknown

## Project Structure

**Unknown.** The repository is not visible. The relevant areas, by name only:

- The module defining legends and `set_draggable`
- The module defining annotations and their draggable support
- The module defining the shared draggable helper (suspected to be the offset-box module)
- The existing pickling test module

None of the paths are confirmed.

## Code Style

Follow the existing Matplotlib conventions in the touched modules. The issue contains no style examples. Specific conventions to respect:

- Do not add new public API unless agreed.
- Keep private attributes underscore-prefixed.
- If a stored attribute or property is changed, follow the project's deprecation policy.

## Testing Strategy

Add regression tests to the existing pickling test suite (location unknown). Tests should cover:

1. **Draggable legend:** a figure with `legend.set_draggable(True)` round-trips via `pickle.dumps` / `pickle.loads` without error.
2. **Draggable annotation:** a figure with a draggable annotation round-trips without error.
3. **Interactive canvas reference:** reproduce the failure using a canvas object that cannot be pickled, so the test does not depend on Qt being installed. The exact mechanism is unknown; it may require a backend fixture or a stub canvas.
4. **Post-unpickle sanity:** the unpickled figure can be drawn, for example with `fig.canvas.draw()` on Agg. The legend or annotation still exists with the same position and properties.
5. **Optional, depending on the answer to Open Question 1:** after unpickling, the draggable state is preserved and responds to simulated mouse events on the new canvas.
6. **Non-regression:** existing figure pickling tests still pass. Dragging behavior on a live, non-pickled figure is unchanged.

## Boundaries

**Always:**
- Keep `pickle.dumps(fig)` behavior identical for figures without draggable artists.
- Add regression tests for both the legend and annotation cases.
- Preserve existing interactive drag behavior.

**Ask first:**
- Changing or removing any public attribute of the draggable helper, such as an exposed `canvas` attribute. This would need a deprecation path.
- Deciding whether draggability is restored or dropped after unpickling.
- Changes to the figure or canvas pickling protocol itself.

**Never:**
- Make canvases or GUI objects picklable.
- Silently disable dragging on live figures as a side effect of the fix.
- Remove or skip existing pickling tests.

## Success Criteria

- [ ] The reproduction script from the issue runs without `TypeError` on the QtAgg backend and on a non-interactive backend.
- [ ] The equivalent script with a draggable annotation also pickles without error.
- [ ] `pickle.loads(pickle.dumps(fig))` returns a figure that draws without error, with the legend or annotation present at the same location.
- [ ] Draggable behavior after unpickling matches the agreed answer to Open Question 1, and is covered by a test.
- [ ] Interactive dragging on non-pickled figures behaves exactly as before.
- [ ] New regression tests fail on the current code and pass after the fix.
- [ ] The full existing test suite passes.

## Open Questions

1. **What happens to dragging after unpickling?** After loading, should the legend or annotation still be draggable once attached to a new canvas? The alternative is that it unpickles as non-draggable.
2. **Is the root-cause hypothesis correct?** Assumption 1 needs verification against the source.
3. **Which other artists are affected?** Are other artists or tools that cache the canvas or callback ids affected in the same way? Examples include widgets and other users of the draggable helper. Should they be in scope, or tracked separately?
4. **Is the helper's `canvas` attribute public API?** If it must be replaced, for example by deriving the canvas from the reference artist's figure, is a deprecation required?
5. **Target branch:** should the fix target a bugfix release of 3.7.x or only the main development branch?
6. **Reproducing the failure in CI:** how should tests simulate a canvas that cannot be pickled, given that Qt may not be installed on CI?
7. **Other backends:** has the failure been confirmed on non-Qt backends such as TkAgg, MacOSX, or Agg? This determines how broadly the tests should claim coverage.