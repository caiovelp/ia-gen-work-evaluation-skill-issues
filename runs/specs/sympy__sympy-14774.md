# Spec: Full inverse-trig names for `acsc` and `asec` in the LaTeX printer

## Objective

The SymPy LaTeX printer's `inv_trig_style` option is ignored for `acsc` and `asec`. Every style leaves them unchanged, so they print as `\operatorname{acsc}` and `\operatorname{asec}`. The other inverse trig functions (`asin`, `acos`, `atan`, `acot`) do respect the option.

**Who is affected:** Users who call `latex(expr, inv_trig_style=...)` and expect all six inverse trig functions to follow the same style.

**Current behavior (from the issue):**

| Call | Actual | Expected |
|---|---|---|
| `latex(asin(x), inv_trig_style="full")` | `\arcsin{\left (x \right )}` | (correct) |
| `latex(acsc(x), inv_trig_style="full")` | `\operatorname{acsc}{\left (x \right )}` | `\operatorname{arccsc}{\left (x \right )}` |

**Root cause the reporter suggests:** In `sympy/printing/latex.py` (around line 743), `inv_trig_table` lists only `["asin", "acos", "atan", "acot"]`. The proposed change adds `"acsc"` and `"asec"` to it.

**Success looks like:** `acsc` and `asec` follow `inv_trig_style` exactly as `asin`, `acos`, `atan` and `acot` do, for every supported style.

## Assumptions

1. Supported `inv_trig_style` values are `"abbreviated"`, `"full"` and `"power"`. I inferred this from SymPy convention; the issue does not show it, so it needs confirming against the source.
2. The style transformation is generic: `"full"` replaces the leading `a` with `arc`, and `"power"` produces `\func^{-1}`. If so, adding the names to `inv_trig_table` is enough.
3. `\arccsc` and `\arcsec` are not standard LaTeX commands, so the output must be `\operatorname{arccsc}` and `\operatorname{arcsec}`. The issue's expected output agrees. I assume the existing printing path already wraps names that are not known LaTeX commands in `\operatorname{...}`.
4. With `"power"` style, the expected output is `\csc^{-1}{...}` and `\sec^{-1}{...}`. `\csc` and `\sec` are standard LaTeX commands.
5. `"abbreviated"` (the default) output for `acsc` and `asec` stays exactly as it is today.
6. The `\left (x \right )` spacing in the issue reflects the reporter's SymPy version. Tests should assert against whatever the current printer emits for parentheses, not copy the issue's literal spacing.
7. Exponentiated forms such as `acsc(x)**2` use the same existing code path as `asin(x)**2` and should behave the same way.

## Tech Stack

- Python, SymPy (exact version: **unknown**)
- Affected module: `sympy/printing/latex.py` (named in the issue)

## Commands

- Build: **unknown** (pure Python; possibly none needed)
- Test: **unknown**. The SymPy test runner invocation is not given in the issue.
- Lint: **unknown**

## Project Structure

- `sympy/printing/latex.py`: LaTeX printer; `inv_trig_table` is defined here (from the issue)
- LaTeX printer tests: location **unknown**, presumably under the printing package's tests directory. Confirm before editing.

## Code Style

The issue shows only this snippet from the existing code:

```python
inv_trig_table = ["asin", "acos", "atan", "acot"]
```

Follow the surrounding conventions in `latex.py`. Keep the table's ordering consistent and readable, for example grouped by function family as in the reporter's suggestion: `asin, acos, atan, acsc, asec, acot`.

## Testing Strategy

- Add regression tests to the existing LaTeX printer test module (path unknown).
- Cover `acsc(x)` and `asec(x)` under each `inv_trig_style` value: `"abbreviated"`, `"full"` and `"power"`.
- Cover at least one exponentiated case, e.g. `acsc(x)**2` with `"full"` and `"power"`, to confirm power handling matches `asin(x)**2`.
- Run the full existing LaTeX printer test suite to confirm `asin`, `acos`, `atan` and `acot` output is unchanged.

## Boundaries

- **Always:** Add regression tests for both `acsc` and `asec`. Keep default (`"abbreviated"`) output unchanged. Run the existing printing tests.
- **Ask first:** Changing output for any function other than `acsc` and `asec`. Changing how unknown function names are wrapped (`\operatorname` vs. a bare command). Touching other printers (e.g. MathML or pretty printing).
- **Never:** Emit non-standard LaTeX commands like a bare `\arccsc` without `\operatorname`. Modify or delete existing passing tests to make new ones pass.

## Success Criteria

1. `latex(acsc(x), inv_trig_style="full")` returns `\operatorname{arccsc}` applied to `x`, using the printer's current parenthesis formatting.
2. `latex(asec(x), inv_trig_style="full")` returns `\operatorname{arcsec}` applied to `x`.
3. `latex(acsc(x), inv_trig_style="power")` and `latex(asec(x), inv_trig_style="power")` return `\csc^{-1}` and `\sec^{-1}` forms, consistent with how `asin` renders as `\sin^{-1}`.
4. Default and `"abbreviated"` output for `acsc` and `asec` is unchanged.
5. Output for `asin`, `acos`, `atan` and `acot` is unchanged under all styles.
6. Exponentiated `acsc` and `asec` (e.g. `**2`) render consistently with exponentiated `asin` under each style.
7. New regression tests exist and pass, and the existing LaTeX printer test suite passes.

## Open Questions

1. What exact `inv_trig_style` values are supported, and how does each one transform the name? This decides whether the table change alone is enough (Assumptions 1–2).
2. Under `"power"` style, should `acsc` and `asec` really become `\csc^{-1}` and `\sec^{-1}`? This is consistent, but it changes existing output for anyone currently using `"power"` with these functions.
3. Does the printer already wrap `arccsc` and `arcsec` in `\operatorname{}`? Or is there a list of LaTeX-known function names that has to be checked or kept unchanged?
4. Should the inverse hyperbolic functions (e.g. `acsch`, `asech`) be audited for the same gap, or are they out of scope?
5. Are any other printers affected by the same omission (e.g. MathML), and should they be fixed in this change or tracked separately?
6. What is the target SymPy version or branch, and what is the test command and test file location?