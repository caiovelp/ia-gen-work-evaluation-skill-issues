# Spec: Accept `RR[...]` / `CC[...]` polynomial-ring domain strings in `Poly(..., domain=...)`, and improve the domain-option error message

## Assumptions

1. The project is SymPy, and the failing code is the `Domain` option's `preprocess` classmethod in `sympy/polys/polyoptions.py`. This comes from the traceback. Line numbers in the traceback come from the reporter's checkout and may have changed since.
2. `Domain.preprocess` matches domain strings against regular expressions, one per pattern: ground domains, finite fields, polynomial rings, fraction fields and algebraic fields. The polynomial-ring pattern currently accepts only `Z`/`ZZ`/`Q`/`QQ` as the ground domain. I have not seen this code; the assumption rests only on the fact that `RR[y,z]` reaches the final `raise`.
3. `RR[y,z]` should mean the same domain that `Poly(1.2*x*y*z, x)` builds automatically today. That domain prints as `RR[y,z]`, which is the polynomial ring over SymPy's default real field `RR`.
4. Because `RR` is not allowed, `CC` is very likely not allowed either, and fraction fields over these grounds (`RR(y,z)`, `CC(y,z)`) are probably rejected the same way. Fixing these together is natural, but it is not confirmed in scope (see Open Questions).
5. Precision-qualified grounds such as `RR_53` and `CC_53` are already accepted as plain domains. Whether they should be allowed as polynomial-ring grounds is unspecified (see Open Questions).
6. Existing accepted spellings and their results must not change, for example `ZZ[x]`, `QQ[x,y]`, `ZZ(x)`, `QQ<sqrt(2)>`, `GF(p)`, `RR`, `CC` and `EX`.
7. "Improve the wording of the error message" means making it more informative. That would mean naming the offending value and/or showing accepted forms. It does not mean changing the exception type, which stays `OptionError`.

## Objective

**Problem.** SymPy prints an automatically chosen domain as `RR[y,z]`, but a user cannot pass that same string back through `domain=`:

```py
>>> Poly(1.2*x*y*z, x)
Poly(1.2*y*z*x, x, domain='RR[y,z]')

>>> Poly(1.2*x*y*z, x, domain='RR[y,z]')
OptionError: expected a valid domain specification, got RR[y,z]
```

So the printed form of a `Poly` does not round-trip. The error message is also unhelpful because it does not say which forms are valid.

**Users.** These are SymPy users who build `Poly` objects with an explicit domain, often by copying the `domain='...'` from printed output. Code that builds domain strings programmatically is also affected.

**Success looks like:**
- `domain='RR[y,z]'` is accepted. It produces a `Poly` equal to the one built automatically, including the same domain.
- An invalid domain string still raises `OptionError`. The message is clearer and helps the user correct the input.

## Tech Stack

- Python, SymPy polys module (`sympy/polys/polytools.py`, `sympy/polys/polyoptions.py`, `sympy.polys.domains`), as seen in the traceback.
- Supported Python versions and SymPy version/branch: **unknown**.

## Commands

All commands are **unknown** because the repository is not visible. A test command would likely look like `pytest sympy/polys/tests/test_polyoptions.py` or `bin/test sympy/polys`, but the maintainers need to confirm this.

```
Build: unknown (pure Python; likely none)
Test:  unknown
Lint:  unknown
```

## Project Structure

Known from the traceback:
```
sympy/polys/polytools.py    → Poly.__new__, calls options.build_options
sympy/polys/polyoptions.py  → build_options, Options, Domain.preprocess (raises the OptionError)
sympy/polys/domains/        → domain objects (QQ.algebraic_field referenced; RR, CC presumed here)
```
Test locations are **unknown**. A likely location is `sympy/polys/tests/test_polyoptions.py` and/or `sympy/polys/tests/test_polytools.py`, but this needs confirming.

## Code Style

**Unknown** from the issue. Follow the existing conventions in `polyoptions.py`. Per Assumption 2, this means extending the existing regex/branch structure in `Domain.preprocess` rather than adding a new parsing mechanism.

## Testing Strategy

- **Framework:** unknown (SymPy's test suite, pytest-compatible style presumed).
- **Unit level (`Domain.preprocess`):**
  - Newly accepted strings map to the expected domain objects.
  - Previously accepted strings map exactly as before.
  - Invalid strings raise `OptionError` with the improved message.
- **Integration level (`Poly`):**
  - The example from the issue works.
  - Round-trip: for a `Poly` whose auto-detected domain is `RR[...]`, passing `domain=str(p.domain)` back gives an equal `Poly`.
- **Regression:** the existing polys test suite passes unchanged, except for any tests that assert the old error message text. Those tests are updated deliberately.
- **Coverage expectations:** unknown.

## Boundaries

- **Always:**
  - Keep every currently valid domain string behaving identically.
  - Keep raising `OptionError`, not a new exception type, for invalid domains.
  - Add tests for every newly accepted form and for the new message.
- **Ask first:**
  - Extending support beyond `RR[...]`. Candidates are `CC[...]`, `RR(...)`/`CC(...)`, precision-qualified grounds such as `RR_53[...]`, and `EX[...]`.
  - Changing the error message in a way that breaks downstream code or doctests matching the old text.
  - Changing how domains are printed.
- **Never:**
  - Change domain auto-detection or `Poly` printing as part of this fix.
  - Rework domain-string parsing into a new mini-language.
  - Remove or loosen existing tests without approval.

## Success Criteria

1. `Poly(1.2*x*y*z, x, domain='RR[y,z]')` does not raise.
   - The result equals `Poly(1.2*x*y*z, x)`.
   - Its `.domain` equals that `Poly`'s domain, the polynomial ring over `RR` in `y, z`.
2. A single generator also works: `domain='RR[y]'` is accepted. Spacing variants are accepted to the same degree as the existing `ZZ[...]`/`QQ[...]` patterns already allow.
3. Round-trip property: for the issue example, `Poly(expr, x, domain=str(Poly(expr, x).domain)) == Poly(expr, x)`.
4. All previously valid domain strings resolve to the same domains as before. The existing polys tests pass.
5. An invalid domain string, such as `domain='foo[y]'`, raises `OptionError`. The message:
   - includes the offending value, quoted or otherwise delimited, and
   - gives guidance on valid forms, for example by listing the accepted patterns or pointing to documentation.
   
   The exact wording needs maintainer agreement (Open Question 4).
6. Each scope extension agreed in Open Questions 1–3 gets its own acceptance test of the same shape as criteria 1–3.

## Open Questions

1. **Scope of ground domains.** Should `CC[...]` be accepted too, alongside `RR[...]`? It is presumably broken the same way. Should `EX[...]` be accepted, or is that intentionally excluded?
2. **Fraction fields.** Should `RR(y,z)` and `CC(y,z)` be fixed in the same change, assuming they are rejected today (unverified)?
3. **Precision-qualified grounds.** Should `RR_<prec>[...]` and `CC_<prec>[...]` be accepted? If so, should the printed form of a non-default-precision `RR[...]` domain round-trip with its precision intact?
4. **Error message wording.** What should the improved message look like? Options:
   - (a) quote the bad value, e.g. `expected a valid domain specification, got 'RR[y,z]'`;
   - (b) also list accepted forms, e.g. `ZZ, QQ, RR, CC, EX, GF(p), K[x,...], K(x,...), QQ<a,...>`;
   - (c) point to documentation.
   
   Do any tests or doctests assert the current exact text?
5. **Generator consistency.** If a user passes `domain='RR[x]'` while also passing `x` as a generator, should that be rejected? It may already be handled downstream for `ZZ[x]`. Confirm that the existing behaviour simply carries over.
6. **Test layout and commands.** Which test files and which test command should be used?