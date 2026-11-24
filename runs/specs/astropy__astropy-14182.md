# Spec: Support `header_rows` in the RestructuredText (`ascii.rst`) writer

## Assumptions

1. The `header_rows` keyword should behave the same way in `ascii.rst` as it already does in `ascii.fixed_width`. The issue shows `header_rows=["name", "unit"]` working there and producing one header line per requested attribute.
2. The `RST` writer is related to the fixed-width writer family, since both produce aligned, column-separated output. The exact class relationship is **unknown** because the source is not visible.
3. In the expected RST output, all header rows sit between the top `=` border line and the second `=` border line, in the order given. Example:
   ```
   ===== ========
    wave response
      nm       ct
   ===== ========
   350.0      0.7
   950.0      1.2
   ===== ========
   ```
4. Column widths are computed over all header rows and all data values. A unit string longer than the name or the data therefore widens the column, including its `=` borders.
5. Default behaviour without `header_rows` must stay byte-for-byte identical to current output. The implicit default is equivalent to `["name"]`.
6. The `ascii.rst` reader is in scope only for round-trip symmetry. This is to be confirmed (see Open Questions).
7. Unit strings are rendered the same way as in `ascii.fixed_width`. For example, `u.count` renders as `ct`.

## Objective

Users who generate documentation from astropy tables want RST "simple table" output that includes extra header lines, such as units. Today the following call fails:

```python
tbl.write(sys.stdout, format="ascii.rst", header_rows=["name", "unit"])
```

It raises `TypeError: RST.__init__() got an unexpected keyword argument 'header_rows'`. The equivalent `ascii.fixed_width` call works.

**User story:** As a user writing a `Table`/`QTable` to RST, I can pass `header_rows` so that the header shows column names and other attributes such as units. The result must be valid RST that renders correctly in docs.

**Acceptance criteria:**

- `tbl.write(..., format="ascii.rst", header_rows=["name", "unit"])` no longer raises. It produces output matching Assumption 3 for the issue's example table.
- `header_rows=["name"]` produces output identical to omitting `header_rows`.
- Omitting `header_rows` produces output identical to the current behaviour shown in the issue.
- Other header row attributes accepted by `ascii.fixed_width` (e.g. `dtype`, `format`, `description`, if supported there) are accepted with the same semantics.
- Border lines (`=`) are sized to the widest cell across all header rows and data.

## Tech Stack

- Python, astropy (`astropy.io.ascii`, `astropy.table`, `astropy.units`).
- Supported Python and astropy versions: **unknown**.

## Commands

All commands are **unknown** because the repository is not visible. Fill these in from the project's contributor docs:

- Build: unknown
- Test: unknown (likely pytest-based; exact invocation unknown)
- Lint: unknown

## Project Structure

Only these locations are known, from the traceback (installed paths under `astropy/`):

- `astropy/io/ascii/core.py`: `_get_writer`, which instantiates `Writer(**writer_kwargs)`
- `astropy/io/ascii/ui.py`: `write`, `get_writer`
- `astropy/io/ascii/connect.py`: `io_write`
- `astropy/table/connect.py`, `astropy/io/registry/core.py`: unified I/O dispatch

The following locations are **unknown**:

- The module defining the `RST` class.
- The module defining the fixed-width writer's `header_rows` handling.
- The location of the test files for `ascii.rst`.

## Code Style

Unknown. Follow the conventions of the existing `RST` and fixed-width writer code. Mirror the existing `header_rows` keyword name and semantics exactly; do not introduce a new parameter name.

## Testing Strategy

- **Framework:** the existing `astropy.io.ascii` test suite. The framework and location are **unknown** (presumably pytest).
- **Unit tests for the RST writer:**
  - The issue's example table with `header_rows=["name", "unit"]`, checked against the expected exact string.
  - No `header_rows`, checked as a regression test against current output.
  - `header_rows=["name"]`, checked to be identical to the default.
  - A unit or attribute string wider than the name and data, verifying that column and border widths expand.
  - At least one other attribute (e.g. `dtype`) if `fixed_width` supports it.
- **Round-trip test (if the reader is in scope):** write with `header_rows=["name", "unit"]` and read back with the same `header_rows`. Names and units should be preserved.
- **Optional:** confirm the produced text is valid RST, for example by parsing it with docutils if that is already a test dependency. Whether it is a dependency is unknown.

## Boundaries

- **Always:**
  - Keep default `ascii.rst` output unchanged.
  - Match the `ascii.fixed_width` `header_rows` semantics.
  - Add tests for every new behaviour.
- **Ask first:**
  - Changing the `RST` class hierarchy or the shared fixed-width base behaviour that other formats depend on.
  - Adding the feature to the reader.
  - Adding new dependencies, such as docutils for validation.
  - Changing the fast writer path.
- **Never:**
  - Change the output of other formats (`fixed_width`, `fixed_width_two_line`, etc.).
  - Remove or loosen existing tests.
  - Silently ignore an unsupported `header_rows` value.

## Success Criteria

- The issue's reproduction prints the table with the `wave`/`response` names line and the `nm`/`ct` units line between the first two `=` borders, followed by the data and the closing border. It does not raise `TypeError`.
- All existing `ascii.rst` and fixed-width tests pass unchanged.
- The new tests listed in the Testing Strategy pass.
- A changelog or what's-new entry is added, if that is the project convention (convention **unknown**).

## Open Questions

1. Is the exact layout in Assumption 3 correct? Specifically, should all header rows sit inside the top two `=` borders, with no separator between the name row and the unit row?
2. Should the `ascii.rst` **reader** also accept `header_rows`, so that a written table can be read back with units? Or is this a writer-only change?
3. What should happen with missing attributes, for example a column without a unit? Should the cell be blank, as presumably in `fixed_width`?
4. Should the feature also be documented in the `ascii.rst` format docs or examples, and where do those docs live?
5. How should header cell alignment be handled? The current output shows names right-aligned with a leading space (` wave`). Should unit rows follow the same alignment as names, or as data?
6. Are there other `fixed_width`-derived formats lacking `header_rows` that should be fixed at the same time, or is the scope strictly `ascii.rst`?
7. What are the project's test, build, and changelog commands and conventions?