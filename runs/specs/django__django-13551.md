# Spec: Invalidate Password Reset Tokens When a User's Email Changes

## Objective

**Problem.** A password reset token stays valid after the account's email address changes. This is the sequence:

1. An account exists with email `foo@…`.
2. Someone requests a password reset for that email. The token is issued and not yet used.
3. The account owner changes the email address on the account.
4. Someone uses the original reset link and token.
5. **Expected:** the token is rejected. **Actual:** the token is accepted and the password can be reset.

**Why it matters.** The email address on file defines who controls the account. After it changes, a reset link sent to the old address should no longer grant access. Today, whoever controls the old mailbox can still take over the account.

**Users affected.**
- End users whose accounts can be reset through emailed tokens.
- Developers who use the framework's `PasswordResetTokenGenerator`, including those with custom user models.

**Proposed direction (from the issue, not yet approved).**
- Include the user's email address in the data hashed by `PasswordResetTokenGenerator._make_hash_value()`. Any change to the email then produces a different hash, so earlier tokens fail the check.
- The design must handle the fact that `AbstractBaseUser` does not require an email field.
- An alternative raised in the issue: move the hash-value contribution onto the user model, similar to `get_session_auth_hash()`.

**Acceptance criteria (user stories).**
- As an account owner, after I change my email, any reset token issued before the change is rejected.
- As an account owner whose email has not changed, a valid, unexpired, unused reset token still works.
- As a developer with a custom user model that has no email field, token generation and checking still work without errors.

## Assumptions

1. The codebase is Django, or a framework with the same `django.contrib.auth` design. This is inferred from `PasswordResetTokenGenerator`, `_make_hash_value()`, `AbstractBaseUser` and `get_session_auth_hash()`.
2. `_make_hash_value(user, timestamp)` already folds user state into the hash. That state includes the password hash and last-login timestamp, so a password change or login already invalidates tokens. Adding the email follows the same pattern.
3. The email field should be resolved through the model's configured email-field name, not a hard-coded `email` attribute. Assumed accessor: the `get_email_field_name()` pattern on `AbstractBaseUser`. Not verified.
4. A missing email field, or an email value of `None`, is treated as an empty string in the hash.
5. The email value is hashed as stored, with no case or whitespace normalization.
6. After this change, all outstanding reset tokens become invalid on upgrade, because the hash input changes for every user. This is assumed acceptable for short-lived reset tokens if it is documented in release notes. See Open Questions.
7. The token format, timeout setting and public API of `make_token()` / `check_token()` stay the same.
8. Third-party subclasses that override `_make_hash_value()` keep their own behavior and are not changed by this work.

## Tech Stack

- **Language/framework:** Python, Django auth (`django.contrib.auth`). This is assumed; versions are unknown.
- **Components named in the issue:** `PasswordResetTokenGenerator`, `_make_hash_value()`, `AbstractBaseUser`, `get_session_auth_hash()`.
- **Exact module paths and supported Python/Django versions:** unknown.

## Commands

| Purpose | Command |
|---|---|
| Build | Unknown (not provided in the issue) |
| Test (full suite) | Unknown |
| Test (auth/token tests only) | Unknown |
| Lint / format | Unknown |

## Project Structure

| Item | Location |
|---|---|
| `PasswordResetTokenGenerator` source | Unknown (assumed: the auth app's tokens module) |
| `AbstractBaseUser` source | Unknown (assumed: the auth app's base user module) |
| Existing token tests | Unknown (assumed: the auth tests package) |
| Release notes / docs for the auth token behavior | Unknown |

## Code Style

- Follow the existing conventions of the module containing `PasswordResetTokenGenerator`. The real code was not visible, so no snippet is given here.
- Resolve the email via the user model's configured email-field name. Do not assume an attribute called `email`.
- Keep changes minimal and local to the hash-value computation, unless the model-method alternative is approved.

## Testing Strategy

- **Framework:** the project's existing test framework (unknown; assumed Django's test runner / `TestCase`).
- **Location:** alongside the existing password-reset token tests (path unknown).
- **Level:** unit tests on the token generator, plus at least one test that exercises the full reset flow if such tests already exist.

**Required cases.**
1. **Regression.** Generate a token, change the user's email, save, then call `check_token`. The result must be `False`.
2. **Control.** Generate a token, change nothing, then call `check_token`. The result must be `True`.
3. **Custom user without an email field.** Token generation and checking must succeed with no `AttributeError`.
4. **Email set to `None` or empty.** Token generation and checking must succeed.
5. **Custom email field name.** Use a custom user model whose email field name is not `email`. Changing that field must invalidate the token.
6. **Existing invalidation still works.** Changing the password or `last_login` still invalidates tokens. This covers the existing tests.

**Coverage expectation:** the new branches have 100% coverage, specifically the email present, absent and `None` paths.

## Boundaries

- **Always:**
  - Run the full auth test suite before committing.
  - Keep `make_token` / `check_token` signatures unchanged.
  - Handle user models without an email field.
  - Add a regression test for the reported sequence.
- **Ask first:**
  - Moving the hash contribution onto the user model (the `get_session_auth_hash()`-style alternative).
  - Normalizing the email (case or whitespace).
  - Any change to the token format, algorithm or timeout.
  - Adding a migration or deprecation path for tokens issued before the upgrade.
  - Documentation or release-note wording about invalidating outstanding tokens.
- **Never:**
  - Weaken existing invalidation inputs (password hash, last login, timestamp).
  - Hard-code the `email` attribute name.
  - Remove or loosen existing failing tests without approval.
  - Change security-sensitive comparison logic (for example, constant-time compare).

## Success Criteria

1. Following the issue's sequence (request reset, change email, use token), `check_token` returns `False` and the reset view rejects the link.
2. Tokens for users whose email has not changed still validate within the timeout.
3. User models without an email field, or with a `None` / empty email, generate and validate tokens without errors.
4. User models with a custom email field name are covered. Changing that field invalidates tokens.
5. All existing auth/token tests pass unchanged.
6. The behavior change is documented: email changes invalidate reset tokens, and outstanding tokens are invalidated on upgrade. Wording and location must be approved.

## Open Questions

1. **Hash change or model method?** Should the fix only add the email to `_make_hash_value()`? Or should the hash contribution be moved onto the user model (like `get_session_auth_hash()`) so custom user models can control which fields invalidate tokens?
2. **Upgrade impact.** Is it acceptable that every outstanding reset token is invalidated when this ships? Or is a transition period required, for example accepting tokens under the legacy hash for one timeout window?
3. **Email normalization.** Should a case-only change (`Foo@…` to `foo@…`) invalidate tokens? Should the email be normalized before hashing?
4. **Missing email.** For users without an email field, or with a null email, is substituting an empty string the desired behavior?
5. **Scope.** Should other identity fields also invalidate tokens, such as username or `USERNAME_FIELD` changes? Or is this strictly about email?
6. **Release target.** Which versions or branches should receive this fix? Is it treated as a security fix requiring a backport?
7. **Documentation.** Where are the commands, test paths and release-note files for this project?