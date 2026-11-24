# Spec: Compilable LaTeX for Indexed Matrix Products

## Objective

`latex()` should produce valid, compilable LaTeX for an element of a matrix-expression product, such as `(M*N)[i, j]`.

Reproduction from the issue:

```python
i, j, k = symbols("i j k")
M = MatrixSymbol("M", k, k)
N = MatrixSymbol("N", k, k)
latex((M*N)[i, j])
```

Current output:

```
\sum_{i_{1}=0}^{k - 1} M_{i, _i_1} N_{_i_1, j}
```

The subscripts contain `_i_1`. LaTeX rejects this with a "double subscript" error, and MathJax will not render it either. The summation bound already prints the same index correctly as `i_{1}`. That points to the element subscripts formatting the summation (dummy) index differently from the rest of the LaTeX printer, apparently with a raw, non-LaTeX representation that includes a leading underscore. This is unconfirmed.

**Users:** anyone who renders SymPy matrix-expression results as LaTeX, for example in Jupyter/MathJax, documentation, or papers.

**Desired output** (exact form subject to Open Questions):

```
\sum_{i_{1}=0}^{k - 1} M_{i, i_{1}} N_{i_{1}, j}
```

## Tech Stack

- Python, SymPy. The affected SymPy version is not stated in the issue (unknown).
- Components involved, by API name: `latex()` (LaTeX printer), `MatrixSymbol`, matrix-product element access (`MatMul` indexing producing a `Sum` over a dummy index), and `MatrixElement` printing.
- Exact source files: unknown (no repository access).

## Commands

Unknown. The issue gives no build, test, or lint commands. Use the project's standard test runner and confirm the invocation with the maintainers.

## Project Structure

Unknown. The locations of the LaTeX printer source and its tests are not visible in the issue.

## Code Style

Unknown. Follow the existing conventions in the LaTeX printer module and its test file. Tests should assert the exact expected LaTeX string, in the style of existing printer tests.

## Testing Strategy

- **Unit tests** for the LaTeX printer, asserting exact output strings for:
  - The issue's reproduction: `latex((M*N)[i, j])`.
  - Element subscripts containing a `Dummy` symbol, so they print in LaTeX form (`i_{1}`) and never with a leading `_`.
  - Element subscripts with plain symbols and integers (`M[i, j]`, `M[0, 1]`), which must stay unchanged (regression guard).
  - Element subscripts containing compound expressions (e.g. `M[i + 1, j]`), which must print as valid LaTeX.
  - Longer products (e.g. `(M*N*P)[i, j]`) that introduce several dummy indices, so that each index prints consistently in the summation bounds and in the subscripts.
- **Validity check (recommended):** where tooling allows, confirm the generated strings contain no `_` directly after `{`, `,`, or `_` without braces. Optionally compile them with a LaTeX engine or render them in MathJax, outside the unit suite if that tooling isn't available.
- Coverage expectation: unknown. Follow project norms.

## Boundaries

- **Always:** Keep the summation-bound index and the subscript index rendered identically. Add regression tests for the exact issue example. Run the existing printer test suite before committing.
- **Ask first:**
  - Changing how `Dummy` symbols print in general, in LaTeX or in other printers such as `str`.
  - Changing the output for non-dummy matrix elements.
  - Changing the dummy-index naming scheme (e.g. `i_1`) produced by matrix-product indexing.
- **Never:** Change the `str`/`repr` output of these expressions as a side effect. Weaken or remove existing printer tests. Paper over the problem with string post-processing (e.g. stripping `_`) instead of printing the indices through the LaTeX printer.

## Success Criteria

1. `latex((M*N)[i, j])` returns a string with no double-subscript constructs. The expected value is `\sum_{i_{1}=0}^{k - 1} M_{i, i_{1}} N_{i_{1}, j}`, subject to Open Question 1.
2. The dummy index renders identically in the `\sum` bound and in every matrix subscript.
3. The output compiles under standard LaTeX (amsmath) and renders in MathJax.
4. All matrix-element subscripts (symbols, integers, expressions, dummies) are rendered by the LaTeX printer, not by a plain string representation.
5. Existing LaTeX printer tests pass unchanged, unless a change is explicitly approved.
6. `str()` output for the same expression is unchanged.

## Assumptions

1. The bug is in how `MatrixElement` (matrix-entry) subscripts are printed in LaTeX. They appear to use a plain string form of the index (where `Dummy` shows a leading `_`) instead of the LaTeX printer.
2. The summation bound output `i_{1}` is correct and is the target format for the subscripts.
3. The internal dummy name `i_1` and the summation range `0` to `k - 1` are correct and in scope only as far as printing goes.
4. The fix targets the LaTeX printer. Other printers (pretty, MathML, str) are out of scope unless they show the same defect.
5. A comma-separated subscript style (`M_{i, j}`) is the established format and should be kept.

## Open Questions

1. What exactly should the dummy index look like in output: `i_{1}` (matching the current `\sum` bound), or something else such as `i_1` or a distinct glyph that marks it as a bound variable?
2. Should other printers (pretty printer, MathML, code printers) be checked for the same `Dummy`-subscript defect, and fixed in this change or tracked separately?
3. Which SymPy version(s) are affected, and does the fix need backporting?
4. Should compound subscripts (e.g. `M[i + 1, j]`) get any extra formatting, such as parentheses or spacing, or just whatever the LaTeX printer produces by default?
5. What are the project's test commands, and where are the relevant source and test files? (Unknown from the issue.)