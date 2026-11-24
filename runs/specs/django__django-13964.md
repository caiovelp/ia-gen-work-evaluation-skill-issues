# Spec: FK attribute not refreshed when a related object's non-numeric primary key is set after assignment

## Objective

**Problem.** A model can have a `ForeignKey` to a model whose primary key is a non-auto `CharField`. If you assign an unsaved, pk-less instance of the target model to that foreign key, then set its primary key, then save both objects, the referencing object is saved with an empty-string foreign key value (`product_id = ""`) instead of the related object's real primary key. On a backend with deferred FK constraints, the failure only shows up at transaction commit as a `ForeignKeyViolation`. Inside the transaction, queries return wrong results. The result is silent data corruption or a failed commit.

**Reproduction (from the issue):**

```python
class Product(models.Model):
    sku = models.CharField(primary_key=True, max_length=50)

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

with transaction.atomic():
    order = Order()
    order.product = Product()
    order.product.sku = "foo"
    order.product.save()
    order.save()
    assert Order.objects.filter(product_id="").exists()           # succeeds, but shouldn't
    assert Order.objects.filter(product=order.product).exists()   # fails
```

**Control case that already works:** if `Product(sku="foo")` is built with its pk before assignment, `order.save()` stores `product_id="foo"` and the commit succeeds.

**Desired behaviour.** When the referencing (child) object is saved, its foreign key attribute must hold the related object's current primary key. This must hold even if that pk was set after assignment and its type's "empty" value is not `None`, for example `""` for `CharField`. The behaviour must be the same as when the pk was supplied at construction.

**Users.** Django ORM users whose models have foreign keys to models with non-auto, non-integer primary keys (for example `CharField`).

**Terminology.** The issue calls `Order` the "parent" and `Product` the "child". This spec uses the ORM terms instead:
- **referencing model:** `Order`, which holds the FK.
- **related model:** `Product`, which is the FK target.

## Assumptions

1. The bug is in Django core, in the logic that runs at save time to sync a cached related object's pk into the local FK attname. It is not in backend-specific code. (This is unverified because I have no repo access.)
2. The root cause is likely this: the "FK value is unset" check treats only `None` as unset. A `CharField` pk on a fresh instance defaults to `""`, so `""` is copied into `product_id` at assignment time and is never refreshed. (This is a hypothesis taken from the issue's closing remark. It must be confirmed before implementation.)
3. When a related object is assigned, the existing behaviour of copying its current pk into the FK attname stays in place. The fix only concerns refreshing that value before save.
4. The existing guard must keep raising: saving a referencing object whose related object is unsaved or has no pk raises `ValueError` ("save() prohibited to prevent data loss due to unsaved related object…").
5. The fix should cover `ForeignKey` and `OneToOneField` alike. Both go through the same related-field save path.
6. The behaviour is the same for every database backend. Deferred constraints (PostgreSQL) only change *when* the bug becomes visible.
7. No public API, migration, or schema change is needed.
8. Explicitly setting the FK attname to an empty-string value on purpose is unusual. The fix may treat empty values as "not yet set" while a cached related object exists, as long as existing tests still pass.

## Tech Stack

- Python and the Django ORM (django/django). The exact branch and supported Python versions are **unknown**.
- Database backends: all supported backends. PostgreSQL (deferred FK constraints) is the backend where the reported symptom appears.

## Commands

The exact invocation is **unknown** because the repository is not visible. Django's test runner script and the test-settings layout must be confirmed from the repository.
- Build: N/A (pure Python).
- Test: **unknown**. It should run the targeted test module(s), and the full suite on at least SQLite and PostgreSQL.
- Lint: **unknown**. Use the project's configured linters/formatters.

## Project Structure

**Unknown.** The repository is not visible. The relevant areas to locate are:
- The model save path that prepares related fields before save.
- The FK descriptor `__set__` logic that copies the related pk into the attname.
- The existing test modules covering FK assignment of unsaved objects and non-integer pks.

## Code Style

Follow the existing Django coding style and conventions, which are not visible here. Regression tests should follow the shape of the issue's reproduction above. Use minimal models with a `CharField(primary_key=True)` target.

## Testing Strategy

- **Level:** unit/integration tests using Django's own test suite against a real database.
- **Regression test (required):** reproduces the issue's scenario. It assigns a pk-less related instance, sets its pk, saves the related object, then saves the referencing object. It asserts that `order.product_id == "foo"` and that `Order.objects.filter(product=order.product).exists()` holds.
- **Control tests:**
  - Assigning a related object with its pk set at construction still works.
  - The auto-pk case still works: assign unsaved, save related, save referencing.
- **Guard tests:** saving the referencing object while the related object is unsaved, or has an empty pk, still raises `ValueError`.
- **Variants worth covering:** `OneToOneField`, and at least one other non-integer pk type if relevant (for example `UUIDField` without a default). Whether that type shows the bug is listed under Open Questions.
- **Backends:** the regression test must fail before the fix and pass after it on SQLite and PostgreSQL. On PostgreSQL, the transaction must commit without a `ForeignKeyViolation`.
- **Coverage:** no numeric target is known. The full existing suite must stay green.

## Boundaries

- **Always:**
  - Add a regression test that fails before the change.
  - Keep the "unsaved related object" `ValueError` guard working.
  - Run the full test suite on at least two backends.
- **Ask first:**
  - Changing which values count as "empty" for FK attnames in general, beyond the save-time refresh.
  - Changing descriptor assignment semantics.
  - Touching backend-specific code.
  - Adding release notes or docs (confirm the target release).
- **Never:**
  - Change the database schema or constraint deferral behaviour as a workaround.
  - Silently drop or weaken existing data-loss guards.
  - Remove or alter existing tests to make the change pass.

## Success Criteria

1. In the issue's scenario, after `order.save()`, `order.product_id == "foo"` and the stored row has `product_id = "foo"`.
2. `Order.objects.filter(product=order.product).exists()` is `True`, and `Order.objects.filter(product_id="").exists()` is `False`.
3. On PostgreSQL, the enclosing `transaction.atomic()` block commits without a `ForeignKeyViolation`.
4. Saving `order` while the assigned `Product` has no pk value, or has not been saved, still raises `ValueError`. No row with an empty FK is written.
5. Existing behaviour is unchanged for:
   - integer/auto pk targets;
   - related objects that have their pk at assignment time;
   - explicitly assigning `product_id` without a cached related object.
6. The same scenario passes for `OneToOneField`.
7. The full test suite passes on SQLite and PostgreSQL.

## Open Questions

1. Should the fix refresh the FK attname on save whenever the cached related object's pk differs from the attname? Or only when the attname holds an "empty" value (`None` or the field's empty values)? The second option is narrower. The first also handles a pk that changes from one non-empty value to another after assignment. Is that case in scope?
2. What should happen if a user deliberately sets `order.product_id = ""` while a different related object is cached? Should save-time sync override it?
3. Should a related pk of `""` count as "no pk" for the unsaved-object `ValueError` guard? It is a technically valid `CharField` value, but in practice it is almost always unintended.
4. Are other non-integer pk types affected the same way (for example `UUIDField` without a default, or custom fields whose empty value is not `None`)? Should they be covered in this change?
5. Does the same problem affect `GenericForeignKey` or other relation types that cache a related object and copy its pk? Is that in scope?
6. Which Django branch or release is the target? Is a release note required?
7. What are the exact test-runner command and test module locations in the repository? These are unknown here.