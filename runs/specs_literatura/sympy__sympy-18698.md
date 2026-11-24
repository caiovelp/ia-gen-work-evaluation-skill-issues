## Summary

`sqf_list` returns inconsistent results. When a polynomial has several distinct factors with the same multiplicity, `sqf_list` lists them separately instead of combining them into one factor of that multiplicity. In the first example below, `(x - 2)**3` and `(x - 3)**3` are returned as two separate factors of multiplicity 3. The reporter expects a single factor `(x**2 - 5*x + 6, 3)`. The second example combines factors as expected. The title says both `sqf` and `sqf_list` are inconsistent, but the report only shows output for `sqf_list`.

## Steps to reproduce

1. Call `sqf_list` on `(x**2 + 1) * (x - 1)**2 * (x - 2)**3 * (x - 3)**3`.
2. Note that the result has two separate factors with multiplicity 3.
3. For comparison, call `sqf_list` on `x**5 - 2*x**4 - 2*x**3 + 4*x**2 + x - 2`.
4. Note that this result combines factors of equal multiplicity into one factor, `(x**2 - 1, 2)`.

## Observed behavior

Inconsistent case:

```
>  sqf_list(  (x**2 + 1)  * (x - 1)**2 * (x - 2)**3 * (x - 3)**3  )

>  (1, [(x**2 + 1, 1), (x - 1, 2), (x - 3, 3), (x - 2, 3)])
```

`(x - 3)` and `(x - 2)` appear as two separate factors, each with multiplicity 3.

Case the reporter considers correct ("one factor of multiplicity 2"):

```
>  sqf_list( x**5 - 2*x**4 - 2*x**3 + 4*x**2 + x - 2 )

>  (1, [(x - 2, 1), (x**2 - 1, 2)])
```

## Expected behavior

Factors with the same multiplicity should be combined into one factor. For the first example, the result should contain `(x**2 - 5*x + 6, 3)`, which is `(x - 2)*(x - 3)`, instead of two separate factors of multiplicity 3.

## Stack trace / error output

Not provided in the original report. There is no error; the issue is incorrect output.

## Test case

A minimal test case based on the report's example. `x` is a symbol. The expected value is the reporter's stated expectation.

```
sqf_list((x**2 + 1) * (x - 1)**2 * (x - 2)**3 * (x - 3)**3)
# expected: (1, [(x**2 + 1, 1), (x - 1, 2), (x**2 - 5*x + 6, 3)])
# actual:   (1, [(x**2 + 1, 1), (x - 1, 2), (x - 3, 3), (x - 2, 3)])
```

## Code example

```
sqf_list(  (x**2 + 1)  * (x - 1)**2 * (x - 2)**3 * (x - 3)**3  )
sqf_list( x**5 - 2*x**4 - 2*x**3 + 4*x**2 + x - 2 )
```

## Version and environment

Not provided in the original report.