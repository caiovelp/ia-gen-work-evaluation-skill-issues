# Spec: MathML Printing Support for `Indexed` and `IndexedBase`

## Assumptions

1. **Affected code.** The bug is in the MathML printer at `sympy/printing/mathml.py`, as shown in the traceback. The reported version is `1.0.1.dev` and the class involved is `MathMLPrinter`. The current codebase may have changed since then (for example, it may have split into content and presentation printers). Treat the printer class structure as **unknown** until it is checked.
2. **Root cause.** `Indexed` has no dedicated `_print_Indexed` method. It falls through to `_print_Basic`, which runs `for arg in e:`. That loop iterates the expression itself, not `e.args`. `Indexed` is not iterable, so a `TypeError` is raised.
3. **Scope.** The fix covers both `Indexed` (e.g. `IndexedBase(a)[b]`) and `IndexedBase` (the title says "IndexedBase"). `Idx` objects used as indices are also in scope where they reach the MathML printer.
4. **All MathML printers.** If the codebase now has more than one MathML printer (content and presentation), every one of them should handle `Indexed` and `IndexedBase`.
5. **Expected output.**
   - **Presentation MathML:** `Indexed` renders as a subscript of the base label with the indices: `<msub>` with base `a` and index `b`. Multiple indices are grouped in an `<mrow>`.
   - **Content MathML:** `Indexed` renders using the standard `<selector/>` construct: `<apply><selector/>base indices…</apply>`.
   - **`IndexedBase` alone:** renders as its label, the same as the equivalent `Symbol`.
6. **Composite expressions.** Expressions that contain `Indexed` (sums, products, powers, function arguments, etc.) must print without error. They should need no special handling beyond correct `Indexed` printing.
7. **`_print_Basic` iteration.** It is unclear whether `_print_Basic` iterating over `e` instead of `e.args` is itself a bug that affects other types. It is recorded as an open question, not assumed to be in scope.

## Objective

Make `sympy.printing.mathml(expr)` produce valid MathML for any expression containing `Indexed` or `IndexedBase` objects, instead of raising `TypeError: 'Indexed' object is not iterable`.

**User:** SymPy users exporting symbolic expressions with indexed quantities (tensors, sequences, array elements) to MathML for display or interchange.

**User stories / acceptance criteria:**
- As a user, `mathml(IndexedBase(a)[b])` returns a MathML string and does not raise.
- As a user, `mathml(IndexedBase(a)[b, c])` (multiple indices) returns a MathML string containing the base and both indices.
- As a user, `mathml(IndexedBase(a))` returns a MathML string representing the label `a`.
- As a user, more complex expressions such as `IndexedBase(a)[b] + 1`, `2*IndexedBase(a)[b]**2`, and `sin(IndexedBase(a)[b])` print without error.
- The output encodes the base label and the indices in the correct order.

## Tech Stack

- Python (the traceback shows a Python 3.5 environment; currently supported versions are **unknown**)
- SymPy. Relevant modules from the traceback:
  - `sympy/printing/mathml.py`: `MathMLPrinter`, `mathml()`, `_print_Basic`
  - `sympy/printing/printer.py`: `Printer._print` dispatch via `_print_<ClassName>`
- `sympy.tensor.indexed`: `Indexed`, `IndexedBase`, `Idx` (module location assumed from SymPy's public API; not verified)
- XML DOM (`mathML.toxml()` in the traceback suggests `xml.dom.minidom`; **unverified**)

## Commands

The project's build, test and lint commands are not visible in the issue.

```
Build: unknown
Test:  unknown (project test runner and invocation not shown in the issue)
Lint:  unknown
Dev:   n/a
```

Reproduction, taken directly from the issue:

```python
import sympy
from sympy.abc import a, b
sympy.printing.mathml(sympy.IndexedBase(a)[b])
# currently: TypeError: 'Indexed' object is not iterable
```

## Project Structure

Only the following paths are known from the traceback:

```
sympy/printing/mathml.py   → MathML printer (location of the bug)
sympy/printing/printer.py  → Base Printer and _print dispatch
```

Location of MathML printer tests: **unknown**.

## Code Style

- Follow the existing printer convention: add a dedicated `_print_<ClassName>` method on the MathML printer class(es). `Printer._print` dispatches on `'_print_' + cls.__name__`, as the traceback shows.
- Build output with the printer's existing DOM helpers (e.g. `self.dom.createElement(...)`, `appendChild`, `self._print(sub)`), matching the surrounding methods.
- No other style details are visible in the issue; match the surrounding code in `mathml.py`.

## Testing Strategy

- **Framework / location:** unknown. Use whatever the existing MathML printer tests use.
- **Unit tests (required):**
  - `Indexed` with a single `Symbol` index: no exception, and the output contains the expected elements (per Assumption 5) with base and index in order.
  - `Indexed` with multiple indices.
  - `Indexed` with `Idx` indices.
  - `IndexedBase` alone.
  - Composite expressions containing `Indexed` (Add, Mul, Pow, function application).
  - The same cases for each MathML printer variant, if more than one exists.
- **Regression test:** the exact reproduction from the issue.
- **Coverage:** every new `_print_*` method is exercised by at least one test.

## Boundaries

- **Always:**
  - Add regression tests reproducing the issue.
  - Run the existing MathML printer tests to confirm no regressions.
  - Follow existing `_print_<ClassName>` dispatch conventions.
- **Ask first:**
  - Changing `_print_Basic`'s generic behaviour (e.g. iterating `e.args` instead of `e`). This affects every type without a dedicated printer.
  - Changing the output format of existing types.
  - Adding new dependencies.
  - Changing the public `mathml()` signature or settings.
- **Never:**
  - Remove or weaken existing tests.
  - Silence the error, e.g. by catching `TypeError` and returning an empty or placeholder element.
  - Change `Indexed` or `IndexedBase` class behaviour (such as making them iterable) just to satisfy the printer.

## Success Criteria

1. `sympy.printing.mathml(sympy.IndexedBase(a)[b])` returns a string and raises no exception.
2. The output contains the base label `a` and index `b`, structured as agreed (see Assumption 5 and Open Questions).
3. Multi-index `Indexed`, `Indexed` with `Idx` indices, standalone `IndexedBase`, and composite expressions containing `Indexed` all print without error.
4. Every MathML printer variant in the codebase (content and/or presentation) satisfies criteria 1–3.
5. New tests covering the above pass, and the existing MathML printer test suite still passes.
6. The output is well-formed XML, i.e. it can be parsed by an XML parser.

## Open Questions

1. **Printer variants.** Does the current codebase still have a single `MathMLPrinter`, or separate content and presentation printers? Should all variants be fixed?
2. **Content MathML encoding.** Is `<apply><selector/>base idx…</apply>` the desired representation for `Indexed`, or is something else preferred (e.g. a `<ci>` with a subscripted presentation)?
3. **Presentation MathML encoding for multiple indices.** Should multiple indices be shown as `<msub>` with an `<mrow>` of comma-separated indices, or concatenated without separators?
4. **`IndexedBase` with shape or other attributes.** Should anything beyond the label be rendered (e.g. shape information)? Assumed no.
5. **`_print_Basic`.** It iterates over `e` rather than `e.args`. Is that a separate latent bug affecting other non-iterable `Basic` subclasses, and should it be fixed in this change or tracked separately?
6. **Supported Python/SymPy versions, and the test command,** for the target branch.