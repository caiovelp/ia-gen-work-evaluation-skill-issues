# Spec: Readable `ResolverMatch.__repr__()` for `functools.partial` views

## Objective

When a URL pattern's view is a `functools.partial` object, `ResolverMatch.__repr__()` shows the func as `functools.partial`. That tells a developer nothing: it hides both the underlying view function and the arguments bound to it.

**Goal:** a developer inspecting a resolved match (in a debugger, a log or a test failure) can see:

1. the real underlying view callable, and
2. the arguments the partial pre-supplies.

**User:** Django developers who build views with `functools.partial`, for example to reuse one view function with different preset arguments, and who rely on `repr(resolve(path))` for debugging.

**Proposed direction (from the issue):** unwrap `functools.partial` objects in `ResolverMatch.__init__()` so the representation reflects the wrapped function and its pre-bound arguments. This is a proposal, not a decided design. See the Open Questions.

### User stories / acceptance criteria

- **Shows the wrapped function:** Given a URL pattern whose view is `functools.partial(my_view, template_name="x.html")`, when the URL is resolved and `repr()` is called on the match, then the output identifies the wrapped function by its dotted path (e.g. `myapp.views.my_view`). It must not show `functools.partial`.
- **Shows pre-bound arguments:** In the same case, the output includes the partial's pre-supplied positional and keyword arguments (here, `template_name='x.html'`).
- **Views still receive bound arguments:** Resolving and dispatching to a partial-based view still calls the view with the partial's bound arguments plus the URL-captured args/kwargs, exactly as today.
- **No change for other views:** The repr for plain function views and class-based views (`as_view()`) is unchanged.

## Tech Stack

- Python, Django. The affected component is `ResolverMatch`, Django's URL resolution result object.
- Supported Python and Django versions: **unknown** (not stated in the issue).
- Standard library: `functools.partial`, which exposes `.func`, `.args` and `.keywords`.

## Commands

Not stated in the issue. All are **unknown** and must be confirmed:

- Build: unknown (likely not applicable for a pure-Python change)
- Test: unknown. Django's own test runner invocation is assumed to exist but its exact command is not given here.
- Lint: unknown
- Dev: not applicable

## Project Structure

Not visible from the issue. Known only by name:

- `ResolverMatch` class, including its `__init__()` and `__repr__()`. File location is **unknown**. It is assumed to be in Django's URL resolution module but is unverified.
- Tests for URL resolution / `ResolverMatch` repr: location **unknown**.

## Code Style

Unknown. Follow the existing conventions of the file that contains `ResolverMatch`. No code snippets are provided because none are visible in the issue.

## Testing Strategy

- **Framework:** Django's existing test suite. The framework and runner command are unknown; see Commands.
- **Test level:** unit tests on `ResolverMatch` repr, plus a resolve-level test using a URLconf that contains a `functools.partial` view.
- **Cases to cover:**
  1. A partial with keyword arguments only: the repr shows the wrapped function path and the keywords.
  2. A partial with positional arguments: the repr shows the positional arguments.
  3. A partial with both positional and keyword arguments.
  4. A nested partial (a partial of a partial): the behaviour must be defined (see Open Questions) and then tested.
  5. Regression: the repr for a plain function view and for a class-based view is unchanged.
  6. Regression: a resolved partial view still gets called with its bound arguments, so dispatch behaviour is unchanged.
  7. If `view_name` or `_func_path` is derived from the func, test unnamed URL patterns that use partial views (see Open Questions).
- **Coverage expectations:** unknown. At minimum, every acceptance criterion has a test.

## Boundaries

- **Always:**
  - Keep the callable that is actually invoked for the request semantically identical, so the bound partial arguments are still applied.
  - Add regression tests for the non-partial view types.
  - Follow existing repr formatting conventions.
- **Ask first:**
  - Changing the public value of `ResolverMatch.func` or any other public attribute.
  - Changing derived values such as `view_name` for unnamed patterns.
  - Adding new public attributes to `ResolverMatch`.
  - Recursively unwrapping nested partials.
- **Never:**
  - Drop or silently ignore the partial's pre-bound arguments at dispatch time.
  - Change URL resolution or matching behaviour.
  - Alter the repr of non-partial views.

## Success Criteria

1. `repr()` of a `ResolverMatch` for a partial-based view contains the dotted path of the wrapped function and no longer contains `functools.partial` as the func path.
2. The same repr contains the partial's pre-bound positional and keyword arguments, in a readable form.
3. Requests routed to partial-based views behave exactly as before: the view receives the bound args plus the captured args/kwargs.
4. The repr output for function-based and class-based views is byte-for-byte unchanged, verified by tests.
5. All existing URL resolution tests pass.

## Assumptions

1. The current repr shows `functools.partial` because the func path is computed from the callable's module and name. A partial has no `__name__`, so a fallback based on the class name is used.
2. `ResolverMatch.func` is used (directly or indirectly) to invoke the view. Replacing it outright with the unwrapped function would therefore break the partial's bound arguments. Any unwrapping must preserve the original callable for dispatch, or store the unwrapped info separately.
3. "Unwrap in `__init__()`" means deriving the display information (wrapped function path and bound args) at construction time. It does not mean changing the callable used for dispatch.
4. The bound arguments are taken from the standard `partial.func`, `partial.args` and `partial.keywords` attributes.
5. This is a single capability, so no capability map (Phase 0) is needed.

## Open Questions

1. **Value of `ResolverMatch.func`:** should it keep returning the original partial object (safest for backward compatibility and dispatch), or the unwrapped function? If unwrapped, where are the bound args stored so dispatch still works?
2. **Exact repr format:** should the partial's args be shown as separate fields, or merged into the existing `args=` / `kwargs=` fields? Merging would blur URL-captured arguments with preset ones. Alternatively, should the func field show something like `functools.partial(<path>, *args, **kwargs)`?
3. **Nested partials:** should a partial of a partial be unwrapped recursively, with its arguments combined in the correct order?
4. **Other wrappers:** what about `functools.partialmethod`, or partials that wrap class-based views (`partial(MyView.as_view(), ...)`)? Are these in scope?
5. **`view_name` impact:** does the func path also feed `view_name` for unnamed URL patterns? If so, is changing it from `functools.partial` to the wrapped function's path an acceptable behaviour change, and does it need a release note?
6. **Target versions:** which Django and Python versions must this support? Is a release note or changelog entry required?
7. **Test location and commands:** which test module and which test command should be used?