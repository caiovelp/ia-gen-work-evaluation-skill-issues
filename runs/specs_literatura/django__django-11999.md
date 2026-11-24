## Summary

Since Django 2.2, a user-defined `get_FOO_display()` method on a model is ignored. Django's auto-generated `get_FOO_display()` is called instead. In Django 2.1, the user-defined override was used.

## Steps to reproduce

1. Define a model with a `CharField` that has `choices`. In the example the field is `foo_bar`.
2. On the same model, define your own `get_foo_bar_display()` method that returns a custom value, e.g. `"something"`.
3. Call `get_foo_bar_display()` on an instance of the model, for example from `__str__`.
4. Compare the result on Django 2.1 and Django 2.2+.

## Observed behavior

On Django 2.2+, `self.get_foo_bar_display()` returns the choice label (`'foo'` or `'bar'`), not the value from the overriding method.

## Expected behavior

The user-defined `get_foo_bar_display()` should override the generated one and return `"something"`, as it did in Django 2.1.

## Stack trace / error output

Not provided in the original report. No exception is raised; the wrong method is called.

## Test case

A minimal test derived from the example in the report:

```python
def test_get_FOO_display_can_be_overridden():
    instance = FooBar(foo_bar=1)
    # Django 2.1: "something"; Django 2.2+: "foo"
    assert instance.get_foo_bar_display() == "something"
    assert str(instance) == "something"
```

## Code example

From the original report:

```python
class FooBar(models.Model):
    foo_bar = models.CharField(_("foo"), choices=[(1, 'foo'), (2, 'bar')])

    def __str__(self):
        return self.get_foo_bar_display()  # This returns 'foo' or 'bar' in 2.2, but 'something' in 2.1

    def get_foo_bar_display(self):
        return "something"
```

## Version and environment

- Django 2.1: works as expected (the override is used).
- Django 2.2 and later: broken (the override is ignored).
- Python version, database and OS: Not provided in the original report.