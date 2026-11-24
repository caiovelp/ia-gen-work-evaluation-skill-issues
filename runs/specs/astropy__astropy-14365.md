# Spec: Case-Insensitive QDP Command Parsing in `ascii.qdp`

## Objective

The `ascii.qdp` reader in astropy only recognizes QDP commands written in upper case, such as `READ SERR 1 2`. QDP itself is case-insensitive, and many QDP files are written by hand in lower or mixed case. Such files are valid for the `qdp` tool, but astropy fails to read them:

```
ValueError: Unrecognized QDP line: read serr 1 2
```

**Goal:** `Table.read(..., format='ascii.qdp')` recognizes QDP commands in any letter case and produces the same `Table` it would produce for the upper-case equivalent.

**Users:** Astronomers and astropy users reading QDP files that were hand-written or produced by tools that don't use upper case.

**User story:** As a user with a QDP file containing `read serr 1 2`, I want `Table.read('test.qdp', format='ascii.qdp')` to return a table with symmetric error columns for columns 1 and 2. I don't want a `ValueError`.

**Reference case from the issue:**

```
read serr 1 2
1 0.5 1 0.5
```

- Expected: a `Table` with error columns. This file has one row with a value plus symmetric error for column 1 and the same for column 2.
- Actual (astropy 5.1): `ValueError: Unrecognized QDP line: read serr 1 2`.
- Running `qdp test.qdp` on the same file works.

## Assumptions

1. The fix covers **command lines** that the reader currently recognizes in upper case. Per the issue, this includes at least `READ SERR`, and presumably `READ TERR` too. It does not add support for new QDP commands.
2. "Case-insensitive" covers all lower-case input (`read serr`) and mixed-case input (`Read Serr`, `READ serr`), not only all-lower-case input.
3. Upper-case input must keep working exactly as it does today, so existing behavior is not affected.
4. The `ascii.qdp` **writer** keeps emitting upper-case commands. This change affects only the reader.
5. Column indices and numeric data lines are already case-neutral and need no change. Mantissa/exponent forms such as `1e3` vs `1E3` may be an exception; see Open Questions.
6. The trailing whitespace in the issue's example (`read serr 1 2 `) must also be tolerated. This is assumed to be handled already for upper-case lines, but it must be verified for lower case.
7. The fix should be made in the `astropy.io.ascii.qdp` module, which is named in the warning output in the issue. The exact file path and the function or regex that classifies lines are not visible in the issue and are **unknown**.
8. The issue was reported against astropy 5.1. The fix targets the current development branch.

## Tech Stack

- Python. The issue reports 3.10.9; the project's supported range is unknown.
- astropy (`astropy.io.ascii`, `astropy.table.Table`). The issue reports 5.1.
- NumPy. The issue reports 1.24.1.
- Other dependency versions for the dev branch: **unknown**.

## Commands

The project's build, test and lint commands are not visible in the issue and are **unknown**. To be confirmed from the repository's contributor docs or CI config:

```
Build:   unknown
Test:    unknown (likely a pytest invocation scoped to the io.ascii QDP tests — unconfirmed)
Lint:    unknown
```

Reproduction, taken from the issue:

```
cat > test.qdp <<'EOF'
read serr 1 2
1 0.5 1 0.5
EOF
python -c "from astropy.table import Table; print(Table.read('test.qdp', format='ascii.qdp'))"
```

## Project Structure

Not visible in the issue; **unknown**. Known only:

- The reader lives in the `astropy.io.ascii.qdp` module.
- The error originates from a line-classification step that raises `ValueError(f'Unrecognized QDP line: {line}')`.
- The location of the existing QDP tests: **unknown**.

## Code Style

Unknown from the issue. Follow the existing conventions in `astropy.io.ascii.qdp` and astropy's contributor guidelines, which have not been seen. No snippet is provided here, so as not to invent code.

## Testing Strategy

- **Framework:** assumed to be pytest, as used by astropy (unconfirmed).
- **Location:** alongside the existing `ascii.qdp` tests (path unknown).

**Unit tests (reader):**
- The issue's exact file (`read serr 1 2` plus one data row) reads successfully and produces the expected columns and values.
- Mixed-case variants (`Read Serr 1 2`, `READ serr 1 2`) produce a table identical to the upper-case version.
- `read terr ...` in lower case behaves identically to `READ TERR ...`.
- Upper-case input still produces identical results (regression).

**Round-trip test:**
- Write a table with errors using the writer, convert the command lines to lower case, read it back, and check equality with the original.

**Negative test:**
- Genuinely unrecognized lines still raise `ValueError: Unrecognized QDP line: ...`. Case-insensitivity must not make the parser accept garbage.

**Coverage:** every command form the reader recognizes is tested in at least one non-upper-case variant.

## Boundaries

**Always:**
- Keep upper-case parsing behavior unchanged.
- Add regression tests for the lower-case case from the issue.
- Run the existing `io.ascii` test suite before committing.
- Add a changelog entry if the project requires one (format unknown).

**Ask first:**
- Changing writer output case.
- Extending case-insensitivity to non-command tokens such as `NO` missing-value markers or `NaN`.
- Changing the public reader API or adding new options, such as a strict-case flag.

**Never:**
- Silently accept lines that QDP itself would reject.
- Remove or weaken existing tests.
- Change the error message text for genuinely unrecognized lines without approval.

## Success Criteria

1. `Table.read('test.qdp', format='ascii.qdp')` on the issue's file returns a `Table` without raising. The table has a data column and a symmetric-error column for each of columns 1 and 2, with values `1`, `0.5`, `1`, `0.5`. The exact column names follow existing reader conventions.
2. For every command the reader supports (at minimum `READ SERR` and `READ TERR`), lower-case and mixed-case forms produce a `Table` identical to the upper-case form.
3. All existing `ascii.qdp` tests pass unchanged.
4. Lines that are not valid QDP commands or data still raise `ValueError: Unrecognized QDP line: ...`.
5. Writer output is byte-for-byte unchanged.

## Open Questions

1. Which commands does the reader currently recognize besides `READ SERR` and `READ TERR`? All of them should become case-insensitive. Please confirm the full list.
2. Should the `NO` missing-value marker also be accepted as `no` or `No`? Is that how QDP itself behaves?
3. Should other case-sensitive tokens be accepted in any case, such as `NaN`/`nan` and exponent markers (`e` vs `E`), or is this out of scope?
4. Should the writer continue emitting upper-case commands? (Assumed yes.)
5. Which version or branch should receive the fix, and should it be backported to a 5.x maintenance release?
6. What are the exact test, lint and changelog commands and locations for this repository?
7. Are there other QDP behaviors that differ from the `qdp` tool and should be tracked separately rather than handled here, for example command abbreviations like `rea ser`?