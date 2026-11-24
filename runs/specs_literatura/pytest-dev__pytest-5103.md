## Summary
Unroll the iterable passed to `all()`/`any()` calls in assertions so that failure reports show which element failed.

## Description
Using the built-in `all()` or `any()` to assert a predicate over an iterable is concise. When such an assertion fails, however, pytest's report does not show which element caused the failure.

The same test written three ways gives these results:

**1. Generator expression**
```sh
    def test_all_even():
        even_stevens = list(range(1,100,2))
>       assert all(is_even(number) for number in even_stevens)
E       assert False
E        +  where False = all(<generator object test_all_even.<locals>.<genexpr> at 0x101f82ed0>)
```
The report shows only the generator object, which gives no useful information.

**2. List comprehension**
```sh
    def test_all_even():
        even_stevens = list(range(1,100,2))
>       assert all([is_even(number) for number in even_stevens])
E       assert False
E        +  where False = all([False, False, False, False, False, False, ...])
```
The report shows a list of boolean results but not the input values that produced them.

**3. For loop**
```sh
    def test_all_even():
        even_stevens = list(range(1,100,2))
        for number in even_stevens:
>           assert is_even(number)
E           assert False
E            +  where False = is_even(1)

test_all_any.py:7: AssertionError
```
Only this form gives a meaningful report, identifying the failing call `is_even(1)`.

## Product version
- pytest 4.4.0
- Python 3.7.3
- Platform: darwin (macOS)
- py 1.8.0, pluggy 0.9.0

Full `pip list` of the environment:
```
Package        Version
-------------- -------
atomicwrites   1.3.0
attrs          19.1.0
more-itertools 7.0.0
pip            19.0.3
pluggy         0.9.0
py             1.8.0
pytest         4.4.0
setuptools     40.8.0
six            1.12.0
```

## Rationale
- `all()`/`any()` are a natural and concise way to assert a predicate over an iterable, but their failure messages are not useful for debugging.
- The for-loop form gives a good report but is much more verbose.
- `all()`-style assertions do not translate cleanly into a for loop. Doing so requires a `break` or a helper function, which the author considers undesirable.
- Users should not have to give up concise test code to get informative failure reports.

## Use case or scenario
A developer wants to assert that every element of a collection satisfies a predicate, for example that every number in `even_stevens = list(range(1,100,2))` is even, using `assert all(is_even(number) for number in even_stevens)`. When the assertion fails, the developer wants the report to identify the specific failing element (e.g., `where False = is_even(1)`), as the for-loop version does, rather than an opaque generator object or a list of `False` values.

## Possible solution
The original request proposes that pytest's assertion rewriter "unroll" the iterable in `all()`/`any()` calls into the equivalent for-loop form (form 3 above). The existing assertion reporting would then produce a detailed message for the failing element.