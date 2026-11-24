## Summary

Django 3.2 alpha raises the system check warning `models.W042` ("Auto-created primary key used when not defining a primary key type") for models that inherit their primary key from an ancestor model where it was manually defined. The same models produce no warnings with Django 3.1. The reporter believes this is a regression in Django 3.2 alpha.

## Steps to reproduce

1. Have a project with models that inherit from other models, where the primary key is manually defined on an ancestor model. For example, the reporter's `User` model inherits from a class `Entity` that defines the primary key.
2. Using Django 3.1, run `makemigrations`. No warnings are reported.
3. Install Django 3.2 alpha.
4. Run `makemigrations` again.

## Observed behavior

The system check reports `models.W042` for each model that inherits its primary key from an ancestor. Django treats these models as if they use an auto-created primary key. Affected models in the reporter's project:

- `accounts.ReservedUsername`
- `accounts.User`
- `blocks.Block`
- `contact_by_form.Feedback`
- `core_messages.ReadMark`
- `friendship.Block`
- `friendship.Follow`
- `friendship.Friend`
- `friendship.FriendshipRequest`
- `likes.UserLike`
- `uploads.Image`

## Expected behavior

No `models.W042` warning should be raised for these models. They do not use an auto-created primary key, because the primary key is already defined on an ancestor model (e.g., `Entity`, which `User` inherits from). This matches the behavior in Django 3.1.

## Stack trace / error output

```
System check identified some issues:
WARNINGS:
accounts.ReservedUsername: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the SpeedyCoreAccountsConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
accounts.User: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the SpeedyCoreAccountsConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
blocks.Block: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
contact_by_form.Feedback: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the SpeedyCoreContactByFormConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
core_messages.ReadMark: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the SpeedyCoreMessagesConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
friendship.Block: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
friendship.Follow: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
friendship.Friend: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
friendship.FriendshipRequest: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
likes.UserLike: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
uploads.Image: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
		HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
```

## Test case

Not provided in the original report.

## Code example

Not provided in the original report. The report only describes the model structure in prose: `User` inherits from an ancestor class `Entity`, which manually defines the primary key.

## Version and environment

- Works as expected: Django 3.1
- Warning raised: Django 3.2 alpha
- Triggered when running `makemigrations` (the system checks run as part of it)
- Python version, database and OS: Not provided in the original report.