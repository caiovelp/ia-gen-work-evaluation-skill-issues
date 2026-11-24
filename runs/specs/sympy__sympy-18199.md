# Spec: `nthroot_mod` must return the root `x ≡ 0 (mod p)` when `a ≡ 0 (mod p)`

## Assumptions
1. `nthroot_mod` is a function in a number-theory library. The issue's style (`17*17`, `x**n`) suggests a Python library, probably SymPy's `ntheory` module. This is unconfirmed.
2. The call shape `nthroot_mod(a, n, p)` means: solve `x**n ≡ a (mod p)`. In the issue's example, `a = 289`, `n = 5`, `p = 17`.
3. The function may take an extra flag that chooses between returning one root and returning all roots, for example `all_roots`. The issue does not mention one. The name, default value and return types are unknown.
4. `p` is mainly meant to be prime, as the issue's use of "p" suggests. Whether composite moduli are supported is unknown.
5. When `p` is prime and `a ≡ 0 (mod p)`, the congruence `x**n ≡ 0 (mod p)` with `n ≥ 1` has exactly one solution, `x ≡ 0`. A prime cannot divide `x**n` unless it divides `x`. So 0 is not just one missing root among others. It is the whole solution set.
6. The current behaviour for the example is a wrong or empty result, for example `None`, `[]`, or an exception. The issue only says the root "is not returned". The exact output is unknown.
7. Behaviour when `a % p != 0` is correct today and must not change.

## Objective
Fix `nthroot_mod` so it handles the case where `a` is divisible by the modulus. Today, for `x**n ≡ a (mod p)` with `a % p == 0`, the function does not check this condition and misses the root `x ≡ 0 (mod p)`. The issue gives this reproducer:

```
nthroot_mod(17*17, 5, 17)   # expected to include 0 (mod 17); currently does not
```

**Users:** anyone calling `nthroot_mod`, directly or through higher-level solvers, who may pass an `a` that is a multiple of `p`.

**Success looks like:** `nthroot_mod` returns `0` whenever `0` is a valid root. It returns it in the same form the function already uses for its results, in both single-root and all-roots modes. Results for every other input stay the same.

## Tech Stack
- Language: probably Python (see Assumption 1). The version is unknown.
- Library and module: unknown. Possibly SymPy's number-theory module.
- Dependencies: unknown.

## Commands
- Build: unknown
- Test: unknown. If this is SymPy, there is probably a pytest-style test runner, but the exact command is not visible.
- Lint: unknown
- Dev: unknown

## Project Structure
- Location of `nthroot_mod`: unknown
- Location of its tests: unknown
- Docs or docstring location: unknown. The function's docstring may need an example for the `a ≡ 0` case.

## Code Style
- Unknown. Follow the conventions already in the module that contains `nthroot_mod`.
- The fix must keep the function's existing return conventions: scalar vs. list, sorting, and how "no solution" is represented.

## Testing Strategy
- Framework: unknown. Use whatever the existing `nthroot_mod` tests use.
- Add regression tests, at unit level, next to the existing `nthroot_mod` tests:
  - The issue's reproducer: `nthroot_mod(17*17, 5, 17)` yields `0`.
  - `a == 0` exactly, for example `nthroot_mod(0, n, p)`, for several primes and exponents.
  - `a` a non-trivial multiple of `p`, for example `a = k*p`, for several values of `n`, including `n` that do and do not divide `p - 1`.
  - All-roots mode, if it exists: the result is exactly `[0]` for prime `p`.
  - Single-root mode, if it exists: the result is `0`.
- Keep or extend the existing tests for `a % p != 0` to show nothing has regressed.
- Optional: a brute-force property check for small primes. It should compare `nthroot_mod` against `{x in range(p) : pow(x, n, p) == a % p}` for all `a`, including `a ≡ 0`.

## Boundaries
- **Always:**
  - Keep the public signature and return-type conventions unchanged.
  - Add the issue's reproducer as a regression test.
  - Run the existing number-theory tests before committing.
- **Ask first:**
  - Changing behaviour for composite moduli. When `p` is not prime, `x**n ≡ 0` can have many roots, for example mod `p**k`.
  - Changing the result for `n ≤ 0` or other edge cases not covered by the issue.
  - Changing the documented API.
  - Adding dependencies.
- **Never:**
  - Change results for inputs where `a % p != 0`.
  - Remove or weaken existing tests.
  - Return `0` as a root when it does not satisfy the congruence.

## Success Criteria
1. `nthroot_mod(17*17, 5, 17)` returns `0` in the function's single-root form. In all-roots mode it returns `[0]`.
2. For every tested prime `p`, every `n ≥ 1`, and every `a` with `a % p == 0`, the function returns `0`. In all-roots mode the result is exactly `{0}`.
3. For every `a` with `a % p != 0`, the output is identical to the current behaviour, as checked by the existing tests and, optionally, the brute-force comparison.
4. Optionally, the docstring documents the `a ≡ 0 (mod p)` case.
5. The full existing test suite for the module passes.

## Open Questions
1. Which library and file contain `nthroot_mod`? What is its exact signature: parameter names, an all-roots flag, and its default?
2. What exactly does `nthroot_mod(17*17, 5, 17)` return today: `None`, `[]`, a wrong value, or an exception?
3. Is `p` required to be prime, or must composite moduli and prime powers also be handled? If composite moduli are allowed, should all roots of `x**n ≡ 0 (mod m)` be returned, for example the non-zero nilpotent roots mod `p**k`, or is that a separate issue?
4. The issue says "misses one root". Is the reporter expecting `0` in addition to other roots? For prime `p`, 0 is the only root, so this spec assumes the result should be exactly `0` or `[0]`.
5. How should `n = 0` or negative `n` behave when `a ≡ 0`? Is that case in scope?
6. Do other functions that depend on `nthroot_mod`, such as polynomial or equation solvers, need verifying or updating as part of this change?