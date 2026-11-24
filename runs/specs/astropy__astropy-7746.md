# Spec: Empty Input Handling in WCS Transformations

## Objective

Calling a WCS transformation with empty coordinate inputs raises an error. It should return empty output instead.

**Reproduction (from the issue):**

```python
from astropy.wcs import WCS
wcs = WCS('2MASS_h.fits')
wcs.wcs_pix2world([], [], 0)
# InconsistentAxisTypesError: ERROR 4 in wcsp2s() at line 2646 of file
# cextern/wcslib/C/wcs.c: ncoord and/or nelem inconsistent with the wcsprm.
```

**Expected:** The call succeeds and returns empty lists/arrays, one per world axis.

**Root cause path (from the traceback):**
`WCS.wcs_pix2world` → `WCS._array_converter` → inner `_return_list_of_arrays` → `func(xy, origin)` → `self.wcs.p2s(xy, o)['world']` → wcslib `wcsp2s()`. The wcslib C routine rejects `ncoord == 0`. The empty input reaches the C layer without being short-circuited.

**Users:** Astropy users who transform coordinate collections that may legitimately be empty, such as filtered source lists or masked selections. Today they must special-case empty input themselves.

**User stories / acceptance:**
- As a user, when I call `wcs.wcs_pix2world([], [], 0)`, I get empty results rather than an exception.
- As a user, when I pass an empty array in the single-array form (shape `(0, naxis)`), I get an empty array of shape `(0, naxis)` rather than an exception.
- As a user, empty input behaves the same across all public transformation methods routed through `_array_converter`.

## Assumptions

1. The fix belongs in the Python layer (`astropy/wcs/wcs.py`, `_array_converter` and/or its inner helpers), not in vendored wcslib (`cextern/wcslib`).
2. "Empty" means zero coordinates (length-0 per-axis arrays, or an `(0, naxis)` array). It does not mean a wrong number of axes. Passing the wrong number of axes should still raise the existing errors.
3. All public methods that delegate to `_array_converter` share this bug. Examples include `wcs_pix2world`, `wcs_world2pix`, `all_pix2world`, `all_world2pix`, and the SIP/distortion helpers. All of them should get the same empty-input behavior. Only `wcs_pix2world` is shown in the issue.
4. Output types for empty input should mirror non-empty input:
   - **List-of-arrays form:** a list of `naxis` empty `ndarray`s, each with the same shape as the input arrays (e.g. `(0,)`).
   - **Single-array form:** an `ndarray` of shape `(0, naxis)`.
5. Output dtype should be float, matching the normal output.
6. The `ra_dec_order=True` path should return empty results too, in the same `(ra, dec)` tuple structure it normally uses.
7. Inputs with zero size but more than one dimension (e.g. shape `(0, 3)` per axis, if broadcasting allows it) should keep their input shape in the output.
8. `origin` validation and axis-count validation still run for empty input. Empty input does not bypass argument checking.

## Tech Stack

- Python package `astropy`, subpackage `astropy.wcs`
- NumPy arrays
- Vendored C library wcslib (`cextern/wcslib`), accessed through the `Wcsprm.p2s` / `s2p` wrappers
- Versions: **unknown**

## Commands

All unknown. They are not visible in the issue.

- Build: unknown
- Test: unknown (presumably a pytest invocation scoped to `astropy/wcs`, exact command unknown)
- Lint: unknown
- Dev: unknown

## Project Structure

Known from the traceback:

```
astropy/wcs/wcs.py      → WCS class; _array_converter, wcs_pix2world, etc.
cextern/wcslib/C/wcs.c  → vendored wcslib; wcsp2s() raises the error
```

Test location: **unknown** (likely under `astropy/wcs/tests/`, unconfirmed).

## Code Style

Unknown beyond what is visible in the traceback. Follow the existing conventions in `astropy/wcs/wcs.py`. No snippet is provided, to avoid inventing code.

## Testing Strategy

- **Framework:** unknown (assumed pytest, consistent with astropy).
- **Levels:** unit tests on `WCS` transformation methods. A FITS header fixture or a programmatically constructed `WCS` is preferred over the user's `2MASS_h.fits`, which may not exist in the repository.
- **Required test cases:**
  - Each public transformation method receives empty per-axis lists. It returns `naxis` empty arrays.
  - Each public transformation method receives an empty `(0, naxis)` array. It returns an empty `(0, naxis)` array.
  - The `ra_dec_order=True` variant receives empty input. It returns an empty `(ra, dec)` result.
  - Regression: empty input with the wrong number of axes still raises the existing error.
  - Regression: existing non-empty transformation tests stay green.
- **Coverage expectations:** unknown. At minimum, the new empty-input branch must be exercised for both input forms.

## Boundaries

- **Always:**
  - Keep return types and shapes consistent between empty and non-empty input.
  - Keep existing argument validation.
  - Add regression tests.
  - Run the existing `astropy.wcs` test suite.
- **Ask first:**
  - Modifying vendored wcslib in `cextern/`.
  - Changing the public return types of any transformation method.
  - Extending the change to `Wcsprm.p2s` / `s2p` directly, since that is a lower-level public API.
- **Never:**
  - Swallow genuine errors by catching `InconsistentAxisTypesError` broadly.
  - Remove or weaken existing tests.
  - Change behavior for non-empty input.

## Success Criteria

1. `wcs.wcs_pix2world([], [], 0)` returns a list of 2 empty float arrays for a 2-axis WCS, without raising.
2. `wcs.wcs_pix2world(np.empty((0, 2)), 0)` returns a float array of shape `(0, 2)`.
3. Criteria 1 and 2 hold for every public method routed through `_array_converter`, including `wcs_world2pix`, `all_pix2world`, and `all_world2pix`.
4. Empty input with `ra_dec_order=True` returns an empty result in the normal `(ra, dec)` structure.
5. Malformed input (wrong axis count, missing origin) raises the same errors as before.
6. All existing `astropy.wcs` tests pass.

## Open Questions

1. Should the guard live in `_array_converter`, applying to all methods, or only in specific methods? (Assumed: `_array_converter`.)
2. Should `Wcsprm.p2s` / `s2p` and other low-level wrappers also accept empty input, or only the high-level `WCS` methods?
3. What exact output type is expected for empty list input: Python lists or NumPy arrays? The issue says "lists/arrays". Non-empty input currently returns arrays.
4. Are there iterative methods (e.g. `all_world2pix` with its convergence options) where empty input needs special handling of keyword arguments such as `quiet` or `detect_divergence`?
5. Should zero-size inputs with extra dimensions (e.g. shape `(0, 3)`) preserve their shape? Is that case supported at all?
6. Which test command and test file should be used, and is there an existing FITS fixture that matches the `2MASS_h.fits` case?
7. Should this be backported to maintenance branches? Does it need a changelog entry?