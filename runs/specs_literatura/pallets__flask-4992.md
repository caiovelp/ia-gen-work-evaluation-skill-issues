## Summary

Add a file mode parameter to `flask.Config.from_file()` so that files can be opened in binary mode.

## Description

`flask.Config.from_file()` always opens the config file in text mode. Some loader functions need a file opened in binary mode. One example is `tomllib.load()`, which is part of Python's native TOML support added in Python 3.11.

Passing `tomllib.load` directly to `from_file()` fails:

```python
app.config.from_file("config.toml", tomllib.load)
```

```
TypeError: File must be opened in binary mode, e.g. use `open('foo.toml', 'rb')`
```

The request is to add a parameter to `from_file()` that controls the mode in which the file is opened.

## Product version

- Python: 3.11 (the version that introduced `tomllib`)
- Flask version: Not provided in the original request.

## Rationale

Python 3.11 now supports TOML natively, so `from_file()` would be a natural, easy way to load TOML config files. Because `from_file()` only opens files in text mode, users need a longer workaround instead:

```python
# We have to repeat the path joining that from_file() does
with open(os.path.join(app.config.root_path, "config.toml"), "rb") as file:
    app.config.from_mapping(tomllib.load(file))
```

This workaround has two drawbacks:
- It is more verbose.
- It repeats the path joining that `from_file()` already does internally.

A file mode parameter would remove the need for this workaround.

## Use case or scenario

A developer on Python 3.11 keeps the application configuration in a `config.toml` file. They want to load it with the standard library's `tomllib.load` through `app.config.from_file()`, just as they would load JSON or other formats, without opening the file by hand and calling `from_mapping()`.

## Possible solution

Add a file mode parameter to `flask.Config.from_file()` so that callers can ask for binary mode, for example:

```python
app.config.from_file("config.toml", tomllib.load, mode="b")
```