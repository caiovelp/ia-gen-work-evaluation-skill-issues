## Summary
Use an Admin Inline's `verbose_name` as the default for the Inline's `verbose_name_plural`.

## Description
Django lets you set both a `verbose_name` and a `verbose_name_plural` on Inline classes in admin views. Today, an Inline's `verbose_name_plural` does not take a `verbose_name` set on the Inline into account. It is still derived from one of two sources:
- the model name, or
- a `verbose_name` set in the model's `Meta` class.

As a result, if you want to override the default name for an Inline, you have to set both the singular and the plural form explicitly.

## Product version
Not provided in the original request.

## Rationale
- **Confusing behavior:** The reporter did not understand at first why both name forms had to be set on an Inline just to override the default name.
- **Inconsistency:** A model's `Meta` class already derives the plural form from a given `verbose_name`. Inline classes do not, so they behave differently from model `Meta` classes.

## Use case or scenario
A developer sets a custom `verbose_name` on an admin Inline class to override its default display name. They expect the plural form to follow from that custom name, as it does in a model's `Meta` class. Instead, the plural is still based on the model name, or on the model's `Meta` `verbose_name`. The developer must also set `verbose_name_plural` to get a consistent result.

## Possible solution
When an Inline class has a `verbose_name` but no `verbose_name_plural`, the `verbose_name_plural` should default to a value based on the Inline's `verbose_name`. This matches how a model's `Meta` class works. The reporter has written a patch that does this, with tests, and offers to submit it.