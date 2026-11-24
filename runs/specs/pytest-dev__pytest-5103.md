# Spec: Detailed Assertion Reports for `all()` / `any()` Calls

## Assumptions

1. The target is pytest's **assertion rewriter**, the AST transformation that produces the `+ where …` explanations. The issue says this, but I have not seen the module path or code.
2. The change only affects test modules that pytest already rewrites. Modules where rewriting is disabled, or which were imported before rewriting took effect, keep their current behaviour.
3. The reported environment is pytest 4.4.0 on Python 3.7.3. The feature targets the **current development branch** of pytest, and it must work on every Python version that branch supports. That version range is unknown to me.
4. "Unroll" means the assertion behaves *as if* it were written as a `for` loop with an inner `assert`. Failure output should reuse the existing per-expression explanation machinery, for example `where False = is_even(1)`. No new reporting format is invented.
5. Only calls whose callee is the builtin `all` or `any` are candidates. A call to some other object bound to the name `all` or `any` must keep its original behaviour.
6. Only two argument forms are in scope: a **single generator expression** or a **single list comprehension** passed directly as the only positional argument. Calls such as `all(some_list)`, `all(map(...))` and `all(x for x in y, ...)` with extra arguments are out of scope and keep today's output.
7. The rewrite must not change test outcomes. A passing assertion still passes, a failing one still fails, and evaluation order, laziness and side effects stay the same except where an Open Question below says otherwise.
8. This is a feature or enhancement, not a bug fix. Its changelog category is unknown.

## Objective

**Problem.** `assert all(pred(x) for x in xs)` and `assert any(...)` currently fail with messages that carry no information:

- With a generator: `where False = all(<generator object ... at 0x...>)`
- With a list comprehension: `where False = all([False, False, False, ...])`. This shows that something failed but not which element or why.

Users who want a useful report must rewrite the assertion as a `for` loop with an inner `assert`. That is more verbose, and for `any` it needs `break` or helper logic.

**Goal.** When an `assert` uses `all()` over a generator expression or list comprehension, the failure report should identify the **first element whose predicate is falsy**. It should explain that predicate with pytest's existing explanation output, matching what the equivalent `for`-loop form produces today.

**Users.** People writing pytest tests who assert a predicate across a collection.

**User stories**

- As a test author, when `assert all(is_even(n) for n in nums)` fails, I see which `n` failed and the explanation for `is_even(n)`, e.g. `where False = is_even(1)`.
- As a test author, I get the same improved report whether I use a generator expression or a list comprehension.
- As a test author, assertions that pass behave exactly as before, with no new side effects and no changed evaluation.
- As a test author, if I have shadowed or redefined `all`/`any`, my function is called unmodified.
- As a test author using `any(...)`, I get a report that is more informative than the bare `<generator object>` repr. The exact content is still open (see Open Questions).

**Out of scope**

- Other reducers such as `sum`, `min`, `max`, `sorted`, or user-defined helpers.
- Set or dict comprehensions, and arbitrary iterables passed by name. These are candidates for follow-up; see Open Questions.
- Changing explanation formatting for anything other than these calls.

## Tech Stack

- Language: Python. The supported version range on the target branch is **unknown**. The issue reporter uses 3.7.3.
- Component: pytest assertion rewriting, which is AST-based. The exact module path is **unknown**.
- Reporter environment from the issue: pytest 4.4.0, py 1.8.0, pluggy 0.9.0, attrs 19.1.0, more-itertools 7.0.0, six 1.12.0, atomicwrites 1.3.0, macOS (darwin).
- New dependencies: none expected. Adding any requires asking first.

## Commands

All commands are **unknown**, because the repository is not visible. They need to be filled in from the project's contributor docs or CI config.

```
Build:  unknown
Test:   unknown (likely the project's tox/pytest invocation — to be confirmed)
Lint:   unknown
Dev:    unknown
```

## Project Structure

**Unknown**, because the repository is not visible. To be confirmed:

```
<assertion rewriter module>   → unknown path
<assertion rewriter tests>    → unknown path
<changelog fragments dir>     → unknown path / naming convention
<user docs on assertions>     → unknown path
```

## Code Style

The project's conventions are unknown. The behaviour example below comes straight from the issue and is the reference for the desired output. It is a test input, not implementation code.

```python
def is_even(n):
    return n % 2 == 0

def test_all_even():
    even_stevens = list(range(1, 100, 2))
    assert all(is_even(number) for number in even_stevens)
```

Desired failure output: equivalent to the existing `for`-loop output, i.e. it contains

```
E       assert False
E        +  where False = is_even(1)
```

## Testing Strategy

- **Framework:** pytest's own test suite. It presumably includes facilities for running inner test files and matching their output, but the specific fixtures and helpers are **unknown**.
- **Test level:** mostly integration-style tests. Each one writes a small test module, runs pytest on it, and asserts on the failure output. A few unit-level checks of the rewriting may be useful if the existing suite does that.
- **Cases to cover:**
  - `all(<genexp>)` failing: the report names the first falsy element's explanation.
  - `all([<listcomp>])` failing: the same report.
  - `all(...)` passing: no failure and no behavioural change.
  - Empty iterable: `all(...)` passes, and `any(...)` fails with a sensible message.
  - `any(<genexp>)` and `any([<listcomp>])` failing: the agreed report format.
  - `all`/`any` shadowed by a local, global or import: no rewrite, original behaviour.
  - Comprehensions with `if` filters, with multiple `for` clauses, and with nested comprehensions.
  - The iteration variable does not leak into the enclosing scope, and it does not clash with names in the test.
  - Short-circuiting is preserved for generator expressions. Elements after the first falsy one are not consumed, for example by an iterator with side effects or a counter.
  - Eager evaluation is preserved for list comprehensions. All elements are still evaluated before `all`/`any` sees them, even if the report only explains one of them.
  - A predicate that raises still raises the same exception.
  - The assertion has a custom message: `assert all(...), "msg"`.
  - `all(...)` appears inside a larger expression, such as `not all(...)`, `all(...) and x`, or a comparison. The behaviour here depends on an Open Question.
  - Async comprehensions inside `async def` tests, if supported. This depends on an Open Question.
- **Coverage:** the project's expectations are unknown. Every new branch of the rewrite should be exercised by at least one test.

## Boundaries

- **Always:**
  - Preserve the semantics of the original assertion: outcome, evaluation order, laziness and short-circuiting, side effects, exceptions, and scoping.
  - Reuse the existing assertion-explanation machinery rather than adding a parallel format.
  - Fall back to the current behaviour for any argument shape that is not explicitly supported.
  - Add tests and a changelog entry following the project's conventions.
- **Ask first:**
  - Changing which builtins or argument shapes are rewritten beyond `all`/`any` with a single genexp or listcomp.
  - Anything that evaluates list-comprehension elements differently from plain Python.
  - Adding dependencies, or changing the minimum supported Python version.
  - Adding a config option or opt-out flag.
  - Changes to user-facing docs beyond a changelog entry.
- **Never:**
  - Rewrite calls to a user-shadowed `all`/`any`.
  - Change the result of a passing or failing assertion.
  - Consume more elements of a generator than plain `all`/`any` would.
  - Leak comprehension variables into the test's namespace.
  - Remove or weaken existing assertion-rewriting tests.

## Success Criteria

1. Running the issue's generator-expression example produces a failure report that contains `where False = is_even(1)`, or the equivalent per-element explanation, instead of `all(<generator object ...>)`.
2. Running the issue's list-comprehension example produces the same per-element report instead of `all([False, False, ...])`.
3. For every supported form, a passing `all(...)` or `any(...)` assertion still passes. The test suite of a project that relies on these calls passes unchanged.
4. For generator expressions, the number of elements consumed from the underlying iterator matches plain Python in both the pass and fail cases. A test with a counting iterator verifies this.
5. For list comprehensions, the evaluation side effects match plain Python. This is verified by test.
6. When `all` or `any` is rebound in the test module or function, the original object is called and the output matches today's.
7. Unsupported shapes, such as a named iterable, `map(...)`, set or dict comprehensions, or extra arguments, produce output identical to today's.
8. Exceptions raised by the predicate or the iterable propagate unchanged.
9. The `any(...)` failure output follows whatever format is agreed in Open Questions, and a test covers it.
10. The full existing pytest test suite passes. The command for running it is unknown.

## Open Questions

1. **`any` semantics.** When `any(...)` fails, every element was falsy, so there is no single "first failing" element. What should the report show? Options:
   - (a) The explanation for the last element.
   - (b) The first element.
   - (c) Something else, such as a summary.
   - (d) No unrolling for `any`, only for `all`.
2. **List comprehensions and eagerness.** A list comprehension evaluates every element before `all` runs. Should the rewrite keep full eager evaluation and then explain only the first falsy element? Or is changing to short-circuit evaluation acceptable? The current proposal is to preserve eager evaluation, per Boundaries.
3. **Assertion position.** Should only an assertion whose top-level expression is exactly `all(...)` or `any(...)` be rewritten? Or should nested occurrences also be rewritten, such as `not all(...)`, `all(...) and other`, or `x == all(...)`?
4. **Shadowing detection.** Is a static check enough, meaning no local, global or import binding of `all`/`any` in the module? Or must the check happen at runtime, e.g. confirming the called object `is` the builtin? Runtime checking also covers `builtins` being patched.
5. **Comprehension shapes.** Should comprehensions with multiple `for` clauses, `if` filters, nested comprehensions, or `async for` be supported? Or should they fall back to today's behaviour?
6. **Other iterables.** Is it in scope, now or later, to improve reports for `all(iterable_name)`, `all(map(f, xs))`, or set and dict comprehensions?
7. **Element identification.** Should the report also show the value of the loop variable, e.g. `number = 1`, or only the predicate explanation as in the `for`-loop form?
8. **Python version support.** What Python versions does the target branch support? AST node shapes for comprehensions and calls differ across versions.
9. **Opt-out.** Should users be able to disable this behaviour, e.g. via a config option, in case of unexpected semantic differences?
10. **Prior attempts.** Has this been attempted or discussed before in the project, for example an earlier implementation that was reverted? If so, which semantic problems must this spec explicitly guard against?
11. **Project logistics.** What are the exact build, test and lint commands, the module and test file paths, and the changelog fragment convention?