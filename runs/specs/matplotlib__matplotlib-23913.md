# Spec: `draggable` Keyword Argument for `Legend` Construction

## Assumptions

1. The project is **Matplotlib**. The issue names a `Legend` class with an `__init__` method, and that matches Matplotlib's `matplotlib.legend.Legend`. The repository was not inspected to confirm this.
2. `Legend` already has a public post-creation method that turns dragging on and off. It is assumed to be `set_draggable(state, use_blit=False, update='loc')`, possibly alongside an older `draggable()` method. The exact name and signature are unverified.
3. The user wants a **convenience shortcut** only. Passing `draggable=True` at construction should behave the same as creating the legend and then turning dragging on through the existing method. No new dragging behavior is requested.
4. `Axes.legend(...)` and `Figure.legend(...)` pass extra keyword arguments through to `Legend.__init__`. If so, the new keyword would work from those entry points with no changes there. This is unverified.
5. The default is `draggable=False`, so existing code behaves exactly as before.
6. Any existing rcParams-driven legend defaults are left alone. No new rcParam is added unless maintainers request one (see Open Questions).
7. The project is Python. The test framework is assumed to be pytest, but this is unverified.

## Objective

Let users make a legend draggable when they create it, for example `ax.legend(draggable=True)`, instead of needing a second call after creation.

**User story:** As a Matplotlib user building interactive figures, I want to pass `draggable=True` when I create a legend, so I can enable mouse dragging in one expression.

**Acceptance criteria:**
- `Legend(..., draggable=True)` produces a legend whose dragging state is on. This is the same state that calling the existing enable method right after construction would produce.
- `Legend(..., draggable=False)` and omitting the keyword both produce a non-draggable legend. This is the current behavior.
- The keyword works through the high-level entry points, `Axes.legend(...)` and `Figure.legend(...)`, and through `pyplot.legend(...)` if that function delegates to them.
- The existing post-creation method still works unchanged and is not deprecated by this change.
- The new keyword is documented in the `Legend` constructor docstring and in any shared legend keyword documentation.

**Question raised in the issue:** "Is there a code reason why this would not work?" The spec treats this as an open question to verify before implementation, not a settled fact. Possible blockers include:
- Dragging may need the legend to already be attached to a figure or canvas.
- Construction order may matter.
- Pickling or copying behavior may be affected.

## Tech Stack

- Language: Python (version unknown)
- Library: Matplotlib (version and branch unknown)
- Relevant components (assumed): `Legend` class, `Axes.legend`, `Figure.legend`, `pyplot.legend`, and the existing draggable-legend helper (assumed to be something like `DraggableLegend`)

## Commands

The issue does not show these, and they were not verified in the repository.

```
Build:   UNKNOWN
Test:    UNKNOWN (likely pytest-based; exact invocation and test path unknown)
Lint:    UNKNOWN
Docs:    UNKNOWN
```

## Project Structure

Unknown. The file holding the `Legend` class, the legend test module, and the docs or changelog location ("what's new" or API-change notes) all need to be identified in the repository.

```
<legend module>        → Legend class and __init__ (path UNKNOWN)
<axes/figure modules>  → legend() entry points (paths UNKNOWN)
<tests>                → legend tests (path UNKNOWN)
<docs>                 → user docs / release notes (path UNKNOWN)
```

## Code Style

Follow the project's existing conventions; none were visible in the issue. Intended usage:

```python
# Current behavior (two steps)
leg = ax.legend()
leg.set_draggable(True)   # method name assumed

# Requested behavior (one step)
leg = ax.legend(draggable=True)
```

Conventions to confirm:
- Keyword-argument ordering and placement in the `__init__` signature, such as whether it should be keyword-only.
- Docstring format (the project likely uses numpydoc; unverified).
- How legend keywords are documented in shared docstrings.

## Testing Strategy

- **Framework:** assumed pytest; unverified.
- **Unit tests** for the `Legend` constructor:
  - `draggable=True` results in the legend reporting a draggable state, through whatever getter or attribute exists today, which is unknown.
  - `draggable=False` and the omitted default both result in a non-draggable state.
- **Entry-point tests:** `ax.legend(draggable=True)` and `fig.legend(draggable=True)` produce draggable legends.
- **Equivalence check:** the state after `draggable=True` matches the state after calling the existing enable method post-construction.
- **Regression:** the existing legend test suite passes unchanged.
- **Out of scope:** interactive mouse-drag simulation is not required, unless the project already has a pattern for it.

## Boundaries

- **Always:**
  - Keep `draggable=False` as the default and preserve current behavior when the keyword is omitted.
  - Reuse the existing dragging mechanism rather than duplicating it.
  - Document the new keyword.
  - Add tests.
- **Ask first:**
  - Exposing `use_blit` or `update` options at construction.
  - Adding an rcParam for a global default.
  - Changing the signature or semantics of the existing post-creation method.
  - Deprecating any existing API.
- **Never:**
  - Change the default legend behavior.
  - Break the existing post-creation dragging API.
  - Remove or alter existing tests without approval.

## Success Criteria

- [ ] `Legend.__init__` accepts a `draggable` keyword, defaulting to `False`.
- [ ] Passing `draggable=True` gives a draggable legend, equivalent to calling the existing enable method after creation.
- [ ] `ax.legend(draggable=True)` and `fig.legend(draggable=True)` work without additional changes from the user.
- [ ] Omitting the keyword gives identical behavior to before the change.
- [ ] New tests cover True, False, and default, at both the constructor level and the entry-point level.
- [ ] The full existing test suite passes.
- [ ] The docstring documents `draggable`, and release notes are updated per project convention.

## Open Questions

1. **Feasibility:** Can dragging be enabled during `Legend.__init__`? It might need a canvas, figure, or event connection that does not exist yet at construction time. If so, should enabling be deferred, for example until the legend is added to the figure?
2. **Extra options:** Should the constructor also expose the `use_blit` and `update` options of the existing method? Possible forms include separate keywords or a dict, or keeping just a boolean.
3. **Global default:** Should there be an rcParam, for example `legend.draggable`, to set the default globally?
4. **API surface:** What is the exact name and signature of the existing post-creation method in the target version? Is a deprecated `draggable()` method still present, and could it clash with an attribute or keyword named `draggable`?
5. **Introspection:** Is there a public getter, such as `get_draggable()`, that tests should use to assert state? If not, should one be added?
6. **Signature placement:** Should `draggable` be keyword-only?
7. **Copy and pickle:** Does a legend created with `draggable=True` need to survive pickling or figure copying with its dragging state preserved?
8. **Commands and paths:** Where do the build, test, and lint commands, the legend source and test files, and the release-note locations live? None of these are known.