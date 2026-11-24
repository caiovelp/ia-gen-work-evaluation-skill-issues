# Spec: Serialize combined Enum flag values in migrations

## Objective

When a model field's default (or any other value written into a migration) is a **combination of `enum.Flag` / `enum.IntFlag` members**, the migration serializer produces invalid code.

**Example from the issue:**

```python
regex_flags = models.IntegerField(default=re.UNICODE | re.IGNORECASE)
```

This currently produces the following in the generated migration:

```python
default=re.RegexFlag[None]
```

That expression is wrong. It raises `KeyError` when the migration is loaded.

**Root cause, as stated in the issue:** `EnumSerializer` serializes an enum value through its `.name`. A combined flag value has no single member, so its `.name` is `None`.

**Proposed direction, from the issue:** decompose the value into its member names. Then emit an expression that ORs the members back together. The issue suggests `enum._decompose` for the decomposition.

**Users:** Django developers whose model fields have defaults (or other deconstructed arguments) built from combined enum flags. Examples are `re` flags and custom `IntFlag` / `Flag` classes.

**User story:** As a developer, when I run `makemigrations` on a field whose default is `re.UNICODE | re.IGNORECASE`, I get a migration that imports cleanly. Its default must evaluate to a value equal to `re.UNICODE | re.IGNORECASE`.

**Out of scope:**
- Changes to how single-member enums are serialized. The existing output stays as it is.
- Changes to non-enum serializers.

## Assumptions

1. The project is Django. The affected component is the migrations serializer's `EnumSerializer`. The class name comes from the issue. Its file location is **unknown** (unverified guess: `django/db/migrations/serializer.py`).
2. The current single-member output format is roughly `module.EnumClass[‘NAME’]`. I infer this from `re.RegexFlag[None]` in the issue. For combined values, the output should be the same per-member form joined with ` | `, for example:
   ```python
   re.RegexFlag['IGNORECASE'] | re.RegexFlag['UNICODE']
   ```
   The exact format is an Open Question.
3. The required imports for a combined value are the same as for a single member. That is one import of the enum's module.
4. Output must be **deterministic**, so repeated `makemigrations` runs produce no spurious diffs. Member order must therefore be stable.
5. Behavior for single-member values and for plain `Enum` (non-flag) values must stay byte-for-byte unchanged.
6. Supported Python versions are **unknown**. `enum._decompose` is a private CPython helper. Its availability and behavior differ across Python versions; for example, enum internals changed in 3.11.

## Tech Stack

- Python, using the stdlib `enum` module (`Flag`, `IntFlag`) and `re.RegexFlag`. Supported versions are unknown.
- Django migrations framework. The version and branch are unknown.

## Commands

All commands are **unknown**, because the issue does not provide them.
- Test: unknown. The project's own test runner should be used, scoped to the migrations writer/serializer tests.
- Lint/format: unknown.
- Build: not applicable / unknown.

## Project Structure

**Unknown.** The issue does not reference any paths. The relevant areas are:
- **Migrations serializer module.** This contains `EnumSerializer`. The path is unknown.
- **Migrations writer/serializer tests.** The path is unknown.

## Code Style

**Unknown.** Follow the existing style of the serializer module. In particular:
- Match the existing serializer return contract, which appears to be a `(string, imports)` pair. This is unverified.
- Match how existing enum output is formatted.

## Testing Strategy

The test framework and test locations are unknown. The serializer tests should cover these cases:

| Case | Example input | Expected |
|---|---|---|
| Combined stdlib IntFlag | `re.UNICODE \| re.IGNORECASE` | Valid expression. It evaluates equal to the input and imports `re`. |
| Combined custom `IntFlag` | a user-defined `IntFlag` with ≥2 members ORed | Valid expression, equal on round-trip. |
| Combined custom `Flag` (non-int) | a user-defined `Flag` with ≥2 members ORed | Valid expression, equal on round-trip. |
| Single flag member | `re.IGNORECASE` | Output unchanged from current behavior. |
| Plain `Enum` member | any non-flag enum | Output unchanged. |
| Determinism | same combined value serialized twice | Identical strings. |

Edge cases are listed under Open Questions:
- the zero value
- values with bits not covered by any member
- aliases and composite named members

The primary verification is a **round-trip check**: `eval(serialized_string)` with the reported imports must equal the original value.

## Boundaries

**Always:**
- Keep the existing single-member enum serialization output unchanged.
- Produce deterministic output.
- Add regression tests for the `re.UNICODE | re.IGNORECASE` case from the issue.

**Ask first:**
- Relying on private `enum` APIs such as `enum._decompose`, rather than a version-portable approach.
- Changing the textual format of existing enum serialization.
- Changing supported-Python-version guards.

**Never:**
- Emit a raw integer in place of the enum expression without approval. That would silently lose the enum type.
- Emit output that cannot be evaluated, such as `[None]`.
- Modify unrelated serializers.

## Success Criteria

1. Serializing `re.UNICODE | re.IGNORECASE` no longer yields `re.RegexFlag[None]`. It yields an expression that ORs named members of `re.RegexFlag`.
2. Evaluating that expression with the reported imports gives a value equal to `re.UNICODE | re.IGNORECASE`.
3. A migration generated for `models.IntegerField(default=re.UNICODE | re.IGNORECASE)` imports and loads without error.
4. Custom `Flag` and `IntFlag` combinations round-trip the same way.
5. Single-member and non-flag enum serialization output is identical to the current output.
6. Serializing the same value repeatedly gives identical output.
7. Existing serializer and migration tests still pass.

## Open Questions

1. **Decomposition mechanism.** Is using the private `enum._decompose` acceptable? Or should the implementation use a version-portable approach? One option is iterating the flag's members and testing bit inclusion. Another is relying on flag iteration where Python supports it. Which Python versions must be supported?
2. **Output format.** Should the expression be `re.RegexFlag['IGNORECASE'] | re.RegexFlag['UNICODE']`, which matches the bracket-by-name style? Or should it use another form, such as attribute access?
3. **Member ordering.** Should members appear in definition order, ascending value order, or alphabetical order?
4. **Zero value.** What should a flag value of `0` serialize to? It has no members, and its `.name` may be `None` depending on the Python version. Options include `EnumClass(0)` or an error.
5. **Uncovered bits.** What if the value contains bits not covered by any named member? Should it emit something like `EnumClass(value)`, combine the named members with the leftover integer, or raise an error?
6. **Aliases and composite named members.** If a flag class defines a named member equal to a combination, should that name be used directly? It would already have a `.name`. And how should aliases be handled?
7. **Backporting.** Should the fix target only the main branch, or be backported? The version or branch is unknown.
8. **Commands and paths.** What are the test commands and file paths for the serializer and its tests? Both are unknown from the issue.