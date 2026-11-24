# Spec: Log Exceptions Handled in `Signal.send_robust()`

## Objective

`Signal.send_robust()` catches exceptions raised by signal receivers and returns them in its result list. It currently does not log them. Unless the caller inspects the return value, the failures are invisible.

**Goal:** When `send_robust()` catches an exception from a receiver, it logs it with `logger.exception()` in the `except` clause. The exception and its traceback then reach users' error-handling tools (e.g. Sentry) through standard logging.

**Rationale (from issue):**
- Django already logs exceptions in similar situations, such as missing template variables.
- Developers should handle *expected* exceptions with a `try` inside the receiver. Anything that reaches `send_robust()`'s handler is unexpected and worth surfacing.

**Users:**
- Developers who use `send_robust()` and want visibility into receiver failures.
- Operators who rely on log-based error aggregation.

**User story:** As a developer, when one of my signal receivers raises during `send_robust()`, I want an error-level log record with the traceback. That way I can find and fix the failure without changing how my code handles the return value.

## Assumptions

1. The existing behaviour of `send_robust()` is unchanged. It still catches `Exception`, still continues to the remaining receivers, and still returns `(receiver, exception)` tuples.
2. Logging is added only to `send_robust()`, not to `send()`. `send()` propagates exceptions, so the caller sees them already.
3. The log call is `logger.exception(...)` inside the existing `except` clause. That makes the level ERROR and attaches the traceback (`exc_info`).
4. The logger is a module-level `logging.getLogger(...)` following Django's existing logger naming convention. The exact name is not given in the issue (see Open Questions).
5. The message identifies the failing receiver, and possibly the signal/sender, so the log entry is actionable.
6. Log records are emitted through Python's standard `logging` module only. No new dependencies are added.
7. If an async variant of `send_robust()` exists in the target version, it should behave the same way. This is unverified (see Open Questions).

## Tech Stack

- Python, standard library `logging`.
- Django's signal dispatch module. The exact file path is **unknown** (not stated in the issue).
- Python and Django versions: **unknown**.

## Commands

| Purpose | Command |
|---|---|
| Build | Unknown (not stated in issue) |
| Test (full) | Unknown |
| Test (signals/dispatch only) | Unknown |
| Lint / format | Unknown |

## Project Structure

| Item | Location |
|---|---|
| `Signal` class / `send_robust()` implementation | Unknown — Django's dispatch module; exact path not visible |
| Tests for signal dispatch | Unknown |
| Logging documentation (list of Django loggers) | Unknown |
| Signals documentation (`send_robust()` reference) | Unknown |
| Release notes for the target version | Unknown |

## Code Style

- Follow the existing conventions of the dispatch module and Django's codebase. These are not visible here.
- Use a module-level logger, not the root logger.
- Use lazy `%`-style logging arguments (e.g. `logger.exception("... %r ...", receiver)`) rather than pre-formatted strings, consistent with standard `logging` practice.
- Keep the change minimal: one logger definition and one logging call in the `except` clause.

## Testing Strategy

- **Framework:** Django's test suite. The runner command is unknown.
- **Level:** Unit tests on `Signal.send_robust()`.
- **Cases:**
  1. A receiver that raises produces exactly one ERROR-level record on the chosen logger. The record's `exc_info` contains the raised exception, and its message identifies the receiver.
  2. The return value still contains `(receiver, exception)` for the failing receiver.
  3. Later receivers are still called after one raises.
  4. Receivers that succeed produce no log records.
  5. With multiple failing receivers, there is one log record per failure.
  6. If an async `send_robust` variant exists, the same assertions apply to it.
- **Technique:** Capture logs with `assertLogs(<logger name>, "ERROR")`, or equivalent.
- **Regression:** Existing signal/dispatch tests pass unchanged.

## Boundaries

- **Always:**
  - Preserve `send_robust()`'s return contract and its exception-swallowing behaviour.
  - Add tests for the new logging.
  - Document the new logger and the behaviour change in the docs and release notes.
- **Ask first:**
  - Choosing or creating a new logger name.
  - Logging in `send()` or anywhere other than `send_robust()`.
  - Changing the log level from ERROR.
  - Adding configuration to disable the logging.
- **Never:**
  - Re-raise exceptions from `send_robust()`.
  - Change which exceptions are caught.
  - Add third-party dependencies.
  - Log at a level that bypasses the user's logging configuration.

## Success Criteria

- [ ] When a receiver raises an `Exception` subclass during `send_robust()`, exactly one ERROR-level log record is emitted on the designated Django logger.
- [ ] That record includes the traceback (`exc_info` set) and identifies the receiver.
- [ ] `send_robust()` return values and the receiver invocation order are identical to current behaviour.
- [ ] No log records are emitted when all receivers succeed.
- [ ] `send()` behaviour is unchanged.
- [ ] New tests cover the cases above, and the existing test suite passes.
- [ ] Documentation lists the logger and describes the logging in `send_robust()`, and a release note mentions the change.

## Open Questions

1. **Logger name:** Which logger should be used? Possible choices are a new logger such as `django.dispatch`, or an existing Django logger. If it is new, it must be added to the logging docs.
2. **Message content:** Should the message include the signal and sender in addition to the receiver? What is the exact wording?
3. **Async variant:** Does the target Django version have an async `send_robust`, and should it log identically?
4. **Opt-out:** Do users need a way to suppress this logging beyond standard logger configuration? The current assumption is no.
5. **Default logging config:** Will Django's default `LOGGING` configuration emit these records anywhere, for example to the console or to admin emails? Is that acceptable as the default?
6. **Target version:** Which release is this for, so the release notes go in the right place?
7. **Commands and paths:** Which test runner command, module path, and docs locations apply? None are given in the issue.