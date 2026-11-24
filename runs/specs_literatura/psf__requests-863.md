## Summary
Allow lists of hook functions as values in the `hooks` argument of `Request`

## Description
The `Request` class has a `.register_hook()` method, but the dictionary passed through its `hooks` argument is parsed in a way that allows only one hook function per hook.

If a list of hook functions is passed for a hook, the code in `Request.__init__()` wraps that list in another list. This fails when the hooks are consumed, because a list is not callable.

## Product version
Not provided in the original request.

## Rationale
- The current behavior prevents using multiple hooks from a session, which the reporter calls especially annoying.
- Right now, the only way to register multiple hooks for a single hook is a workaround:
  1. Create the request object without sending it.
  2. Call `.register_hook()` multiple times.
  3. Call `.send()`.
- Accepting lists directly in the `hooks` argument would make this much easier.

## Use case or scenario
A user wants to attach several hook functions to the same hook. They want to do this either from a session or by passing them directly to the `Request` constructor as a list in the `hooks` dictionary. Currently this fails because the list is wrapped in another list and is not callable.

## Possible solution
Change how `Request.__init__()` parses the `hooks` parameter so that it accepts lists of hook functions as dictionary values, in addition to single hook functions.