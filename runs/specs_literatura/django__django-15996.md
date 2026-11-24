## Summary
Support serialization of combined Enum flags (e.g. `re.UNICODE | re.IGNORECASE`) in migrations.

## Description
Take a model field defined with a default that combines several Enum flags:

```python
regex_flags = models.IntegerField(default=re.UNICODE | re.IGNORECASE)
```

The generated migration contains:

```python
default=re.RegexFlag[None]
```

This happens because the `EnumSerializer` serializes an enum value using the `.name` of the item. A combination of flags does not match any single enum member, so the value has no name. The serializer then produces `re.RegexFlag[None]`, which is not a valid value.

## Product version
Not provided in the original request.

## Rationale
Migrations for fields whose defaults combine Enum flags are serialized incorrectly. The generated `re.RegexFlag[None]` does not represent the original value, so the default cannot be reproduced from the migration. To support these fields, the serializer must handle values that are combinations of multiple flag members.

## Use case or scenario
A developer defines an `IntegerField` whose default combines regex flags with a bitwise OR, such as `re.UNICODE | re.IGNORECASE`. When they generate migrations, they expect the migration to contain an expression that recreates the same combined flag value. They do not expect `re.RegexFlag[None]`.

## Possible solution
When the enum value has no single matching item (no `.name`), use `enum._decompose` to get the list of member names that make up the value. Then generate an expression that recreates the value by ORing those members together.