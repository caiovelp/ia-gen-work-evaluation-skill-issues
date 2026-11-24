## Summary

The `tmpdir`, `tmpdir_factory` and `tmp_path_factory` fixtures use `getpass.getuser()` to determine the `basetemp` directory. `getpass.getuser()` can return a user name containing characters that are not allowed in directory names, such as a backslash in a domain user name like `contoso\john_doe`. When this happens, creating the temporary directory fails with a `FileNotFoundError`.

## Steps to reproduce

**Option A: simple reproduction from `cmd` (reported with pytest 6.2.2)**

1. Open a Windows `cmd` prompt.
2. Create a test file that uses the `tmpdir` fixture:
   ```bat
   echo def test_tmpdir(tmpdir):>test_tmp.py
   echo   pass>>test_tmp.py
   ```
3. Set a user name that contains a backslash:
   ```bat
   set LOGNAME=contoso\john_doe
   ```
4. Run pytest:
   ```bat
   py.test test_tmp.py
   ```

**Option B: original scenario (SSH session on Windows)**

1. Log in to a Windows 10 x64 Enterprise (1909) machine over SSH, using an OpenSSH_for_Windows_7.7p1 server.
2. Run `python -c "import getpass; print(getpass.getuser())"`. It returns the domain user name, for example `contoso\john_doe`. In a regular local session it returns `john_doe`.
3. In a pytest test, create a temp directory, for example with `tmpdir_factory.mktemp('foobar')`.

## Observed behavior

pytest builds the base temp path from the user name. The backslash in the name is treated as a path separator, which produces the nested path `...\Temp\pytest-of-contoso\john_doe`. Creating this directory fails with `FileNotFoundError: [WinError 3] The system cannot find the path specified`.

The reporter states that the `cmd` reproduction (Option A) also reproduces the issue. The output below comes from the SSH scenario (Option B).

## Expected behavior

The original report does not state this explicitly. It implies that pytest should create the temporary directory even when the user name returned by `getpass.getuser()` contains characters that are not allowed in directory names.

## Stack trace / error output

```
self = WindowsPath('C:/Users/john_doe/AppData/Local/Temp/pytest-of-contoso/john_doe')
mode = 511, parents = False, exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        if self._closed:
            self._raise_closed()
        try:
>           self._accessor.mkdir(self, mode)
E           FileNotFoundError: [WinError 3] The system cannot find the path specified: 'C:\\Users\\john_doe\\AppData\\Local\\Temp\\pytest-of-contoso\\john_doe'

C:\Python38\lib\pathlib.py:1266: FileNotFoundError
```

## Test case

`test_tmp.py`:

```python
def test_tmpdir(tmpdir):
  pass
```

Run it with the user name environment variable set to a value containing a backslash (Windows `cmd`):

```bat
set LOGNAME=contoso\john_doe
py.test test_tmp.py
```

## Code example

Command showing the user name returned in the SSH session:

```
python -c "import getpass; print(getpass.getuser())"
```

The output is `contoso\john_doe` over SSH and `john_doe` in a local session.

Call that triggers the failure in the SSH scenario:

```python
tmpdir_factory.mktemp('foobar')
```

## Version and environment

- pytest: 6.2.2 (stated for the `cmd`/`LOGNAME` reproduction)
- Python: installed at `C:\Python38` according to the traceback (Python 3.8; exact patch version not provided)
- OS: Windows 10 x64 Enterprise, version 1909
- SSH server (original scenario): OpenSSH_for_Windows_7.7p1
- User name format that triggers the issue: domain user name, for example `contoso\john_doe`