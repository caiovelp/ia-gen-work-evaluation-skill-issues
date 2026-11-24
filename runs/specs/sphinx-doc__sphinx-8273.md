# Spec: Man Page Section Directories for the Sphinx Man Builder

## Objective

The man page builder writes every generated page into one flat directory, `<build-dir>/man`. The `man` program looks for pages in section subdirectories (`man1/`, `man3/`, and so on) under each `MANPATH` entry. Because of this, the build output cannot be added to `MANPATH` as is, and projects must copy the files into a section layout themselves.

**Goal:** the man builder can produce a `MANPATH`-compatible layout, placing each page in a subdirectory named for its section (e.g. `<build-dir>/man/man1/foo.1`, `<build-dir>/man/man3/bar.3`).

**Users:**
- Documentation authors who want to test built man pages with `MANPATH=<build-dir>/man man <page>`.
- Packagers and build-system maintainers who install man pages and want the build tree to match the install layout.
- Existing users who rely on the flat `<build-dir>/man/*.N` layout. The issue author notes this group may break.

**User stories:**
- As a doc author, I can point `MANPATH` at the man build output, and `man <name>` finds pages in every section I generate.
- As an existing user, my build output does not change unexpectedly unless the project decides on and documents a breaking change.

## Assumptions

1. "Sphinx" means the Sphinx documentation generator, and the change belongs in its built-in man page builder.
2. Each man page already has a known section number from its configured entry. The builder already uses that number in the output filename, e.g. `name.1`.
3. The section directory name is `man<section>`, so `man1` for section 1 and `man3` for section 3. This follows the standard `man`/`MANPATH` convention.
4. Sections with suffixes, such as `3p` or `1x`, follow the usual `man` convention. Whether this means `man3p/` or `man3/` is an open question.
5. The new layout is opt-in through a configuration setting, so existing users are not broken. The name and default of the setting are **unknown** and need a decision. See Open Questions.
6. Only the output layout changes. Page content, filenames and the roff output stay the same.
7. The change must work on every platform Sphinx supports, including creating directories on Windows, even though `MANPATH` is a Unix concept.

## Tech Stack

- Language and framework: Python, Sphinx. The exact supported Python and Sphinx versions are **unknown**.
- Component: the Sphinx man page builder. The source file path is **unknown** because the repository was not available.
- Key dependencies: **unknown**. No new dependencies are expected.

## Commands

The repository was not available, so all commands are **unknown**:

```
Build:   unknown
Test:    unknown
Lint:    unknown
Docs:    unknown (the man builder is presumably invoked through the Sphinx build with the "man" builder; exact invocation unknown)
```

## Project Structure

**Unknown.** The following locations still need to be identified in the repository:
- the man builder source module
- the configuration value registration for the man builder
- the man builder tests and their test-root fixtures
- the user documentation for man builder configuration and the changelog

## Code Style

**Unknown.** Follow the existing conventions of the man builder module and of how Sphinx registers configuration values. No snippet is available.

## Desired Behavior

### Proposed layout (when enabled)

```
<build-dir>/man/
├── man1/
│   └── foo.1
├── man3/
│   └── bar.3
└── man5/
    └── baz.5
```

### Current layout (preserved when disabled)

```
<build-dir>/man/
├── foo.1
├── bar.3
└── baz.5
```

### Rules

- The builder creates a section directory only for sections that have at least one page.
- The builder creates section directories on demand. It does not fail if a directory already exists, for example after an incremental rebuild.
- Each page is written to exactly one location. The flat copy is not also written, unless a compatibility decision says otherwise. See Open Questions.

## Testing Strategy

- **Framework and locations:** **unknown**. Use the project's existing test framework and man builder test fixtures.
- **Unit and integration tests for the man builder:**
  - With the feature enabled and pages in sections 1 and 3, the output contains `man1/<name>.1` and `man3/<name>.3`, and no flat `<name>.N` files.
  - With the feature disabled, or with the default if the default stays flat, the output matches the current flat layout exactly.
  - Several pages in the same section all land in the same directory.
  - Rebuilding into an existing output directory succeeds.
  - Section values with suffixes behave as decided in Open Questions.
- **Manual check on a Unix system:** run `MANPATH=<build-dir>/man man <section> <name>` and confirm the page is found.
- **Coverage:** every new branch in the builder (enabled and disabled) is exercised. The coverage threshold is **unknown**.

## Boundaries

- **Always:**
  - Keep current behavior available.
  - Add tests for both layouts.
  - Document the new option and its default in the user docs and the changelog.
  - Derive the directory name from each page's configured section.
- **Ask first:**
  - Making the sectioned layout the default. This is a breaking change.
  - Adding a deprecation path for the flat layout.
  - Changing output filenames.
  - Changing other builders.
  - Adding any dependency.
- **Never:**
  - Silently change the default output layout without a documented decision.
  - Change man page content as part of this work.
  - Remove or weaken existing man builder tests.

## Success Criteria

1. When the new behavior is enabled, every generated man page is located at `<build-dir>/man/man<section>/<name>.<section>`.
2. When the new behavior is enabled, `MANPATH=<build-dir>/man man <section> <name>` resolves every generated page on a standard Unix `man` implementation.
3. When the new behavior is disabled, the output is byte-for-byte the same in content and identical in paths to the current flat layout.
4. The configuration option is documented, including its name, type, default, and the version that introduced it.
5. The changelog records the new option, and any change to the default is flagged as a breaking change.
6. All existing man builder tests pass without changes, unless the default is intentionally changed. New tests cover the cases listed under Testing Strategy.

## Open Questions

1. **Default and compatibility.** Should the sectioned layout be opt-in, which avoids breaking anyone? Or should it become the default, possibly after a deprecation period? This is the central decision raised by the issue author.
2. **Configuration name and type.** What should the setting be called? Should it be a boolean, or a layout choice that leaves room for future variants?
3. **Suffixed sections.** For sections like `3p` or `1x`, should the directory be `man3p/` or `man3/`? Conventions differ between `man` implementations.
4. **Transitional output.** Should a transitional mode write both layouts, or should the builder never duplicate output?
5. **Other consumers of the man output path.** Do any other features, extensions or downstream tools assume the flat layout and need updating? Examples are post-build hooks, install helpers and docs that reference `<build-dir>/man/<name>.N`.
6. **Cleanup on layout switch.** When a user switches layouts in an existing build directory, should stale files from the other layout be removed, or left alone?
7. **Repository details.** The supported versions, test, build and lint commands, and the file locations are all unknown and must be confirmed from the repository.