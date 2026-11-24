## Summary
When the Django `UserAdmin` change page is opened through another model's admin that references `User` with `to_field` set (e.g. `to_field="uuid"`), the change page URL contains the `to_field` value instead of the primary key. The password help text in `UserChangeForm` links to the password change form with the relative URL `../password/`, which assumes the URL contains the pk. In this case the link is wrong and returns a 404.

## Steps to reproduce
1. Have a `User` model with a non-primary-key unique field, e.g. `uuid`.
2. Create another model with a reference to `User` that uses `to_field="uuid"`, and register it in the admin.
3. In that model's admin, follow the link to the related user. The `UserAdmin` change page opens at a URL like:
   `.../user/22222222-3333-4444-5555-666677778888/change/?_to_field=uuid`
4. On the user change page, click the "this form" link in the help text of the Password field.

## Observed behavior
The link to the password change form is built from the relative path `../password/`. Because the change page URL contains the `uuid` value rather than the user's pk, the resulting link points to the wrong URL and the request ends in a 404.

## Expected behavior
The "this form" link should open the password change form for that user, even when the `UserAdmin` change page was opened via `_to_field` rather than via the user's primary key.

## Stack trace / error output
Not provided in the original report. The report only states that the request results in a 404.

## Test case
Not provided in the original report.

## Code example
The relevant part of `UserChangeForm`, as quoted in the report:

```python
class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user’s password, but you can change the password using "
            '<a href="{}">this form</a>.'
        ),
    )
    ...
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get("password")
        if password:
            password.help_text = password.help_text.format("../password/")
    ...
```

## Version and environment
Not provided in the original report. The affected component is the Django admin (`UserAdmin` / `UserChangeForm`). The reporter mentions having opened a pull request on GitHub for this ticket.