# Spec: FileBasedCache `has_key` Race-Condition Fix

## Objective

`django.core.cache.backends.filebased.FileBasedCache.has_key()` checks `os.path.exists(fname)` and then calls `open(fname, "rb")`. This is a time-of-check/time-of-use (TOCTOU) race. Another thread or process can delete the cache file between the two calls. Deletion can come from:

- the `_is_expired()` method of a concurrent reader, which deletes expired files;
- `delete()`;
- culling;
- `clear()`.

When the race hits, `has_key()` raises `FileNotFoundError` instead of returning `False`. The error also reaches callers built on `has_key()`, such as `add()` and therefore `get_or_set()`.

The reported traceback is:

```
File "django/core/cache/backends/base.py", line 229, in get_or_set
    self.add(key, default, timeout=timeout, version=version)
File "django/core/cache/backends/filebased.py", line 26, in add
    if self.has_key(key, version):
File "django/core/cache/backends/filebased.py", line 94, in has_key
    with open(fname, "rb") as f:
FileNotFoundError: [Errno 2] No such file or directory: '/app/var/cache/<hash>.djcache'
```

The race is most likely when many threads or processes read the same expired key at once.

**Users:** Django applications that use the file-based cache backend under concurrency, such as multi-threaded or multi-process WSGI/ASGI servers.

**Desired behavior:**

- If the cache file disappears at any point before or during the check, `has_key()` returns `False`.
- `has_key()` never raises `FileNotFoundError` in this situation.
- Callers like `add()` and `get_or_set()` keep working normally and see a "key absent" outcome.

### User stories / acceptance criteria

- As a developer using `FileBasedCache` under concurrent load, I want `cache.has_key(k)` to return `False` instead of raising when the entry file is deleted concurrently.
- As a developer calling `cache.get_or_set(k, default)` on an expired key from many threads, I want no `FileNotFoundError` to surface.
- Existing semantics stay the same:
  - `has_key()` returns `True` for a present, non-expired entry.
  - `has_key()` returns `False` for a missing or expired entry.
  - Expired entries are still deleted when they are detected.

## Assumptions

1. The fix lives in `django/core/cache/backends/filebased.py`, the path shown in the traceback. Exact line numbers in the current codebase are unknown and may differ from the report.
2. The desired semantics follow the pattern other `FileBasedCache` read paths are assumed to use: attempt `open()` directly and treat `FileNotFoundError` as "key not present". This is not verified because the repository is not visible.
3. Only `FileNotFoundError` gets the "key absent" treatment. Other `OSError`s keep propagating as they do today:
   - `PermissionError`;
   - `IsADirectoryError`;
   - disk/I/O errors.
4. `_is_expired()` behavior (reads the expiry and deletes the file if it has expired) is out of scope. Its own deletion step is assumed to already tolerate a missing file. If not, that is an open question (see below).
5. The public API stays unchanged: signature `has_key(self, key, version=None)` and a boolean return value.
6. No new dependencies, no settings changes, and no change to the on-disk cache format.
7. A deterministic test is preferred over a real multi-threaded stress test. One way is to simulate deletion between the existence check and `open()`, for example by mocking `os.path.exists` or `open`.

## Tech Stack

- Python, within the Django codebase. Supported Python and Django versions: **unknown** (not stated in the issue).
- Component: Django cache framework, `FileBasedCache` backend (`django/core/cache/backends/filebased.py`), with `django/core/cache/backends/base.py` (`get_or_set`) as an indirect caller.

## Commands

The issue does not provide these, and they cannot be confirmed without repository access.

```
Build: unknown (pure-Python change; likely none required)
Test:  unknown — Django's test runner invocation for the cache test suite must be confirmed
Lint:  unknown — project linters/formatters must be confirmed
Dev:   not applicable
```

## Project Structure

Only these paths are known, from the traceback:

```
django/core/cache/backends/filebased.py → FileBasedCache (has_key, add, _is_expired)
django/core/cache/backends/base.py      → BaseCache (get_or_set → add)
```

The location of the cache backend tests is **unknown**, though a cache test module presumably exists. Release notes and docs locations are also **unknown**.

## Code Style

Use the existing style of `filebased.py`. The only verbatim snippet available is the current (buggy) code from the issue:

```python
def has_key(self, key, version=None):
    fname = self._key_to_file(key, version)
    if os.path.exists(fname):
        with open(fname, "rb") as f:
            return not self._is_expired(f)
    return False
```

Conventions to follow:

- Keep the method small.
- Use context managers for file handles.
- Catch the narrowest exception possible.
- Match naming and formatting of neighboring methods. The formatter and line-length rules are unknown and must be confirmed.

## Testing Strategy

- **Framework:** Django's own test suite. The exact runner command and test module are unknown.
- **Regression test (required):** a unit test that deterministically reproduces the race. The file must exist at the check and be gone at `open()`. Example approach: create the cache entry, then patch so the file is removed just before opening. The test asserts that `has_key()` returns `False` and does not raise.
- **Caller-level test (recommended):** with the same simulated race, `add()` (and so `get_or_set()`) completes without raising `FileNotFoundError`.
- **Existing behavior tests:** the existing cache test suite for the file-based backend must still pass, covering:
  - a present key returns `True`;
  - a missing key returns `False`;
  - an expired key returns `False` and its file is removed.
- **Non-goal:** no flaky timing-based multi-threaded stress tests in the suite.

## Boundaries

**Always:**

- Keep `has_key()`'s public signature and boolean contract.
- Catch only `FileNotFoundError` for the "absent" path.
- Add a regression test that fails before the fix and passes after it.
- Run the full file-based cache test suite before submitting.

**Ask first:**

- Changing `_is_expired()`, `delete()`, culling, or `clear()` behavior.
- Broadening exception handling to `OSError`.
- Adding file locking.
- Adding a release note or backporting to stable branches.
- Refactoring other `FileBasedCache` methods that may share the exists-then-open pattern.

**Never:**

- Swallow unrelated exceptions such as permission or I/O errors.
- Change the on-disk cache format.
- Add dependencies.
- Introduce timing-dependent or flaky tests.
- Remove or weaken existing tests.

## Success Criteria

1. When the cache file is removed between the existence check and the open, or at any point before the open, `FileBasedCache.has_key()` returns `False` and raises no exception.
2. `add()` and `get_or_set()` do not raise `FileNotFoundError` under the same simulated race.
3. For present, missing, and expired entries, `has_key()` returns the same results as before the change. Expired entries are still removed.
4. A new deterministic regression test covers the race and passes. The full existing cache test suite passes.
5. Exceptions other than `FileNotFoundError` from `open()` still propagate unchanged.

## Open Questions

1. Do other `FileBasedCache` methods have the same exists-then-open TOCTOU pattern, and should they be fixed in this change or tracked separately? Candidates include `get`, `touch`, and `_is_expired`'s own delete step.
2. Does `_is_expired()` (or `_delete()`) already tolerate the file being deleted by another thread during its own removal step? If not, is that in scope?
3. Should the fix be backported to supported stable branches? Does it need a release note?
4. What are the exact test command, test module location, and lint/format tooling for this repository?
5. Which Django and Python versions does this fix target? The report's line numbers (e.g. `base.py` line 229) may not match the current main branch.