# Spec: Restore NDDataRef mask propagation when only one operand has a mask (astropy v5.3 regression)

## Objective

Fix a regression in astropy v5.3. NDData arithmetic fails during mask propagation when exactly one operand has a mask and `handle_mask` is a callable such as `np.bitwise_or`.

**Who is affected:** Users of `astropy.nddata.NDDataRef` (and any class using the same arithmetic mixin) who call `add`, `subtract`, `multiply` or `divide` with a custom `handle_mask` callable.

**Observed in v5.3:**
- `nref_mask.multiply(1., handle_mask=np.bitwise_or)` raises `TypeError: unsupported operand type(s) for |: 'int' and 'NoneType'`.
- `nref_mask.multiply(nref_nomask, handle_mask=np.bitwise_or)` raises the same error.

The reporter suspects that the operand without a mask is treated as a mask of `None` values, which is then passed to `bitwise_or`.

**Expected behavior (v5.2 parity):** When exactly one operand has a mask, the result's mask is a copy of the existing mask. `handle_mask` is not applied to a `None` mask.

**User stories:**
- As a user, I can multiply a masked `NDDataRef` by a scalar with `handle_mask=np.bitwise_or` and get the original mask back.
- As a user, I can combine a masked and an unmasked `NDDataRef` with `handle_mask=np.bitwise_or` and get the masked operand's mask back.
- As a user, existing behavior for "no mask with no mask" and "mask with mask" is unchanged.

## Assumptions

1. The regression is in the shared NDData arithmetic mask-handling logic, not specific to `multiply`. The fix is therefore expected to cover `add`, `subtract`, `multiply` and `divide`.
2. The v5.2 semantics are the intended contract:
   - If neither operand has a mask, the result mask is `None`.
   - If only one operand has a mask, the result mask is a (deep) copy of that mask.
   - If both have masks, the result mask is `handle_mask(mask1, mask2, **kwds)`.
3. The scalar operand case (`1.`) is internally wrapped into an NDData-like object with `mask=None`, and should follow the "only one operand has a mask" rule.
4. Order should not matter. Both "masked op unmasked" and "unmasked op masked" must work, including when the unmasked operand is on the left and the masked operand is passed as an argument.
5. Behavior when `handle_mask=None` (the result has no mask) and `handle_mask='first_found'` should remain as it is today. This is to be verified against v5.2.
6. The result mask should be a copy rather than a reference to the input mask, so that mutating the result does not affect the operand. This is assumed from v5.2 behavior and needs confirmation.
7. No public API signature changes are required.

## Tech Stack

- Python (the issue shows 3.10.11), NumPy (the issue shows 1.24.3), astropy v5.3 (the affected version).
- Exact minimum supported versions on the development branch: **unknown**.

## Commands

All unknown, because there is no repository access. They must be taken from the astropy contributor documentation or CI configuration.
- Build: unknown
- Test: unknown (likely pytest-based; exact invocation unknown)
- Lint: unknown
- Dev install: unknown

## Project Structure

Unknown without repository access. Relevant public API: `astropy.nddata.NDDataRef`. The internal module that implements arithmetic and mask handling is not shown in the issue, and its path is unknown. Test file locations are also unknown.

## Code Style

Unknown from the issue. Follow the existing astropy conventions in the touched module. No code snippet is available to cite.

## Testing Strategy

- **Framework:** Unknown, presumed pytest, as in the existing astropy test suite.
- **Level:** Unit tests on NDData arithmetic.
- **Regression tests to add** (reproducing the issue). For each arithmetic operation (`add`, `subtract`, `multiply`, `divide`) with `handle_mask=np.bitwise_or`:
  1. no mask op scalar → result mask is `None`
  2. no mask op no mask → result mask is `None`
  3. mask op scalar → result mask equals the original mask
  4. mask op mask → result mask equals `np.bitwise_or(mask, mask)`
  5. mask op no mask → result mask equals the original mask
  6. no mask op mask (reverse order) → result mask equals the original mask
- **Additional checks:**
  - The result mask in cases 3, 5 and 6 is not the same object as the input mask, if assumption 6 is confirmed.
  - Integer mask dtype is preserved.
  - Existing tests for the default `handle_mask` (`np.logical_or`), for `handle_mask=None`, and for `'first_found'` still pass.
- **Coverage expectations:** Unknown project threshold. The new branch(es) in the mask-handling logic must be covered.

## Boundaries

- **Always:**
  - Restore v5.2-equivalent semantics.
  - Add regression tests reproducing the issue's examples.
  - Run the existing nddata test suite.
  - Add a changelog entry per astropy convention (mechanism unknown).
- **Ask first:**
  - Changing the semantics of `handle_mask` beyond v5.2 parity (e.g., calling `handle_mask` with a synthesized all-zero/False mask).
  - Touching uncertainty, WCS or meta propagation.
  - Changing public signatures.
- **Never:**
  - Remove or weaken existing tests.
  - Special-case `np.bitwise_or` only; the fix must be generic to any `handle_mask` callable.
  - Change behavior of the mask-with-mask path.

## Success Criteria

1. With astropy built from the fix, every example in the issue runs without exception.
   - `nref_mask.multiply(1., handle_mask=np.bitwise_or).mask` equals `mask`.
   - `nref_mask.multiply(nref_nomask, handle_mask=np.bitwise_or).mask` equals `mask`.
2. `nref_nomask.multiply(nref_mask, handle_mask=np.bitwise_or).mask` equals `mask`.
3. Unmasked op unmasked/scalar still yields a `None` mask.
4. Masked op masked still yields `handle_mask(mask1, mask2)`.
5. The same holds for `add`, `subtract` and `divide`.
6. All new regression tests pass, and the existing nddata test suite passes with no modifications to existing tests.

## Open Questions

1. Which change between v5.2 and v5.3 introduced the regression? Identifying it would confirm the intended v5.3 behavior for other cases. Was it, for example, related to collapse operations or `operation_ignores_mask`?
2. Should the result mask be a deep copy of the existing mask, or may it share memory? What did v5.2 do exactly?
3. Should the fix be backported to a v5.3.x bugfix release? Which branch should it target?
4. Are there other `handle_mask` modes (e.g., `'first_found'`, `None`) or subclasses (`CCDData`, `NDDataArray`) with a dedicated code path that also needs verifying?
5. What are the exact test, build and lint commands, and what is the changelog procedure for this repository?
6. For reduction/collapse operations where `operand2` is absent, is current v5.3 behavior with a custom `handle_mask` correct, or does it share the same bug?