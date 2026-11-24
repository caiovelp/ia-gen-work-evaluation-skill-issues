# Spec: PostScript backend handles empty lines in multi-line text

## Objective

Saving a figure with the PostScript backend (`.eps`, and likely `.ps`) fails with `TypeError: cannot unpack non-iterable NoneType object` when a text artist contains an empty line, for example `'\nLower label'`. The goal is to let these figures save without error, matching the behavior of the PNG, PDF, SVG and Qt backends.

**Users:** Matplotlib users who export figures to PostScript/EPS with multi-line text (annotations, titles, possibly other `Text` artists) that contain an empty line.

**Regression context:** The issue reports this works in matplotlib ≤ 3.5.3 and fails in 3.6.0.

**Observed failure path (from the traceback):**
`Figure.savefig` → `backend_ps._print_ps` → `_print_figure` → `Figure.draw` → `Axes.draw` → `Annotation.draw` → `Text.draw` (text.py:736, called per line with `clean_line`) → `RendererPS.draw_text` (backend_ps.py:673, `for ps_name, xs_names in stream:`) → `TypeError`.

**Reporter's hypothesis (not verified):** In `RendererPS.draw_text`, the code that builds `stream` appends the "current stream" without checking whether it is set. When the line string is empty, no glyph is processed, so the current stream stays `None` and a `None` entry reaches the unpacking loop. The reporter says that adding `if curr_stream:` before line 669 of `backend_ps.py` appears to fix it.

### Acceptance criteria / user stories

- As a user, I can save a figure whose annotation text is `'\nLower label'` as `figure.eps` without an exception.
- As a user, I can save a figure whose title is `'\nLower title'` as EPS without an exception.
- The rendered output still shows the non-empty lines in the same positions as before the regression, and the empty line still takes up vertical space.
- Text without empty lines renders exactly as it does today, with no regression in PS output.

## Assumptions

1. The root cause is in `RendererPS.draw_text` in `matplotlib/backends/backend_ps.py`, which receives an empty string for the empty line. This is based on the traceback and the reporter's hint, and has not been confirmed against the source.
2. The bug affects the default (non-usetex, non-mathtext) text path, i.e. the font-subsetting/glyph-stream path. The usetex and mathtext paths are assumed to be unaffected or out of scope unless investigation shows otherwise.
3. Both `.eps` and `.ps` outputs go through the same `draw_text` code, so both are affected.
4. Any text with an empty line triggers the failure, whether it is a leading empty line, a trailing one, a middle one, or an entirely empty string. Only the leading-empty-line case is confirmed by the issue.
5. The fix should be minimal and local to the PS backend. No change to `Text.draw` line-splitting behavior is intended.
6. The project uses pytest and has an existing test module for the PS backend. This is assumed, not seen; the exact path is unknown.
7. The fix targets the current development branch, with a possible backport to the 3.6.x maintenance line.

## Tech Stack

- Python (the issue reports 3.9.13; the supported range is unknown)
- Matplotlib: the bug is reported in 3.6.0, and 3.5.3 is the last known good version
- Affected component: PostScript backend (`backend_ps.py`)
- Other dependencies and versions: unknown

## Commands

All commands are unknown because the repository is not visible.

```
Build:   UNKNOWN
Test:    UNKNOWN (likely a pytest invocation targeting the PS backend tests)
Lint:    UNKNOWN
Dev:     N/A
```

Reproduction script (from the issue):

```python
from matplotlib.figure import Figure

figure = Figure()
ax = figure.add_subplot(111)
# ax.set_title('\nLower title')  # this would cause an error as well
ax.annotate(text='\nLower label', xy=(0, 0))
figure.savefig('figure.eps')
```

## Project Structure

Only what the traceback reveals:

```
matplotlib/backends/backend_ps.py  → PostScript backend; RendererPS.draw_text (failure site, ~line 669–673 in 3.6.0)
matplotlib/text.py                 → Text.draw splits text into lines and calls renderer.draw_text per line (~line 736)
matplotlib/figure.py               → Figure.savefig entry point
matplotlib/backend_bases.py        → print_figure dispatch
```

- Location of the PS backend tests: UNKNOWN
- Location of the changelog / release notes for bug fixes: UNKNOWN

## Code Style

UNKNOWN. Follow the existing conventions in `backend_ps.py`. Keep the change minimal, guard against the empty/`None` stream case at the point where it arises, and add no new public API.

## Testing Strategy

- **Framework:** assumed pytest (unverified).
- **Regression test(s):** add tests to the existing PS backend test module (path unknown) that save to an in-memory buffer or a temporary file in PS/EPS format:
  - an annotation whose text has a leading empty line (`'\nLower label'`)
  - a title with a leading empty line (`'\nLower title'`)
  - optionally, a middle empty line (`'A\n\nB'`), a trailing empty line (`'A\n'`), and an empty string (`''`)
- **Pass condition:** `savefig` completes without raising, for both `format='ps'` and `format='eps'`.
- **Non-regression:** the existing PS backend tests, including any image-comparison tests, still pass.
- **Optional:** check that the output contains the non-empty line's glyphs, so we know nothing was silently dropped.
- **Coverage expectation:** UNKNOWN. At minimum, the new guard branch is exercised by a test.

## Boundaries

- **Always:**
  - Reproduce the failure with the issue's script before changing code.
  - Add a regression test that fails before the fix and passes after it.
  - Run the existing PS backend tests.
  - Keep the fix scoped to the PS backend.
- **Ask first:**
  - Changing `Text.draw` line-splitting, for example skipping empty lines before they reach renderers. This affects all backends.
  - Changing the usetex or mathtext code paths.
  - Modifying or regenerating baseline images.
  - Backporting to maintenance branches.
- **Never:**
  - Swallow exceptions broadly (for example, a blanket `try/except` around `draw_text`).
  - Change other backends' behavior.
  - Remove or skip failing tests to make the suite pass.
  - Change the public API.

## Success Criteria

1. The reproduction script from the issue runs without exception and produces `figure.eps`.
2. The same holds with `ax.set_title('\nLower title')`, and for `.ps` output.
3. The regression tests cover at least the leading-empty-line case. They fail on the pre-fix code and pass after the fix.
4. All existing PS backend tests pass unchanged.
5. The visual output for text without empty lines is unchanged.
6. For text with empty lines, the empty line still contributes vertical spacing, consistent with other backends such as PDF and SVG.

## Open Questions

1. Is the reporter's diagnosis correct, i.e. that the per-glyph stream builder in `draw_text` appends a `None` "current stream" when the line is empty? Or does an earlier code path return `None` for some other reason?
2. Should the guard go where the stream is built (skip appending a `None` or empty stream), or should `draw_text` return early when given an empty string? Which approach matches the backend's conventions?
3. Which change between 3.5.3 and 3.6.0 introduced this regression, for example a refactor of font subsetting or text streaming? Should that change be reviewed for related edge cases, such as strings made only of characters that produce no glyphs?
4. Are the usetex and mathtext PS paths affected by empty lines as well? Should they be covered by this fix or by tests?
5. Where do PS backend tests live, and is there a preferred pattern for "saves without error" tests (in-memory buffer vs. temp file)?
6. Is a changelog / release note entry required for bug fixes, and where does it go?
7. Should the fix be backported to 3.6.x?
8. Is the whitespace-only line case (e.g. `'  \nLabel'`) also relevant to verify?