# Spec: Emit `xlim_changed` on Axes Whose Limits Change via a Shared Axis

## Objective

**Problem.** If two Axes share an x-axis (e.g. `sharex=`), calling `set_xlim` on one Axes also updates the limits of its siblings. The siblings' registered `xlim_changed` callbacks do not fire. Code listening on a sibling never learns that its visible x-range changed.

**Root cause, as quoted in the issue** (`lib/matplotlib/axes/_base.py`, `set_xlim`):

```python
if emit:
    self.callbacks.process('xlim_changed', self)
    # Call all of the other x-axes that are shared with this one
    for other in self._shared_x_axes.get_siblings(self):
        if other is not self:
            other.set_xlim(self.viewLim.intervalx,
                           emit=False, auto=auto)
```

Siblings are updated with `emit=False`. In this code `emit` controls two separate things:

1. Whether this Axes processes its own `xlim_changed` callbacks.
2. Whether this Axes propagates the change to its shared siblings.

Passing `emit=False` to siblings prevents infinite mutual recursion between siblings. That is behaviour (2). It also suppresses their callbacks, which is behaviour (1).

**Reporter's observations.**
- Passing `emit=True` to siblings causes a recursion problem.
- Moving `callbacks.process('xlim_changed', ...)` outside the `if emit:` block appeared to fix the problem in local testing. This is a candidate approach, not a validated decision.

**Users.**
- Users who register `ax.callbacks.connect('xlim_changed', ...)` on Axes in shared-axis layouts. Examples include linked views, custom tick and annotation updates, and data reloading on zoom or pan.
- Downstream libraries that rely on `xlim_changed` to stay in sync with the view.

**User story.** As a user with Axes `A` and `B` sharing an x-axis and a `xlim_changed` callback on `B`, I want that callback to fire when `A`'s x-limits change. `B`'s limits changed too, so `B`'s listeners need to know.

**Success.** Every Axes whose x view limits change because of a shared-axis update fires its `xlim_changed` callbacks:
- exactly once per change,
- without infinite recursion,
- without changing which Axes end up with which limits.

## Assumptions

1. The intended meaning of `xlim_changed` is "this Axes' x view limits changed", whatever the source of the change, including propagation from a shared sibling.
2. The same defect almost certainly exists for `ylim_changed` in `set_ylim`, which most likely mirrors `set_xlim`. It may also exist for the z-axis equivalent in 3D Axes. This is unverified because only the `set_xlim` snippet is visible.
3. Sibling propagation should remain one level deep from the originating Axes, as it is today. `get_siblings` returns the whole share group, so siblings do not need to re-propagate.
4. A call to `set_xlim(..., emit=False)` made directly by user code is assumed to still suppress callbacks on that Axes. Only internally propagated updates to siblings are in scope. See Open Questions, because the reporter's proposed fix would change this.
5. The callback receives the sibling Axes whose limits changed, not the originating Axes. This matches the existing `process('xlim_changed', self)` signature.
6. Python version, supported matplotlib branch, and the code layout outside `_base.py` are unknown.

## Tech Stack

- Python, matplotlib (version or branch affected: **unknown**).
- Relevant component: `lib/matplotlib/axes/_base.py`, specifically `set_xlim` (and probably `set_ylim`), the Axes `callbacks` registry, and `_shared_x_axes` / `get_siblings`.
- Other modules involved, such as the 3D Axes or the axis-sharing grouper implementation: **unknown**.

## Commands

**Unknown.** No build, test, or lint commands are given in the issue.
- Build: unknown
- Test: unknown (the project likely uses pytest, but the exact invocation is not confirmed)
- Lint: unknown

## Project Structure

Only the following is known from the issue:

```
lib/matplotlib/axes/_base.py   → Axes base class; contains set_xlim and shared-axis propagation
```

The test file locations for Axes behaviour and the location of 3D Axes code are **unknown**.

## Code Style

- Follow the existing style of `_base.py`, as shown in the snippet above.
- The existing convention for firing callbacks is `self.callbacks.process('<signal>', self)`. Keep it.
- No further conventions are visible.

## Testing Strategy

- **Framework:** unknown (presumed pytest, unconfirmed).
- **Test level:** unit tests on Axes objects. No rendering or image comparison is needed.
- **Scenarios to cover:**
  1. Two Axes share x. A callback is registered on `B`. Calling `A.set_xlim(...)` fires `B`'s callback exactly once, and the callback receives `B`.
  2. The callback on `A` still fires exactly once when `A.set_xlim(...)` is called.
  3. Three or more Axes in a share group: every sibling's callback fires exactly once, and no recursion error occurs.
  4. Limit values on all siblings after the change are identical to current behaviour.
  5. The direct `A.set_xlim(..., emit=False)` case behaves as decided in Open Questions Q1.
  6. Equivalent tests for `ylim_changed`, and for 3D if it is in scope.
  7. Interactive-style changes such as pan, zoom, and autoscale that route through `set_xlim` also notify siblings. The exact entry points are unknown, so these tests are optional and depend on the scope decision.
- **Coverage expectation:** unknown. At minimum, every scenario above must have a regression test.

## Boundaries

- **Always:**
  - Keep the recursion guard so that sibling propagation terminates.
  - Preserve the final limit values on all shared Axes.
  - Add regression tests.
  - Apply the same fix consistently to x and y, and to z if in scope.
- **Ask first:**
  - Changing the public meaning of the `emit` parameter on `set_xlim` / `set_ylim`.
  - Adding a new public or private parameter to these methods.
  - Extending the fix to 3D Axes.
  - Any change to the order in which callbacks fire, for example originator before or after siblings.
- **Never:**
  - Pass `emit=True` to siblings in a way that reintroduces recursion.
  - Fire a callback more than once per Axes per change.
  - Change which Axes are considered siblings.
  - Remove or weaken existing tests.

## Success Criteria

1. After `A.set_xlim(new)`, where `A` and `B` share x, every `xlim_changed` callback registered on `B` has been called exactly once with `B` as its argument.
2. The same holds for every member of a share group of size 3 or more.
3. `A`'s own `xlim_changed` callbacks still fire exactly once.
4. No `RecursionError` occurs and no infinite loop occurs, for any share-group size.
5. Final `get_xlim()` values on all shared Axes are unchanged from current behaviour.
6. Criteria 1–5 hold for `ylim_changed` / `set_ylim`.
7. The behaviour of a direct user call with `emit=False` matches the documented decision from Q1, and that behaviour is covered by a test.
8. All existing tests pass. The exact test command is unknown.

## Open Questions

1. **Semantics of `emit=False` for direct calls.** Should `A.set_xlim(..., emit=False)` called directly by user code still suppress `A`'s own callbacks?
   - The reporter's proposed fix moves the callback outside `if emit:`. That would always fire callbacks and make `emit` control only propagation, which is a public behaviour change.
   - The alternative is to separate the two concerns, so that internal propagation fires sibling callbacks but does not re-propagate.
   - Which is preferred?
2. **Silent updates for siblings.** If callbacks are always fired, will user code that uses `emit=False` to avoid callback feedback loops break? This applies to code that sets limits from inside a `xlim_changed` handler. Is there a known downstream reliance on this?
3. **Scope.** Is the fix limited to 2D `set_xlim` and `set_ylim`, or should it include 3D Axes, for example z-limits and any equivalent shared-axis logic?
4. **Siblings whose limits do not change.** Should a sibling's callback fire if its limits were already equal to the new values? Does the originator's callback currently fire in that case?
5. **Callback order.** Should the originator's callback fire before or after its siblings' callbacks? Do any callers depend on the current order?
6. **Callbacks that modify limits.** If a sibling's `xlim_changed` handler itself calls `set_xlim`, what is the expected behaviour, and what recursion protection is required?
7. **Versioning.** Which matplotlib versions or branches should receive the fix? Does the behaviour change need a changelog or API-change note?
8. **Project details.** What are the project's test and lint commands, and where should the regression tests go? All three are unknown.