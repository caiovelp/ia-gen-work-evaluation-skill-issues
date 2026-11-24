## Summary

`method_decorator()` passes a `functools.partial` object to the decorator instead of a function-like object. The partial lacks the attributes expected of a function, such as `__name__` and `__module__`. A decorator that reads these attributes, for example `func.__name__`, raises an `AttributeError` when it is applied to a method through `method_decorator()`. The title states that `method_decorator()` should preserve wrapper assignments.

## Steps to reproduce

1. Define a decorator that wraps the received function with `@wraps(func)` and reads `func.__name__` inside the wrapper.
2. Apply this decorator to a class method using `@method_decorator(logger)`.
3. Instantiate the class and call the decorated method.

Note: the original snippet has two inconsistencies:
- It calls `Test().test_method()`, but the decorated method is named `hello_world`.
- It calls `logger.debug(...)`, where `logger` is the decorator function itself.

The reported problem is the access to `func.__name__` on the object passed to the decorator.

## Observed behavior

The object passed to the decorator is a `functools.partial` instance with no `__name__`, `__module__`, etc. Accessing `func.__name__` inside the decorator raises an `AttributeError`.

## Expected behavior

The function passed to the decorator by `method_decorator()` should have the attributes expected from a function (e.g. `__name__`, `__module__`). A decorator that accesses `func.__name__` should then work without raising an `AttributeError`.

## Stack trace / error output

```
AttributeError: 'functools.partial' object has no attribute '__name__'
```

Only this final error line was provided. The full traceback was not included in the original report.

## Test case

Minimal test derived from the report's snippet. The import location of `method_decorator` is not given in the original report.

```python
from functools import wraps

# method_decorator: import path not provided in the original report


def logger(func):
    @wraps(func)
    def inner(*args, **kwargs):
        # Accessing __name__ on the object passed by method_decorator()
        name = func.__name__
        return func(*args, **kwargs)
    return inner


class Test:
    @method_decorator(logger)
    def hello_world(self):
        return "hello"


def test_method_decorator_passes_function_attributes():
    # Expected: no AttributeError; currently raises
    # AttributeError: 'functools.partial' object has no attribute '__name__'
    assert Test().hello_world() == "hello"
```

## Code example

Original code from the report:

```python
def logger(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            result = str(e)
        finally:
            logger.debug(f"{func.__name__} called with args: {args} and kwargs: {kwargs} resulting: {result}")
    return inner

class Test:
    @method_decorator(logger)
    def hello_world(self):
        return "hello"

Test().test_method()
```

## Version and environment

Not provided in the original report.