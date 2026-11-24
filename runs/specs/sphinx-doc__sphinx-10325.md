# Spec: `:inherited-members:` accepts multiple base classes

## Objective

Let users exclude inherited members from **several** base classes at once, while still documenting members inherited from all other bases.

**Problem today:** `:inherited-members:` takes one class name. Members inherited from that class are excluded and all other inherited members are documented. This leaves two cases unsolved:

1. **Multiple inheritance.** A class inherits from several bases. The user wants members from some bases documented and members from other bases ignored.
2. **Module-wide filtering.** A module has many classes that subclass different built-ins (`list`, `set`, `tuple`). The user wants members from `list`, `set` and `tuple` ignored, and every other inherited member documented, with one `automodule` directive.

The only workaround is to write one `autoclass` block per class. That is tedious and does not solve case 1.

**Users:** Documentation authors who use the autodoc `automodule` and `autoclass` directives.

**User stories:**
- As a doc author, I can write `:inherited-members: list, set, tuple` on `automodule`. Then no documented class shows members inherited from `list`, `set` or `tuple`, and other inherited members still appear.
- As a doc author, for `class C(A, B)` I can write `:inherited-members: B`. Then `C` shows members inherited from `A` and none inherited from `B`.
- As an existing user, my current single-class usage (`:inherited-members: Foo`) and bare usage (`:inherited-members:`) behave exactly as before.

## Assumptions

1. The project is **Sphinx**, and the option belongs to the `sphinx.ext.autodoc` extension. I inferred this from the option name and directive names. I have not seen the repository.
2. The option currently accepts one class name. A bare `:inherited-members:` (no value) currently means "document everything inherited except from `object`".
3. Classes are matched by **class `__name__`**, compared as plain strings, as the single-class option does today. They are not matched by import path or identity.
4. The list is **comma-separated**, and whitespace around entries is ignored. For example, `list, set,tuple` gives `{"list", "set", "tuple"}`.
5. The option applies to both `automodule` and `autoclass`, and it propagates from `automodule` to the classes it documents, as it does today.
6. The same multi-value syntax should work when the option is set in `autodoc_default_options` in `conf.py`. That setting is assumed to accept a string value today.
7. The class being documented is never treated as "ignored", even if its own name appears in the list. Its own members are always documented when members are requested.
8. Only member *filtering* changes. Rendering, ordering, and other options (`:members:`, `:exclude-members:`, `:private-members:`, `:special-members:`, `:undoc-members:`) are unaffected.

## Tech Stack

- Language: Python. The supported version range is **unknown**.
- Library: Sphinx, autodoc extension. The version and branch are **unknown**.
- Other dependencies: **unknown**.

## Commands

The repository was not available, so all commands are **unknown**:

```
Build:   unknown
Test:    unknown (likely a pytest-based suite — unconfirmed)
Lint:    unknown
Docs:    unknown
```

## Project Structure

**Unknown.** The following locations need to be identified, but their paths are not confirmed:

- The autodoc option parser for `inherited-members`
- The inherited-member filtering logic in the class documenter
- The autodoc test suite and its test-root fixture modules
- The user documentation for autodoc directive options
- The changelog

## Code Style

**Unknown.** Follow the conventions already used in the autodoc extension and its tests. No style snippet is available.

## Functional Requirements

**R1 — Parsing**
- The option value is parsed into a set of class names.
- **Accepted input:** a comma-separated list. Entries are stripped of whitespace, and empty entries are dropped.
- **Single value:** gives a one-element set. This preserves existing behaviour.
- **Bare option (no value) or `None`:** keeps the current default, equivalent to `{"object"}`.
- **`autodoc_default_options`:** the same string format is accepted there.

**R2 — Filtering semantics.** When deciding whether to document an inherited member of class `C`:
- **Defined on `C` itself:** the member is never filtered by this option.
- **Inherited:** find the class in `C`'s MRO that actually provides the member, i.e. the first class in the MRO whose `__dict__` contains the name.
  - If that class's `__name__` is in the ignore set, the member is filtered.
  - Otherwise, the member is documented, provided the other options allow it.
- **Precedence:** a member defined in a non-ignored base is documented even if an ignored base also defines it. For example, a base that overrides `list.append` documents its `append`. *(Must be confirmed against current behaviour; see Open Questions Q1.)*

**R3 — Multiple inheritance (case 1).** For `class C(A, B)` with `:inherited-members: B`:
- Members provided by `A` are documented.
- Members provided only by `B` are not documented.
- Members `B` itself inherits from its own bases are handled per Q2.

**R4 — Module-wide (case 2).** With `automodule` and `:inherited-members: list, set, tuple`:
- Every documented class in the module omits members provided by `list`, `set` or `tuple`.
- Each class still shows members inherited from its other bases.

**R5 — Backward compatibility.** Existing single-name and bare usages produce identical output to before the change.

**R6 — Documentation.**
- The autodoc docs describe the comma-separated form, with at least one example.
- A changelog entry is added.

## Testing Strategy

The framework and test locations are **unknown**. Use the existing autodoc test infrastructure. The following tests are expected:

**Parser unit tests:**
- Bare value
- Single name
- Multiple names
- Names with surrounding whitespace
- Trailing or duplicate commas

**Directive-level tests using fixture modules:**
- Single-name behaviour is unchanged (regression).
- Bare option behaviour is unchanged (regression).
- `class C(A, B)` with `:inherited-members: B` shows `A`'s members and hides `B`'s.
- A module with classes subclassing `list`, `set` and `tuple`, documented via `automodule` with `:inherited-members: list, set, tuple`, hides the built-in methods and shows members from user-defined bases.
- An override case: a user base overrides a method of an ignored base, and the override is documented.
- The same filtering works via `autodoc_default_options`.

**Coverage target:** **unknown**. At minimum, every branch of the new parsing and filtering logic must be covered.

## Boundaries

- **Always:**
  - Keep existing single-value and bare-option behaviour byte-for-byte identical.
  - Add regression tests for the old behaviour alongside the new tests.
  - Update the user docs and the changelog.
- **Ask first:**
  - Changing matching from `__name__` to qualified or dotted names.
  - Changing which MRO classes count as "providing" a member, if that alters current single-class output.
  - Changing the public option-spec or converter API used by third-party extensions.
  - Adding dependencies.
- **Never:**
  - Break the existing option syntax.
  - Change unrelated autodoc options.
  - Remove or loosen existing tests to make the new ones pass.

## Success Criteria

- [ ] `:inherited-members: list, set, tuple` on `automodule` excludes members provided by any of those three classes from every documented class in the module, and keeps other inherited members.
- [ ] For `class C(A, B)`, `:inherited-members: B` documents `A`'s members and excludes `B`'s.
- [ ] `:inherited-members: Foo` and bare `:inherited-members:` produce the same output as before the change, confirmed by regression tests.
- [ ] Whitespace around comma-separated names does not affect results.
- [ ] Multi-value config works through `autodoc_default_options`.
- [ ] Docs and changelog are updated.
- [ ] The full existing test suite passes.

## Open Questions

1. **Current filtering algorithm (critical).** Does the current implementation stop at the *first* ignored class it meets while walking the MRO, filtering everything after it? Or does it check only the class that actually provides the member?
   - If the former, ignoring `B` in `class C(A, B)` might also hide members from classes later in the MRO.
   - Should the multi-class version switch to "the providing class is ignored" semantics, even if that subtly changes single-class output in diamond or multi-base hierarchies?
2. **Transitive bases.** If `B` is ignored and `B` inherits from `Base0`, should members `C` gets from `Base0` *via `B`* also be hidden? Or only members defined directly on `B`? What if `Base0` is also reachable through a non-ignored base `A`?
3. **Name matching.** Should entries match only `__name__`? Or also fully qualified names like `collections.OrderedDict`, to tell apart same-named classes from different modules?
4. **Is `object` implicit?** If a user writes `:inherited-members: list`, should members from `object` (e.g. `__init_subclass__`, if special members are enabled) still be hidden as with the bare form? Or is `object` excluded only when it is listed?
5. **Accepted formats in `conf.py`.** Should `autodoc_default_options` also accept a Python list or set, or only a comma-separated string?
6. **Invalid or unknown names.** Should names that match no class in any MRO be silently ignored, or produce a warning?
7. **Interaction with `:exclude-members:`.** Confirm that `:exclude-members:` still applies on top of this filtering. The assumption is yes, it is applied independently.
8. **Target version.** Which Sphinx release should this ship in? Is it treated as a feature addition (minor release)?