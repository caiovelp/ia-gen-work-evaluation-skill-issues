# Spec: Complete expansion of `TensorProduct` when factors carry scalar coefficients

## Assumptions

1. This is the SymPy project. The affected code is `TensorProduct._eval_expand_tensorproduct()` in `quantum/tensorproduct.py`. The issue names that path; I take the full path to be `sympy/physics/quantum/tensorproduct.py`, but I have not confirmed it against a checkout.
2. Root cause, as the reporter states it:
   - `TensorProduct.__new__` pulls commutative (scalar) factors out of its arguments.
   - When it does, it returns `Mul(c_factors, TensorProduct(...))` rather than a bare `TensorProduct`.
   - The recursion check in `_eval_expand_tensorproduct()` only recurses when the result is a `TensorProduct` instance, so it stops after the first `Add` factor.
3. `TensorProduct.__new__` can also return a non-`TensorProduct` value with no `TensorProduct` inside it. For example, `TensorProduct(U-U, U+V)` returns `0`. The fix must handle that case without errors.
4. The intended fix changes only `_eval_expand_tensorproduct()`. The `TensorProduct.__new__` constructor keeps its current behaviour, including pulling scalars out.
5. The output form for fully expanded expressions should not change. It should be a sum of terms, each a scalar coefficient times a `TensorProduct` of non-`Add` factors.
6. Other code that relies on `expand(tensorproduct=True)` should be fixed by this change without editing it. The issue names `qapply()`; there may be others.
7. The reporter's code fragment, which elides its surrounding loop with `...`, is a proposed direction. It is not a required implementation.

## Objective

`TensorProduct(...).expand(tensorproduct=True)` must fully distribute over **every** tensor factor that is an `Add`, in a single call. This must hold even when the factors' summands have scalar coefficients.

Current behaviour, quoted from the issue:

```python
from sympy import *
from sympy.physics.quantum import *
U = Operator('U')
V = Operator('V')
P = TensorProduct(2*U - V, U + V)
print(P.expand(tensorproduct=True))
# actual:   2*Ux(U + V) - Vx(U + V)        (second factor not expanded)
```

Expected behaviour:

```
2*UxU + 2*UxV - VxU - VxV                  (order/printing may differ)
```

**Users affected:**
- Users of `sympy.physics.quantum` who expand tensor products.
- Users of code that depends on that expansion, such as `qapply()`.

**Current workaround:** call `.expand(tensorproduct=True)` repeatedly until the result stops changing. That is not acceptable inside algorithms.

**Success means:** one call to `expand(tensorproduct=True)` returns a result that does not change if you call it again (a fixed point).

## Tech Stack

- Python, SymPy, and specifically the `sympy.physics.quantum` subpackage.
- The supported Python and SymPy versions are not known from the issue.

## Commands

The exact commands are not known. I have no repository access and the issue does not give them. These are the commands I would use for a SymPy project; confirm them before relying on them:

| Purpose | Command |
|---|---|
| Test | **unknown**; likely the SymPy test runner pointed at the quantum tensorproduct tests |
| Lint | **unknown** |
| Build | **unknown**; a pure-Python change, so a build step is probably not needed |

## Project Structure

| Path | Status |
|---|---|
| `quantum/tensorproduct.py` (presumed `sympy/physics/quantum/tensorproduct.py`) | Location of `TensorProduct.__new__` and `TensorProduct._eval_expand_tensorproduct` |
| Tests for tensorproduct | **Unknown path**; presumed to sit in a `tests/` directory next to the module, e.g. `sympy/physics/quantum/tests/test_tensorproduct.py` (unconfirmed) |
| Tests for `qapply` | **Unknown path** |

## Code Style

- Follow the existing style of `tensorproduct.py`. I cannot see it.
- The only code shown in the issue is the reporter's proposed fragment. It uses:
  - `args_cnc()`, to split commutative from non-commutative parts;
  - `Mul(*c_part) * Mul(*nc_part)`, to rebuild each term.
- No other style conventions are known.

## Testing Strategy

- **Framework:** SymPy's existing test framework. The runner command is unknown (see Commands).
- **Level:** unit tests against `TensorProduct` expansion, plus at least one regression test through `qapply()`, because the issue names it as affected.
- **Required regression cases:**
  1. `TensorProduct(2*U - V, U + V).expand(tensorproduct=True)` equals `2*TP(U,U) + 2*TP(U,V) - TP(V,U) - TP(V,V)`.
  2. Three or more tensor factors, each an `Add` with scalar coefficients. All factors must expand fully in one call.
  3. A factor that is zero after construction, e.g. `TensorProduct(U - U, U + V)`. Expansion returns `0` without raising.
  4. A purely scalar overall coefficient, e.g. `TensorProduct(3*U, U + V)`. The coefficient is kept and the `Add` factor is expanded.
  5. Inputs with no scalar coefficients, e.g. `TensorProduct(U + V, U + V)`. The output must be the same as before the fix (non-regression).
  6. Idempotence: for every case above, `e.expand(tensorproduct=True)` is equal to `e.expand(tensorproduct=True).expand(tensorproduct=True)`.
  7. A `qapply()` case whose correct result depends on full tensor-product expansion. The specific input is unknown; see Open Questions.
- **Coverage:** every new branch in `_eval_expand_tensorproduct()` is exercised:
  - the result contains a `TensorProduct`;
  - the result is a scalar times a `TensorProduct`;
  - the result contains no `TensorProduct` (e.g. `0`).

## Boundaries

- **Always:**
  - Add the regression tests above alongside the fix.
  - Run the existing quantum test suite before submitting.
  - Keep the change local to `_eval_expand_tensorproduct()`.
- **Ask first:**
  - Changing `TensorProduct.__new__`, including how it pulls out scalars or returns `Mul`/`0`.
  - Changing the printed or canonical form of expanded results.
  - Touching `qapply()` or other callers directly.
  - Changing how expansion treats non-commutative coefficients.
- **Never:**
  - Change the public signature of `expand` or its `tensorproduct` hint.
  - Hide the bug by having callers loop `expand`; that is the workaround, not the fix.
  - Delete or weaken existing tests.

## Success Criteria

1. Cases 1 through 6 in Testing Strategy pass.
2. A single `expand(tensorproduct=True)` call on any `TensorProduct` returns an expression containing no `TensorProduct` with an `Add` among its arguments.
3. `TensorProduct(U - U, U + V).expand(tensorproduct=True)` returns `0` without an exception.
4. All existing tests in the quantum subpackage pass. The test command is unknown.
5. At least one `qapply()` regression test that failed or gave an incompletely expanded result before the fix now passes.

## Open Questions

1. What are the exact repository paths, and the commands to run the quantum tests and the linter?
2. Can someone give a concrete `qapply()` input that shows the bug, to use as the regression test (case 7)?
3. Can tensor factors include non-commutative scalar-like coefficients, or anything other than operators and commutative scalars? The fix assumes the `TensorProduct` is the only non-commutative factor in each term. Does that hold for every input `TensorProduct.__new__` can produce?
4. Is the reporter's fragment correct when the constructor returns a `Mul` with a `TensorProduct` and also other non-commutative factors? The fragment only recurses when `len(nc_part) == 1`; what happens otherwise?
5. Should the fix also handle nested `TensorProduct`s, or `Add`s that only appear after recursive expansion, or is that out of scope?
6. Is a fixed ordering of terms or printed form expected in the output, or is symbolic equality enough for the tests?
7. Do other code paths have the same check, "the constructor result is a `TensorProduct` instance"? Possible places are other `_eval_expand_*` methods or `tensor_product_simp`. Should they be fixed in the same change?