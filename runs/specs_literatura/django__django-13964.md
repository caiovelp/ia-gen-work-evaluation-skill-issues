## Summary

When a `ForeignKey` points to a model whose primary key is a non-auto `CharField`, the parent object stores the wrong foreign key value in this case:

1. An unsaved related instance with no primary key is assigned to the parent.
2. The related instance's primary key is set afterwards.

Saving the parent then stores an empty string (`""`) as `product_id` instead of the related object's primary key. This causes data loss. Inside a transaction, the error only appears at commit time, as a `ForeignKeyViolation`. If the primary key is set before assignment, the value is stored correctly.

The reporter suspects the cause is how `Order.product_id` is handled at assignment time, combined with how primary keys are fetched from the related instance for auto vs. non-auto primary keys.

## Steps to reproduce

1. Define the following models:
   ```python
   class Product(models.Model):
       sku = models.CharField(primary_key=True, max_length=50)

   class Order(models.Model):
       product = models.ForeignKey(Product, on_delete=models.CASCADE)
   ```
2. Inside `transaction.atomic()`, create an `Order` instance.
3. Assign an empty, unsaved `Product()` with no `sku` to `order.product`.
4. Set `order.product.sku = "foo"`.
5. Save `order.product`, then save `order`.
6. Query for `Order` objects by `product_id` and by `product`.
7. Let the transaction commit.

## Observed behavior

- `order.product_id` is saved as an empty string (`""`) instead of `"foo"`.
- `Order.objects.filter(product_id="").exists()` returns `True`.
- `Order.objects.filter(product=order.product).exists()` returns `False`.
- The foreign key constraint is deferred, so no error occurs inside the transaction. On commit, the transaction fails with a `ForeignKeyViolation` because no `Product` with primary key `""` exists.

For comparison, if the `Product` is created with its primary key before assignment (`order.product = Product(sku="foo")`), the order is saved correctly, the lookup by `product=order.product` succeeds, and the commit succeeds.

## Expected behavior

`order.product_id` should be populated with `order.product.sku` (`"foo"`) when `order` is saved, even if the primary key was set after the related instance was assigned.

- `Order.objects.filter(product=order.product).exists()` should return `True`.
- `Order.objects.filter(product_id="").exists()` should return `False`.
- The transaction should commit without a `ForeignKeyViolation`.

## Stack trace / error output

No stack trace was provided. The report states only that the transaction fails on commit with a `ForeignKeyViolation`, because no product with an empty-string primary key exists.

## Test case

Minimal test derived from the reproduction in the report, using the `Product` and `Order` models above:

```python
from django.db import transaction

def test_fk_to_charfield_pk_set_after_assignment():
    with transaction.atomic():
        order = Order()
        order.product = Product()
        order.product.sku = "foo"
        order.product.save()
        order.save()
        assert not Order.objects.filter(product_id="").exists()  # currently fails (row with product_id="" exists)
        assert Order.objects.filter(product=order.product).exists()  # currently fails
```

Working variant for comparison, where the primary key is set before assignment:

```python
def test_fk_to_charfield_pk_set_before_assignment():
    with transaction.atomic():
        order = Order()
        order.product = Product(sku="foo")
        order.product.save()
        order.save()
        assert Order.objects.filter(product=order.product).exists()  # succeeds
```

## Code example

Failing case:

```python
with transaction.atomic():
    order = Order()
    order.product = Product()
    order.product.sku = "foo"
    order.product.save()
    order.save()
    assert Order.objects.filter(product_id="").exists()  # Succeeds, but shouldn't
    assert Order.objects.filter(product=order.product).exists()  # Fails
```

Working case:

```python
with transaction.atomic():
    order = Order()
    order.product = Product(sku="foo")
    order.product.save()
    order.save()
    assert Order.objects.filter(product=order.product).exists()  # succeeds
```

## Version and environment

Not provided in the original report. The report mentions only that the foreign key constraint is deferred until commit and that the database raises a `ForeignKeyViolation`. Django version, database backend and Python version are not stated.