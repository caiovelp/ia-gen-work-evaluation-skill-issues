# Spec: LaTeX printing for matrix `Trace` expressions

## Objective

Calling `latex()` on a `Trace` of a matrix expression returns a plain-text string. Both the operator name and its argument come out wrong:

```py
>>> A = MatrixSymbol("A", n, n)
>>> latex(trace(A**2))
'Trace(A**2)'
```

The issue reports two defects:

1. **`Trace` has no LaTeX rendering.** The LaTeX printer does not recognize the `Trace` node and emits its class name.
2. **The argument is not printed as LaTeX.** The inner expression `A**2` is rendered in string/Python syntax, not as LaTeX (`A^{2}`). Whatever path handles `Trace` does not hand its arguments back to the LaTeX printer.

**Users:** Anyone using SymPy's `latex()` on matrix expressions, such as notebook rendering, documentation and papers.

**Desired outcome:** `latex(trace(A**2))` returns a proper LaTeX trace operator wrapping the LaTeX form of the argument. A candidate output is `\operatorname{tr}\left(A^{2} \right)`, but the exact notation is an open question. Every sub-expression inside the trace must be printed by the LaTeX printer.

### Acceptance criteria
- AC1: `latex(trace(A**2))` produces a LaTeX trace operator applied to `A^{2}`. The output contains no `Trace(`, no `**`, and no Python-style syntax.
- AC2: `latex(trace(A))` produces the trace operator applied to `A`.
- AC3: Nested or compound arguments are fully LaTeX-printed. Examples include `trace(A*B)`, `trace(A + B)`, `trace(A.T)` and `trace(A**-1)`.
- AC4: The argument is delimited unambiguously, using parentheses or the equivalent.
- AC5: LaTeX output for other matrix expressions is unchanged, with no regressions in existing printing tests.
- AC6 (conditional): If the investigation shows that the "no fallback to LaTeX for inner expressions" behaviour is a generic fallback path, the spec owner decides whether to fix it generically. See Open Questions. At minimum, `Trace` must not hit that path.

## Assumptions
1. This is the SymPy library. `latex`, `trace` and `MatrixSymbol` are SymPy public APIs, and `n` is a SymPy `Symbol`.
2. `trace(A**2)` returns an unevaluated `Trace` object, since `A` is symbolic. The defect is purely in printing, not in construction or evaluation.
3. The LaTeX printer falls back to a generic or string-based representation for classes it has no handler for. This fallback explains both symptoms. It is inferred from the output and not verified.
4. The fix belongs in the LaTeX printer, which needs a handler for `Trace`. The `Trace` class itself should not change.
5. The trace notation should follow existing SymPy LaTeX conventions for named operators, such as `\operatorname{...}` and `\left( ... \right)`. Those conventions are not visible here.
6. Other printers (str, pretty, MathML, code printers) are out of scope unless they are found to share the same defect.

## Tech Stack
- Python, SymPy. Versions are **unknown**.

## Commands
- Build: **unknown**. This is likely pure Python with no build step, but that is unverified.
- Test: **unknown**. Presumably the project's standard test runner, run against the LaTeX printing tests. The exact command is not visible.
- Lint: **unknown**.
- Reproduction (from the issue):
  ```py
  from sympy import MatrixSymbol, Symbol, latex, trace
  n = Symbol("n")
  A = MatrixSymbol("A", n, n)
  latex(trace(A**2))   # currently 'Trace(A**2)'
  ```

## Project Structure
**Unknown.** The repository is not accessible. The following locations need to be found:
- The LaTeX printer implementation.
- The `Trace` matrix-expression class.
- The existing LaTeX printer tests.

## Code Style
**Unknown.** Follow the existing per-class handler convention of the LaTeX printer. Arguments must be printed by recursing through the LaTeX printer, never through `str()` or another printer.

## Testing Strategy
- Add unit tests alongside the existing LaTeX printer tests, at a location still to be found, covering AC1–AC4.
- Use exact-string assertions on `latex(...)` output, matching how existing LaTeX tests are written. This is an assumption.
- Run the full printing test suite to confirm AC5.
- Optionally confirm the output compiles in a LaTeX/MathJax renderer as a manual check.

## Boundaries
- **Always:** Print every sub-expression through the LaTeX printer. Add regression tests for the reported case. Follow the existing printer handler conventions.
- **Ask first:** Changing the generic fallback behaviour of the LaTeX printer for all unknown classes. Changing the `Trace` class or its evaluation semantics. Changing output of other printers. Choosing a notation that departs from existing SymPy conventions.
- **Never:** Change the semantics of `trace()`. Alter existing LaTeX output for unrelated expressions. Remove or weaken existing tests.

## Success Criteria
- `latex(trace(A**2))` returns the agreed trace notation wrapping `A^{2}`, for example `\operatorname{tr}\left(A^{2} \right)`.
- AC2–AC4 pass as new tests.
- The existing printing test suite passes unchanged (AC5).
- No Python-syntax fragments (`**`, `Trace(`) appear in LaTeX output for trace expressions.

## Open Questions
1. **Notation:** Should the output use `\operatorname{tr}`, `\operatorname{Tr}`, `\mathrm{tr}` or `\text{Tr}`? Should the argument use `\left( \right)` or plain parentheses? Is there an established SymPy convention?
2. **Root cause scope:** Why are inner expressions printed with non-LaTeX syntax? Is it the generic fallback for unknown classes, which uses a string representation? If so, should that fallback be fixed for all unhandled classes? Doing so would be a broader behaviour change.
3. Do other matrix-expression nodes have the same missing-handler problem, and should they be included in this change or tracked separately?
4. Do the pretty printer or the MathML printer also lack `Trace` support, and is that in scope?
5. Should the trace of an explicit (non-symbolic) matrix be considered? It probably evaluates and so never reaches the printer, but this is unverified.
6. What are the project's test command, file locations and supported Python/SymPy versions?