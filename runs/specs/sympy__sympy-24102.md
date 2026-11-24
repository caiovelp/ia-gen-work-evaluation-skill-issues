# Spec: `parse_mathematica` support for Greek and other non-ASCII identifiers

## Objective

`parse_mathematica` in `sympy.parsing.mathematica` is the replacement for the `mathematica` function, which is deprecated as of SymPy 1.11. It currently fails on input that the deprecated function handled:

```
from sympy.parsing.mathematica import parse_mathematica
parse_mathematica('λ')
# SyntaxError: unable to create a single AST for the expression
```

The deprecated function returns the symbol `λ` for the same input.

**Users:** People who move from `mathematica(...)` to `parse_mathematica(...)`, as the deprecation asks them to. Also anyone parsing Mathematica expressions with non-ASCII symbol names, such as Greek letters.

**Goal:** `parse_mathematica` accepts identifiers made of Greek characters, and possibly other non-ASCII letters, and turns them into SymPy symbols. This closes a regression compared with the deprecated parser.

**Acceptance criteria (user-level):**
- `parse_mathematica('λ')` returns a SymPy object equal to `Symbol('λ')`.
- Expressions that combine Greek identifiers with operators and function calls parse the same way their ASCII equivalents do.
- No existing `parse_mathematica` behaviour changes for ASCII input.

## Assumptions

1. The failure comes from the tokenizer or lexer in `parse_mathematica`. Its identifier pattern most likely accepts only ASCII letters, so `λ` is never tokenized as a symbol. The traceback suggests this, but I have not confirmed it because I have no access to the source.
2. The expected result for a bare Greek letter is a plain `Symbol` with the same Unicode name. This matches what the deprecated `mathematica('λ')` returns.
3. The scope is literal Unicode characters typed directly in the input string. Mathematica named-character escapes such as `\[Lambda]` are a separate feature and are out of scope unless confirmed otherwise (see Open Questions).
4. "Possibly others" means Unicode letters in general, not just the Greek block. Identifiers should follow a "letter-like" rule rather than a hard-coded list of Greek characters.
5. Digits may follow the first character of an identifier, as in ASCII identifiers (for example `α1`). Digits may not start an identifier.
6. The deprecated `mathematica` function is not modified.
7. Python 3, which handles `str` as Unicode, is the only runtime that matters.

## Tech Stack

- Python, as part of the SymPy library.
- Module: `sympy.parsing.mathematica`, which contains `parse_mathematica` and the deprecated `mathematica`.
- Minimum Python version and exact SymPy version: **unknown**. The issue mentions SymPy 1.11.

## Commands

Not visible in the issue, so all of these are **unknown** and must be confirmed from the repository:

- Test: unknown. Presumably the project's standard test runner, targeting the Mathematica parser tests.
- Lint / code quality: unknown.
- Build: unknown. It is probably not needed for a pure-Python change.

## Project Structure

- Implementation: the module behind `sympy.parsing.mathematica`. The exact file path is **unknown**.
- Tests: the existing test file for the Mathematica parser. The path is **unknown**.
- Docs: the `parse_mathematica` docstring and any deprecation or migration notes. The location is **unknown**.

## Code Style

**Unknown.** The project's existing conventions apply. No code snippet is available from the issue. Any new identifier-matching logic should follow the way the existing tokenizer defines its token patterns.

## Testing Strategy

- **Level:** unit tests on `parse_mathematica` at its public API.
- **Location:** alongside the existing Mathematica parser tests (path unknown).
- **Cases to cover:**
  - A single Greek letter: `'λ'` gives `Symbol('λ')`.
  - Multiple Greek letters as one identifier: `'αβ'` gives a single symbol `αβ`, matching how ASCII multi-letter names behave.
  - Greek letters in arithmetic: `'λ + 1'`, `'2 λ'` (implicit multiplication), `'α^2'`.
  - Greek letters as function arguments: `'Sin[θ]'` gives `sin(Symbol('θ'))`.
  - Mixed identifiers: `'α1'` and `'xα'` are each one symbol.
  - Uppercase Greek: `'Λ'`.
  - A non-Greek, non-ASCII letter, if assumption 4 holds, for example a Latin letter with a diacritic.
  - Regression: the existing ASCII test suite for `parse_mathematica` passes unchanged.
  - Negative case: non-letter Unicode symbols that are not valid identifier characters still raise an error rather than being silently accepted. The exact set of such characters is to be confirmed.
- **Coverage expectations:** unknown. Every new branch in the tokenizer should be exercised by at least one test.

## Boundaries

- **Always:**
  - Keep ASCII parsing behaviour identical.
  - Add regression tests for the reported input `'λ'`.
  - Run the full Mathematica parser test suite before committing.
- **Ask first:**
  - Supporting `\[Name]` escape sequences.
  - Changing how the deprecated `mathematica` function behaves.
  - Changing which Unicode categories count as identifier characters beyond letters and digits.
  - Adding any new dependency.
- **Never:**
  - Hard-code a list of individual Greek characters as the only fix.
  - Remove or weaken existing tests.
  - Alter public function signatures.

## Success Criteria

1. `parse_mathematica('λ') == Symbol('λ')` evaluates to `True`.
2. All Greek-letter test cases listed under Testing Strategy pass.
3. Non-ASCII letters beyond Greek are accepted as identifiers, if assumption 4 is confirmed.
4. The existing `parse_mathematica` tests pass with no modifications.
5. For every Greek-letter case in the test list, the output of `parse_mathematica` matches what the deprecated `mathematica` produces for the same input.

## Open Questions

1. Should identifiers accept any Unicode letter (for example, characters where Python's `str.isalpha()` is true, or the Unicode identifier rules), or only a defined set such as Greek?
2. Should Mathematica named-character escapes like `\[Lambda]` or `\[Alpha]` also be supported and mapped to the corresponding Unicode symbol? Or should that be a separate issue?
3. How should Mathematica's built-in Greek-named constants be handled? For example, `π` could map to `pi`, and `ⅇ` to `E`. Or should every Greek character, including `π`, become a plain `Symbol`?
4. Should non-letter Unicode characters, such as math operators like `×` or `≤` and other non-ASCII symbols, raise a clear error? Or should they map to their Mathematica operator meanings? Is a more descriptive error message wanted than "unable to create a single AST for the expression"?
5. What are the exact file paths for the implementation and tests, and what is the project's test command?
6. Is there a list of other inputs that the deprecated `mathematica` parsed and `parse_mathematica` rejects, which should be included in scope here?