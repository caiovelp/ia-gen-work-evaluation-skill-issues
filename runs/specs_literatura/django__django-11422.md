## Summary

When running the Django development server with the StatReloader, edits to `manage.py` no longer trigger an automatic reload. This is a regression: Django 2.1.8 and earlier reload when `manage.py` changes, but Django 2.2.1 does not. According to the `django.utils.autoreload` log lines, the autoreloader never sees `manage.py` itself.

## Steps to reproduce

1. Install Django 2.2.1: `pip install Django==2.2.1`
2. Use a project whose `manage.py` sets `DJANGO_SETTINGS_MODULE` to `'ticket_30479.settings'`.
3. Start the development server: `python manage.py runserver`
4. While the server is running, edit `manage.py`. For example, add a `print()` call at the start of `main()` (see Code example).
5. Save the file and watch the server output.

## Observed behavior

Under Django 2.2.1, saving the change to `manage.py` does not trigger the auto-reloading mechanism. The server does not restart. The `django.utils.autoreload` log lines show that `manage.py` is never among the files the autoreloader sees.

## Expected behavior

Editing `manage.py` should trigger an automatic reload of the development server. This is what happens under Django 2.1.8 and earlier.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report.

## Code example

This is the edit made to `manage.py` while the server is running. The `print('sth')` line is the added line, and the rest of the function is elided in the original report.

```python
def main():
    print('sth')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket_30479.settings')
    ...
```

## Version and environment

- OS: OS X 10.11
- Python: 3.6.2
- pip: 19.1.1
- Django: 2.2.1 (affected); 2.1.8 and prior (not affected)
- Autoreloader: StatReloader