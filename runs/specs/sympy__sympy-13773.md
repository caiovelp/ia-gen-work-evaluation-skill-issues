# Spec: Restrict `@` (`__matmul__` / `__rmatmul__`) on `Matrix` to matrix–matrix operands

## Objective

The `@` operator on `Matrix` objects currently copies the behavior of `*` (`__mul__`). It therefore accepts scalar operands and performs scalar multiplication:

```
>>> A = Matrix([[1, 2], [3, 4]])
>>> B = Matrix([[2, 3], [1, 2]])
>>> A@B
Matrix([
[ 4,  7],
[10, 17]])
>>> 2@B
Matrix([
[4, 6],
[2, 4]])
```

`2@B` should not succeed. `@` should mean matrix multiplication only. If either operand is not a matrix, the operation must fail. This matches NumPy:

```
>>> 2@a
ValueError: Scalar operands are not allowed, use '*' instead
```

**Users:** Library users who write linear algebra code with `Matrix`. They expect `@` to reject scalars, and so to catch mistakes where a scalar was passed by accident, the same way NumPy does.

**Acceptance (user stories):**
- As a user, `A @ B` with two compatible matrices still returns the matrix product. This is the same result as today and the same as `A * B`.
- As a user, `2 @ B` raises an error telling me to use `*` instead.
- As a user, `B @ 2` raises an error telling me to use `*` instead.
- As a user, `A * 2` and `2 * A` keep working unchanged.

## Assumptions

1. The library is SymPy. This is inferred from the `Matrix([...])` repr style, and it is not stated in the issue.
2. "Copies `__mul__`" means that `__matmul__`, and probably `__rmatmul__`, delegate to `__mul__` / `__rmul__` or are aliased to them. Both directions (`M @ x` and `x @ M`) are in scope.
3. "Scalar" covers Python numbers (`int`, `float`, `complex`) and symbolic scalar expressions such as `Symbol('x')` and `Integer(2)`. All of them must be rejected by `@`.
4. Matrix–matrix `@` should give exactly the same results as matrix–matrix `*` today, including the error raised for incompatible shapes.
5. All matrix classes that share the operator implementation are in scope. This includes the mutable, immutable, and possibly sparse variants. Other matrix-like types, such as matrix expressions, are not in scope unless they inherit the same method.
6. `*` (`__mul__` / `__rmul__`) behavior is out of scope and must not change.
7. This is a deliberate backward-incompatible behavior change. Any existing code that relies on `scalar @ Matrix` will break.

## Tech Stack

- Language: Python. The supported versions are unknown, but `@` requires Python ≥ 3.5.
- Library: assumed SymPy, version unknown.
- Reference behavior: NumPy `ndarray.__matmul__`.

## Commands

Unknown. Nothing in the issue shows them.

```
Build: unknown
Test:  unknown (likely the project's test runner targeting the matrices test module, exact command unknown)
Lint:  unknown
Dev:   unknown
```

## Project Structure

Unknown. The issue does not show which files define `Matrix.__matmul__` / `__rmatmul__` or where their tests live.

```
<unknown>  → module defining Matrix arithmetic operators (__mul__, __matmul__, __rmatmul__)
<unknown>  → matrix arithmetic tests
```

## Code Style

Unknown. Follow the conventions of the surrounding operator-method code in the existing matrix module. No snippet is available from the issue.

## Testing Strategy

- **Framework:** unknown. Use the project's existing test framework and test module for matrix arithmetic.
- **Level:** unit tests on operator behavior.
- **Cases to cover:**
  - `Matrix @ Matrix` with compatible shapes returns the product (e.g. `A@B == Matrix([[4, 7], [10, 17]])`).
  - `Matrix @ Matrix` with incompatible shapes raises the same error as `*` does today.
  - `int @ Matrix`, `Matrix @ int` raise.
  - `float`, `complex`, and symbolic scalar (`Symbol`, `Integer`, `Rational`) operands in both positions raise.
  - Each in-scope matrix class (mutable, immutable, and others per Open Question 4) behaves the same way.
  - `2 * B` and `B * 2` are unchanged.
- **Coverage:** every new branch in `__matmul__` / `__rmatmul__` is exercised in both operand orders.

## Boundaries

- **Always:**
  - Keep matrix–matrix `@` results identical to `*`.
  - Test both `__matmul__` and `__rmatmul__`.
  - Run the existing matrix test suite before committing.
- **Ask first:**
  - Choice of exception type and message (see Open Questions).
  - Whether to emit a deprecation warning instead of a hard error.
  - Whether non-SymPy array-likes (lists, NumPy arrays) should be accepted by `@`.
  - Changing behavior of matrix-expression classes.
- **Never:**
  - Change `*` semantics.
  - Remove or weaken existing tests without approval.
  - Silently coerce scalars into matrices for `@`.

## Success Criteria

1. `Matrix([[1, 2], [3, 4]]) @ Matrix([[2, 3], [1, 2]]) == Matrix([[4, 7], [10, 17]])`.
2. `2 @ Matrix([[2, 3], [1, 2]])` raises an exception and does not return `Matrix([[4, 6], [2, 4]])`.
3. `Matrix([[2, 3], [1, 2]]) @ 2` raises an exception.
4. The same holds for symbolic scalars (e.g. `Symbol('x') @ B`, `B @ Symbol('x')`).
5. The error message tells the user to use `*` for scalar multiplication, as in NumPy's "Scalar operands are not allowed, use '*' instead".
6. `2 * B`, `B * 2`, and `A * B` produce the same results as before.
7. All existing matrix tests pass, except tests that explicitly asserted scalar `@` behavior. Any such test is updated with approval.

## Open Questions

1. **Exception type:** should it be `ValueError`, which matches NumPy, or `TypeError`? The other option is to return `NotImplemented`, which makes Python raise `TypeError: unsupported operand type(s) for @` and lets other types' `__rmatmul__` / `__matmul__` handle the operation.
2. **Deprecation path:** should scalar `@` raise immediately, or first emit a deprecation warning for a release cycle, given it's a breaking change?
3. **Non-SymPy operands:** should `Matrix @ list_of_lists` or `Matrix @ numpy_array` work, if `*` accepts them today, or be rejected?
4. **Scope of classes:** which matrix classes share this operator? Examples are mutable, immutable, sparse, and matrix expressions. Should matrix-expression `@` (e.g. `MatrixSymbol`) follow the same rule?
5. **Definition of "matrix":** what about 1×1 matrices, or objects that have a `shape` attribute but are not matrix instances? Should they count as matrix operands?
6. **Location of code and tests:** unknown. Where are `__matmul__` / `__rmatmul__` defined, and which test module should cover them?
7. **Project commands:** the test, lint, and build commands are unknown.