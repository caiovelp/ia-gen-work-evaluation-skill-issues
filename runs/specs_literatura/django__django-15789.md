## Summary
Add an `encoder` parameter to `django.utils.html.json_script()` so that a custom JSON encoder class can be used.

## Description
`django.utils.html.json_script()` serializes values to JSON for output to the template layer. Right now the JSON encoder is hardcoded to `DjangoJSONEncoder`, so callers can't customize how values are encoded. The request is to let callers pass a custom encoder class to the function.

A related point: `django.utils.html.json_script()` is not documented. Only its template filter counterpart is documented. The reporter asks whether the function should be added to the documentation as well.

## Product version
Not provided in the original request.

## Rationale
The reporter needs to customize the JSON encoding of some values that are output to the template layer. `json_script()` looks like the right utility for this. However, because `DjangoJSONEncoder` is hardcoded, it can't be used when custom encoding is needed. Documenting the function would also make it easier to discover and use.

## Use case or scenario
A developer wants to output values to the template layer with `json_script()`, but some of those values need custom JSON encoding. With a configurable encoder, the developer could pass their own encoder class (for example, a subclass or replacement of `DjangoJSONEncoder`) and still get the existing behaviour of `json_script()`.

## Possible solution
- Add an optional `encoder` parameter to `django.utils.html.json_script()` that accepts a custom JSON encoder class. `DjangoJSONEncoder` would stay the default when no encoder is given.
- Optionally, add `django.utils.html.json_script()` to the documentation, since currently only the template filter is documented.