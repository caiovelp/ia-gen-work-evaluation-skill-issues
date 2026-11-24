# Spec: Consistent numeric value of `(-a)**x * a**(-x)` for a concrete positive integer `a`

## Objective

When `a` is a concrete positive integer such as `S(2)`, substituting a rational exponent into the unsimplified expression `(-a)**x * a**(-x)` gives a different number from substituting into its simplified form `(-1)**x`. With a symbolic `a` (integer, positive), both forms agree. The goal is that both forms give the same value for the concrete case, and that the value is mathematically correct under SymPy's principal-branch convention.

**Analysis of the reported numbers (principal branch, `z**w = exp(w*log(z))`, `arg ∈ (-π, π]`):**

- `(-1)**(-10/3) = exp(-10πi/3) = cos(10π/3) - i·sin(10π/3) = -0.5 + 0.866…i`.
- `(-2)**(-10/3) * 2**(10/3) = 2**(-10/3)·exp(-10πi/3) · 2**(10/3) = -0.5 + 0.866…i`.

So the expected value is `-0.5 + 0.866025403784439*I`. In the concrete case:

- `n2` from the simplified form is correct.
- `n1` from the unsimplified form is wrong. It returns `0.5 - 0.866…i`, which is the negation of the correct value.

The defect therefore appears to be in how a negative numeric base raised to a negative non-integer rational exponent is evaluated or auto-simplified (`(-2)**(-10/3)`). It does not appear to be in `simplify`. This is a hypothesis to confirm (see Open Questions).

**User:** SymPy users who evaluate expressions with numeric bases and symbolic or rational exponents. They expect results that are consistent across substitution, simplification and `N()`.

**Acceptance criteria:**

1. For `a = S(2)`, `x = Symbol('x')`, `t = -S(10)/3`:
   - `N(((-a)**x * a**(-x)).subs(x, t))` equals `-0.5 + 0.866025403784439*I`, to numerical tolerance.
2. In the same setup, `N(simplify((-a)**x * a**(-x)).subs(x, t))` still equals `-0.5 + 0.866025403784439*I`.
3. The symbolic case (`a = Symbol('a', integer=True, positive=True)`) keeps producing `-0.5 + 0.866025403784439*I` for both forms.
4. The exact (unevaluated-by-`N`) value of `(-2)**(-S(10)/3)` agrees numerically with `exp(-S(10)/3 * log(-2))` evaluated by `N`.

## Assumptions

1. SymPy's convention for `z**w` with non-integer `w` is the principal branch, `exp(w*log(z))` with `arg(z) ∈ (-π, π]`, so `(-1)**x` is not "equal" to `(-a)**x * a**(-x)` only up to branch choice. They should agree exactly for positive `a`.
2. The simplified result `(-1)**x` is correct, and the bug is in automatic evaluation of the numeric power `(-2)**(-10/3)`, or of the product `(-2)**(-10/3) * 2**(10/3)`. This is not yet verified.
3. `x` in the report is a plain `Symbol('x')` with no assumptions.
4. The fix should not change the documented principal-branch semantics of `Pow`.
5. Other negative integer or rational bases and other negative non-integer rational exponents may be affected in the same way. The fix is expected to cover the general case, not only `-2` and `-10/3`.

## Tech Stack

- Python, SymPy. The version is unknown, so the affected version(s) are unknown.
- Relevant components (names from the issue only): `Symbol`, `S`, `simplify`, `subs`, `N`, power and multiplication auto-evaluation. The exact modules and classes are unknown and must be confirmed in the repository.

## Commands

- Build: unknown (not stated in the issue)
- Test: unknown (not stated in the issue)
- Lint: unknown (not stated in the issue)
- Reproduce: run the two snippets from the issue in a Python session with SymPy importable. The exact invocation is unknown.

## Project Structure

Unknown. The repository is not visible, so the locations of the source files for numeric power evaluation and of their tests are not known.

## Code Style

Unknown. Follow the existing conventions of the SymPy codebase. No style samples are available from the issue.

## Testing Strategy

- **Regression tests** reproducing the issue:
  - The concrete case `a = S(2)`, `t = -S(10)/3`, checking `n1` and `n2` against the expected value.
  - The symbolic case (`integer=True, positive=True`), confirming it is unchanged.
- **Direct power test:** compare the exact form of `(-2)**(-S(10)/3)` against principal-branch numeric evaluation, i.e. `N` of `exp(-S(10)/3*log(-2))`.
- **Broader numeric consistency checks:** cover several negative integer or rational bases (e.g. `-2`, `-3`, `-S(2)/3`) and several rational exponents. These should include positive and negative exponents, proper and improper fractions, and denominators 2, 3, 4 and 6. Each auto-evaluated result should match `N(exp(w*log(z)))`.
- **Run the existing core and simplify test suites** to confirm nothing else regresses. The test framework and locations are unknown.

## Boundaries

- **Always:**
  - Preserve the principal-branch semantics.
  - Add regression tests for the reported case.
  - Verify the result numerically against `exp(w*log(z))`.
  - Run the existing test suites.
- **Ask first:**
  - Changing how numeric powers of negative bases are canonicalized, e.g. which form is printed or auto-extracted. This can change the output of many existing expressions and tests.
  - Changing `simplify` / `powsimp` behaviour.
  - Modifying existing test expectations.
- **Never:**
  - Make the two forms agree by changing the correct result (`(-1)**x` → `0.5 - 0.866…i`).
  - Remove or weaken failing tests without approval.
  - Introduce branch conventions that differ from the rest of SymPy.

## Success Criteria

- [ ] In the concrete case `a = S(2)`, `x = -10/3`, both `n1` and `n2` evaluate to `-0.5 + 0.866025403784439*I`.
- [ ] The symbolic case is unchanged and correct.
- [ ] For the tested grid of negative numeric bases and rational exponents, auto-evaluated `z**w` matches `N(exp(w*log(z)))`.
- [ ] Regression tests have been added and pass.
- [ ] Existing test suites pass, or every changed expectation has been reviewed and justified.

## Open Questions

1. Is the root cause confirmed to be the evaluation of `(-2)**(-S(10)/3)` on its own, or does it appear only in the product with `2**(10/3)` (e.g. during `Mul` combination of powers)? This needs reproduction.
2. Which SymPy version(s) show the bug, and is it a regression from an earlier version?
3. Are other negative bases and exponents affected? Possible patterns include only negative exponents, only exponents with `|w| > 1`, or only particular denominators.
4. If the fix changes the canonical printed form of numeric powers with negative bases (for example how `(-1)**(...)` factors are extracted), is that acceptable, given it may change many existing doctests and test expectations?
5. Should `simplify` (or `powsimp`) also be reviewed for branch safety when combining `(-a)**x * a**(-x)` → `(-1)**x`, or is that transformation considered correct for positive `a` and out of scope?
6. What are the project's test, build and lint commands, and where should regression tests live?