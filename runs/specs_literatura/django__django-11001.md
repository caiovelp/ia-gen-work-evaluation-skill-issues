## Summary

`SQLCompiler.get_order_by()` drops an `order_by()` expression when several multiline `RawSQL` expressions share the same last line. To detect duplicate ordering clauses, the compiler runs the `self.ordering_parts` regular expression over the compiled SQL:

```python
without_ordering = self.ordering_parts.search(sql).group(1)
```

When `sql` spans multiple lines, the regex returns only the last line, the one containing `ASC`/`DESC`. That line is added to the `seen` set. Any later ordering expression whose last line is identical is then treated as a duplicate and removed, even though the full SQL expressions are different.

## Steps to reproduce

1. Define a model (`MyModel`) with the fields `status`, `accepted_datetime`, `preferred_datetime` and `created_at`.
2. Build a queryset ordered by three multiline `RawSQL` expressions, where the second and third expressions end with the same line (`else null end`):
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
3. Compile or execute the query and inspect the generated `ORDER BY` clause.

## Observed behavior

`self.ordering_parts.search(sql).group(1)` returns only the last line of each expression:

```
'				 then 2 else 1 end)'
'				 else null end'
'				 else null end'
```

The second and third expressions produce the same string, so they are treated as duplicates. Only one of them makes it into the `ORDER BY` clause, so one ordering clause is silently dropped. The reporter describes the second `RawSQL` (the one ending in `else null end`) as the one removed from the query.

The problem goes away if a space or any other character is added to the last line of one of the expressions, so that the last lines differ. Because of this, duplicate detection in the `ORDER BY` clause only works correctly in special cases. It compares only the last line of the SQL, not the whole expression.

## Expected behavior

All three ordering expressions appear in the generated `ORDER BY` clause. Ordering expressions should be treated as duplicates only when the whole expression is the same, not when they just share the same last line.

## Stack trace / error output

Not provided in the original report. No error is raised; the ordering clause is silently omitted.

## Test case

This minimal test case is derived from the reproduction snippet in the report:

```python
qs = MyModel.objects.all().order_by(
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

Assert that the compiled `ORDER BY` clause of `qs` contains all three `RawSQL` expressions: one `DESC`, one `ASC`, and one `DESC`. With the current behavior, one of the two expressions ending in `else null end` is missing.

## Code example

The relevant line in `SQLCompiler.get_order_by()`, as cited in the report:

```python
without_ordering = self.ordering_parts.search(sql).group(1)
```

Here `sql` contains multiline SQL. The `without_ordering` value, which is only the last line, is the value added to the `seen` set.

## Version and environment

Not provided in the original report. No Django, Python or database versions are given. The reporter notes that Py2.x unicode strings and `\r` line endings may also be relevant to this code path.