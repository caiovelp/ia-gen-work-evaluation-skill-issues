## Summary
`nthroot_mod` misses the root `x = 0 mod p` of `x**n = a mod p` when `a % p == 0`. In that case `x = 0 mod p` is always a root, but the function does not check for this condition and does not return it.

## Steps to reproduce
1. Call `nthroot_mod(17*17, 5, 17)`. This solves `x**5 = 289 mod 17`, where `289 % 17 == 0`.
2. Look at the returned result.

## Observed behavior
`0 mod 17` is not returned, even though it is a root of the equation. The report does not show the exact value that is returned.

## Expected behavior
When `a % p == 0`, the result should include `x = 0 mod p`. For `nthroot_mod(17*17, 5, 17)`, it should include `0`.

## Stack trace / error output
Not provided in the original report. There is no error; the result is incorrect.

## Test case
Minimal check based on the report:
- Input: `nthroot_mod(17*17, 5, 17)`
- Check: `0` is among the returned roots. `0**5 = 0 ≡ 289 (mod 17)`, so `0` is a valid root.

## Code example
```python
nthroot_mod(17*17, 5, 17)  # 0 mod 17 is a root, but it is not returned
```

## Version and environment
Not provided in the original report.