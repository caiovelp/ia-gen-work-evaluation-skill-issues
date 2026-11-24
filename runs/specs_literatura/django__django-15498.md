## Summary
An empty string value for the `If-Modified-Since` HTTP header now raises an exception. It used to be ignored. The report says this regression started with commit `d6aff369ad3`.

## Steps to reproduce
1. Use a version that includes commit `d6aff369ad3`.
2. Send a request where the `If-Modified-Since` header is set to an empty string (`""`).
3. Let the request go through the code that handles `If-Modified-Since`.

(The original report does not give the exact entry point, function or request setup.)

## Observed behavior
An exception is raised when the `If-Modified-Since` header is an empty string.

## Expected behavior
An empty `If-Modified-Since` header should be ignored, as it was before commit `d6aff369ad3`.

## Stack trace / error output
Not provided in the original report.

## Test case
Not provided in the original report.

## Code example
Not provided in the original report.

## Version and environment
- The regression was introduced in commit `d6aff369ad3`. The behavior was correct before this commit.
- No other version or environment details are provided in the original report.