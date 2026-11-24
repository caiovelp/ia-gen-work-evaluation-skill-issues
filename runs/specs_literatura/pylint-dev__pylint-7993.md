## Summary

Escaped (doubled) braces in `--msg-template` no longer work in pylint 2.12.2. With the template `{{ "Category": "{category}" }}`, pylint 1.7.4 (Python 3.6) printed a literal brace-wrapped string for each message, for example `{ "Category": "convention" }`. Pylint 2.12.2 (Python 3.9) instead emits a `UserWarning` saying it does not recognize the argument `{ "Category"`, and prints only `" }` for each message.

## Steps to reproduce

1. Use a Python file (`test.py`) that produces pylint messages. The reporter's file produced convention and error messages; its contents were not shared.
2. Run pylint with a message template that uses doubled braces to output literal `{` and `}`:
   ```shell
   pylint test.py --msg-template='{{ "Category": "{category}" }}'
   ```
3. Look at the warning output and the per-message lines.

## Observed behavior

With pylint 2.12.2 on Python 3.9:

- pylint emits a `UserWarning` saying it doesn't recognize the argument `'{ "Category"'` in `--msg-template`.
- Each message is printed only as `" }`. The literal braces, the `"Category":` key and the category value are all missing.

With pylint 1.7.4 on Python 3.6, the same command worked as intended (see Expected behavior).

## Expected behavior

Doubled braces `{{` and `}}` should produce literal `{` and `}`. `{category}` should be replaced with the message category. Each message should print as a dictionary-like line with `"Category"` as the key, as pylint 1.7.4 did:

```
{ "Category": "convention" }
{ "Category": "error" }
{ "Category": "error" }
{ "Category": "convention" }
{ "Category": "convention" }
{ "Category": "convention" }
{ "Category": "error" }
```

No warning about an unrecognized template argument should be emitted.

## Stack trace / error output

Pylint 2.12.2 output (paths redacted by the reporter):

```
[redacted]/site-packages/pylint/reporters/text.py:206: UserWarning: Don't recognize the argument '{ "Category"' in the --msg-template. Are you sure it is supported on the current version of pylint?
  warnings.warn(
************* Module [redacted].test
" }
" }
" }
" }
" }
" }
```

Pylint 1.7.4 output (previously working):

```
No config file found, using default configuration
************* Module [redacted].test
{ "Category": "convention" }
{ "Category": "error" }
{ "Category": "error" }
{ "Category": "convention" }
{ "Category": "convention" }
{ "Category": "convention" }
{ "Category": "error" }
```

## Test case

Minimal check based on the report:

1. Run `pylint <file-with-messages> --msg-template='{{ "Category": "{category}" }}'`.
2. Assert that no `UserWarning` about an unrecognized `--msg-template` argument is emitted.
3. Assert that each message line has the form `{ "Category": "<category>" }`, for example `{ "Category": "convention" }` or `{ "Category": "error" }`, and not `" }`.

## Code example

The only code in the report is the command line:

```shell
pylint test.py --msg-template='{{ "Category": "{category}" }}'
```

The contents of `test.py` were not provided in the original report.

## Version and environment

**Affected version:**
```
pylint 2.12.2
astroid 2.9.2
Python 3.9.9+ (heads/3.9-dirty:a2295a4, Dec 21 2021, 22:32:52)
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
```

**Previously working version:**
```
pylint 1.7.4
astroid 1.6.6
Python 3.6.8 (default, Nov 16 2020, 16:55:22)
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
```

- Configuration: none. The 1.7.4 run reports "No config file found, using default configuration."
- OS / environment: not provided in the original report. The GCC build string mentions Red Hat.
- Additional dependencies: not provided in the original report.