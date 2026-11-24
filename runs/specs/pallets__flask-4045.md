# Spec: Reject Blueprint Names Containing a Dot

## Objective

Blueprint names should not be allowed to contain a dot (`.`). When someone creates a blueprint with a dotted name, the framework should raise an error.

**Why:** Blueprints can now be nested, so every dot in a fully qualified endpoint or blueprint name is significant. The dot is the separator between nesting levels. A dot inside a single blueprint's own name makes the name ambiguous. For example, `"a.b"` could be one blueprint named `a.b`, or a blueprint `b` nested under `a`. That ambiguity can break endpoint resolution, URL building and lookups keyed by blueprint name.

**Precedent:** Version 1.0 already added an error for endpoint names that contain a dot. The same check was never added for blueprint names. This change closes that gap.

**Users affected:**
- Application and extension developers who define blueprints.
- Maintainers of the framework, who rely on dot-delimited names being unambiguous.

**User stories / acceptance criteria:**
- As a developer, if I create a blueprint whose name contains a `.`, I get an immediate error that explains why.
- As a developer, if my blueprint name has no `.`, nothing changes for me.
- As a maintainer, I can rely on blueprint names never containing the nesting separator.

## Assumptions

1. The project is Flask (Python). The terms "blueprint", "endpoint" and "1.0", plus "blueprints can be nested", suggest this, but the issue does not say so.
2. The check belongs where the blueprint is constructed, so the error is raised at definition time and not later at registration time.
3. Only the `name` given to the blueprint is validated. Other identifiers are out of scope: import name, URL prefix, subdomain, and endpoint names (which are already validated).
4. Any occurrence of `.` makes the name invalid, including leading, trailing or repeated dots. No other characters are restricted by this change.
5. The error type and message style should match the existing endpoint-name check from 1.0, so the two behave alike. The exact existing type is unknown from the issue.
6. This is a breaking change for anyone currently using dotted blueprint names. It will be documented in the changelog. Whether to add a deprecation period first is an open question.
7. Nested registration builds the dotted path from parent and child names internally. The new validation must not reject those internally composed names, only the name a user passes in.

## Tech Stack

- Language: Python (assumed). The version is unknown.
- Framework: Flask (assumed). The target release or version number is unknown.
- Dependencies: no new dependencies expected.

## Commands

The issue does not show any commands. All are unknown and must be confirmed from the repository.

```
Build:   UNKNOWN
Test:    UNKNOWN (likely a pytest invocation — unconfirmed)
Lint:    UNKNOWN
Dev:     N/A (library)
```

## Project Structure

The issue does not show the repository layout. All paths are unknown.

```
[blueprint implementation module] → UNKNOWN path
[existing endpoint-dot validation] → UNKNOWN path (reference for consistency)
[blueprint tests]                 → UNKNOWN path
[changelog]                       → UNKNOWN path
[blueprint documentation]         → UNKNOWN path
```

## Code Style

Unknown, since no code is visible in the issue. Conventions to follow:
- Mirror the style of the existing 1.0 endpoint-name dot check: the same kind of exception and a similar message wording.
- The error message should name the offending value and explain that dots are not allowed because they separate nested blueprint names.

## Testing Strategy

- Framework: the project's existing test framework (unknown, likely pytest).
- Location: alongside the existing blueprint tests (path unknown).
- Test levels: unit tests are sufficient, because this is input validation at construction time.
- Cases to cover:
  - A name with a single dot (e.g. `"a.b"`) raises the error.
  - Names with a leading, trailing or multiple dots raise the error.
  - A valid name with no dot still constructs without error.
  - Nested blueprint registration still works with valid names. Internally composed dotted names must not trigger the new error.
  - The existing endpoint-name dot check is unaffected.
  - The error message mentions the dot restriction.
- Coverage: the new validation branch is fully covered. Overall coverage expectations are unknown.

## Boundaries

- **Always:**
  - Keep behavior and error type consistent with the existing endpoint-name check.
  - Add tests for both rejected and accepted names.
  - Add a changelog entry that describes the behavior change.
  - Run the full test suite before committing.
- **Ask first:**
  - Choosing a deprecation warning period instead of an immediate error.
  - Changing the exception type used by the existing endpoint check.
  - Extending validation to other characters or other identifiers.
  - Deciding which release this ships in (patch or minor).
- **Never:**
  - Change the behavior of valid blueprint names.
  - Break nested blueprint registration.
  - Remove or weaken the existing endpoint-name validation.
  - Silently rewrite dotted names, for example by replacing the dots, instead of raising.

## Success Criteria

- [ ] Creating a blueprint whose name contains at least one `.` raises an error at construction time.
- [ ] The error message clearly states that blueprint names may not contain a dot.
- [ ] The error type is consistent with the existing endpoint-name dot error, or the decision in Open Question 1 is followed.
- [ ] Blueprints with dot-free names behave exactly as before. All existing tests pass.
- [ ] Nested blueprint registration with valid names still works and produces correct dotted endpoint names.
- [ ] New tests cover rejected names (single, leading, trailing and multiple dots) and accepted names.
- [ ] A changelog entry documents the new restriction.
- [ ] Documentation that describes blueprint naming mentions the restriction, if such documentation exists.

## Open Questions

1. **Exception type:** Should this raise the same exception type as the 1.0 endpoint check, or a more appropriate one such as `ValueError`? If the endpoint check uses `assert`, should both be aligned?
2. **Deprecation vs. hard error:** Should the release first emit a deprecation warning for dotted blueprint names, or raise immediately? The issue says "raise error", but this may break existing users.
3. **Target release:** Which version should this ship in? Is it a bugfix release (treated as an oversight from nesting support) or a feature release?
4. **Where to validate:** Is constructor-time validation acceptable? Or are there cases where the name is set or changed after construction, for example renaming at registration via a name option, that also need checking?
5. **Registration-time name override:** If blueprints can be registered under an alternate name, must that alternate name also be validated?
6. **Other characters:** Should any other characters (e.g. whitespace or empty names) be rejected now, or is this strictly limited to dots?
7. **Documentation:** Where is blueprint naming documented, so the restriction can be added there?