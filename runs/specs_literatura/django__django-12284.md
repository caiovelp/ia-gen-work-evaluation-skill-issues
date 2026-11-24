## Summary

`Model.get_FOO_display()` returns the wrong value when a child model overrides a field with choices inherited from an abstract base model and adds new choices. For choices that exist in both the base and the child, the method returns the correct display label. For choices added only in the child, it returns the raw stored value instead of the label.

## Steps to reproduce

1. Define an abstract base model `A` with a `CharField` `field_foo` whose choices are `[("A", "output1"), ("B", "output2")]`.
2. Define a concrete model `B` that inherits from `A`. It overrides `field_foo` with a `CharField` whose choices are `[("A", "output1"), ("B", "output2"), ("C", "output3")]`.
3. Create an instance of `B` with `field_foo = "A"` and call `get_field_foo_display()`. Repeat with `"B"`.
4. Create an instance of `B` with `field_foo = "C"` and call `get_field_foo_display()`.

Note: the prose of the original report says the base has 3 choices and the child adds 2 more. The example code shows 2 base choices and 1 added choice. The steps above follow the example code.

## Observed behavior

- For `field_foo = "A"`, `get_field_foo_display()` returns `"output1"` (correct).
- For `field_foo = "B"`, `get_field_foo_display()` returns `"output2"` (correct).
- For `field_foo = "C"`, `get_field_foo_display()` returns `"C"` instead of the display label.

## Expected behavior

For `field_foo = "C"`, `get_field_foo_display()` on an instance of `B` should return `"output3"`, the label defined in the child model's overridden choices.

## Stack trace / error output

Not provided in the original report. No exception is raised; the method returns an incorrect value.

## Test case

Minimal test case derived from the report's example (models as defined in the Code example section):

```python
# Using models A (abstract) and B from the code example below
b = B(field_foo="A")
assert b.get_field_foo_display() == "output1"  # passes

b = B(field_foo="B")
assert b.get_field_foo_display() == "output2"  # passes

b = B(field_foo="C")
assert b.get_field_foo_display() == "output3"  # fails: returns "C"
```

## Code example

```python
class A(models.Model):
    foo_choice = [("A", "output1"), ("B", "output2")]
    field_foo = models.CharField(max_length=254, choices=foo_choice)

    class Meta:
        abstract = True


class B(A):
    foo_choice = [("A", "output1"), ("B", "output2"), ("C", "output3")]
    field_foo = models.CharField(max_length=254, choices=foo_choice)
```

## Version and environment

Not provided in the original report.