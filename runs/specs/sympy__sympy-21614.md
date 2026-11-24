# Spec: Correct `kind` for `Derivative` of non-scalar expressions

## Objective

`Derivative(A, x).kind` returns `UndefinedKind` when `A` is a `MatrixSymbol`. The analogous `Integral(A, x).kind` correctly returns `MatrixKind(NumberKind)`. `Derivative` should report the kind of the expression it differentiates, so that code dispatching on `kind`, such as matrix-aware algorithms, treats unevaluated derivatives the same way it treats unevaluated integrals.

**User story:** As a SymPy user, when I build an unevaluated `Derivative` of an expression, `.kind` tells me what kind of object the derivative represents (scalar number, matrix, and so on), so I can reason about it without evaluating it.

**Acceptance criteria (from the issue):**
- `Derivative(A, x).kind == MatrixKind(NumberKind)` for `A = MatrixSymbol('A', 2, 2)` and `x` a scalar symbol.
- `Integral(A, x).kind` behaviour is unchanged. It is already correct.

## Assumptions

1. The intended rule mirrors `Integral`. When every differentiation variable is a scalar, the kind of a `Derivative` equals the kind of the expression being differentiated (`self.expr.kind`). This is inferred from the "correct" `Integral` example. I have not verified how `Integral` actually implements `kind`.
2. `Derivative` currently inherits a default `kind` (`UndefinedKind`) from a base class and never overrides it. I have not seen the code to confirm this.
3. The fix only affects the `kind` property. It does not change differentiation results, `doit()`, printing, or how `Derivative` is constructed.
4. Multiple scalar variables or higher-order derivatives (e.g. `Derivative(A, (x, 2), y)`) should produce the same kind as a single derivative: `expr.kind`.
5. For scalar expressions (e.g. `Derivative(f(x), x)`), the result should be `NumberKind`, which is whatever `f(x).kind` is.
6. The bug is in SymPy's core `Derivative` class. I do not know the version from the issue, and I cannot see the repository.

## Tech Stack

- Python, SymPy. The version is unknown and not stated in the issue.
- Relevant public API from the issue: `sympy.Derivative`, `sympy.Integral`, `sympy.MatrixSymbol`, `sympy.abc.x`, and the `.kind` attribute (`MatrixKind`, `NumberKind`, `UndefinedKind`).

## Commands

- Build: unknown (not visible in the issue)
- Test: unknown (not visible in the issue)
- Lint: unknown (not visible in the issue)
- Reproduction, taken from the issue:
  ```python
  from sympy import Integral, Derivative, MatrixSymbol
  from sympy.abc import x
  A = MatrixSymbol('A', 2, 2)
  Integral(A, x).kind    # MatrixKind(NumberKind)  — correct
  Derivative(A, x).kind  # UndefinedKind           — wrong; expected MatrixKind(NumberKind)
  ```

## Project Structure

Unknown. I don't have repository access.
- The file defining `Derivative` is unknown. I assume it lives in SymPy's core function module, but this is unverified.
- The file defining `Integral.kind` is unknown. It would serve as the reference implementation.
- The location of existing `kind` tests is unknown.

## Code Style

Unknown, beyond the public API in the issue. Follow the existing conventions for `kind` properties wherever `Integral` or similar classes define them. The fix should be a small property consistent with the existing pattern, not a new mechanism.

## Testing Strategy

- The framework is unknown. SymPy is assumed to use pytest-compatible test functions, but this is unverified.
- Add regression tests next to the existing `kind` tests, wherever those live (location unknown). Cover:
  - `Derivative(MatrixSymbol('A', 2, 2), x).kind == MatrixKind(NumberKind)`, the case from the issue.
  - A scalar case: `Derivative(f(x), x).kind == NumberKind`, or whatever the scalar expression's kind is.
  - Higher-order and multi-variable scalar derivatives of a matrix expression, which should keep `MatrixKind(NumberKind)`.
  - The existing `Integral(A, x).kind == MatrixKind(NumberKind)`, so this behaviour does not regress.
- Run the existing test suites for `kind`, core functions, and matrix calculus to confirm nothing else changes.

## Boundaries

- **Always:**
  - Keep `Derivative.kind` consistent with `Integral.kind` semantics.
  - Add a regression test reproducing the issue.
  - Run the existing tests before considering the work done.
- **Ask first:**
  - Defining a kind for derivatives taken *with respect to* non-scalar variables (matrix or array variables).
  - Changing `kind` on any class other than `Derivative`.
  - Altering the kind-dispatch system itself.
- **Never:**
  - Change the evaluation or differentiation results of `Derivative`.
  - Modify `Integral` behaviour.
  - Remove or weaken existing tests.

## Success Criteria

- [ ] `Derivative(MatrixSymbol('A', 2, 2), x).kind` returns `MatrixKind(NumberKind)`.
- [ ] `Integral(MatrixSymbol('A', 2, 2), x).kind` still returns `MatrixKind(NumberKind)`.
- [ ] Derivatives of scalar expressions with respect to scalar variables return the expression's kind, e.g. `NumberKind`.
- [ ] The new regression tests pass, and all pre-existing tests pass.
- [ ] No change to `Derivative.doit()` results or to construction behaviour.

## Open Questions

1. **Non-scalar differentiation variables.** What should `kind` be when differentiating with respect to a matrix or array variable, e.g. `Derivative(x, A)` or `Derivative(A, A)`? The result there is generally an array or matrix whose shape depends on both operands. Options:
   - leave these as `UndefinedKind` for now;
   - return the expression's kind;
   - define a combined kind.
2. **Undefined kinds.** If `expr.kind` is itself `UndefinedKind`, should `Derivative` just propagate it? (I assume yes.)
3. **Other related classes.** Should other unevaluated calculus or operator classes be audited for the same gap in this change, or handled separately? Examples include `Subs`, `Limit`, `Sum`, `Product`, and array derivatives.
4. **Implementation source.** Where and how is `Integral.kind` implemented (file and base class)? Should `Derivative` reuse that mechanism, for example via a shared base class, or define its own property?
5. **Target version.** Which SymPy version and branch should the fix target?