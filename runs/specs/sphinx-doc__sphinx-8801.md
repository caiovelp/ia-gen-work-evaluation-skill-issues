# Spec: autodoc — Inherited annotation-only members with doc comments are treated as "undocumented"

## Assumptions

1. The bug lives in `sphinx.ext.autodoc`. The exact module, function and line are unknown because I have no repository access.
2. "HEAD of 3.x" means the fix targets the Sphinx 3.x maintenance branch. Forward-porting to later branches is not covered here.
3. An "annotation-only member" is a class-level name declared with a type annotation and no value, such as `attr1: int`. It appears in `__annotations__` but not in the class `__dict__`.
4. A `#:` doc comment on such a member counts as documentation. This already works for members declared on the documented class itself: `Bar.attr2` shows up without `:undoc-members:`.
5. `Foo.attr1`, when documented directly via `.. autoclass:: example.Foo` with `:members:`, presumably shows correctly. The issue does not confirm this.
6. The reported failure is limited to doc comments (`#:`) on inherited annotation-only members. Other documentation forms are not reported:
   - docstring-after-attribute (`"""..."""` on the next line)
   - entries from `__slots__` dicts
7. The expected result for `Bar.attr1` matches what users get today with `:undoc-members:`: the attribute is rendered with its type annotation (`int`) and its doc comment (`docstring`). The only difference is that the attribute is included without `:undoc-members:`.
8. The reporter's environment (macOS, Python 3.9.1) is incidental. The bug is assumed to be platform-independent.

## Objective

When a user documents a class with `:members:` and `:inherited-members:`, autodoc should treat an annotation-only attribute inherited from a superclass as **documented** if it has a doc comment in the superclass source. It should then include it in the output without `:undoc-members:`.

**User:** Sphinx users who document class hierarchies with type-annotated attributes. This pattern is common with dataclass-style or typed classes.

**Current behavior:** `Bar.attr1`, declared in `Foo` as `attr1: int  #: docstring`, is omitted. It appears only when `:undoc-members:` is added, so autodoc considers it undocumented.

**Expected behavior:** `Bar.attr1` appears in the output with `:members:` and `:inherited-members:` alone.

### Acceptance criteria (user-level)

Reproduction input:

```python
# example.py
class Foo:
    """docstring"""
    attr1: int  #: docstring


class Bar(Foo):
    """docstring"""
    attr2: str  #: docstring
```

```rst
.. autoclass:: example.Bar
   :members:
   :inherited-members:
```

- AC1: The output for `example.Bar` includes `attr1` with its doc comment `docstring`, with no `:undoc-members:`.
- AC2: The output for `example.Bar` still includes `attr2` with its doc comment, as it does today.
- AC3: An inherited annotation-only attribute **without** any doc comment is still omitted unless `:undoc-members:` is given. Undocumented members must not leak into the output.
- AC4: Without `:inherited-members:`, `Bar`'s output does not include `attr1`. Existing semantics are preserved.
- AC5: The rendered entry for `attr1` carries the same type annotation and content as it does today under `:undoc-members:`.

## Tech Stack

- Python (reporter on 3.9.1; the range of supported Python versions for the 3.x branch is unknown)
- Sphinx 3.x branch, `sphinx.ext.autodoc`
- Other dependencies and versions: unknown

## Commands

Unknown. The issue gives no build, test or lint commands, and I cannot see the repository.

- Build docs: unknown
- Test: unknown (likely pytest-based, but unverified)
- Lint: unknown

## Project Structure

Unknown. The issue references only:

- `example.py`: user module from the reproduction
- `index.rst`: user doc source from the reproduction

The location of autodoc's source, its tests and its test fixture roots is unknown.

## Code Style

Unknown. Follow existing conventions in the autodoc codebase. No style examples are available from the issue.

## Testing Strategy

- **Regression test (required):** A test that reproduces the issue's `Foo`/`Bar` example and asserts AC1 and AC2. Framework, location and fixture mechanism are unknown and must follow existing autodoc tests.
- **Negative tests:** Cover AC3 (undocumented inherited annotation-only member stays hidden) and AC4 (no `:inherited-members:` means no inherited attribute).
- **Edge cases worth covering**, subject to Open Questions:
  - multi-level inheritance (`Baz(Bar(Foo))`)
  - a superclass defined in a different module from the subclass
  - a subclass that overrides/re-annotates the inherited attribute
  - a superclass attribute that has both an annotation and a value (`attr: int = 1  #: doc`), as a control case
- **Existing tests:** The full autodoc test suite must still pass. The command is unknown.
- Coverage expectations: unknown.

## Boundaries

- **Always:**
  - Add a regression test reproducing the issue's example.
  - Keep `:undoc-members:` semantics unchanged for genuinely undocumented members.
  - Preserve behavior of non-inherited annotation-only members.
  - Run the existing autodoc test suite.
- **Ask first:**
  - Changing which members are considered "documented" in cases beyond inherited annotation-only attributes.
  - Changing the public behavior or signature of any autodoc API or event, such as `autodoc-skip-member`.
  - Changing the order of inherited members in output.
  - Adding dependencies.
- **Never:**
  - Make inherited members always visible regardless of documentation.
  - Remove or weaken existing tests.
  - Fix this only on a branch other than 3.x without agreement.

## Success Criteria

1. Building docs from the issue's `example.py` and `index.rst` renders `Bar.attr1` with its doc comment, without `:undoc-members:` (AC1).
2. `Bar.attr2` continues to render as before (AC2).
3. Undocumented inherited annotation-only attributes remain hidden without `:undoc-members:` (AC3).
4. Inherited attributes remain hidden without `:inherited-members:` (AC4).
5. The rendered `attr1` entry matches its current rendering under `:undoc-members:`, including the type `int` (AC5).
6. A regression test encoding criteria 1–4 exists and passes, and the existing autodoc test suite passes.

## Open Questions

1. Does `.. autoclass:: example.Foo` with `:members:` currently render `attr1` correctly? This would confirm the bug is specific to inheritance (Assumption 5).
2. Should other documentation forms on inherited annotation-only attributes also be covered? Candidates are docstring-after-attribute (`"""..."""` on the following line) and `__slots__` dict docs, or only `#:` comments as reported.
3. When a superclass lives in a different module from the subclass, must its doc comments still be picked up? Expected yes, but please confirm.
4. If a subclass re-annotates an inherited attribute without a doc comment (e.g., `attr1: int` in `Bar`), should the superclass's doc comment be used, or should the member be treated as undocumented?
5. If both the superclass and subclass provide doc comments for the same attribute, which wins? Presumably the subclass.
6. Does `autodoc_inherit_docstrings` (if applicable in 3.x) affect whether inherited doc comments should be used? Should setting it to `False` hide `Bar.attr1` again?
7. Which branch or branches should receive the fix: 3.x only, or also later branches?
8. What are the project's test, build and lint commands, and where do autodoc tests and their fixtures live?