## Summary
Allow `ValidationError` instances (`django.core.exceptions.ValidationError`) that are created identically to compare as equal.

## Description
At present, two `ValidationError` instances with identical messages are not equal to each other. The request is to add an `__eq__` method to `ValidationError` so that two instances can be compared.

The comparison should ideally do more than check `self.messages == other.messages`. It should not depend on the order in which errors were raised, either within a field or in `non_field_errors`.

## Product version
Not provided in the original request.

## Rationale
- Identical `ValidationError` instances that are not equal is counter-intuitive behavior.
- Because they cannot be compared directly, some kinds of testing become more complicated.

## Use case or scenario
In tests, a developer wants to check that a raised `ValidationError` equals an expected `ValidationError` built with the same messages. Two errors with the same messages for a field or in `non_field_errors` should count as equal even if the errors were raised in a different order. No more detailed scenario is given in the original request.

## Possible solution
Add an `__eq__` method to `django.core.exceptions.ValidationError`. The original request suggests it should go beyond a simple `self.messages == other.messages` check and compare errors independently of the order in which they were raised within a field or in `non_field_errors`.