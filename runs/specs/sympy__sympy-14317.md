# Spec: LaTeX printer — consistent monomial order for `Poly`

## Assumptions

1. This is the SymPy project, a Python library. The relevant code is the LaTeX printer's handling of `Poly` objects. The exact file and method are **unknown**, because I cannot see the repository.
2. The expected order is the one the `str` and `pretty` printers already produce for the same `Poly`. That means the polynomial's own term order: descending by degree, or more generally by the Poly's monomial ordering.
3. The issue output suggests that LaTeX prints the polynomial through a path that loses the Poly's term order. One likely cause is converting it to an `Add` expression and letting the default `Add` ordering apply. This explains the symptom but has not been verified.
4. The issue shows `pretty(p)` returning a string identical to `str(p)`. I assume this reflects how the reporter's session was configured, and that the pretty printer in normal 2D mode also follows the Poly order.
5. Only the term order of the polynomial expression should change. The rest of the LaTeX output should stay the same: `\operatorname{Poly}{\left( ... \right)}`, the generator list, and the `domain=` part.
6. Multivariate Polys should also follow the Poly's term order, which is the ordering `str` uses.
7. Each term should keep the LaTeX formatting it has today: coefficients (`2 x^{2}`), symbolic coefficients (`a x^{5}`), unit coefficients (`x^{4}`), and constants (`3`).

## Objective

The LaTeX printer should render the terms of a `Poly` in the same order as the `str` and `pretty` printers: from highest to lowest degree, following the Poly's monomial ordering.

**User:** SymPy users who render polynomials in LaTeX (Jupyter, documentation, papers) and expect that output to match the textual and pretty forms.

**Current behavior (from the issue):**
```
>>> var('a b c x')
>>> p = Poly([a, 1, b, 2, c, 3], x)
>>> latex(p)
'\\operatorname{Poly}{\\left( a x^{5} + b x^{3} + c x + x^{4} + 2 x^{2} + 3, x, domain=\\mathbb{Z}\\left[a, b, c\\right] \\right)}'
```

**Expected behavior:**
```
'\\operatorname{Poly}{\\left( a x^{5} + x^{4} + b x^{3} + 2 x^{2} + c x + 3, x, domain=\\mathbb{Z}\\left[a, b, c\\right] \\right)}'
```

**Acceptance criteria:**
- `latex(Poly([a, 1, b, 2, c, 3], x))` produces the expected string above.
- For any `Poly`, the order of terms in `latex(p)` matches the order in `str(p)`.
- Signs are rendered correctly when coefficients are negative. For example, a Poly such as `Poly([-1, 2, -3], x)` gives `- x^{2} + 2 x - 3`, not `+ -...`.
- Everything outside the polynomial expression is unchanged: generators, domain, and the wrapping `\operatorname{Poly}`.

## Tech Stack

- Python, SymPy. The supported Python and SymPy versions are **unknown**.
- Components involved: the LaTeX printer, the `Poly` class and its term iteration, and `str` printing for reference behavior.

## Commands

All **unknown**, since I don't have repository access. Presumably:
- Test: the project's pytest or `bin/test` runner targeting the LaTeX printer tests. The exact command is unknown.

## Project Structure

**Unknown.** Expected locations to confirm:
- The LaTeX printer module, containing the `Poly` printing method.
- The LaTeX printer test module.
- The `str` printer's `Poly` method, as a reference for how terms are iterated in order.

## Code Style

Unknown. Follow the existing conventions of the LaTeX printer module and match the formatting of the existing printing methods. No snippet is available.

## Testing Strategy

- **Unit tests** in the LaTeX printer test module:
  - The exact reproduction from the issue.
  - A Poly with negative coefficients, to check sign handling.
  - A Poly with rational or composite coefficients, such as `(a+b)*x`, to check that coefficients get parentheses where needed.
  - A multivariate Poly, to check that term order is consistent with `str`.
  - A Poly with zero coefficients, to check that zero terms are omitted.
  - A constant-only Poly and the zero Poly.
- **Regression:** existing LaTeX printer tests involving `Poly` must still pass. If existing expected strings encode the old, inconsistent order, they should be updated, and the change should be called out.
- **Consistency check (optional):** a test comparing the term sequence of `latex` with that of `str` for several Polys.

## Boundaries

- **Always:** keep LaTeX term formatting consistent with the existing printer conventions, add regression tests for the reported case, and run the full printing test suite.
- **Ask first:** changing the order used by `str` or `pretty`, changing `Poly`'s public API, changing `latex()` output for non-`Poly` objects (such as `Add` or `PurePoly` beyond the order fix), or adding new printer settings.
- **Never:** change the global `Add` ordering for LaTeX, alter the `domain=` or generators rendering, or remove or weaken existing tests without justification.

## Success Criteria

1. The issue's reproduction returns `a x^{5} + x^{4} + b x^{3} + 2 x^{2} + c x + 3` inside the Poly wrapper.
2. For every test Poly, the term order of `latex(p)` equals that of `str(p)`.
3. Negative, rational, symbolic-compound, zero, and constant coefficients render correctly.
4. Univariate and multivariate cases are covered.
5. The existing printing tests pass, and any updated expectations are justified by the order fix.

## Open Questions

1. Should `PurePoly` follow the same rule? I assume yes.
2. If the user passes `order=` to `latex()`, should it override the Poly's native term order? Or should the Poly's order always win, matching `str`?
3. Should the pretty printer, in 2D Unicode or ASCII mode, be verified and fixed as part of this issue if it is also inconsistent? Or should that be kept separate?
4. Are there existing tests whose expected LaTeX strings depend on the current, `Add`-sorted order? If so, is updating them acceptable?
5. For composite coefficients such as `(a + b)`, what is the expected parenthesization, `\left(a + b\right) x`? Should it match the existing `Mul` LaTeX conventions?
6. Which SymPy versions or branches should get the fix?