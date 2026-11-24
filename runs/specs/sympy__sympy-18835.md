# Spec: `uniq` raises `RuntimeError` when its sequence argument changes size during iteration

## Objective

`uniq` yields the unique elements of its argument. If the caller modifies a passed list while consuming `uniq`, the output is silently wrong. In the reported example, removing each yielded item from `f` shifts the list, so `'H'`, `'S'` and `'E'` are skipped:

```python
>>> f = list('THISTLE')
>>> for i in uniq(f):
...   f.remove(i)
...   i
...
'T'
'I'
'L'
```

Python already guards against this for dictionaries and sets with `RuntimeError: dictionary changed size during iteration`. `uniq` should behave the same way for sized sequences. It should record the argument's size when iteration starts. If the size has changed when iteration resumes, it should raise a `RuntimeError` rather than return wrong results.

**Users:** anyone calling `uniq` on a mutable sequence, typically a list, who might mutate that sequence inside the consuming loop.

**User stories / acceptance criteria**
- As a caller who mutates the input list while iterating `uniq(f)`, I get a `RuntimeError` instead of a silently incomplete result.
- As a caller who does not mutate the input, behaviour and output are unchanged from today.
- As a caller who passes a generator or other unsized iterable, behaviour is unchanged and no error is raised.

## Assumptions

1. This is SymPy, and `uniq` and `multiset` are the functions from SymPy's iterables utilities. The issue does not name the project or the module path, so both are unconfirmed.
2. `uniq` is a generator function. The size check can therefore run each time the generator resumes, i.e. on each `next()` call after the first.
3. The check only applies to arguments that support `len()`. Arbitrary iterables such as generators and iterators cannot be size-checked and are passed through unchanged.
4. The error type is `RuntimeError`, with a message modelled on the built-in one, e.g. `"sequence changed size during iteration"`. The issue does not give exact wording.
5. Changing the size is the only mutation detected. Same-size mutations are explicitly out of scope, matching the limits of Python's own dict and set check. Examples:
   - item assignment such as `f[0] = 'X'`
   - a remove followed by an append
6. `uniq` may have an internal path for unhashable elements, or extra parameters. Whatever paths exist, the size check applies to all of them.
7. The check runs before producing the next element. A mutation made after the first yield is therefore detected on the next `next()` call, so in the example above `RuntimeError` is raised right after `'T'` is yielded and removed.

## Tech Stack

- Language: Python (from the issue's REPL examples).
- Project, Python versions and dependencies: **unknown**. SymPy is assumed (Assumption 1).

## Commands

All unknown; the issue provides none.

- Build: unknown
- Test: unknown (likely a pytest-style runner, unconfirmed)
- Lint: unknown
- Dev: not applicable (library function)

## Project Structure

Unknown. The file defining `uniq` and its test file are not shown in the issue. Locate them before planning.

## Code Style

Unknown. No project code is visible. Follow the existing style of the module that defines `uniq`. The only behavioural reference is Python's built-in error:

```
RuntimeError: dictionary changed size during iteration
```

## Testing Strategy

- Framework and test location: unknown. Use the existing test file for `uniq`'s module.
- Unit tests should cover:
  1. **Mutation is detected.** `f = list('THISTLE')`, then `f.remove(i)` inside `for i in uniq(f)`, raises `RuntimeError`.
  2. **Appending is detected**, so growth is caught as well as shrinkage.
  3. **No mutation, unchanged output.** `list(uniq(list('THISTLE')))` returns `['T', 'H', 'I', 'S', 'L', 'E']`.
  4. **Unsized iterables still work.** A generator input yields the same unique elements and raises no error.
  5. **Unhashable elements.** If `uniq` supports them (e.g. a list of lists), the size check also applies when the input is a mutable sequence.
  6. **Existing tests** for `uniq` and its callers pass without modification.
- Coverage expectations: unknown. At minimum, every new branch is exercised.

## Boundaries

- **Always:**
  - Keep output identical for unmodified inputs.
  - Keep `uniq` lazy, as a generator. Do not copy the whole input up front just to avoid the problem, since that hides the mutation instead of reporting it.
  - Run the existing test suite.
  - Add regression tests.
- **Ask first:**
  - Changing `uniq`'s signature or return type.
  - Changing behaviour for unsized iterables.
  - Choosing a different exception type than `RuntimeError`.
  - Detecting same-size mutations (out of scope here).
- **Never:**
  - Silently "fix" the caller's loop by iterating a private copy.
  - Change other functions such as `multiset`.
  - Remove or weaken existing tests.

## Success Criteria

- [ ] Iterating `uniq(f)` over a list `f` while removing items from `f` raises `RuntimeError`, not a truncated result.
- [ ] Iterating `uniq(f)` while appending to `f` raises `RuntimeError`.
- [ ] The error is raised on the first `next()` call after the size change is observed, not deferred or skipped.
- [ ] The error message clearly states that the sequence changed size during iteration.
- [ ] For inputs that are not modified, `uniq` output is unchanged, order included.
- [ ] Generators and other inputs without `len()` work exactly as before, with no exception.
- [ ] All pre-existing tests pass, and new regression tests cover the cases in Testing Strategy.

## Open Questions

1. **Project and location.** Is this SymPy, and which file and test file contain `uniq`?
2. **Exact error message.** Should the wording mirror Python's built-in message exactly, using "list" or "sequence"?
3. **Mutation after the last element.** If the caller mutates the input after the final yield, should exhausting the generator still raise? Python's dict iterator does. Assumption 7 implies yes, since the check runs on every resume.
4. **Sized but non-list inputs.** Should the check apply to any object with `__len__` (tuples, strings, custom sequences), or only to mutable sequences? Applying it to all sized inputs is harmless for immutable ones.
5. **Inputs whose `len()` is expensive or misbehaving.** Are there callers passing such objects that must not be checked?
6. **Internal `uniq` paths.** Does `uniq` have extra parameters (e.g. an accumulator argument) or a separate code path for unhashable items that needs the same guard?
7. **Same-size mutations.** Is it acceptable that mutations which keep the length constant remain undetected, as with Python's dict and set?
8. **Commands.** What are the build, test and lint commands, and which Python versions are supported?