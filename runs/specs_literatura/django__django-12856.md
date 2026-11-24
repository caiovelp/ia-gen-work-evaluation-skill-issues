## Summary
Add a check that the fields named in a `UniqueConstraint` actually exist.

## Description
When a model gains a `UniqueConstraint`, `makemigrations` doesn't check that the fields named in the constraint actually exist on the model.

The older `unique_together` syntax behaves differently. It raises `models.E012` if the fields don't exist.

A demonstration project was attached to the original request. To show that `unique_together` raises E012, uncomment `"with_unique_together"` in that project's `settings.py`.

## Product version
Not provided in the original request.

## Rationale
`unique_together` validates its field names and raises `models.E012` for fields that don't exist. `UniqueConstraint` does no such validation. This is inconsistent, and a `UniqueConstraint` that refers to fields that don't exist goes unreported when `makemigrations` runs.

## Use case or scenario
A developer adds a `UniqueConstraint` to a model's constraints and names one or more fields that don't exist on the model. When they run `makemigrations`, no error is reported. If they had used `unique_together` with the same field names, they would have received `models.E012`. The attached demonstration shows both cases.

## Possible solution
The request suggests adding a check for the fields of `UniqueConstraint` that works like the existing check for `unique_together`. That check raises `models.E012` when a named field doesn't exist.