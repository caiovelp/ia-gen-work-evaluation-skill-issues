# Spec: Figure remains picklable after `align_labels()`

## Objective

Calling `fig.align_labels()` (and probably `align_xlabels()` / `align_ylabels()`) makes a Matplotlib figure unpicklable. `pickle.dumps(fig)` then fails with:

```
TypeError: cannot pickle 'weakref.ReferenceType' object
```

The same figure pickles fine if the `align_labels()` call is removed.

**User:** Matplotlib users who serialize figures, for example to cache them, send them between processes, or save and restore them later, and who also align axis labels.

**Goal:** A figure on which label alignment has been requested can be pickled and unpickled. The restored figure keeps its aligned-label behaviour.

**Reported environment:** Matplotlib 3.7.0 on Windows. Backend and Python version were not given.

**Reproduction (from the issue):**

```python
import matplotlib.pyplot as plt
import pickle

fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)
time=[0,1,2,3,4]
speed=[40000,4300,4500,4700,4800]
acc=[10,11,12,13,14]
ax1.plot(time,speed)
ax1.set_ylabel('speed')
ax2.plot(time,acc)
ax2.set_ylabel('acc')

fig.align_labels()  # pickling works after removing this line

pickle.dumps(fig)
```

## Assumptions

1. The bug is not specific to Windows or to any backend. It is a serialization defect in figure state, so it should reproduce on all platforms.
2. The error is in the Python layer: some object that `align_labels()` stores on the figure holds `weakref` references, and the default pickling cannot handle them. Hypothesis, not verified: this is the figure's label-alignment grouping structure, likely a weakref-based grouping helper. The exact attribute and class are unknown without the source.
3. `align_xlabels()` and `align_ylabels()` record alignment state the same way `align_labels()` does, so they fail the same way.
4. Expected behaviour after unpickling: the alignment groups refer to the unpickled Axes objects, not to stale or missing ones. Labels stay aligned when the restored figure is drawn.
5. The bug is present in the current development branch, not only in 3.7.0.
6. The fix must not change the public API of `align_labels` / `align_xlabels` / `align_ylabels`.
7. Pickling an unaligned figure must keep working exactly as it does today.

## Tech Stack

- Python and Matplotlib. The affected version is 3.7.0; the target branch is unknown.
- The standard library modules `pickle` and `weakref` are involved.
- Supported Python versions and other dependencies are unknown, because they are not visible in the issue.

## Commands

All unknown, since the repository is not visible:

- **Build/install:** unknown
- **Test:** unknown. The project likely uses pytest, but the exact invocation and test file paths are not confirmed.
- **Lint:** unknown
- **Dev:** not applicable

## Project Structure

Unknown. The issue does not show any of these:

- The module that implements `Figure.align_labels`
- The module that implements the grouping helper that holds weakrefs
- The location of the existing pickling tests

## Code Style

Unknown. Follow the existing conventions of the files being modified. No style snippet is available from the issue.

## Testing Strategy

Add a regression test at the unit/integration level. The test location and framework are unknown.

The test should cover:

1. **Main regression.** Build a figure with at least two subplots and labels, call `align_labels()`, and assert that `pickle.dumps(fig)` succeeds.
2. **Round-trip.** `pickle.loads(pickle.dumps(fig))` succeeds and returns a usable figure that can be drawn, for example to an Agg canvas, without errors.
3. **Alignment preserved.** After round-trip and draw, the y-labels of the aligned axes are still aligned. One possible check is that their x positions in display coordinates are equal.
4. **Variants.** Repeat the checks after only `align_xlabels()` and after only `align_ylabels()`.
5. **No regression.** Pickling a figure without alignment still works. Existing pickle tests still pass.

## Boundaries

**Always:**
- Add a regression test that fails before the fix and passes after it.
- Keep the public signatures of `align_labels` / `align_xlabels` / `align_ylabels` unchanged.
- Keep the weak-reference semantics at runtime, so that grouping does not keep deleted Axes alive.

**Ask first:**
- Changing the behaviour or public interface of the shared grouping helper class, if other parts of the library use it.
- Replacing weak references with strong references.
- Adding new dependencies.

**Never:**
- Silently drop alignment state on pickling without agreement. That would change behaviour after unpickling.
- Remove or skip existing pickle tests.
- Fix this only for the reporter's platform or backend.

## Success Criteria

- [ ] The issue's reproduction script runs without raising, on the target branch.
- [ ] `pickle.loads(pickle.dumps(fig))` succeeds after `align_labels()`, `align_xlabels()`, or `align_ylabels()`.
- [ ] The unpickled figure draws without error, and its aligned labels are still aligned.
- [ ] Alignment groups in the unpickled figure refer only to the unpickled figure's own Axes.
- [ ] All existing tests, including pickling tests, still pass.
- [ ] A regression test covering the above is added.

## Open Questions

1. Which object exactly holds the weakrefs? Is it a shared grouping utility? If so, should that utility become picklable in general, which may affect other users of it, or should only the figure's pickling handle it?
2. Should alignment be preserved across pickling, or is it acceptable to drop alignment state on pickle and require users to call `align_labels()` again? This spec assumes it must be preserved.
3. Do other figure-level methods store similar weakref-based state that would hit the same error, for example subfigures or shared-axes groupings? Should they be in scope?
4. Which branch and versions should get the fix? Should it be backported to 3.7.x?
5. What are the test command and test file locations for pickling tests in this repository?
6. Does the bug also reproduce with `copy.deepcopy(fig)`, and is that in scope?