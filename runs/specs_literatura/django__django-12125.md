## Summary

When a `django.db.models.Field` subclass is defined as an inner (nested) class of another class and used in a model, `manage.py makemigrations` writes a migration that refers to the inner class as if it were a top-level class of its module. For example, it writes `test1.models.Inner` instead of `test1.models.Outer.Inner`. The same happens when an inner class, such as an enum nested in a model, is passed as a field argument.

## Steps to reproduce

1. In an app's `models.py` (the app is `test1` in the report), define a field subclass as an inner class and use it in a model:
   ```python
   class Outer(object):
       class Inner(models.CharField):
           pass

   class A(models.Model):
       field = Outer.Inner(max_length=20)
   ```
2. Run `manage.py makemigrations`.
3. Open the generated migration file and look at the field definition for `field`.

## Observed behavior

The generated migration refers to the inner class by a top-level path that does not include the outer class:

```python
migrations.CreateModel(
    name='A',
    fields=[
        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('field', test1.models.Inner(max_length=20)),
    ],
),
```

A real-life case uses `EnumField` from `django-enumfields` with an enum nested inside a model:

```python
import enum
from enumfields import Enum, EnumField

class Thing(models.Model):
    @enum.unique
    class State(Enum):
        on = 'on'
        off = 'off'
    state = EnumField(enum=State)
```

It produces:

```python
migrations.CreateModel(
    name='Thing',
    fields=[
        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('state', enumfields.fields.EnumField(enum=test1.models.State, max_length=10)),
    ],
),
```

## Expected behavior

The migration should reference inner classes by their full nested path:

- `test1.models.Outer.Inner(max_length=20)` instead of `test1.models.Inner(max_length=20)`
- `enum=test1.models.Thing.State` instead of `enum=test1.models.State`

## Stack trace / error output

Not provided in the original report.

## Test case

A minimal manual test case based on the report's reproduction:

1. Use the `Outer` / `Inner` / `A` models from "Steps to reproduce" in app `test1`.
2. Run `manage.py makemigrations`.
3. Check that the generated migration contains `test1.models.Outer.Inner(max_length=20)`.
   - **Currently fails:** the migration contains `test1.models.Inner(max_length=20)`.

The `Thing.State` example gives a second case. The migration should contain `enum=test1.models.Thing.State`, but it currently contains `enum=test1.models.State`.

## Code example

Inner field class:

```python
class Outer(object):
    class Inner(models.CharField):
        pass

class A(models.Model):
    field = Outer.Inner(max_length=20)
```

Inner enum class passed to a third-party field (`django-enumfields`):

```python
import enum
from enumfields import Enum, EnumField

class Thing(models.Model):
    @enum.unique
    class State(Enum):
        on = 'on'
        off = 'off'
    state = EnumField(enum=State)
```

## Version and environment

Not provided in the original report. The report only mentions that the real-life case uses the third-party package `django-enumfields` (version not given).