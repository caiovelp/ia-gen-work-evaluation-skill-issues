# Spec: Accept Non-Standard Option Syntax in the `option::` Directive

## Objective

Sphinx 3.2 rejects `.. option::` descriptions that earlier versions accepted. A project that builds with warnings-as-errors (QEMU) therefore fails to build. Example from the issue:

```rst
.. option:: [enable=]PATTERN

   Immediately enable events matching *PATTERN*
```

Under Sphinx 3.2 this produces:

```
Warning, treated as error:
../../docs/qemu-option-trace.rst.inc:4:Malformed option description '[enable=]PATTERN', should look like "opt", "-opt args", "--opt args", "/opt args" or "+opt args"
```

**Users:** documentation authors who describe command-line options with the `option::` directive. Their projects must build with whatever `sphinx-build` their Linux distribution ships.

**Goal:** documentation that built without warnings on Sphinx versions before 3.2 builds again without a "Malformed option description" warning. The option is still rendered and still registered so that it can be referenced.

**What the user is asking for:**

1. **Backwards compatibility (primary).** `option::` content accepted before 3.2, such as `[enable=]PATTERN`, must not raise a warning or error in 3.2+.
2. **Permissiveness (secondary).** The directive should accept arbitrary option strings, because real programs and operating systems use option syntaxes outside `-opt`, `--opt`, `/opt` and `+opt`.

**Acceptance criteria (from the issue):**

- `.. option:: [enable=]PATTERN` builds with `-W` (warnings as errors) and no "Malformed option description" warning.
- The option description is still rendered in the output.
- Option descriptions that already parsed correctly keep their current rendering and cross-reference targets. For example `-opt args`, `--opt args`, `/opt args`, `+opt args` and `opt` must not regress.

## Assumptions

1. The regression comes from a tightened option-description pattern or parser in the standard domain's `option` directive, introduced in Sphinx 3.2. The exact code location and the commit that introduced the change are **unknown**, since the repository is not visible.
2. Before 3.2, a string like `[enable=]PATTERN` was accepted. Whether it was then indexed and cross-referenceable, and under what name, is **unknown**. The fix should preserve that behaviour, whatever it was.
3. Malformed-option warnings are emitted through the normal Sphinx logger. They become fatal only because QEMU builds with `-W`.
4. The fix belongs in Sphinx itself, not in QEMU's documentation.
5. Changing the warning text or the warning category is in scope only if the decision is to keep a warning in some cases (see Open Questions).

## Tech Stack

- Python, Sphinx. Supported Python and Sphinx versions are **unknown**.
- The affected component is the standard domain's `option` directive (`.. option::`). The source file path is **unknown**.

## Commands

All unknown, because the repository is not visible:

- Build: unknown
- Test: unknown (likely pytest, unconfirmed)
- Lint: unknown
- Reproduce: build a minimal project containing the reST snippet above with `sphinx-build -W`. The exact project layout is unknown.

## Project Structure

Unknown. Expected areas to locate during planning:

- The standard domain implementation containing the `option` directive.
- The existing tests for the standard domain or `option` directive.
- The changelog file.

## Code Style

Unknown. Follow the existing conventions of the module that contains the `option` directive. No snippet is available from the issue.

## Testing Strategy

The framework and test locations are unknown. Required test coverage:

- **Regression test:** an `option::` with `[enable=]PATTERN` produces no warning and renders a description node.
- **Non-regression tests:** the existing forms `opt`, `-opt args`, `--opt args`, `/opt args` and `+opt args` produce the same signature nodes and index/target entries as before.
- **Other forms seen in practice**, if the permissive approach is chosen. Examples are bracketed optional prefixes, `key=value` and other non-dash syntaxes. The concrete list is to be confirmed.
- **Cross-references:** the `:option:` role still resolves for options that parse in the standard form.

## Boundaries

- **Always:**
  - Keep existing valid option descriptions rendering and resolving exactly as before.
  - Add a regression test that reproduces the issue's example.
  - Add a changelog entry.
- **Ask first:**
  - Removing the "Malformed option description" warning entirely, as opposed to relaxing it.
  - Changing how option names are derived for indexing or cross-referencing.
  - Adding a configuration option.
  - Any change to public API.
- **Never:**
  - Break `:option:` cross-references for currently valid options.
  - Require users to edit existing documentation to get back to a clean build.
  - Silently drop the option description from the output.

## Success Criteria

- [ ] A document containing `.. option:: [enable=]PATTERN` builds with `sphinx-build -W` and no "Malformed option description" warning.
- [ ] The description `[enable=]PATTERN` appears in the rendered output.
- [ ] Existing tests for the `option` directive pass unchanged.
- [ ] A new regression test covers the issue's example.
- [ ] The behaviour for inputs that pre-3.2 Sphinx accepted is identical to pre-3.2 behaviour, or any difference is documented and approved.

## Open Questions

1. **Scope.** Should the fix restore exactly the pre-3.2 behaviour, or make the directive accept *any* string, as the reporter suggests?
2. **Warning policy.** Should the "Malformed option description" warning be removed completely? Alternatives:
   - Lower it so that it is not fatal under `-W`.
   - Emit it under a suppressible warning type.
3. **Indexing of non-standard strings.** How should strings like `[enable=]PATTERN` be indexed and cross-referenced?
   - Use the whole string as the option name?
   - Strip a bracketed optional prefix and use `enable` or `PATTERN`?
   - Render the option without creating a reference target?
4. **Root cause.** What change in 3.2 introduced the stricter check? Was it intentional, for example to fix another bug that must not be reintroduced?
5. **Release target.** Should this go into a 3.2.x bugfix release?
6. **Option forms.** Are there other real-world option forms that should be explicitly supported and tested? Candidates: `-o=value`, Windows `/opt:value`, and options with no prefix plus arguments.