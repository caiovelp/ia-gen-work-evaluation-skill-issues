# Spec: C code printing support for `sinc(x)`

## Objective

`ccode(sinc(x))` currently emits an "unsupported" comment followed by a call to a non-existent C function:

```
In [30]: ccode(sinc(x))
Out[30]: '// Not supported in C:\n// sinc\nsinc(x)'
```

The reporter notes that `math.h` likely has no `sinc`. Instead of marking the function as unsupported, the C printer should emit an equivalent piecewise expression, since `sinc(x)` is mathematically:

```
sinc(x) = sin(x)/x   if x != 0
        = 1          otherwise
```

The issue's own workaround also shows a second defect. In the C output the relational `Ne(theta, 0)` is printed literally as `Ne(theta, 0)`, which is not valid C:

```
In [38]: ccode(Piecewise((sin(theta)/theta, Ne(theta, 0)), (1, True)))
Out[38]: '((Ne(theta, 0)) ? (\n   sin(theta)/theta\n)\n: (\n   1\n))'
```

So the generated code for `sinc` would only be valid C if `Ne` is also printed correctly, as `theta != 0`.

**User:** SymPy users generating C code from symbolic expressions that contain `sinc`.

**Acceptance criteria:**
1. `ccode(sinc(x))` produces valid C that evaluates to `sin(x)/x` when `x != 0` and to `1` when `x == 0`.
2. The output contains no "Not supported in C" comment for `sinc`.
3. `ccode(Ne(theta, 0))` and relationals used inside a `Piecewise` condition print as C operators (`theta != 0`), not as `Ne(theta, 0)`.
4. `sinc` with a compound argument, e.g. `ccode(sinc(2*x + 1))`, substitutes the full argument correctly in both the condition and the expression.
5. `ccode(sinc(x), assign_to=y)` produces valid C. Piecewise with `assign_to` normally emits an `if/else` block, and this case should too.

## Tech Stack

- Python, SymPy (version unknown, not given in the issue)
- Target output language: C (C89/C99 standard selection unknown, see Open Questions)

## Commands

Unknown. The issue gives no build or test commands. The SymPy test runner invocation is to be confirmed by the maintainer.

- Build: unknown
- Test: unknown
- Lint: unknown

## Project Structure

Unknown. The issue does not reference files. The locations of the C code printer and its tests must be confirmed against the repository.

## Code Style

Unknown from the issue. Follow the existing conventions of the C code printer module, such as how other functions without a direct `math.h` equivalent are handled. No code snippet is included here because none is visible in the issue.

## Testing Strategy

- Framework: the project's existing test framework (unknown, to be confirmed)
- Tests belong alongside the existing C code printer tests (location unknown)
- Required test cases:
  - `ccode(sinc(x))` expected output, as an exact string match
  - `ccode(sinc(<compound expr>))`
  - `ccode(sinc(x), assign_to=y)`
  - `ccode(Ne(x, 0))` and `ccode(Piecewise((..., Ne(x, 0)), (1, True)))` produce `!=`
  - A regression check that the printing of other relationals (`Eq`, `Lt`, `Gt`, `Le`, `Ge`) is unchanged, or corrected if also broken
- Optional, ask first: a compile/numeric check of the generated C against `sympy`'s numeric evaluation at `x = 0` and `x != 0`

## Boundaries

- **Always:** Produce output that is valid C. Keep existing `ccode` outputs for unrelated functions unchanged. Add tests for every new printing path.
- **Ask first:**
  - Extending the same fix to other code printers (Fortran, Octave, JS, etc.)
  - Changing how `sinc` itself is defined or evaluated in the core
  - Emitting a helper function definition instead of an inline expression
- **Never:**
  - Emit a call to a non-standard C `sinc` function
  - Change the mathematical definition of `sinc`, for example by switching to the normalized `sin(pi*x)/(pi*x)`

## Success Criteria

- `ccode(sinc(x))` returns a string equivalent to `((x != 0) ? (sin(x)/x) : (1))`, with exact whitespace following the printer's existing Piecewise formatting.
- No `Ne(`, `Eq(`, or other SymPy function-style relational appears in any `ccode` output for relationals.
- All new tests pass and existing printer tests remain green.

## Assumptions

1. SymPy's `sinc` is the unnormalized form `sin(x)/x`. The issue's workaround uses this form.
2. The preferred fix is to rewrite `sinc` as a `Piecewise` at print time, and then print that, rather than emitting a helper C function.
3. The `Ne(...)` output in the issue is a genuine bug in C relational printing and is in scope, because it makes the `sinc` output invalid C.
4. The condition `x != 0` (exact float comparison) is acceptable. Precision near zero is out of scope.
5. Only the C printer is in scope for this issue.

## Open Questions

1. Should the `Ne` relational printing bug be fixed in this issue, or tracked separately? This spec currently assumes the former, since the `sinc` output depends on it.
2. Should other code printers (Fortran, JavaScript, Octave, Rust, etc.) receive the same `sinc` handling in this change?
3. What are the exact SymPy version and the C standard targeted? Do C89 and C99 printers differ in their handling here?
4. Is a ternary/`Piecewise` expansion acceptable when the argument is expensive or has side effects? The argument would be evaluated more than once. Should a helper function or temporary be used instead?
5. Is exact-zero comparison acceptable, or should near-zero handling (e.g. a Taylor expansion for small `|x|`) be considered?
6. Where do the C printer and its tests live, and what is the test command?