## Summary

The `--notes` option ignores note tags made up entirely of punctuation. When a tag such as `???` is passed to `--notes`, pylint does not emit the fixme warning (W0511) for comments that use it. Tags made of letters, such as `YES`, are reported normally.

## Steps to reproduce

1. Create a file `test.py` with this content:
   ```python
   # YES: yes
   # ???: no
   ```
2. Use the default configuration.
3. Run:
   ```shell
   pylint test.py --notes="YES,???"
   ```
4. Look at the reported W0511 (fixme) messages.

## Observed behavior

Pylint reports W0511 only for line 1, which uses the `YES` tag. It reports nothing for line 2, which uses the punctuation-only tag `???`.

```shell
************* Module test
test.py:1:1: W0511: YES: yes (fixme)
```

## Expected behavior

Pylint should report W0511 for both lines, because both tags were passed to `--notes`:

```
************* Module test
test.py:1:1: W0511: YES: yes (fixme)
test.py:2:1: W0511: ???: no (fixme)
```

## Stack trace / error output

Not provided in the original report. No crash occurs. The full pylint output appears under "Observed behavior".

## Test case

A minimal test case built from the report:

- Input file `test.py`:
  ```python
  # YES: yes
  # ???: no
  ```
- Command: `pylint test.py --notes="YES,???"`
- Pass condition: the output contains `test.py:2:1: W0511: ???: no (fixme)` as well as `test.py:1:1: W0511: YES: yes (fixme)`.

## Code example

```python
# YES: yes
# ???: no
```

## Version and environment

- pylint 2.12.2
- astroid 2.9.0
- Python 3.10.2 (main, Feb  2 2022, 05:51:25) [Clang 13.0.0 (clang-1300.0.29.3)]
- OS: macOS 11.6.1
- Configuration: default
- Additional dependencies: none given