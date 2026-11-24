## Summary

A password reset token stays valid after the user changes their email address. A reset link requested for the old email address can still be used to reset the password, even though the account's email has since changed. Token generation is handled by `PasswordResetTokenGenerator`. Note that `AbstractBaseUser` does not require a user to have an email address.

## Steps to reproduce

1. Have a user account with the email address `foo@…`.
2. Request a password reset for that email address. Do not use the reset email yet.
3. Change the account's email address from `foo@…` to a different address.
4. Use the password reset link/token from the email sent in step 2.

## Observed behavior

The token from the password reset email is accepted, and the password reset is allowed.

## Expected behavior

The token should be rejected, because the account's email address changed after the token was issued.

## Stack trace / error output

Not provided in the original report.

## Test case

A minimal test case derived from the reported steps (no code was provided in the original report):

1. Create a user with email `foo@…`.
2. Generate a password reset token for that user with `PasswordResetTokenGenerator`.
3. Change the user's email to a different address and save the user.
4. Check the token from step 2 against the updated user.
5. Expected: the token is reported as invalid. Observed: the token is reported as valid.

## Code example

Not provided in the original report.

## Version and environment

Not provided in the original report.