## Summary

`python -m django shell -c` raises `NameError` when the passed Python code defines a function that uses a name imported at the top level of that same code. The same code runs correctly with plain `python -c`.

## Steps to reproduce

1. Use Python 3.7 and Django 2.2.16. The reporter says the relevant code is the same on master and behaves the same on Python 3.8.
2. For comparison, run the snippet with plain Python:
   ```bash
   $ python -c <<EOF "
   import django
   def f():
       print(django.__version__)
   f()"
   EOF
   ```
   It prints `2.2.16`.
3. Run the same snippet through Django's `shell` command:
   ```bash
   $ python -m django shell -c <<EOF "
   import django
   def f():
       print(django.__version__)
   f()"
   EOF
   ```
4. The command crashes with `NameError: name 'django' is not defined`.

## Observed behavior

`python -m django shell -c` raises `NameError: name 'django' is not defined`. The error comes from inside function `f`, even though `django` was imported at the top of the same code.

## Expected behavior

`python -m django shell -c` should behave like `python -c`. The function should see the module-level import, and the command should print the Django version (`2.2.16`).

## Stack trace / error output

Paths were shortened by the reporter.

```
Traceback (most recent call last):
  File "{sys.base_prefix}/lib/python3.7/runpy.py", line 193, in _run_module_as_main
    "__main__", mod_spec)
  File "{sys.base_prefix}/lib/python3.7/runpy.py", line 85, in _run_code
    exec(code, run_globals)
  File "{sys.prefix}/lib/python3.7/site-packages/django/__main__.py", line 9, in <module>
    management.execute_from_command_line()
  File "{sys.prefix}/lib/python3.7/site-packages/django/core/management/__init__.py", line 381, in execute_from_command_line
    utility.execute()
  File "{sys.prefix}/lib/python3.7/site-packages/django/core/management/__init__.py", line 375, in execute
    self.fetch_command(subcommand).run_from_argv(self.argv)
  File "{sys.prefix}/lib/python3.7/site-packages/django/core/management/base.py", line 323, in run_from_argv
    self.execute(*args, **cmd_options)
  File "{sys.prefix}/lib/python3.7/site-packages/django/core/management/base.py", line 364, in execute
    output = self.handle(*args, **options)
  File "{sys.prefix}/lib/python3.7/site-packages/django/core/management/commands/shell.py", line 86, in handle
    exec(options['command'])
  File "<string>", line 5, in <module>
  File "<string>", line 4, in f
NameError: name 'django' is not defined
```

## Test case

This is a minimal input for `shell -c`. It should print the Django version, but it currently raises `NameError`:

```python
import django
def f():
    print(django.__version__)
f()
```

Run it with:

```bash
python -m django shell -c "<code above>"
```

## Code example

The reporter points to the use of `exec` in the `handle` method of `django/core/management/commands/shell.py`. Both the `-c` command and the stdin input are passed to `exec`:

```python
def handle(self, **options):
    # Execute the command and exit.
    if options['command']:
        exec(options['command'])
        return
    # Execute stdin if it has anything to read and exit.
    # Not supported on Windows due to select.select() limitations.
    if sys.platform != 'win32' and not sys.stdin.isatty() and select.select([sys.stdin], [], [], 0)[0]:
        exec(sys.stdin.read())
        return
```

## Version and environment

- Django 2.2.16. The reporter says the code is the same on master.
- Python 3.7. The reporter says behavior is the same on Python 3.8.
- Commands were run from a shell using heredoc input. The OS is not provided in the original report.