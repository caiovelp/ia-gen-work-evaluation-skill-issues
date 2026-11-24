# Spec: Correct Summation over Elements of a Symbolic Identity Matrix

## Objective

When a symbolic `n×n` identity matrix comes out of `refine((M.T * M).doit())` under `Q.orthogonal(M)`, summing all of its elements gives `0`. The correct answer is `n`. This spec defines correct behavior for symbolic-index element access and summation on such identity matrices, so the result matches the mathematical definition.

**Users:** SymPy users who do symbolic linear algebra with `MatrixSymbol`, assumptions (`assuming`, `refine`, `ask`) and `Sum` over symbolic matrix entries.

**What the reporter observed:**

| Expression | Observed | Expected | Status |
|---|---|---|---|
| `e` (refined `M.T*M`) | identity matrix | identity matrix | correct |
| `e[0,0], e[0,1], e[1,0], e[1,1]` | `1, 0, 0, 1` | `1, 0, 0, 1` | correct |
| `ask(Q.diagonal(e))`, `ask(Q.integer_elements(e))` | `True True` | `True True` | correct |
| `Sum(e[i, i], (i, 0, n-1)).doit()` | `n` | `n` | correct |
| `Sum(Sum(e[i, j], (i, 0, n-1)), (j, 0, n-1)).doit()` | `0` | `n` | **bug** |

**Suspected symptom (unverified):** with symbolic indices `i`, `j` that are not structurally identical, `e[i, j]` seems to evaluate eagerly to `0`. Only the diagonal access `e[i, i]` evaluates to `1`. That would make the inner sum zero before any summation logic runs. This must be confirmed before any fix is designed. See Open Questions.

**User story:** As a SymPy user, I want `e[i, j]` with symbolic `i`, `j` on an identity matrix to keep the information that the entry is `1` when `i == j` and `0` otherwise. Then sums, and other expressions built from it, give mathematically correct results.

## Assumptions

1. The project is SymPy. The bug is in the library, not in the user's script.
2. The refined object `e` is, or behaves as, SymPy's `Identity(n)` matrix expression. The issue prints `e` but does not show its type.
3. The root cause is element access (`e[i, j]` with symbolic, possibly unequal indices), not `Sum.doit()` itself. This is inferred from the diagonal sum being correct, and is unverified.
4. Concrete-index access (`e[0,1] == 0`, `e[1,1] == 1`) is correct and must not change.
5. A result equal to `n` after simplification is acceptable, even if the raw output contains an intermediate form such as `Piecewise` or a delta-like term. This is pending confirmation (Open Question 2).
6. The integer and range assumptions on `i`, `j`, `n` are as written in the issue: `n` positive integer, `i`, `j` integers, summation ranges `0..n-1`.
7. Mathematically, the inner sum over `i` should be `1` for every `j` in range. Summing the other order (`j` inner, `i` outer) must also give `n`.
8. The Python version, SymPy version, and the code locations involved are unknown.

## Tech Stack

- Language: Python (version unknown).
- Library: SymPy (affected version unknown, not stated in the issue).
- Relevant public APIs from the issue: `Symbol`, `symbols`, `MatrixSymbol`, `Q` / `ask`, `assuming`, `refine`, `Sum`, `.doit()`, matrix transpose `.T` and matrix multiplication `*`.

## Commands

Unknown. The issue does not show the build, test or lint commands, and the repository is not visible.

- Build: unknown
- Test: unknown (likely the project's standard test runner; to be confirmed)
- Lint: unknown
- Reproduce: run the script from the issue with Python. The exact invocation is unknown.

## Project Structure

Unknown. Repository layout is not visible. The areas likely involved, by concept rather than path, are:

- Identity matrix expression and its element-access logic
- Matrix expression `refine` and orthogonality handlers
- `Sum` evaluation (`doit`) for nested sums

Exact file paths must be determined by inspecting the repository.

## Code Style

Not determinable from the issue. Follow the existing conventions of the surrounding SymPy code. The only real code available is the reproduction from the issue, which should become the basis of a regression test:

```python
from sympy import *
from sympy import Q as Query

n = Symbol('n', integer=True, positive=True)
i, j = symbols('i j', integer=True)
M = MatrixSymbol('M', n, n)

with assuming(Query.orthogonal(M)):
    e = refine((M.T * M).doit())

assert Sum(e[i, i], (i, 0, n-1)).doit() == n
assert Sum(Sum(e[i, j], (i, 0, n-1)), (j, 0, n-1)).doit() == n  # currently returns 0
```

## Testing Strategy

- **Framework:** the project's existing test framework (name and location unknown).
- **Regression test:** the issue reproduction above, asserting the double sum equals `n`.
- **Unit-level tests for element access on a symbolic identity matrix:**
  - Concrete indices: `e[0,0] == 1`, `e[0,1] == 0`, `e[1,0] == 0`, `e[1,1] == 1`. Must stay unchanged.
  - Identical symbolic indices: `e[i, i] == 1`.
  - Distinct symbolic indices: `e[i, j]` must not evaluate unconditionally to `0`. Substituting `j -> i` must give `1`. Substituting distinct concrete values must give `0`.
- **Summation tests:**
  - Diagonal sum `Sum(e[i,i], (i,0,n-1))` equals `n`. Must not regress.
  - Double sum in both nesting orders equals `n`.
  - Inner sum alone, `Sum(e[i, j], (i, 0, n-1))`, equals `1` for `j` in range. The form is subject to Open Question 2.
  - Optional: the same checks on a directly constructed identity matrix of symbolic size, to confirm the behavior does not depend on the `refine` path.
  - Optional: a concrete size (e.g. `n = 3`) giving `3`.
- **Existing tests:** the full matrix-expression and summation test suites must still pass.
- **Coverage expectation:** unknown project policy. At minimum, every success criterion below has a test.

## Boundaries

- **Always:**
  - Reproduce the bug before changing anything.
  - Add a regression test built from the issue.
  - Preserve correct concrete-index behavior.
  - Run the relevant existing test suites.
- **Ask first:**
  - Changing the public representation of symbolic identity entries, e.g. what type `Identity(n)[i, j]` returns.
  - Changing `Sum` evaluation semantics in general.
  - Extending the change to other structured matrices (zero, diagonal, etc.).
  - Adding dependencies.
- **Never:**
  - Special-case the exact expression from the issue.
  - Weaken or delete existing tests to make the new one pass.
  - Return a result that is wrong for some valid assignment of `i`, `j` (e.g. unconditionally `0` or `1` for distinct symbols).

## Success Criteria

1. `Sum(Sum(e[i, j], (i, 0, n-1)), (j, 0, n-1)).doit()` equals `n`, directly or after `simplify`, for `e` produced as in the issue.
2. The same holds with the summation order swapped.
3. `Sum(e[i, i], (i, 0, n-1)).doit()` still equals `n`.
4. For symbolic indices `i`, `j` with no known relation, `e[i, j]` is not unconditionally `0`. Substituting equal values gives `1`, and substituting unequal concrete values gives `0`.
5. Concrete-index entries are unchanged: `e[0,0]=1`, `e[0,1]=0`, `e[1,0]=0`, `e[1,1]=1`.
6. `ask(Q.diagonal(e))` and `ask(Q.integer_elements(e))` still return `True`.
7. No existing tests regress.

## Open Questions

1. **Root cause confirmation:** Does `e[i, j]` with distinct symbolic indices really evaluate to `0`, or does the error come from `Sum.doit()` or from `refine`? What is `type(e)`?
2. **Acceptable output form:** Must the double sum return exactly `n`, or is an equivalent form (e.g. `Piecewise` or a delta-based expression that simplifies to `n`) acceptable? Same question for the inner single sum.
3. **Entry representation:** What is the preferred symbolic representation of an identity entry at unequal symbolic indices? Is changing it acceptable for backward compatibility?
4. **Scope:** Should this cover only the identity matrix, or also audit similar eager evaluation in other structured matrix expressions (zero matrix, diagonal matrices, refined results of other assumptions)?
5. **Index assumptions:** If `i` or `j` are known to be unequal, or known to be out of range, should element access use that? What should happen when indices may fall outside `0..n-1`?
6. **Versions:** Which SymPy and Python versions are affected and must be supported by the fix?
7. **Project specifics:** What are the test commands, test file locations and coverage requirements? None are visible.