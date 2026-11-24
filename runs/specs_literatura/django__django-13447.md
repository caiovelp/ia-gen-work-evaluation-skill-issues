## Summary
Add the model class to the `app_list` context in the admin, and make the `_build_app_dict` method public.

## Description
In the admin, each model in the `app_list` context is currently a serialized dictionary. It does not give access to the model class itself.

The request has two parts:
1. Add the model class to each model entry in the `app_list` context.
2. Make the `_build_app_dict` method public. The two views `index` and `app_index` both use it.

## Product version
Not provided in the original request.

## Rationale
The requester needs to manipulate the `app_list` in a custom admin view. Having access to the model class is the easiest way to do that. Today this is hard because each model entry is only a serialized dictionary.

Making `_build_app_dict` public is proposed because the `index` and `app_index` views both use it.

## Use case or scenario
A developer writes a custom admin view and needs to change the `app_list` there, for example by working with the models it contains. With the model class in each entry, the developer can use the class directly instead of relying only on the serialized dictionary data.

## Possible solution
- Include the model class in each model dictionary of the `app_list` context.
- Rename `_build_app_dict` to a public method so custom admin views can use it, as `index` and `app_index` already do.