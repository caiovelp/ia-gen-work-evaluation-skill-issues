# Spec: Fix `Prefix * Quantity` collapsing to the number 1 (e.g. `milli*W == 1`)

## Objective

In `sympy.physics.units`, multiplying a prefix by a unit with the prefix on the left returns the plain number `1` instead of a prefixed unit:

```
In [1]: from sympy.physics.units import milli, W
In [2]: milli*W == 1
Out[2]: True          # wrong
In [3]: W*milli
Out[3]: watt*Prefix(milli, m, -3, 10)
```

The reporter confirmed this with watts (`W`) and volts (`V`). Other units are untested. Reported on SymPy 1.11.1 (Arch package 1.11.1-1) with Python 3.10.9.

**Goal:** `milli*W` (and `prefix * unit` in general) must evaluate to milliwatts. It must never collapse to a bare number unless the result really is dimensionless.

**Users:** Anyone building quantities with SI prefixes using the natural left-hand form, such as `milli*W`, `kilo*V` or `micro*A`.

**User stories / acceptance criteria:**
- As a user, when I write `milli*W` I get an expression that represents one milliwatt and is not equal to `1`.
- As a user, `milli*W` and `W*milli` represent the same physical quantity.
- As a user, converting `milli*W` to watts gives `W/1000`, so the magnitude is preserved.
- As a user, existing correct behaviour still works. Examples:
  - Prefix times prefix, such as `kilo*milli`, still combines as it does today.
  - Prefix times a non-unit expression still works.

## Assumptions

1. The bug is in how `Prefix` handles multiplication when the right operand is a unit/`Quantity`. The asymmetry (`W*milli` works, `milli*W` does not) points to the prefix's left-multiplication path.
2. **Unverified hypothesis:** the result is decided by multiplying the prefix's scale factor by the unit's scale factor, and returning `1` when the product is 1. If so, any unit whose SI scale factor is exactly 1000 would trigger the bug with `milli`. That would explain W and V, because SI derived units built on the kilogram can carry a factor of 1000 relative to the gram. By the same logic, other prefix–unit pairs whose factors multiply to 1 would also be affected, for example `kilo` with a unit whose scale factor is 1/1000. The fix must be confirmed against the actual source, which I cannot see.
3. The fix is limited to arithmetic semantics in `sympy.physics.units`. It does not redesign the units system or change how units are printed.
4. Prefix × Prefix behaviour is in scope only to keep it from regressing. It may legitimately combine to a number, for example `kilo*milli == 1`. Whether that is intended is listed as an open question.
5. The fix targets the current development branch, not a backport to 1.11.x.

## Tech Stack

- Python (reporter used 3.10.9). The supported Python range for the target branch is **unknown**.
- SymPy, module `sympy.physics.units` (classes `Prefix` and `Quantity` as named in the repr output). Exact file paths are **unknown**.
- No new dependencies expected.

## Commands

All commands are **unknown**, because the repository is not visible.
- Build: unknown (pure Python; likely none)
- Test: unknown (the test runner and the test file for units prefixes need to be confirmed)
- Lint: unknown
- Dev/repro: the reproduction snippet above, run in a Python session with the SymPy checkout importable

## Project Structure

**Unknown.** The only thing known is the import path `sympy.physics.units`. Where the source lives for `Prefix`, `Quantity` and the SI unit definitions, and where their tests live, must be confirmed from the repo.

## Code Style

Follow existing SymPy conventions in `sympy.physics.units`. No snippet is available from the issue. Match the surrounding code once it is visible.

## Testing Strategy

- **Regression unit tests** in the existing units/prefix test module (location unknown). They should cover:
  - `milli*W != 1`, and the result is equivalent to `W*milli`.
  - `milli*V != 1`, and the result is equivalent to `V*milli`.
  - `convert_to(milli*W, W)` gives `W/1000`, assuming `convert_to` is the appropriate public API in this version.
  - A sweep over the standard prefixes and a representative set of SI base and derived units. For each pair, check that the prefix-on-the-left result is not a bare number and equals the prefix-on-the-right result in magnitude and dimension.
  - Prefix × Prefix behaviour is unchanged, for example `kilo*milli`, matching whatever the current documented expectation is.
- **Full existing test suite** for `sympy.physics.units` must pass, to catch regressions in conversions and unit systems.
- Coverage target: unknown, so follow project norms.

## Boundaries

- **Always:** add a regression test reproducing `milli*W == 1` before fixing; keep `prefix*unit` and `unit*prefix` consistent; run the full units test suite.
- **Ask first:** changing the scale factors of SI units (such as W or V) or the kilogram/gram base handling; changing Prefix × Prefix semantics; changing the public repr or printing of prefixed units; any change outside `sympy.physics.units`.
- **Never:** special-case `milli` or `W` only; delete or weaken existing tests to make the fix pass; return a bare number from `Prefix * Quantity` when the result has a dimension.

## Success Criteria

1. `from sympy.physics.units import milli, W; milli*W == 1` evaluates to `False`.
2. `milli*W` represents 1 mW: converting it to `W` yields `W/1000`.
3. For every standard prefix `p` and every unit `u` in the tested set:
   - `p*u` is dimensionally equal to `u`.
   - `p*u` is numerically equivalent to `u*p`.
   - `p*u` is never a plain number.
4. The same holds for `V`, the other unit the reporter confirmed.
5. All pre-existing `sympy.physics.units` tests pass.

## Open Questions

1. What is the intended return type of `prefix * unit`?
   - A new prefixed `Quantity` (e.g. a quantity named `mW`)?
   - An unevaluated `Mul` like `W*milli` currently gives?
   - Or an expression in base units?
2. Should `prefix * unit` and `unit * prefix` return *identical* objects, or only physically equivalent ones?
3. Is Prefix × Prefix collapsing to a number (e.g. `kilo*milli == 1`) intended, and should it stay?
4. Is the scale factor of 1000 on W/V (relative to gram-based scaling) intended? Should the fix live in `Prefix` multiplication rather than in unit definitions? This depends on confirming Assumption 2.
5. Are there other prefix–unit pairs reported or known to be affected? This includes binary prefixes (kibi etc.) if they exist in this module.
6. Should the fix be backported to a 1.11.x/1.12 release, or only land on the main branch?
7. What are the test command and the test file location for units prefixes?