# Spec: `method_decorator()` preserves wrapper assignments on the bound callable

## Assumptions
1. `method_decorator` is Django's `django.utils.decorators.method_decorator`. The issue does not name the project, but the API name and the behavior match Django. The file path is assumed and has not been verified.
2. Internally, `method_decorator` binds the method to `self` with `functools.partial` and passes that partial to each decorator. A `partial` has no `__name__`, `__module__`, `__qualname__` or `__doc__`, so the decorator sees none of them.
3. "Wrapper assignments" means the attributes in `functools.WRAPPER_ASSIGNMENTS`: `__module__`, `__name__`, `__qualname__`, `__doc__`, `__annotations__`, and `__type_params__` on newer Pythons. "Preserve" means these attributes are copied from the original method onto the bound callable that the decorator receives.
4. The example in the issue has several mistakes, and none of them is the bug being reported:
   - It calls `Test().test_method()` instead of `Test().hello_world()`.
   - `inner` never returns `result`.
   - `logger.debug` refers to the decorator function, not a logging logger.

   The bug being reported is the `AttributeError` when the decorator reads `func.__name__`.
5. The fix should not change the public signature or the documented behavior of `method_decorator`.
6. Existing behavior must keep working. Today, attributes that the decorator sets on its wrapper are copied onto the final method, and `__dict__` and wrapper assignments of the original method are kept on the final decorated method. This includes `update_wrapper` behavior on the outer `_wrapper`.

## Objective
Developers use `method_decorator` to apply function decorators to methods. Many real-world decorators read metadata from the callable they receive, such as `func.__name__` for logging, `func.__module__` for registration, or `func.__doc__`. Today those decorators fail with:

```
AttributeError: 'functools.partial' object has no attribute '__name__'
```

They fail because the callable passed in is a bare `functools.partial`.

**Goal:** the callable that `method_decorator` passes to a decorator must carry the original method's wrapper assignments, so it looks like a function to the decorator. This includes decorators that apply `functools.wraps(func)` and decorators that read `func.__name__` directly.

**User story:** As a developer, I can write `@method_decorator(logger)` on a method, where `logger` uses `@wraps(func)` and reads `func.__name__`. Calling the method then works and logs the method's real name.

## Tech Stack
- Python and the `functools` standard library module (`partial`, `wraps`, `update_wrapper`, `WRAPPER_ASSIGNMENTS`).
- Project: assumed to be Django.
- Supported Python and Django versions: **unknown**.

## Commands
- Build: unknown (not provided in the issue)
- Test: unknown (Django normally uses `tests/runtests.py`, which is not verified; the exact invocation for the decorators test module is unknown)
- Lint: unknown
- Dev: N/A (library change)

## Project Structure
- Implementation: assumed to be `django/utils/decorators.py`, containing `method_decorator` and its private helper `_multi_decorate`. Not verified.
- Tests: assumed to be in the existing decorators test module, `tests/decorators/tests.py`. Not verified.
- Docs/release notes: location unknown. A release note may be needed if this is treated as a bug fix in a supported release.

## Code Style
- Follow the existing conventions in the decorators module. These are unknown here because no source is visible.
- The repro from the issue, corrected, which the fix must make pass:

```python
from functools import wraps

def logger(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            result = str(e)
        finally:
            log.debug(f"{func.__name__} called with args: {args} and kwargs: {kwargs} resulting: {result}")
        return result
    return inner

class Test:
    @method_decorator(logger)
    def hello_world(self):
        return "hello"

Test().hello_world()  # must not raise; returns "hello"
```

## Testing Strategy
- **Framework:** the project's existing unit test framework. For Django this is assumed to be `unittest` / `SimpleTestCase`; the exact base class used in the decorators tests is unknown.
- **Level:** unit tests in the existing `method_decorator` test suite.

**New cases:**
1. A decorator that reads `func.__name__` without using `wraps` sees the original method's name.
2. A decorator that uses `@wraps(func)`, as in the issue, applies without error, and the method returns the correct value.
3. Inside the decorator, the received callable's `__module__`, `__qualname__` and `__doc__` match the original method.
4. Several decorators passed as an iterable, for example `method_decorator((dec_a, dec_b))`, each receive a callable with the wrapper assignments.
5. The class-level form `@method_decorator(dec, name="method")` behaves the same way.

**Regression:** all existing `method_decorator` tests pass unchanged. These cover attribute propagation, `name=` on classes, iterables of decorators, and the descriptor and `self` binding behavior.

**Coverage:** no numeric target is known. Every new code path must be exercised by at least one test.

## Boundaries
- **Always:**
  - Keep the public API of `method_decorator` unchanged.
  - Add regression tests that reproduce the issue's `AttributeError` before the fix.
  - Run the full decorators test suite.
- **Ask first:**
  - Changing which callable type is passed to decorators. For example, replacing `partial` with a real function would change behavior visible to decorators that inspect the callable.
  - Copying attributes beyond `WRAPPER_ASSIGNMENTS`, such as `__dict__` or `__wrapped__`, onto the bound callable.
  - Backporting to older release branches.
- **Never:**
  - Modify user decorators or document a workaround instead of fixing the bug.
  - Remove or loosen existing tests.
  - Break `self` binding. Each call must still bind to the correct instance, with no state shared across instances or calls.

## Success Criteria
- [ ] The corrected repro above runs without `AttributeError` and returns `"hello"`.
- [ ] Inside any decorator applied through `method_decorator`, these attributes of the received callable equal the original method's: `func.__name__`, `func.__module__`, `func.__qualname__`, `func.__doc__` and `func.__annotations__`.
- [ ] The criteria above hold for a single decorator, for an iterable of decorators, and for the class form with `name=`.
- [ ] The decorated method still binds `self` correctly per instance and per call.
- [ ] All pre-existing `method_decorator` tests pass.

## Open Questions
1. Is this Django's `method_decorator`? Which branches and versions should get the fix?
2. Should "wrapper assignments" mean exactly `functools.WRAPPER_ASSIGNMENTS`? Or should the bound callable also get `__dict__` (`WRAPPER_UPDATES`) and a `__wrapped__` reference to the original method?
3. Must the callable passed to decorators stay a `functools.partial` instance with assignments added? Or may it become a different callable type, such as a plain function wrapper? Some third-party decorators might check `isinstance(func, partial)` or inspect `.func` and `.args`.
4. What are the exact test command and test file location?
5. Is a release note or docs change needed, and where?