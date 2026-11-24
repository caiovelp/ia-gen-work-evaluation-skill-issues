## Summary

On SQLite and Oracle, filtering a `JSONField` key transform with `__isnull=True` (the `KeyTransformIsNull` lookup) also matches objects where the key exists with a JSON `null` value. It should match only objects that do not have the key. MariaDB, MySQL and PostgreSQL behave correctly.

For `isnull=False`, `KeyTransformIsNull` uses the same logic as `HasKey`, which the reporter says is correct. Only the `isnull=True` case is affected.

## Steps to reproduce

1. Open `tests.model_fields.test_jsonfield.TestQuerying.test_isnull_key`.
2. Replace the first assertion, which uses `value__a__isnull=True`, with one that uses `value__j__isnull=True` (see **Test case** below).
3. Run the test against SQLite or Oracle.
4. For comparison, run it against MariaDB, MySQL or PostgreSQL.

## Observed behavior

On SQLite and Oracle, `NullableJSONModel.objects.filter(value__j__isnull=True)` returns objects that do not have the key `j`. It also returns objects that have the key `j` with the value JSON `null`.

The existing test does not catch this. It only checks `value__a`, and the value of `a` is never JSON `null` in the test data.

## Expected behavior

`value__<key>__isnull=True` should match only objects that do not have the key. Objects that have the key with the value JSON `null` should not be matched. This is how the query already behaves on MariaDB, MySQL and PostgreSQL.

## Stack trace / error output

Not provided in the original report.

## Test case

In `tests.model_fields.test_jsonfield.TestQuerying.test_isnull_key`, change the first assertion from:

```python
self.assertSequenceEqual(
    NullableJSONModel.objects.filter(value__a__isnull=True),
    self.objs[:3] + self.objs[5:],
)
```

to:

```python
self.assertSequenceEqual(
    NullableJSONModel.objects.filter(value__j__isnull=True),
    self.objs[:4] + self.objs[5:],
)
```

This assertion should pass on all backends. According to the report, it fails on SQLite and Oracle.

## Code example

```python
NullableJSONModel.objects.filter(value__j__isnull=True)
```

## Version and environment

- **Affected database backends:** SQLite, Oracle
- **Unaffected database backends:** MariaDB, MySQL, PostgreSQL
- **Component:** `JSONField` key transforms (`KeyTransformIsNull` lookup)
- **Django version:** Not provided in the original report.