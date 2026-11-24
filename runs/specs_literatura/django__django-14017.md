## Summary
Combining a `Q` object with an `Exists` expression using `&` fails depending on operand order. `Exists(...) & Q(...)` works, but `Q(...) & Exists(...)` raises a `TypeError`. The reporter expects `&` (and `|`) to be commutative for `Q`/`Exists` pairs.

## Steps to reproduce
1. Use any model; the report uses a model named `Product`.
2. In a Django shell (the report uses IPython), import `Q` and `Exists`.
3. Evaluate `Exists(Product.objects.all()) & Q()`. This succeeds.
4. Evaluate `Q() & Exists(Product.objects.all())`. This raises a `TypeError`.

## Observed behavior
- `Exists(Product.objects.all()) & Q()` returns a `Q` object:
  ```
  <Q: (AND: <django.db.models.expressions.Exists object at 0x7fc18dd0ed90>, (AND: ))>
  ```
- `Q() & Exists(Product.objects.all())` raises:
  ```
  TypeError: <django.db.models.expressions.Exists object at 0x7fc18dd21400>
  ```

## Expected behavior
`Q(...) & Exists(...)` should behave like `Exists(...) & Q(...)` and return a combined `Q` object rather than raise an error. The reporter states that the `&` and `|` operators should be commutative on `Q`/`Exists` pairs.

## Stack trace / error output
```
TypeError                                 Traceback (most recent call last)
<ipython-input-4-21d3dea0fcb9> in <module>
----> 1 Q() & Exists(Product.objects.all())

~/Code/venv/ecom/lib/python3.8/site-packages/django/db/models/query_utils.py in __and__(self, other)
     90
     91     def __and__(self, other):
---> 92         return self._combine(other, self.AND)
     93
     94     def __invert__(self):

~/Code/venv/ecom/lib/python3.8/site-packages/django/db/models/query_utils.py in _combine(self, other, conn)
     71     def _combine(self, other, conn):
     72         if not isinstance(other, Q):
---> 73             raise TypeError(other)
     74
     75         # If the other Q() is empty, ignore it and just use `self`.

TypeError: <django.db.models.expressions.Exists object at 0x7fc18dd21400>
```

## Test case
Minimal test case built from the report's example (`Product` is any model):
```python
from django.db.models import Exists, Q

# Works:
Exists(Product.objects.all()) & Q()

# Expected to work as well, but currently raises TypeError:
Q() & Exists(Product.objects.all())
```
The report states that `|` should also be commutative for these pairs. It does not show output for the `|` case.

## Code example
```python
In [3]: Exists(Product.objects.all()) & Q()
Out[3]: <Q: (AND: <django.db.models.expressions.Exists object at 0x7fc18dd0ed90>, (AND: ))>

In [4]: Q() & Exists(Product.objects.all())
# TypeError: <django.db.models.expressions.Exists object at 0x7fc18dd21400>
```

## Version and environment
- Python 3.8, inferred from the traceback path `~/Code/venv/ecom/lib/python3.8/site-packages/`.
- Run in an IPython shell.
- Django version: Not provided in the original report.