# Spec: Correct duplicate detection for multiline ORDER BY expressions in `SQLCompiler.get_order_by()`

## Objective

`SQLCompiler.get_order_by()` drops ORDER BY terms that are not duplicates when they are written as multiline SQL, for example `RawSQL` expressions with embedded newlines.

**Root cause (as reported):** the method strips the ordering direction to get a deduplication key:

```python
without_ordering = self.ordering_parts.search(sql).group(1)
```

The `ordering_parts` regular expression does not match across newlines. For multiline `sql` it captures only the last line, the one before `ASC`/`DESC`. That fragment goes into a `seen` set. Any later ORDER BY term whose **last line** is identical is then treated as a duplicate and removed, even when the full expressions differ.

**Who is affected:** ORM users who pass multiline expressions to `order_by()`, mainly `RawSQL(...)` with `.asc()` or `.desc()`.

**What success looks like:**
- Duplicate detection compares the **entire** SQL of each ordering term, minus its direction.
- Distinct multiline expressions are never collapsed.
- True duplicates are still removed, as today.

### User story
As a developer ordering a queryset by several multiline `RawSQL` expressions that share a final line, I want every expression to appear in the generated ORDER BY clause. Then I don't need workarounds like adding trailing spaces to make the last lines differ.

### Reproduction (from the issue)

```python
MyModel.objects.all().order_by(
    RawSQL('''
        case when status in ('accepted', 'verification')
             then 2 else 1 end''', []).desc(),
    RawSQL('''
        case when status in ('accepted', 'verification')
             then (accepted_datetime, preferred_datetime)
             else null end''', []).asc(),
    RawSQL('''
        case when status not in ('accepted', 'verification')
             then (accepted_datetime, preferred_datetime, created_at)
             else null end''', []).desc())
```

The reported `ordering_parts.search(...).group(1)` results are:
- `'                 then 2 else 1 end)'`
- `'                 else null end'`
- `'                 else null end'`

**Observed:** the third ordering term (the second expression ending in `else null end`) is dropped from the query.

**Expected:** all three ordering terms appear in the ORDER BY clause, in order, with their directions.

## Assumptions

1. The project is Django. `SQLCompiler`, `get_order_by()`, `ordering_parts` and `RawSQL` refer to Django ORM internals and the public `RawSQL` expression.
2. `ordering_parts` is a compiled regex used only to split off the trailing `ASC`/`DESC`. The problem is that it does not match across line boundaries.
3. Dedup semantics stay as they are: two ordering terms with the same SQL text, ignoring direction, are still duplicates and the later one is dropped. Only the key computation changes.
4. Newlines may be `\n`, `\r\n` or `\r`. The issue warns about "EOL dragons (`\r`)". All of them must be handled.
5. The reporter's suggested fix (`' '.join(sql.split('\n'))`) is a workaround, not a required design. Any approach that keeps the full expression in the key is acceptable.
6. The fix should not change the SQL emitted to the database. Only the internal dedup key is affected. Newlines inside literals must not be rewritten in the executed SQL.
7. Python 2 / `u''` concerns in the issue are historical. Whether Python 2 is still supported is unknown (see Open Questions).
8. The same `ordering_parts` pattern may be used elsewhere in the compiler, for example in code that builds extra select columns for ORDER BY with DISTINCT or GROUP BY. If so, it has the same defect. That code is unconfirmed because the repository is not visible.

## Tech Stack

- Python and Django ORM. Supported Python and Django versions: **unknown**.
- Database backends: multiple, through the Django backend abstraction. The issue doesn't say which backend the reporter uses. The example uses row-value expressions like `(a, b)`, which suggests PostgreSQL, but that's unconfirmed.

## Commands

All unknown; none are visible in the issue.

```
Build: unknown
Test:  unknown (Django's own test runner invocation not visible in the issue)
Lint:  unknown
Dev:   n/a
```

## Project Structure

- `SQLCompiler` / `get_order_by()` / `ordering_parts`: their file path is **unknown** (not given in the issue).
- Location of ORM ordering / raw SQL expression tests: **unknown**.
- New regression tests should go in the existing test module that covers queryset ordering or `RawSQL` expressions, wherever that is.

## Code Style

- Follow the existing conventions of the surrounding compiler code. They are not visible here, so they're unknown.
- Keep the change minimal and local to how the dedup key (`without_ordering`) is derived.
- Do not introduce new public API.

## Testing Strategy

- **Framework:** the project's existing test framework (unknown; presumably Django's own test suite).
- **Level:** ORM-level regression tests that build querysets and assert on their ordering, through the compiled SQL and/or result order. No new end-to-end tests.
- **Required regression cases:**
  1. Several multiline `RawSQL` ordering expressions that share an identical last line but differ elsewhere. All of them must be in the ORDER BY clause.
  2. The same as case 1 with `\r\n` line endings.
  3. The same as case 1 with bare `\r` line endings.
  4. Two truly identical multiline `RawSQL` expressions with different directions. The existing dedup behavior is preserved: the second one is still dropped.
  5. Existing single-line ordering and dedup behavior is unchanged. Covered by the current test suite passing.
- **Coverage expectation:** every changed line in the key computation is exercised by the tests above.
- If assumption 8 holds, add an equivalent multiline test for each other use of `ordering_parts`.

## Boundaries

**Always:**
- Run the full existing ordering / expressions test suites before considering the fix done.
- Add a regression test that fails before the fix and passes after it.
- Keep the SQL sent to the database byte-identical to the current output, apart from restoring the terms that were wrongly dropped.

**Ask first:**
- Changing dedup semantics themselves, such as normalizing whitespace so that expressions differing only in formatting count as duplicates.
- Changing the `ordering_parts` regex in ways that affect other call sites.
- Changing how `RawSQL` or other expressions render their SQL.
- Backporting to maintained release branches.

**Never:**
- Remove or weaken existing ordering or dedup tests.
- Rewrite user-supplied raw SQL in the executed query, for example by stripping newlines from it.
- Fix only `\n` while leaving `\r` / `\r\n` broken.

## Success Criteria

- [ ] The reproduction query from the issue produces an ORDER BY clause with all three terms, in the original order and with their original directions.
- [ ] Two multiline ordering expressions that differ anywhere, not just in the last line, are both kept.
- [ ] Two ordering expressions whose full SQL is identical, ignoring direction, are still deduplicated as before.
- [ ] The behavior holds for `\n`, `\r\n` and `\r` line endings.
- [ ] The generated SQL for single-line ordering expressions is unchanged.
- [ ] The new regression tests fail on the current code and pass with the fix.
- [ ] The existing test suite passes.

## Open Questions

1. **Normalization scope:** should the dedup key be the full SQL verbatim, or whitespace-normalized? Normalizing would make `RawSQL('a\n  desc_thing')` and `RawSQL('a desc_thing')` duplicates. That might be desirable, but it changes behavior.
2. **Other call sites:** is `ordering_parts` used anywhere besides `get_order_by()`, for example for DISTINCT or GROUP BY extra select columns? Should those be fixed under this issue?
3. **Preferred approach:** should the fix change the regex (for example, enabling dot-matches-newline) or pre-process `sql` before matching? Is there a project preference?
4. **Supported versions:** which Python and Django versions must the fix support? Is Python 2 `unicode` handling still relevant?
5. **Backports:** is this a candidate for backporting to stable branches, or only for the main development branch?
6. **Commands and paths:** what are the exact test commands, and what are the file locations of the compiler and the relevant test modules?
7. **Dedup for raw SQL at all:** is it acceptable to keep deduplicating `RawSQL` ordering terms? Or should raw expressions be excluded from dedup entirely, since their text-based equality is fragile?