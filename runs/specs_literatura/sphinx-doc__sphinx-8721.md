## Summary

The `sphinx.ext.viewcode` extension creates module (source code) pages for the EPUB output even when `viewcode_enable_epub = False` is set, if both the HTML and EPUB builders run in one invocation (`make html epub`).

## Steps to reproduce

1. Use a Sphinx project with the `sphinx.ext.viewcode` extension enabled.
2. Set `viewcode_enable_epub = False` in the configuration (this is also the default).
3. Build HTML and EPUB in a single command:
   ```
   $ make html epub
   ```
4. Check the generated EPUB output.

## Observed behavior

viewcode creates module pages for the EPUB output, even though `viewcode_enable_epub` is `False`.

## Expected behavior

Module pages should not be created for EPUB by default (i.e. when `viewcode_enable_epub = False`).

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report.

## Code example

Not provided in the original report. The only command given is:
```
$ make html epub
```

## Version and environment

- OS: Mac
- Python version: 3.9.1
- Sphinx version: HEAD of 3.x
- Sphinx extensions: `sphinx.ext.viewcode`
- Extra tools: None