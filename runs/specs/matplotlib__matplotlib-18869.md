# Spec: Easily Comparable Version Info at Matplotlib Top Level

## Objective

Matplotlib exposes its version only as the string `matplotlib.__version__`. Comparing strings is unreliable: `"3.10" < "3.9"` is `True` lexicographically. Users who write version guards (`if mpl version >= X: ...`) need a value at the top level of the `matplotlib` package that compares correctly.

**User:** Downstream library authors and end users who branch on the installed Matplotlib version.

**What we're building:** A new public, top-level attribute on `matplotlib` that represents the installed version in a correctly comparable form. The issue names two candidates:

- **Option A:** a `version_info` tuple, comparable with other tuples. This is the more common convention in other packages and is the reporter's suggested default for simplicity.
- **Option B:** a `LooseVersion`-style object, comparable with version strings. The reporter slightly prefers this.

Choosing between them, or adopting both, is the main decision. See Open Questions.

**User stories:**

- As a library author, I can write `matplotlib.version_info >= (3, 5)` (Option A) and get the correct result for every release, including 3.10+ and 4.x.
- As a user, I can find out how to do version checks from the documentation without parsing `__version__` myself.

## Assumptions

1. `matplotlib.__version__` exists today and must keep its current value and type. This change is purely additive.
2. The attribute name for Option A is `version_info`, mirroring `sys.version_info`. The issue calls this "pretty common."
3. `version_info` must stay consistent with `__version__` for every build type Matplotlib produces: final releases, release candidates, dev builds, and builds whose version string carries a local or git suffix. The exact formats of these strings are unknown from the issue.
4. `distutils.LooseVersion` is not an acceptable implementation choice, because `distutils` is deprecated and removed in recent Python versions. If Option B is chosen, an equivalent comparable version object would be needed. Whether a dependency such as `packaging` is available or acceptable is unknown.
5. Comparisons must not raise for pre-release or dev versions. They must order correctly with respect to the final release.
6. No change to Matplotlib's plotting behavior or other public API is in scope.
7. The public attribute should be documented, with an API/what's-new entry. The exact documentation location and process are unknown.

## Tech Stack

- Language: Python. The supported version range is **unknown**.
- How Matplotlib currently computes `__version__` is **unknown**. It could be a static string, a generated file, or a build-time version tool, and the answer constrains how `version_info` can be derived.
- Version-parsing dependency: **unknown** whether one is available. This matters for Option B.

## Commands

All commands are **unknown**. The issue does not provide them.

```
Build: UNKNOWN
Test:  UNKNOWN
Lint:  UNKNOWN
Docs:  UNKNOWN
```

## Project Structure

**Unknown.** The issue does not state:

- the file where `matplotlib.__version__` is defined or assigned,
- where the tests for top-level package attributes live,
- where API changes and what's-new entries are recorded.

These must be identified before planning.

## Code Style

**Unknown.** No code from the repository is shown. Follow the existing Matplotlib conventions in the file that defines `__version__`. Intended usage, illustrative only and not implementation:

```python
import matplotlib
if matplotlib.version_info >= (3, 10):   # must be True for 3.10.x, False for 3.9.x
    ...
```

## Testing Strategy

- Framework and test locations: **unknown**.
- Required behaviors to test:
  - The new attribute is importable from the top-level `matplotlib` namespace.
  - It is consistent with `__version__`. For example, its leading components equal the parsed major, minor, and micro from `__version__`.
  - Ordering is correct for these representative versions:
    - `3.9.0 < 3.10.0`
    - `3.10.0 < 4.0.0`
    - `X.Y.0rc1 < X.Y.0`
    - a dev or pre-release version of X.Y.0 sorts below the X.Y.0 final release
  - Pre-release, dev, and local-suffix version strings do not raise during parsing or comparison.
  - The attribute is immutable, or at least a tuple or tuple-like type for Option A.
- Coverage expectation: every branch of the version-parsing logic is exercised.

## Boundaries

- **Always:**
  - Keep `__version__` unchanged.
  - Derive the new attribute from the same source as `__version__` so they cannot drift.
  - Add tests and documentation for the new public API.
- **Ask first:**
  - Choosing Option A vs. B vs. both.
  - Adding a new runtime dependency, such as a version-parsing library.
  - Changing how `__version__` itself is generated.
  - The exact structure of non-final releases in the tuple.
- **Never:**
  - Use the deprecated `distutils.LooseVersion`.
  - Break or rename existing version attributes.
  - Make importing `matplotlib` noticeably slower or fail because version parsing failed.

## Success Criteria

1. `import matplotlib; matplotlib.<new_attr>` works on a fresh install with no extra user steps.
2. For final releases, comparisons against the agreed comparand type are correct. That comparand is tuples for Option A or version strings for Option B. In particular, `3.10 > 3.9` and `4.0 > 3.10`.
3. Pre-release and dev builds produce a valid value, compare without error, and sort before their corresponding final release.
4. The value is always consistent with `__version__`, and a test enforces this.
5. The attribute appears in public documentation with a usage example, and a changelog/what's-new entry exists.
6. The existing test suite passes. The command for this is unknown.

## Open Questions

1. **Option A, B, or both?** Should we expose a `version_info` tuple (common convention), a comparable version object (reporter's slight preference), or both?
2. **Tuple shape for Option A.** Should it be `(major, minor, micro)` only, or include release level and serial like `sys.version_info`, e.g. `(3, 10, 0, 'candidate', 1)`? Should it be a named tuple with `.major`, `.minor`, and so on?
3. **Non-final versions.** How should dev builds and git-local suffixes map into the tuple or object? Should they sort below the next final release?
4. **Option B implementation.** If a comparable object is wanted, which class should back it, given that `distutils` is unavailable? Is a dependency on a version-parsing library acceptable?
5. **Source of truth.** Where and how is `__version__` currently computed? Is it static or generated at build time, and can `version_info` be derived at import time or must it be generated alongside it?
6. **Naming.** Is `version_info` the agreed name? If Option B is chosen, what should that attribute be called?
7. **Deprecations.** Should any existing internal version-comparison helpers be migrated to the new attribute, or is that out of scope?
8. **Repository details.** What are the build, test, lint, and docs commands? Which files define `__version__`, and where do tests and changelog entries go?