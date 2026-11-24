## Summary

Fields inherited from an abstract model compare as equal across different concrete models. For example, the `myfield` field on two models that both inherit from the same abstract base is considered equal. As a result, putting the fields from both models into a `set` silently drops one of them.

The report states that field equality is based only on `self.creation_counter`. The reporter found this surprising. Participants in an IRC django-dev discussion agreed that the behavior is not intuitive.

## Steps to reproduce

1. Define an abstract model with a field, and two concrete models that inherit from it:
   ```python
   class A(models.Model):
       class Meta:
           abstract = True
       myfield = IntegerField()

   class B(A):
       pass

   class C(A):
       pass
   ```
2. Compare the inherited field from each concrete model:
   ```python
   B._meta.get_field('myfield') == C._meta.get_field('myfield')
   ```
3. Put both fields into a set and check its size:
   ```python
   len({B._meta.get_field('myfield'), C._meta.get_field('myfield')})
   ```

## Observed behavior

- `B._meta.get_field('myfield') == C._meta.get_field('myfield')` evaluates to `True`.
- `len({B._meta.get_field('myfield'), C._meta.get_field('myfield')})` evaluates to `1`, so one field is de-duplicated away.

According to the report, this happens because fields consider only `self.creation_counter` when comparing for equality.

The reporter notes that using a list instead of a set worked as a workaround.

## Expected behavior

Fields that belong to different models should not compare as equal, even if they were inherited from the same abstract model:

- `B._meta.get_field('myfield') == C._meta.get_field('myfield')` should be `False`.
- A set containing both fields should have a length of `2`.

## Stack trace / error output

Not provided in the original report. No exception is raised; the problem is an incorrect equality result.

## Test case

Minimal test derived from the snippet in the report:

```python
class A(models.Model):
    class Meta:
        abstract = True
    myfield = IntegerField()

class B(A):
    pass

class C(A):
    pass

# Expected to pass; currently fails
assert B._meta.get_field('myfield') != C._meta.get_field('myfield')
assert len({B._meta.get_field('myfield'), C._meta.get_field('myfield')}) == 2
```

## Code example

```python
class A(models.Model):
    class Meta:
        abstract = True
    myfield = IntegerField()

class B(A):
    pass

class C(A):
    pass

len({B._meta.get_field('myfield'), C._meta.get_field('myfield')}) == 1   # True
B._meta.get_field('myfield') == C._meta.get_field('myfield')             # True
```

## Version and environment

Not provided in the original report.