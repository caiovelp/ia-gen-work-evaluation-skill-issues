# Spec: `trigsimp` recognizes complex-exponential forms of trig functions (`sin`, and optionally `sinc`)

## Objective

**Problem.** `trigsimp` does not rewrite combinations of complex exponentials into their trigonometric equivalents. The reporter expects:

```python
f = 1 / 2 * (-I*exp(I*k) + I*exp(-I*k))
trigsimp(f)        # desired: sin(k)
```

and, as a stretch goal:

```python
f = 1 / 2 / k * (-I*exp(I*k) + I*exp(-I*k))
trigsimp(f)        # desired: sinc(k)
```

The math behind this is the identity `sin(k) = (exp(I*k) - exp(-I*k)) / (2*I) = (-I/2)*(exp(I*k) - exp(-I*k))`.

**Users.** People doing symbolic work who get Euler-form results, for example from Fourier transforms, ODE solutions, or `rewrite(exp)`. They want `trigsimp` to return the compact trigonometric form without having to know about `rewrite(sin)` or similar workarounds.

**What we're building.**

1. `trigsimp` recognizes sums of `exp(±I*x)` terms whose combination is a trig function of `x`, and returns that trig function when the result is simpler. The primary case is `sin`. `cos` is the natural companion; see Open Questions.
2. Optionally, when the result has the shape `sin(x)/x`, it is expressed as `sinc(x)`.

**What we're not building.** We are not converting every `exp(I*x)` into `cos(x) + I*sin(x)`. A rewrite should happen only when the trig form is simpler than the input.

**User stories**

- As a user, when I call `trigsimp` on `(-I/2)*(exp(I*k) - exp(-I*k))`, I get `sin(k)`.
- As a user, when I call `trigsimp` on `(exp(I*k) + exp(-I*k))/2`, I get `cos(k)`. This is assumed in scope; see Open Questions.
- As a user, when I call `trigsimp` on `(-I/2)*(exp(I*k) - exp(-I*k))/k`, I get `sinc(k)`. This is the stretch goal and depends on Open Questions.
- As a user, when I call `trigsimp` on an expression with no matching pattern, such as a lone `exp(I*k)`, the result is no more complicated than the input.

## Assumptions

1. The project is SymPy. `I`, `exp`, `sin`, `sinc` and `trigsimp` are SymPy objects, inferred from the names in the issue.
2. The reporter's `1 / 2` is meant as the exact rational `1/2`. Under Python 3, `1 / 2` evaluates to the float `0.5`, so the literal snippet produces a Float coefficient. The core acceptance tests use `S(1)/2` or `Rational(1, 2)`. Float behavior is covered in Open Questions.
3. `k` is a generic Symbol with no assumptions, so it may be complex. The `sin` identity holds for all complex `k`, so no assumptions on `k` should be required for that case.
4. `sinc(x)` in SymPy is the unnormalized `sin(x)/x`, with `sinc(0) = 1`, not the normalized `sin(pi*x)/(pi*x)`.
5. Today, `f.rewrite(sin)` (or a similar call) can already produce `sin(k)`. This is unverified. The issue is about `trigsimp` doing it automatically.
6. The fix belongs to the simplification layer (`trigsimp`, and possibly `simplify`). Constructors and auto-evaluation should not change.
7. Hyperbolic analogues (`exp(k) - exp(-k)` → `2*sinh(k)`) are out of scope unless confirmed otherwise.

## Tech Stack

- Python and SymPy. Exact versions are unknown.
- The test framework is unknown. The issue does not show it.

## Commands

The issue does not show any commands, so all of these are unknown:

```
Build:        UNKNOWN
Test:         UNKNOWN (need the command to run the trigsimp/simplify test modules)
Lint:         UNKNOWN
Dev / REPL:   UNKNOWN
```

## Project Structure

The paths are unknown; the repository is not visible. What we need to know:

- Where `trigsimp` is implemented: UNKNOWN
- Where `sinc` is defined: UNKNOWN
- Where the tests for `trigsimp` live: UNKNOWN

## Code Style

UNKNOWN; it is not visible from the issue. Follow the existing conventions of the module that contains `trigsimp`. New behavior should get regression tests written in the same style as the existing `trigsimp` tests.

## Testing Strategy

- **Framework:** UNKNOWN. Use whatever the existing `trigsimp` tests use.
- **Unit tests on exact outputs:**
  - `trigsimp(S(1)/2*(-I*exp(I*k) + I*exp(-I*k))) == sin(k)`
  - The equivalent forms `(exp(I*k) - exp(-I*k))/(2*I)` and expanded or reordered versions give the same result.
  - Scaled arguments, e.g. `exp(2*I*k)` and `exp(-2*I*k)`, give `sin(2*k)`.
  - The `cos` counterpart, if it is confirmed in scope.
  - The `sinc` case, if it is confirmed in scope.
- **Negative and regression tests:**
  - `trigsimp(exp(I*k))` is not expanded into `cos(k) + I*sin(k)`.
  - All existing `trigsimp` and `simplify` tests still pass.
- **Numerical cross-check:** for each new rewrite, the input and output agree when evaluated at several random complex points.
- **Coverage expectations:** UNKNOWN.

## Boundaries

- **Always:**
  - Keep each rewrite mathematically exact for the stated domain.
  - Add regression tests for the issue's examples.
  - Run the existing simplification test suites before committing.
- **Ask first:**
  - Changing the behavior of `simplify()`, not just `trigsimp()`.
  - Introducing `sinc` into any simplification output.
  - Changing how Float coefficients are handled.
  - Adding the hyperbolic analogues.
  - Changing the default `trigsimp` method or its public signature.
- **Never:**
  - Change auto-evaluation of `exp`, `sin` or `sinc`.
  - Return a result that is wrong for some complex `k`.
  - Remove or weaken existing tests to make new behavior pass.
  - Make `trigsimp` output strictly more complex for inputs that already worked.

## Success Criteria

1. `trigsimp(Rational(1,2)*(-I*exp(I*k) + I*exp(-I*k)))` returns exactly `sin(k)`, with `k = Symbol('k')` and no assumptions.
2. Algebraically equivalent arrangements of the same expression also return `sin(k)`. This includes reordered terms, a factored `1/(2*I)`, and an expanded form.
3. If `cos` is confirmed in scope, `trigsimp((exp(I*k) + exp(-I*k))/2)` returns `cos(k)`.
4. If `sinc` is confirmed in scope, `trigsimp(Rational(1,2)/k*(-I*exp(I*k) + I*exp(-I*k)))` returns `sinc(k)`. Otherwise it returns at least `sin(k)/k`.
5. `trigsimp(exp(I*k))` and other non-matching inputs are not made more complex.
6. All pre-existing `trigsimp` and `simplify` tests pass.
7. Each new rewrite passes a numerical equivalence check at random complex points.

## Open Questions

1. **Float coefficients.** As written in Python 3, the issue's `1 / 2` is the float `0.5`. Must `trigsimp(0.5*(-I*exp(I*k) + I*exp(-I*k)))` also return `sin(k)` (or `1.0*sin(k)`)? Or is support for exact rationals enough?
2. **`sinc` as an output of simplification.** `sin(k)/k` is undefined at `k = 0`, but `sinc(0) = 1`. Is it acceptable for `trigsimp` to silently extend the domain like this? Should it apply only via an opt-in flag or a separate rewrite, such as `rewrite(sinc)`? Or should it be left out of scope entirely?
3. **Scope of the trig family.** Should this cover only `sin`? Or also `cos`, `tan` (ratios of exponential sums), and the hyperbolic analogues `sinh` and `cosh` (real exponentials)?
4. **Layer.** Should only `trigsimp` gain this behavior, or should `simplify()` produce it as well?
5. **Measure of "simpler".** What criterion decides when an exponential → trig rewrite is applied? Candidates include the existing simplification measure (UNKNOWN), removal of `I`, or operation count. This affects mixed expressions such as `exp(I*k) + sin(k)`.
6. **Existing workaround.** Does `f.rewrite(sin)` already produce `sin(k)`? If it does, is the request mainly about discoverability, so that a documentation note would partly address it?
7. **Repository information.** We need the test and lint commands, where `trigsimp` is implemented, where its tests live, and the supported Python and SymPy versions.