## Summary

With `serialized_rollback = True` on a `TransactionTestCase`, restoring the serialized database contents can fail with integrity errors. `deserialize_db_from_string` saves objects one by one without wrapping them in a transaction. `serialize_db_to_string` does not guarantee that models referenced by foreign keys are serialized before the models that point to them. As a result, an instance with a foreign key can be saved before the instance it references.

## Steps to reproduce

The reporter hit this in a complex project and did not write a minimal reproduction. Based on their description of the code path:

1. Use a project where one model has a foreign key to another model, and the app registry orders them so the model holding the foreign key is serialized first. The reporter notes this order is deterministic because the app registry stores apps and models in an `OrderedDict`.
2. Create a `TransactionTestCase` subclass with `serialized_rollback = True`.
3. Run the tests. For each database:
   - `BaseDatabaseCreation.create_test_db` effectively runs `connection._test_serialized_contents = connection.creation.serialize_db_to_string()`.
   - `TransactionTestCase._fixture_setup` effectively runs `connection.creation.deserialize_db_from_string(connection._test_serialized_contents)`.
4. During deserialization, an object holding a foreign key may be saved before the object it references.

## Observed behavior

- `serialize_db_to_string` orders models with `serializers.sort_dependencies`, which only handles natural keys. It does not place models referenced by foreign keys before models that contain those foreign keys. The reporter notes this is not possible in general because circular foreign keys are allowed.
- `deserialize_db_from_string` deserializes and saves each object without a surrounding transaction.
- Integrity errors can occur when an instance with a foreign key is saved before the instance it references, so the objects are not restored.

## Expected behavior

Rollback emulation should restore all serialized objects without integrity errors, whatever order the models were serialized in. The reporter contrasts this with the `loaddata` management command, which does not have this problem because it loads all fixtures inside a single transaction.

## Stack trace / error output

Not provided in the original report. The reporter only mentions "integrity errors".

## Test case

Not provided in the original report. The reporter believes a deterministic test is possible, because `serialize_db_to_string` serializes models in the app registry's deterministic (`OrderedDict`) order.

## Code example

Current body of `BaseDatabaseCreation.deserialize_db_from_string` in `django/db/backends/base/creation.py`, as quoted in the report:

```python
data = StringIO(data)
for obj in serializers.deserialize("json", data, using=self.connection.alias):
    obj.save()
```

For comparison, the `loaddata` command's `handle` method, as quoted in the report:

```python
def handle(self, *fixture_labels, **options):
    # ...
    with transaction.atomic(using=self.using):
        self.loaddata(fixture_labels)
    # ...
```

## Version and environment

Not provided in the original report. The quoted code imports from `django.utils.six`, but no Django, Python, or database versions are given.