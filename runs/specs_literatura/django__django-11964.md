## Summary

When a model instance is created with a `TextChoices` (or `IntegerChoices`) enum member as the value of a `CharField`/`IntegerField` that uses `choices=...choices`, the field attribute on that freshly created instance keeps the enum member itself, not its underlying value. As a result, `str()` on the attribute returns `'MyChoice.FIRST_CHOICE'` instead of `'first'`. An instance retrieved from the database returns the plain value (`'first'`). The type and string representation of the field value therefore differ depending on whether the instance was just created or loaded from the database.

## Steps to reproduce

1. Define a `TextChoices` enum and a model with a `CharField` that uses it:
   ```python
   from django.db import models
   from django.utils.translation import gettext_lazy as _

   class MyChoice(models.TextChoices):
       FIRST_CHOICE = "first", _("The first choice, it is")
       SECOND_CHOICE = "second", _("The second choice, it is")

   class MyObject(models.Model):
       my_str_value = models.CharField(max_length=10, choices=MyChoice.choices)
   ```
2. Create an instance by passing the enum member: `MyObject.objects.create(my_str_value=MyChoice.FIRST_CHOICE)`.
3. Call `str()` on `my_str_value` of the returned (freshly created) instance.
4. Retrieve the same object from the database (e.g. `MyObject.objects.last()`) and call `str()` on its `my_str_value`.
5. Compare the two results.

## Observed behavior

- On the freshly created instance, `str(my_object.my_str_value)` returns `'MyChoice.FIRST_CHOICE'`.
- On the instance retrieved from the database, `str(my_object.my_str_value)` returns `'first'`. The corresponding test passes.

According to the reporter, this inconsistency can cause unexpected issues. For example, when data is sent to an external API, a freshly created instance sends `MyEnum.MyValue`, while a retrieved instance sends `my_value`.

## Expected behavior

The field value should behave the same on a freshly created instance and on a retrieved instance. `str(my_object.my_str_value)` should return the enum's value (`'first'`) in both cases.

## Stack trace / error output

```
(django30-venv) ➜ django30 ./manage.py test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
F.
======================================================================
FAIL: test_created_object_is_str (testing.tests.EnumTest)
----------------------------------------------------------------------
Traceback (most recent call last):
 File "/Users/mikailkocak/Development/django30/testing/tests.py", line 14, in test_created_object_is_str
	self.assertEqual(str(my_object.my_str_value), "first")
AssertionError: 'MyChoice.FIRST_CHOICE' != 'first'
- MyChoice.FIRST_CHOICE
+ first
----------------------------------------------------------------------
Ran 2 tests in 0.002s
FAILED (failures=1)
```

## Test case

```python
from django.test import TestCase
from testing.pkg.models import MyObject, MyChoice

class EnumTest(TestCase):
    def setUp(self) -> None:
        self.my_object = MyObject.objects.create(my_str_value=MyChoice.FIRST_CHOICE)

    def test_created_object_is_str(self):
        my_object = self.my_object
        self.assertIsInstance(my_object.my_str_value, str)
        self.assertEqual(str(my_object.my_str_value), "first")   # fails

    def test_retrieved_object_is_str(self):
        my_object = MyObject.objects.last()
        self.assertIsInstance(my_object.my_str_value, str)
        self.assertEqual(str(my_object.my_str_value), "first")   # passes
```

## Code example

Model used in the reproduction:

```python
from django.db import models
from django.utils.translation import gettext_lazy as _

class MyChoice(models.TextChoices):
    FIRST_CHOICE = "first", _("The first choice, it is")
    SECOND_CHOICE = "second", _("The second choice, it is")

class MyObject(models.Model):
    my_str_value = models.CharField(max_length=10, choices=MyChoice.choices)
```

The report states that the same issue applies to `IntegerField` with `IntegerChoices`. No separate example was given for that case.

## Version and environment

- Django version: not stated explicitly. The tests were run in a virtualenv named `django30-venv`, in a project directory named `django30`.
- Python version, OS, and database backend: Not provided in the original report.