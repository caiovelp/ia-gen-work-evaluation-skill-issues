# Spec: Validate `**kwargs` in `Axis.set_ticks` / `Axes.set_xticks` when *labels* is not passed

## Objective

`Axis.set_ticks` (and wrappers such as `Axes.set_xticks`) accepts `**kwargs`. Its docstring describes them as "`.Text` properties for the labels", which "take effect only if you pass *labels*."

When *labels* is not passed, these kwargs are currently ignored without any validation. A misspelled or misplaced argument therefore has no effect and produces no warning or error. The issue's example is `ax.set_xticks([0, 1], xticklabels=["a", "b"])`. Here `xticklabels` is not a valid parameter: the user meant `labels=`. The call sets the ticks and drops the labels without any signal.

**Goal:** Users get feedback when they pass kwargs to `set_ticks` / `set_xticks` / `set_yticks` that cannot do anything.

**Users:** Matplotlib users who call tick-setting APIs, especially those who confuse `xticklabels=` with `labels=` or pass styling kwargs without labels.

**Acceptance criteria (user stories):**
1. As a user, if I pass an invalid `Text` property to `set_ticks` without *labels*, I get an error instead of silent success.
2. As a user, if I pass a valid `Text` property without *labels*, I either get an error or a clear warning (see Open Questions), and the docs say which one.
3. As a user, existing calls that pass *labels* together with valid `Text` kwargs behave exactly as before.
4. As a user, calls with no kwargs behave exactly as before.

## Assumptions

1. The issue covers `Axis.set_ticks` and every public wrapper that forwards `**kwargs` to it. This includes at least `Axes.set_xticks` and `Axes.set_yticks`. It may also include 3D axes (`set_zticks`) and colorbar tick setters, if they forward kwargs. I have not verified these wrappers.
2. "Valid Text properties" means the same validation that `Text` applies when properties are set via its `set`/`update` mechanism. The new check should reuse that existing mechanism rather than keep a separate list of allowed names.
3. The minimum required behaviour is the issue's first option: always validate kwargs as `Text` properties. Whether kwargs without *labels* also become an error is a design decision that needs a maintainer (Open Questions).
4. If the behaviour change is user-visible, it goes through Matplotlib's normal deprecation policy rather than an immediate hard break. One exception: invalid property names may reasonably raise immediately, because they never worked.
5. Validation happens before any tick state is changed, so a rejected call leaves the Axis unchanged.
6. The error raised for invalid property names matches the type and message style that `Text` already uses for unknown properties. I assume this is `AttributeError`, but have not confirmed it.
7. The docstring for `Axis.set_ticks` and its wrappers will be updated to describe the new behaviour.
8. A release note / API-change note is required, following the project's usual process.

## Tech Stack

- Python, Matplotlib library code.
- Exact Python and Matplotlib versions targeted: **unknown** (not stated in the issue).
- Relevant APIs named in the issue: `Axis.set_ticks`, `Axes.set_xticks`, `.Text`, `Axes.tick_params`.

## Commands

All commands are **unknown**, because the repository is not visible.

```
Build:       unknown
Test:        unknown (project test runner and invocation not visible)
Lint:        unknown
Docs build:  unknown
```

## Project Structure

**Unknown.** Source file locations for `Axis.set_ticks`, `Axes.set_xticks`, the tests, and the API-change/release-note directory are not visible in the issue and must be confirmed in the repository.

```
<unknown>  → module defining Axis.set_ticks
<unknown>  → module defining Axes.set_xticks / set_yticks (and any other wrappers)
<unknown>  → tests for axis/axes tick setting
<unknown>  → API change / release notes location
```

## Code Style

- Follow the existing Matplotlib conventions in the touched modules. Specific style rules and lint configuration are **unknown**.
- Reuse existing `Text` property validation and existing deprecation/warning helpers where the project has them. Their exact names are **unknown** and must be looked up rather than invented.
- No code snippet is included, because no source is visible.

## Testing Strategy

- Framework and test locations: **unknown** (to be confirmed in the repo).
- Test levels: unit tests on `Axis.set_ticks` and on each public wrapper (`Axes.set_xticks`, `Axes.set_yticks`, and others confirmed under Assumption 1).
- Required cases:
  1. `set_ticks(ticks)` with no kwargs: unchanged behaviour, no warning.
  2. `set_ticks(ticks, labels=..., <valid Text kwarg>)`: unchanged behaviour, and the kwarg is applied to the labels.
  3. `set_ticks(ticks, labels=..., <invalid kwarg>)`: still errors, as it does today.
  4. `set_ticks(ticks, <invalid kwarg>)` without labels: raises an error. This includes the issue's exact example, `ax.set_xticks([0, 1], xticklabels=["a", "b"])`.
  5. `set_ticks(ticks, <valid Text kwarg>)` without labels: behaves as decided in Open Question 1 (warning, deprecation warning, or error).
  6. After a rejected call, tick locations and labels are unchanged (Assumption 5).
  7. The `minor=True` path behaves the same as major ticks.
- The existing test suite passes. Any existing tests that rely on silently ignored kwargs are identified and listed for review, not deleted.

## Boundaries

- **Always:**
  - Validate kwargs against `Text` properties in every call path.
  - Keep behaviour identical when *labels* is passed with valid kwargs.
  - Update the docstrings of `Axis.set_ticks` and its wrappers.
  - Add tests for every case listed above.
  - Add an API-change note.
- **Ask first:**
  - Turning valid-but-ineffective kwargs (no *labels*) into a hard error, and whether a deprecation period is required.
  - Changing the signatures of public wrapper methods.
  - Extending the change to other tick-related APIs not named in the issue.
- **Never:**
  - Silently start applying kwargs to existing tick labels when *labels* is absent; that is a different feature.
  - Remove or weaken existing tests without approval.
  - Introduce a hand-maintained list of allowed `Text` properties.

## Success Criteria

1. `ax.set_xticks([0, 1], xticklabels=["a", "b"])` no longer succeeds silently; it raises an error that names the offending kwarg.
2. For any kwarg that is not a valid `Text` property, `Axis.set_ticks` raises an error whether or not *labels* is passed.
3. Passing a valid `Text` kwarg without *labels* produces the behaviour chosen in Open Question 1. That behaviour is documented in the `set_ticks` docstring and the API-change note.
4. All calls with *labels* plus valid kwargs, and all calls without kwargs, produce the same results as before. The existing test suite confirms this.
5. The behaviour is consistent across `Axis.set_ticks` and all public wrappers that forward kwargs.
6. A rejected call leaves the axis tick state unmodified.

## Open Questions

1. When *labels* is not passed and the kwargs are valid `Text` properties, what should happen?
   - (a) Accept them silently, but only after validation. This is the issue's minimum.
   - (b) Emit a warning.
   - (c) Deprecate, then make it an error.
   - (d) Raise an error immediately.
2. Should invalid property names raise immediately, or also go through a deprecation period? Some downstream code may currently pass junk kwargs without noticing.
3. Which exception type and message are expected? Should it match `Text`'s existing unknown-property error, or have a tailored message such as "did you mean `labels=`?" for `xticklabels`/`yticklabels`?
4. Which wrappers are in scope beyond `Axes.set_xticks`/`set_yticks`? Candidates are 3D `set_zticks`, colorbar tick setters, and polar/other projections.
5. Should a kwarg named `labels` passed inside `**kwargs`, or aliases like `ticklabels`, get special handling?
6. Which Matplotlib version is targeted, and where should the API-change note go? Both are unknown without repository access.