## Summary

`ManagementUtility` computes the program name (`self.prog_name`) from the `argv` passed to it, not from `sys.argv`. When it builds the `CommandParser` used to pre-parse `--pythonpath` and `--settings`, it does not pass that value as `prog`. The parser's `%(prog)s` in the usage string therefore falls back to `sys.argv[0]`. In environments where `sys.argv[0]` is wrong (for example, `None`), passing a custom `argv` to `execute_from_command_line` does not avoid the resulting exceptions.

## Steps to reproduce

1. Run in an environment where `sys.argv[0]` is `None`. The reporter has this in an embedded environment.
2. Call `execute_from_command_line` (which uses `ManagementUtility`) with your own `argv` list, where `argv[0]` is a valid program name.
3. `ManagementUtility.__init__` sets `self.prog_name` from the supplied `argv[0]`.
4. `ManagementUtility` creates a `CommandParser` with `usage='%(prog)s subcommand [options] [args]'` to parse `--pythonpath` and `--settings`, without passing `prog`.

## Observed behavior

The `CommandParser` resolves `%(prog)s` from `sys.argv[0]` instead of `self.prog_name`. When `sys.argv[0]` is `None`, exceptions follow, even though a valid `argv` was passed explicitly. As a workaround, the reporter currently modifies `sys.argv[0]` globally.

## Expected behavior

When an `argv` is passed to `ManagementUtility` / `execute_from_command_line`, the program name derived from it (`self.prog_name`) should be used everywhere, including the `CommandParser` used for `--pythonpath` and `--settings`. Passing a custom `argv` should then work without errors even if `sys.argv[0]` is incorrect (e.g., `None`).

## Stack trace / error output

Not provided in the original report. The reporter mentions "ensuing exceptions" but does not include them.

## Test case

Not provided in the original report. A test could follow the steps above:
1. Set `sys.argv[0]` to `None`.
2. Call `execute_from_command_line` with an explicit `argv` whose first element is a valid program name.
3. Check that no exception occurs and that the parser uses the program name from the supplied `argv`.

## Code example

Program name computed in `ManagementUtility.__init__` from the supplied `argv`:

```python
def __init__(self, argv=None):
    self.argv = argv or sys.argv[:]
    self.prog_name = os.path.basename(self.argv[0])
    if self.prog_name == '__main__.py':
        self.prog_name = 'python -m django'
```

Parser creation for `--pythonpath` / `--settings`, where `%(prog)s` resolves from `sys.argv[0]`:

```python
parser = CommandParser(usage='%(prog)s subcommand [options] [args]', add_help=False, allow_abbrev=False)
```

## Version and environment

Not provided in the original report. The reporter says only that they use an embedded environment where `sys.argv[0]` is incorrectly `None`. They also acknowledge that `execute_from_command_line` is a private API.