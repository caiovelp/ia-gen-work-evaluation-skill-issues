# Spec: LaTeX Printing of Sequences (`SeqFormula` and Related) Without Escaped Square Brackets

## Objective

**Problem.** In Jupyter, SymPy renders a sequence as LaTeX with backslash-escaped square brackets:

```python
import sympy as sp
k, m, n = sp.symbols('k m n', integer=True)
sp.init_printing()

sp.SeqFormula(n**2, (n, 0, sp.oo))
```

The current LaTeX output is:

```
\left\[0, 1, 4, 9, \ldots\right\]
```

In LaTeX, `\[` and `\]` mean "start/end display math". They are not bracket delimiters, so `\left\[` and `\right\]` are invalid as sized delimiters. The notebook output appears to display correctly, but pasting this string into a Markdown cell (MathJax/KaTeX) does not render. The unescaped form does render:

```
[0, 1, 4, 9, \ldots ]
```

**Goal.** The LaTeX printer should emit valid, portable LaTeX for sequences. Square-bracket delimiters must be written as `\left[` ... `\right]` (or plain `[` ... `]`), never `\left\[` ... `\right\]`.

**Users.** SymPy users who:
- copy LaTeX output from Jupyter into Markdown or other LaTeX documents, or
- consume `sp.latex(...)` output programmatically.

**Resolution of the issue's either/or question.** The printer should stop escaping the brackets. Changing how `\]` renders is a MathJax/Jupyter concern outside SymPy's control. Also, `\]` has standard LaTeX semantics that make the current output incorrect.

**Acceptance criteria:**
1. `sp.latex(sp.SeqFormula(n**2, (n, 0, sp.oo)))` returns a string containing `\left[` and `\right]`, and contains no `\left\[` and no `\right\]`.
2. The expected output for criterion 1 is `\left[0, 1, 4, 9, \ldots\right]`. The exact spacing and dots must be confirmed against current printer output; only the delimiters should change.
3. The returned string renders correctly in Jupyter Markdown cells (MathJax). Rendering in a standard LaTeX math environment is a secondary check.
4. The same fix applies to every sequence type that shares this printing path. Candidates include `SeqPer`, `SeqFormula`, `SeqAdd`, `SeqMul`, and finite or negative-start sequences (leading `\ldots`). The exact set is unknown and must be confirmed.
5. Existing tests that assert the old escaped form are updated to the new form. No unrelated printer output changes.

## Assumptions

1. The escaped brackets come from SymPy's LaTeX printer, specifically a sequence-printing method. They do not come from Jupyter, MathJax, or `init_printing` post-processing.
2. Jupyter's rich display uses the same LaTeX string as `sp.latex(...)`. Fixing the printer therefore fixes the notebook display.
3. `\left[` / `\right]` is the preferred replacement over bare `[` / `]`. This keeps auto-sizing consistent with other SymPy delimiters such as `\left(` and `\left\{`.
4. Other printers (str, pretty/unicode, MathML) are unaffected and out of scope.
5. Other SymPy objects that print square brackets (e.g., intervals, matrices, lists) may have the same bug. They are out of scope unless the same code path is involved, but they should be checked (see Open Questions).

## Tech Stack

- Python, SymPy (affected version unknown, not stated in the issue).
- Jupyter / IPython display with MathJax rendering (versions unknown).

## Commands

- Build: unknown (pure Python package; no build step stated).
- Test: unknown. Likely the project's pytest-based runner restricted to the LaTeX printing tests; exact command not visible.
- Lint: unknown.
- Manual reproduction: run the snippet from the Objective in Jupyter and in a plain Python session with `print(sp.latex(...))`.

## Project Structure

Unknown. Assumed but unverified:
- The LaTeX printer module lives under SymPy's printing package.
- Its tests sit in that package's test directory.

The exact file and function names must be located in the repository before planning.

## Code Style

Unknown from the issue. Follow the existing conventions of the LaTeX printer module, especially how other methods emit `\left` / `\right` delimiters.

## Testing Strategy

- **Unit tests** in the existing LaTeX printer test suite. Assert exact output strings for:
  - `SeqFormula` infinite on the right (the issue's example)
  - an infinite-on-the-left or negative-range sequence (leading `\ldots`)
  - a finite sequence
  - `SeqPer`
  - `SeqAdd` / `SeqMul`, if they share the code path
- **Regression guard:** a test asserting that `\left\[` and `\right\]` do not appear in sequence LaTeX output.
- **Manual check:** paste the output into a Jupyter Markdown cell and confirm it renders.
- **Coverage:** no specific target stated. All changed lines must be covered by the new or updated tests.

## Boundaries

- **Always:**
  - Keep the change limited to sequence delimiters in the LaTeX printer.
  - Update any existing tests that encode the old escaped form.
  - Run the printing test suite before committing.
- **Ask first:**
  - Changing delimiters for other bracketed objects (intervals, lists, matrices).
  - Switching from `\left[` to bare `[`.
  - Changing anything in str, pretty, or MathML printers.
  - Changing `init_printing` behaviour.
- **Never:**
  - Work around the bug in Jupyter or MathJax configuration.
  - Delete failing tests instead of updating them.
  - Change the sequence contents or `\ldots` placement.

## Success Criteria

- [ ] `sp.latex(sp.SeqFormula(n**2, (n, 0, sp.oo)))` contains `\left[` and `\right]`, and contains neither `\left\[` nor `\right\]`.
- [ ] Every sequence class that uses the shared printing path produces unescaped bracket delimiters, verified by unit tests.
- [ ] The output pasted into a Jupyter Markdown cell renders as `[0, 1, 4, 9, …]`.
- [ ] The full LaTeX printer test suite passes, with updated expectations only where the old escaped brackets appeared.
- [ ] No output changes for non-sequence objects.

## Open Questions

1. Which SymPy version is affected, and is this still reproducible on the current main branch?
2. Which sequence classes share the faulty code path (`SeqFormula`, `SeqPer`, `SeqAdd`, `SeqMul`, others)?
3. Is `\left[ … \right]` acceptable, or does the project prefer bare `[ … ]` for sequences?
4. Do other printers or objects emit `\left\[` / `\right\]` and need the same fix? Should that happen in this change or a follow-up?
5. Do any downstream consumers or doc examples depend on the current escaped output, making this a user-visible change worth a release note?