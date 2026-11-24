# Spec: Correct `lambdify` Printing of Identity Matrices (and Fail Loudly on Unsupported Matrix Expressions)

## Objective

`lambdify` produces wrong numerical results for expressions that contain `Identity(n)`. The code printer emits `Identity(n)` as the bare name `I`. In the generated function's namespace, `I` resolves to the imaginary unit `1j`. As a result, `A + Identity(n)` evaluated on a NumPy array adds `1j` to every element instead of adding an identity matrix.

**Observed (from the issue):**

```python
>>> n = symbols('n', integer=True)
>>> A = MatrixSymbol("A", n, n)
>>> a = np.array([[1, 2], [3, 4]])
>>> f = lambdify(A, A + Identity(n))
>>> f(a)
array([[1.+1.j, 2.+1.j],
       [3.+1.j, 4.+1.j]])
>>> print(inspect.getsource(f))
def _lambdifygenerated(A):
    return (I + A)
>>> f.__globals__['I']
1j
```

**Expected:** `f(a)` equals `array([[2, 2], [3, 5]])`, which is the input array plus an identity matrix.

**Goals stated in the issue:**
1. The code printer used by `lambdify` must support printing identity matrices correctly.
2. The printer must raise an error for unsupported expressions that would otherwise be printed in a way that can be silently misinterpreted. The `I` / `1j` collision is the motivating example.

**Users:** SymPy users who call `lambdify` on matrix expressions, mainly with the NumPy backend.

**Success, in short:** No silent numerical corruption. Each matrix expression is either printed to correct backend code or rejected with a clear error.

## Assumptions

1. The affected component is SymPy's Python/NumPy code printer used by `lambdify`. Its exact module, class names and the method naming convention for per-type printing are unverified, because I have no repository access.
2. The NumPy backend is the primary target. Whether other `lambdify` modules (`math`, `mpmath`, `scipy`, `tensorflow`, etc.) are in scope is an open question.
3. For NumPy, an identity matrix is naturally printed as a call that builds an identity array, such as `numpy.eye(...)`. This needs the dimension to be known when the generated code runs.
4. In the issue's example, the dimension `n` is a free symbol. It is not an argument of the generated function and cannot be inferred from the printed code alone. Supporting the example exactly as written therefore needs either a design decision or an error (see Open Questions).
5. "Correct" output is judged by numerical equality with the mathematically expected matrix. The exact dtype is not required to match: `numpy.eye` returns floats, so the result could be `[[2., 2.], [3., 5.]]` rather than integers.
6. The fallback that prints unrecognized expressions with their plain string form is what produced `I`. The fix should change this behavior, at least for matrix expressions.
7. This change does not alter how the scalar `ImaginaryUnit` (`I`) is printed or bound in `lambdify` namespaces.

## Tech Stack

- Language: Python (supported version range unknown)
- Library: SymPy (version unknown; current development branch assumed)
- Runtime dependency for the bug: NumPy (version unknown)

## Commands

Unknown. No repository access. To be filled from the project's contributor docs. Placeholders:

```
Test:  UNKNOWN (likely a pytest or SymPy test-runner invocation scoped to printing and lambdify tests)
Lint:  UNKNOWN
Build: UNKNOWN (pure-Python library; likely none)
```

## Project Structure

Unknown and unverified. Likely relevant areas, to be confirmed:

```
<printing package>/<python code printer module>   → NumPy/Python code printer used by lambdify
<printing package>/tests/                         → printer tests
<utilities package>/lambdify module               → lambdify, namespace construction
<utilities package>/tests/                        → lambdify tests
```

## Code Style

Follow existing SymPy conventions for code printers. Specifically, add per-type printing methods consistent with how other matrix expression types are already handled in the same printer. No style snippet is available from the issue. Follow the surrounding code.

## Testing Strategy

- **Level: unit tests for the printer.** Assert the printed code string for `Identity` with a concrete integer dimension, for example `Identity(3)`, under the NumPy printer. Assert that a symbolic dimension behaves as decided in Open Question 1.
- **Level: integration tests via `lambdify`.**
  - For a concrete case, check that `lambdify(A, A + Identity(k))` evaluated on a k×k NumPy array returns the array plus an identity matrix, compared numerically, for example with `numpy.allclose` or an equivalent.
  - Regression test for the issue scenario: the result must never contain complex values from `1j`. It must either be correct or raise an error.
- **Level: error behavior.** For at least one unsupported matrix expression, `lambdify` or the printer must raise a clear exception rather than emitting ambiguous code. The exact exception type is an open question.
- Tests that need NumPy must be skipped when NumPy is not installed, following existing project conventions.
- Coverage expectations: unknown. Every new printer branch must be covered by at least one test.

## Boundaries

- **Always:**
  - Add regression tests reproducing the issue.
  - Run the existing printing and lambdify test suites before committing.
  - Keep printed code namespace-safe, so that no bare name can collide with `lambdify` globals.
- **Ask first:**
  - Changing the general fallback behavior for *all* unknown expressions, which could break existing users.
  - Changing the signature or argument semantics of `lambdify`, for example auto-adding dimension symbols as arguments.
  - Extending the fix to non-NumPy backends.
  - Adding dependencies.
- **Never:**
  - Change how scalar `I` (the imaginary unit) is printed or evaluated.
  - Silently emit code whose meaning depends on an ambiguous global name.
  - Remove or weaken existing tests.

## Success Criteria

1. `lambdify` with the NumPy backend, applied to `A + Identity(k)` with a concrete integer `k`, returns a function that, given a k×k array `a`, returns a value numerically equal to `a + numpy.eye(k)`.
2. The generated source for an expression containing `Identity` never references a bare `I`, or any other name that resolves to an unrelated object in the function's globals.
3. For the exact issue scenario (symbolic `n`), the outcome is one of the following, depending on the resolution of Open Question 1:
   - (a) the result `[[2, 2], [3, 5]]`, numerically, or
   - (b) a clear, descriptive error at `lambdify` or print time.

   It is never a complex-valued array.
4. At least one unsupported matrix expression type raises an informative error instead of being printed through the generic string fallback.
5. All existing printing and lambdify tests continue to pass.

## Open Questions

1. **Symbolic dimensions.** How should `Identity(n)` be handled when `n` is a free symbol not passed to the function? Options:
   - (a) raise an error;
   - (b) infer the size from another matrix argument's runtime shape, which is not generally well-defined;
   - (c) require `n` to be supplied as an argument.

   The issue's expected output implies the example should work, which conflicts with (a).
2. **Error scope.** Which "unsupported expressions that might be misinterpreted" must raise errors?
   - Only matrix expression types without a dedicated printer?
   - Any expression whose string form collides with a namespace name?
   - All expressions hitting the generic fallback?
3. **Exception type.** What exception should be raised for unsupported expressions? For example, a not-implemented style error, or the project's existing printer error convention.
4. **Backends.** Are other `lambdify` backends in scope (pure-Python/`math`, `mpmath`, SciPy, TensorFlow, others)? How should identity matrices print for each?
5. **Related matrix types.** Should related constant matrix expressions get the same treatment in this change, or be tracked separately? Examples are `ZeroMatrix`, `OneMatrix`, and other special matrices.
6. **Dtype.** Is a float result from `numpy.eye` acceptable, or must the result preserve the input array's dtype? (The issue shows an integer result.)
7. **Project details.** What are the exact test commands, file locations, and minimum supported Python and NumPy versions?