## Summary
When Django's development server auto-reloads with `StatReloader`, it very intermittently crashes with `ValueError: embedded null byte`. The error comes from `pathlib.Path.resolve()`, which `django/utils/autoreload.py` calls in `iter_modules_and_files` while collecting watched module files. The reporter notes that `pathlib` was not used here before Django 2.2. The root cause and a reliable way to reproduce the crash are unknown.

## Steps to reproduce
The reporter does not know how to reproduce this reliably. The conditions under which it occurred:

1. Run the development server with auto-reloading enabled (`manage.py runserver`, which uses `StatReloader` via `autoreload.run_with_reloader`).
2. Let the reloader run its file-watching loop (`run_loop` → `tick` → `snapshot_files` → `watched_files` → `iter_all_python_module_files`).
3. Very intermittently, the reloader crashes with `ValueError: embedded null byte`.

## Observed behavior
- The auto-reloader crashes with `ValueError: embedded null byte`, raised from `os.readlink(path)` inside `pathlib` while resolving a module file path (`path.resolve().absolute()` in `django/utils/autoreload.py`, line 132).
- The reporter added `print(path)` before `os.readlink(path)` in `pathlib` and got this output before the failure:
  ```
  /Users/kez
  /Users/kez/.pyenv
  /Users/kez/.pyenv/versions
  /Users/kez/.pyenv/versions/3.6.2
  /Users/kez/.pyenv/versions/3.6.2/lib
  /Users/kez/.pyenv/versions/3.6.2/lib/python3.6
  /Users/kez/.pyenv/versions/3.6.2/lib/python3.6/asyncio
  /Users/kez/.pyenv/versions/3.6.2/lib/python3.6/asyncio/selector_events.py
  /Users
  ```
- The last path printed before the error always seems to be `/Users`.
- `/Users` may already have been printed several times by other `.resolve()` calls. The order is not deterministic, and resolution may have gone past `/Users` successfully many times during startup.
- The reporter's unconfirmed guess is that a mountpoint in `/Users` to a Samba share, possibly not yet connected, may be involved.
- It is unknown whether the problem is specific to the reporter's system (pyenv, OS X 10.11) or whether later Python versions fix it.

## Expected behavior
Not explicitly stated in the original report. By implication, the auto-reloader should keep watching files without crashing with `ValueError: embedded null byte`.

## Stack trace / error output
```
Traceback (most recent call last):
 File "manage.py" ...
	execute_from_command_line(sys.argv)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/__init__.py", line 381, in execute_from_command_line
	utility.execute()
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/__init__.py", line 375, in execute
	self.fetch_command(subcommand).run_from_argv(self.argv)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/base.py", line 323, in run_from_argv
	self.execute(*args, **cmd_options)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/commands/runserver.py", line 60, in execute
	super().execute(*args, **options)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/base.py", line 364, in execute
	output = self.handle(*args, **options)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/commands/runserver.py", line 95, in handle
	self.run(**options)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/core/management/commands/runserver.py", line 102, in run
	autoreload.run_with_reloader(self.inner_run, **options)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 577, in run_with_reloader
	start_django(reloader, main_func, *args, **kwargs)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 562, in start_django
	reloader.run(django_main_thread)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 280, in run
	self.run_loop()
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 286, in run_loop
	next(ticker)
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 326, in tick
	for filepath, mtime in self.snapshot_files():
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 342, in snapshot_files
	for file in self.watched_files():
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 241, in watched_files
	yield from iter_all_python_module_files()
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 103, in iter_all_python_module_files
	return iter_modules_and_files(modules, frozenset(_error_files))
 File "/Userz/kez/path/to/venv/lib/python3.6/site-packages/django/utils/autoreload.py", line 132, in iter_modules_and_files
	results.add(path.resolve().absolute())
 File "/Users/kez/.pyenv/versions/3.6.2/lib/python3.6/pathlib.py", line 1120, in resolve
	s = self._flavour.resolve(self, strict=strict)
 File "/Users/kez/.pyenv/versions/3.6.2/lib/python3.6/pathlib.py", line 346, in resolve
	return _resolve(base, str(path)) or sep
 File "/Users/kez/.pyenv/versions/3.6.2/lib/python3.6/pathlib.py", line 330, in _resolve
	target = accessor.readlink(newpath)
 File "/Users/kez/.pyenv/versions/3.6.2/lib/python3.6/pathlib.py", line 441, in readlink
	return os.readlink(path)
ValueError: embedded null byte
```

## Test case
Not provided in the original report.

## Code example
Not provided in the original report.

## Version and environment
- Django: a version that uses `pathlib` in the auto-reloader (the reporter says `pathlib` was not used before 2.2). The exact version is not stated.
- Python: 3.6.2, installed via pyenv (`/Users/kez/.pyenv/versions/3.6.2`), running in a virtualenv.
- OS: OS X 10.11.
- Reloader: `StatReloader`.
- Possibly relevant: a mountpoint under `/Users` to a Samba share (unconfirmed guess by the reporter).