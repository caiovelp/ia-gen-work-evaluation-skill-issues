# Spec: Reject Trailing Newline in Username Validators

## Objective

`ASCIIUsernameValidator` and `UnicodeUsernameValidator` in `contrib.auth.validators` currently use the regex `r'^[\w.@+-]+$'`. In Python regexes, `$` also matches just before a trailing newline. As a result, both validators accept usernames that end in `\n` (for example `"alice\n"`).

The intended behavior is that a username contains only word characters and `.`, `@`, `+`, `-`. Any other character, including a trailing newline, should be rejected.

**Who is affected:** Developers who rely on the built-in username validators, and end users or administrators who could otherwise create accounts whose usernames look identical to existing ones but end in a newline.

**What success looks like:** Both validators reject any username that ends with a newline. Their behavior for every currently valid username stays the same.

**User stories / acceptance criteria:**
- As a developer, when I validate `"alice\n"` with `ASCIIUsernameValidator`, a validation error is raised.
- As a developer, when I validate `"alice\n"` with `UnicodeUsernameValidator`, a validation error is raised.
- As a developer, usernames that were valid before (e.g. `"alice"`, `"a.b@c+d-e"`, and Unicode word characters for the Unicode validator) are still accepted.
- As a developer, usernames that were invalid before are still rejected.

## Assumptions

1. The project is Django, and the validators live in the module the issue names, `contrib.auth.validators` (likely `django/contrib/auth/validators.py`). I have not seen the exact path.
2. Both validators are regex-based validators that define a `regex` attribute and possibly `flags`. The ASCII variant restricts `\w` to ASCII, probably via `re.ASCII`, and the Unicode variant does not. Whatever character classes and flags exist today are kept as they are.
3. The fix proposed in the issue, anchoring with `\A` and `\Z` instead of `^` and `$`, keeps every current match except strings with a trailing newline. No other behavior change is intended.
4. A trailing `\r\n` is already rejected, because `\r` is not in the allowed character class. Only a lone trailing `\n` slips through today.
5. Existing usernames already stored with a trailing newline are out of scope. This change only affects validation from now on, and no data migration is required.
6. This is a fix to the validators' behavior. It does not change the public API, class names, or error messages.
7. Changing the `regex` attribute may surface in Django's migration autodetector wherever these validators are serialized on model fields (e.g. `User.username`). That is acceptable, or not, depending on project policy. See Open Questions.

## Tech Stack

- Language: Python. The supported versions are unknown, but the behavior of `$`, `\A`, and `\Z` is stable across Python 3.
- Framework: Django (`contrib.auth`).
- Dependencies: Python standard library `re` only.

## Commands

The issue does not show any build, test, or lint commands, so all of them are unknown.

```
Build: unknown
Test:  unknown (project test runner not visible in the issue)
Lint:  unknown
Dev:   n/a
```

## Project Structure

Only the following comes from the issue:

```
contrib/auth/validators  → ASCIIUsernameValidator, UnicodeUsernameValidator (exact file path unknown)
```

The location of the existing tests for these validators is unknown. They are presumably in an auth-related test module.

## Code Style

- The current pattern, quoted from the issue, is `r'^[\w.@+-]+$'`.
- The direction the issue proposes is `r'\A[\w.@+-]+\Z'`. It uses raw strings and anchors to the whole string with `\A` and `\Z`.
- Beyond this, the project's conventions are unknown. Follow the surrounding code in the validators module.

## Testing Strategy

- **Level:** Unit tests on the two validator classes.
- **Framework/location:** Unknown. Add the cases alongside the existing tests for the username validators.
- **Required cases (for each validator):**
  - Invalid: `"username\n"`, which is the regression case.
  - Invalid: an embedded newline such as `"user\nname"`, to confirm it is still rejected.
  - Invalid: a leading newline `"\nusername"`, to confirm it is still rejected.
  - Valid: existing valid examples still pass, e.g. `"joe"`, `"René"` (Unicode validator only), and `"a.b@c+d-e"`.
  - Invalid: existing invalid examples still fail, e.g. strings containing spaces or disallowed punctuation, and non-ASCII characters for the ASCII validator.
- **Coverage expectation:** Every changed validator has at least one test that fails before the fix and passes after it.

## Boundaries

- **Always:**
  - Keep the allowed character set and regex flags exactly as they are, so that only the anchoring changes behavior.
  - Add regression tests for the trailing-newline case in both validators.
  - Run the existing test suite before committing.
- **Ask first:**
  - Whether to generate migrations for models whose fields reference these validators, if the regex change shows up in the autodetector.
  - Whether to add a release note or changelog entry, given the security-adjacent nature of the bug.
  - Whether to audit and fix other `^…$`-anchored regex validators elsewhere in the codebase as part of this change.
- **Never:**
  - Strip or normalize input to "fix" the problem. Validation must reject the input, not silently alter it.
  - Change validator class names, the public API, or error messages without approval.
  - Remove or weaken existing tests.

## Success Criteria

1. `ASCIIUsernameValidator()("username\n")` raises a validation error.
2. `UnicodeUsernameValidator()("username\n")` raises a validation error.
3. Every username accepted by either validator before the change is still accepted, and every one rejected before is still rejected, apart from the trailing-newline case.
4. The new regression tests pass, and the existing test suite passes unchanged.
5. The ASCII validator still rejects non-ASCII word characters, and the Unicode validator still accepts them.

## Open Questions

1. Does changing the `regex` attribute cause the migration autodetector to report changes for `auth.User` or custom user models? If it does, should a migration be included, or should the change be handled so that no new migration is required?
2. Should the release notes call this out, possibly as a security-relevant fix since it allows look-alike usernames? Which release or branches should it target?
3. Should existing users whose stored usernames end in a newline be detected or handled, for example with documentation or a management check? Or is that explicitly out of scope?
4. Are there other regex-based validators in the codebase that use `^…$` and are vulnerable to the same quirk? Should they be fixed in this change or tracked separately?
5. What are the exact file path, test location, and test command for running the auth validator tests?