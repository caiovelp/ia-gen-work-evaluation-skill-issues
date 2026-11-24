# Spec: `get_backend()` must not remove figures created under `rc_context`

## Objective

Calling `matplotlib.get_backend()` should only read state. Today it can change global figure state. If the first figure in `Gcf.figs` was created inside `matplotlib.rc_context()`, a later call to `get_backend()` empties `plt._pylab_helpers.Gcf.figs`. After that, the figure is no longer tracked, so operations such as `plt.close(fig2)` silently fail because `Gcf.destroy_fig()` cannot find it.

**Users affected:** anyone who calls `get_backend()` after creating figures inside `rc_context`. This includes user scripts and any library or tool that queries the backend. The report uses Matplotlib 3.5.2 with the QtAgg backend on Xubuntu and Python 3.10.4.

**Observed conditions from the issue:**
- The bug **reproduces** when the first figure is created inside `with rc_context():` and nothing else has resolved the backend first.
- The bug **does not reproduce** if a figure is created outside `rc_context` beforehand (`fig1 = plt.figure()`).
- The bug **does not reproduce** if `plt.ion()` is called beforehand.
- The identity of the `Gcf` object stays the same. Only its contents (`Gcf.figs`) are cleared.

**Success looks like:** the reproduction script from the issue runs without an `AssertionError`. The figure stays registered in `Gcf.figs` and can be closed with `plt.close(fig2)`.

### Hypothesis (to confirm, not established by the issue)
Both workarounds (`plt.figure()` or `plt.ion()` outside the context) force the backend to be resolved before `rc_context` is entered. This suggests the following sequence:
1. Inside the context, backend resolution happens and the result is stored in the context's temporary rcParams.
2. When the context exits, the "not yet resolved / auto" backend value is restored.
3. `get_backend()` sees the unresolved value and resolves the backend again, which closes all existing figures.

This must be confirmed by reading the code before any fix is designed.

## Assumptions
1. The fix belongs in Matplotlib itself, not in user code.
2. `get_backend()` is intended to have no side effects on existing figures or on `Gcf`.
3. The bug is not specific to QtAgg. It is expected to reproduce with any backend that is resolved lazily (for example, the automatic backend selection default), including non-interactive backends such as Agg in CI.
4. `rc_context` should keep restoring all other rcParams exactly as it does now. Only the backend interaction is in scope.
5. An explicitly set backend (for example via `matplotlib.use()` or an explicit `rcParams['backend']` inside the context) should still behave as currently documented. Changing that behavior is not part of this fix.
6. The bug still exists on the current main branch, not only in 3.5.2. This is unverified.

## Tech Stack
- Python, Matplotlib (reported on 3.5.2; target branch unknown)
- Relevant public/internal APIs named in the issue: `matplotlib.get_backend`, `matplotlib.rc_context`, `matplotlib.pyplot.figure`, `matplotlib.pyplot.ion`, `matplotlib.pyplot.close`, `matplotlib._pylab_helpers.Gcf` (`Gcf.figs`, `Gcf.destroy_fig`)
- Test framework: unknown (presumably pytest; not stated in the issue)

## Commands
- Build: unknown
- Test: unknown
- Lint: unknown
- Reproduce: run the script from the issue with a Python interpreter that has Matplotlib installed. The exact invocation and backend environment are unknown.

## Project Structure
Unknown. No repository paths are visible in the issue. The relevant code is expected to be in:
- the `matplotlib` package top-level module, where `get_backend` and `rc_context` live
- `matplotlib.pyplot`, for backend switching and figure creation
- `matplotlib._pylab_helpers`, for `Gcf`

Exact file paths are unknown.

## Code Style
Follow existing Matplotlib conventions. No style snippet is available from the issue.

## Testing Strategy
- Add a regression test that reproduces the issue scenario:
  1. Start with a fresh, unresolved backend state.
  2. Create a figure inside `rc_context()`.
  3. Call `get_backend()`.
  4. Assert that `Gcf.figs` is unchanged, both in its keys and in the manager objects.
- Add a test that `plt.close(fig)` successfully removes the figure from `Gcf` after `get_backend()` was called.
- Keep the two workaround paths (a figure created first, or `plt.ion()` called first) passing as non-regression checks.
- The test must reset backend and rcParams state so it does not leak into other tests. How the test suite isolates this is unknown.
- Test levels: unit or integration within the existing test suite. Test file location is unknown.

## Boundaries
- **Always:**
  - Keep `get_backend()`'s return value semantically correct.
  - Keep `rc_context` restoring all other rcParams.
  - Add a regression test.
- **Ask first:**
  - Changing the documented semantics of `rc_context` with respect to the `backend` rcParam.
  - Changing when or how automatic backend resolution happens.
  - Altering `Gcf` behavior or public APIs.
- **Never:**
  - Make `get_backend()` close, recreate, or drop existing figures.
  - "Fix" the issue by changing the test to call `plt.ion()` or create a figure first.
  - Remove or weaken existing tests.

## Success Criteria
1. The issue's reproduction script completes without `AssertionError`. `before == after` holds for both the `Gcf` id and the `Gcf.figs` contents.
2. After `get_backend()`, `plt.close(fig2)` removes `fig2` from `Gcf.figs`.
3. `get_backend()` returns the same backend name that was actually resolved for the figure created inside the context.
4. Repeated calls to `get_backend()` are idempotent and have no side effects on `Gcf`.
5. The existing behavior of `rc_context` for non-backend rcParams is unchanged, as verified by the existing test suite passing.
6. Explicitly setting a backend inside or outside `rc_context` behaves as before.

## Open Questions
1. Should the backend that is resolved lazily inside an `rc_context` persist after the context exits? Or should `rc_context` restore the unresolved/auto state while `get_backend()` avoids triggering a figure-closing switch? This decides where the fix belongs.
2. If a user *explicitly* sets `rcParams['backend']` inside `rc_context`, what should happen to that backend and its figures when the context exits?
3. Is the bug still present on the current main branch, and which branch or version should the fix target? Should it be backported to 3.5.x?
4. Does the bug reproduce with non-interactive backends (for example Agg) so it can be tested in CI without a display?
5. Are there other read-only accessors that have the same side effect and should be covered too? For example, reading `rcParams['backend']` directly, or `pyplot` functions that query the backend.
6. Which test file and which fixtures for resetting backend state should the regression test use?