# Spec: Widget input is blocked after `clf()` + redraw inside a `RangeSlider.on_changed` callback

## Objective

**Problem.** A `RangeSlider` `on_changed` callback that calls `pyplot.clf()`, recreates widgets, and calls `pyplot.draw()` leaves the figure unresponsive. After that, no widget in the figure (the new slider or the new button) responds to mouse clicks. The same three steps run inside a `Button.on_clicked` callback work correctly.

**Goal.** Clearing and rebuilding a figure from inside a `RangeSlider` (and, if affected, `Slider`) `on_changed` callback must leave the new widgets fully interactive. It should behave the same as doing it from a `Button.on_clicked` callback.

**Users.** Matplotlib users who build interactive GUIs with `matplotlib.widgets` and rebuild figure contents in response to widget events.

**User story.** As a user building an interactive figure, I can call `clf()`, add new widgets and `draw()` inside a slider's change callback. The new widgets then receive mouse input normally.

### Reported reproduction (verbatim from the issue)

```python
import matplotlib.pyplot as pyplot
import matplotlib.widgets as widgets

def onchanged(values):
    print("on changed")
    print(values)
    pyplot.clf()
    addElements()
    pyplot.draw()

def onclick(e):
    print("on click")
    pyplot.clf()
    addElements()
    pyplot.draw()

def addElements():
    ax = pyplot.axes([0.1, 0.45, 0.8, 0.1])
    global slider
    slider = widgets.RangeSlider(ax, "Test", valmin=1, valmax=10, valinit=(1, 10))
    slider.on_changed(onchanged)
    ax = pyplot.axes([0.1, 0.30, 0.8, 0.1])
    global button
    button = widgets.Button(ax, "Test")
    button.on_clicked(onclick)

addElements()

pyplot.show()
```

- **Actual:** After the slider is moved, no widget responds to mouse clicks.
- **Expected:** The slider callback behaves like the button callback, and the rebuilt widgets stay interactive.

### Reported environments

| OS | Python | Matplotlib | Backend | Install |
|---|---|---|---|---|
| Windows 10 | 3.11.0 | 3.6.2 | TkAgg | pip |
| Manjaro Linux | 3.10.9 | 3.6.2 | QtAgg | distro package manager |

The bug shows on two GUI backends, which suggests it is backend-independent.

## Assumptions

1. **Root cause (hypothesis, to be confirmed).**
   - Unlike `Button`, the slider widgets "grab" the mouse for their axes when a drag starts. They fire `on_changed` *during* the drag, before the button-release event.
   - When the callback clears the figure, the grabbing axes is removed but the canvas-level mouse grab is never released.
   - Later mouse events are then routed only to a stale, removed axes, so every widget appears dead.
   - `Button` fires on release, after any grab handling, which would explain why it is unaffected.
2. The fix belongs in Matplotlib core (widgets and/or figure/axes removal and the canvas grab bookkeeping), not in user code.
3. Plain `Slider` likely has the same flaw because it shares the drag/grab mechanism. The fix should cover it too.
4. Clearing the figure by other means has the same effect as `clf()` and should be fixed too. Examples:
   - `fig.clear()`
   - removing the slider's axes, via `fig.delaxes(ax)` or `ax.remove()`
5. The fix must not change the public widget API or callback signatures.
6. Behavior is backend-independent, so it can be tested headlessly by synthesizing mouse events on a non-GUI canvas (e.g. Agg).
7. The target branch is the current development branch. Whether to backport to 3.6.x/3.7.x is unknown.

## Tech Stack

- Python, Matplotlib (affected version: 3.6.2; target branch unknown).
- Components involved (by name, as seen in the issue):
  - `matplotlib.widgets.RangeSlider`
  - `matplotlib.widgets.Button`
  - `matplotlib.pyplot.clf`
  - `matplotlib.pyplot.draw`
- The internal mouse-grab mechanism on the figure canvas is assumed relevant but not verified.
- GUI backends where reported: TkAgg, QtAgg.

## Commands

Unknown. The repository is not visible. Build, test and lint commands must be taken from the project's contributor docs.

- Build/install (dev): unknown
- Test: unknown (presumably pytest; exact invocation unknown)
- Lint: unknown

## Project Structure

Unknown. The exact source and test file locations for the widgets, figure and canvas code are not visible from the issue.

- Widget source module: unknown path (module `matplotlib.widgets`)
- Figure/canvas source modules: unknown paths
- Widget tests: unknown path
- Changelog/API-change notes location: unknown

## Code Style

Follow the existing Matplotlib code style and conventions (not visible here). Regression tests should drive widgets with synthesized mouse events in the same way existing widget tests do. That helper's name and location are unknown.

## Testing Strategy

- **Level: unit/regression tests, headless.** Use a non-interactive canvas with synthesized press/motion/release events. No GUI backend is required.
- **Required regression cases:**
  1. A `RangeSlider` whose `on_changed` calls `fig.clear()` and recreates a `RangeSlider` and `Button`. A full drag (press, motion, release) must run, after which:
     - the canvas holds no lingering mouse grab;
     - a click on the new `Button` fires its `on_clicked`;
     - a drag on the new `RangeSlider` changes its value and fires `on_changed`.
  2. The same as case 1 with `Slider` instead of `RangeSlider` (if confirmed affected).
  3. Removing only the grabbing slider's axes (not the whole figure) mid-drag. The remaining widgets must stay responsive.
  4. The existing `Button.on_clicked` path still works (no regression).
  5. Existing slider drag behavior is unchanged when no figure clearing happens. Values update during drag, and the grab is released on mouse release.
- **Manual check (optional):** Run the reproduction script on TkAgg and QtAgg and confirm the rebuilt widgets respond.
- **Coverage expectations:** Unknown project threshold. The new code paths must be covered by the tests above.

## Boundaries

- **Always:**
  - Add a failing regression test reproducing the issue before the fix.
  - Keep public widget APIs and callback semantics unchanged.
  - Run the existing widget and figure test suites.
- **Ask first:**
  - Changing *when* `on_changed` fires (e.g. deferring it to mouse release). This would alter documented and expected live-update behavior.
  - Changing public canvas/figure APIs.
  - Backporting to maintenance branches.
- **Never:**
  - "Fix" the issue by telling users to avoid `clf()` in callbacks.
  - Special-case only `RangeSlider` if the root cause is shared with `Slider` or general axes removal.
  - Remove or skip existing failing tests without approval.

## Success Criteria

1. The reproduction script needs no modification: after moving the range slider, both rebuilt widgets respond to mouse input on TkAgg and QtAgg.
2. The canvas holds no mouse grab on an axes that has been removed from its figure. This holds whether removal happens through `clf()`/`fig.clear()`, `delaxes`, or `ax.remove()`.
3. All new regression tests pass, and all existing widget and figure tests still pass.
4. Slider/RangeSlider live updates during a drag behave as before when the figure is not cleared.
5. `Button` behavior is unchanged.

## Open Questions

1. **Root cause.** Is it confirmed that a stale canvas mouse grab on a removed axes causes the block? Or is there another cause, such as stale event connections from the old widgets?
2. **Scope.** Should the fix be general (release any mouse grab when its axes is removed or the figure is cleared)? Or should it be local to the slider widgets? The general fix seems preferable but affects core figure/axes code.
3. **Other widgets.** Is plain `Slider` affected? Are other widgets that grab the mouse (e.g. selectors) affected when their axes is removed mid-interaction?
4. **Semantics.** If the grabbing widget's axes is removed mid-drag, should the rest of that drag be ignored? Or should it go to whatever axes is now under the cursor?
5. **Target branch.** Which branch is the target, is a backport to 3.6.x/3.7.x wanted, and is a changelog entry required?
6. **Commands and paths.** What are the project's build/test/lint commands and source/test file locations? These are unknown from the issue.