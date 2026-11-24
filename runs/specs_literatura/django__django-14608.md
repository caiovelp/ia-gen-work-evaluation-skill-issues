## Summary
Add a `nonform` CSS class for non-form errors in FormSets.

## Description
Forms add the `nonfield` CSS class to `ErrorList` instances that hold non-field errors. This is documented in the section on rendering form error messages.

FormSets have no equivalent class for their non-form errors. The request is to add a `nonform` CSS class to the `ErrorList` for non-form errors in FormSets, matching how Forms use `nonfield`. The new class should also be documented for developers.

## Product version
Not provided in the original request.

## Rationale
A custom `ErrorList` currently cannot tell FormSet non-form errors apart from other errors when rendering error messages. With a `nonform` class, a custom `ErrorList` could separate three kinds of errors:
- form field errors
- non-field errors (Forms, via `nonfield`)
- non-form errors (FormSets, via `nonform`)

This would make FormSets behave consistently with the existing `nonfield` behavior in Forms.

## Use case or scenario
A developer uses a custom `ErrorList` to render error messages. They want to show FormSet non-form errors differently from form field errors and from Form non-field errors. A `nonform` CSS class on FormSet non-form errors would let them do this, the same way they can already target non-field errors through the `nonfield` class.

## Possible solution
- Add the `nonform` CSS class to the `ErrorList` used for non-form errors in FormSets, analogous to how Forms add `nonfield` for non-field errors.
- Document the `nonform` CSS class for developers, alongside the existing documentation on rendering form error messages.