# Spec: Restore backward-compatible access to deprecated `seaborn-*` style names via `plt.style.library`

## Assumptions

1. **Cause (unverified).** Matplotlib 3.6 renamed the bundled seaborn styles from `seaborn-<name>` to `seaborn-v0_8-<name>`, because they no longer match what current seaborn ships. The old names were deprecated rather than removed outright.
2. **Inconsistent behavior (unverified).** In 3.6.x, `plt.style.use("seaborn-colorblind")` still resolves the old name and emits a deprecation warning. Direct dictionary access `plt.style.library["seaborn-colorblind"]` raises `KeyError` because `library` only contains the new names. The deprecation period therefore covers one public access path but not the other. That inconsistency is the bug.
3. The intended fix keeps the old names working for the rest of the deprecation period through **every** public lookup path, including `style.library[...]`, with the same deprecation warning `style.use` gives. Removing the alias completely is out of scope; that happens later, on the normal deprecation schedule.
4. `plt.style.library` is the same object as `matplotlib.style.library`, so fixing one fixes both.
5. The reporter's "Expected outcome" ("seaborn-colorblind should be set as the library style") really means: the lookup returns the rcParams dict for that style without raising. `library[...]` reads a style. It does not apply one.
6. The bug is not specific to an OS or backend. The reporter saw the same behavior on macOS and Ubuntu.
7. All other deprecated `seaborn-*` names are affected the same way (e.g. `seaborn-dark`, `seaborn-whitegrid`, `seaborn-deep`, and the bare `seaborn`). The fix should cover the whole set, not only `seaborn-colorblind`.

## Objective

Users upgrading from Matplotlib ≤3.5 to 3.6.x have code like:

```python
import matplotlib.pyplot as plt
the_rc = plt.style.library["seaborn-colorblind"]
```

It now fails with `KeyError: 'seaborn-colorblind'` at import time. It should keep working during the deprecation period and warn the user to migrate to `seaborn-v0_8-colorblind`, as `plt.style.use("seaborn-colorblind")` already does.

**User:** downstream library and application authors who read style definitions directly from `plt.style.library`, for example to merge them into their own rcParams or use them in `rc_context`.

**Acceptance criteria (user stories):**
- As a user on 3.6.x, when I access `plt.style.library["seaborn-colorblind"]`, I get the same rcParams mapping as `plt.style.library["seaborn-v0_8-colorblind"]`, plus a deprecation warning naming the replacement.
- As a user, `plt.style.use(...)`, `plt.style.context(...)`, and `plt.style.library[...]` behave the same way for deprecated seaborn names.
- As a user listing styles (`plt.style.available`, iterating `library`), I don't see the deprecated names advertised as current styles. This needs confirmation; see Open Questions.

## Tech Stack

- Python (reporter: 3.9.7). The project's supported Python range is **unknown**.
- Matplotlib 3.6.1 (regression vs 3.4.3). The fix targets the 3.6.x maintenance line. The exact target branch is **unknown**.
- Module involved: the `matplotlib.style` package (`library`, `use`, `context`, `available`). The internal file layout is **unknown / to be confirmed** from the repo.

## Commands

The issue gives no commands. All of these are **unknown** and must come from the repository's contributor docs:

```
Build/install (dev): UNKNOWN
Test:                UNKNOWN (likely pytest-based; confirm)
Lint:                UNKNOWN
Docs build:          UNKNOWN
```

Reproduction command (from the issue):
```
python -c "import matplotlib.pyplot as plt; plt.style.library['seaborn-colorblind']"
```

## Project Structure

**Unknown.** The repository isn't visible. To be identified:
- Source location of the `matplotlib.style` implementation (where `library` is built and where `use()` handles the seaborn rename)
- Location of existing style tests
- Location of API-change / deprecation notes and what-new docs

## Code Style

**Unknown.** Follow the repository's existing conventions. In particular, use the project's own deprecation-warning helper and warning category, matching what `style.use` already emits for these names. Don't introduce a new warning mechanism.

## Testing Strategy

- **Framework:** unknown (assumed pytest; confirm).
- **Location:** alongside existing `matplotlib.style` tests (path unknown).
- **Required test cases:**
  1. `style.library["seaborn-colorblind"]` does not raise. It returns a mapping equal to `style.library["seaborn-v0_8-colorblind"]` and emits the project's deprecation warning (asserted with the warning-capture utility the project uses).
  2. Parameterized over **every** deprecated `seaborn-*` alias (including bare `seaborn`): each resolves to its `seaborn-v0_8-*` counterpart with a warning.
  3. Accessing the new names (`seaborn-v0_8-colorblind`) emits **no** warning.
  4. A truly unknown key (e.g. `"not-a-style"`) still raises `KeyError`.
  5. `style.use("seaborn-colorblind")` and `style.context("seaborn-colorblind")` keep their current behavior (regression guard).
  6. Whatever is decided for `"seaborn-colorblind" in style.library`, `.get(...)`, iteration, and `style.available`, with an explicit test for each (see Open Questions).
  7. `style.reload_library()` keeps the alias behavior. It must not replace `library` with a plain dict that loses the aliasing, and existing references to `library` must stay valid if the project relies on that.
- **Coverage expectation:** unknown. At minimum, every new branch in the lookup path is exercised.

## Boundaries

- **Always:**
  - Resolve deprecated names to the exact same style data as the `seaborn-v0_8-*` names, not a copy that can drift.
  - Emit the same deprecation message and category as `style.use` for the same name.
  - Keep `KeyError` for genuinely unknown style names.
  - Add a regression test reproducing the issue's exact snippet.
  - Run the full style test suite before committing.
- **Ask first:**
  - Changing the type of the public `style.library` object, e.g. from plain `dict` to a subclass. Possible `isinstance`/pickling/identity implications.
  - Whether deprecated names appear in `in`, `.get()`, `keys()`, iteration, or `style.available`.
  - Backporting to 3.6.x vs fixing only on main.
  - Changing the deprecation removal version or message text.
- **Never:**
  - Re-add the old `seaborn-*` style files or entries as first-class styles. That undoes the deprecation.
  - Silently alias without a warning.
  - Remove or weaken existing deprecation tests for `style.use`.
  - Change the contents of any style sheet.

## Success Criteria

1. Running the issue's reproduction snippet on the fixed build **does not raise**. It emits one deprecation warning naming `seaborn-v0_8-colorblind` as the replacement.
2. `plt.style.library["seaborn-colorblind"] == plt.style.library["seaborn-v0_8-colorblind"]` is `True`.
3. Criteria 1 and 2 hold for every deprecated `seaborn-*` alias accepted by `style.use`.
4. New-style names produce no warnings. Unknown names still raise `KeyError`.
5. `style.use` / `style.context` behavior for old and new names is unchanged. All existing style tests pass.
6. Behavior persists after `style.reload_library()`.
7. A changelog / API note entry exists if the project requires one for behavior changes (format unknown).

## Open Questions

1. **Root cause confirmation:** Does `style.use` already special-case the deprecated seaborn names in 3.6.x, so that only `library[...]` misses it? Assumption 2 needs verification against the repo.
2. **Membership and listing semantics:** Should `"seaborn-colorblind" in plt.style.library` return `True`? Should `.get("seaborn-colorblind")` return the style, with or without a warning? Should deprecated names appear in iteration or `plt.style.available`? Keeping them hidden avoids advertising them. Supporting `in`/`.get` maximizes backward compatibility.
3. **Type of `library`:** Is changing `library` from a plain `dict` to a dict subclass (or another mapping) acceptable for the public API? Do any tests or downstream users depend on `type(library) is dict`?
4. **Target release:** Should this be backported to a 3.6.x bugfix release, or only fixed on main?
5. **Reporter expectation:** The reporter wrote that the style "should be set". Is the expectation only that the lookup succeeds, as assumed, or does their code rely on anything else that changed between 3.4.3 and 3.6.1?
6. **Documentation:** Should the 3.6 API-change note for the seaborn rename be updated to mention `style.library` access explicitly, and tell users to migrate to `seaborn-v0_8-*` (or to use the seaborn package's own styling)?
7. **Removal timeline:** When the alias is eventually removed, the `KeyError` will return. Is the existing deprecation removal version the right one for this access path too?
8. Repository commands, project structure, test framework, and coverage requirements are all **unknown** and must be filled in from the repo.