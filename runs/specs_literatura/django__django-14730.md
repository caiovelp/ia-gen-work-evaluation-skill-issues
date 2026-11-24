## Summary
Prevent developers from defining a `related_name` on symmetrical `ManyToManyField`s by raising an error.

## Description
In `ManyToManyField`, the related field on the target model is not created when either of these is true:
- the `symmetrical` argument is passed, or
- the field defines a self-referential many-to-many relationship.

A developer may still pass a `related_name` in these cases without knowing that it has no effect. The request proposes raising an error when a `ManyToManyField` is defined with a `related_name` under these conditions.

## Product version
Not provided in the original request.

## Rationale
A developer who sets `related_name` on a symmetrical or self-referential `ManyToManyField` may not know that no related field is created on the target model. They may stay confused until they find the documentation about symmetrical relationships. An explicit error would make the problem visible right away.

## Use case or scenario
A developer defines a `ManyToManyField` that is symmetrical or self-referential and passes a `related_name`, expecting a related field to appear on the target model. No such field is created. The developer gets no feedback that `related_name` was ignored and is left confused until they learn how symmetrical relationships work.

## Possible solution
Raise an error when a `ManyToManyField` is defined with a `related_name` and the relationship is symmetrical (the `symmetrical` argument is passed, or the relationship is self-referential).