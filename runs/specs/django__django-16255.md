# Spec: Sitemap `get_latest_lastmod()` handles empty sitemaps with callable `lastmod`

## Objective

When a Django sitemap defines `lastmod` as a callable (a method) and `items()` returns an empty sequence, `Sitemap.get_latest_lastmod()` raises an unhandled error. `max()` gets an empty list and raises `ValueError: max() arg is an empty sequence`. The sitemap index view (`django.contrib.sitemaps.views.index`) calls `get_latest_lastmod()`, so the error propagates and `/sitemap.xml` returns a server error.

**Who is affected:** Django sites that serve a sitemap index where at least one sitemap class defines a `lastmod(item)` method and has no items at request time. Examples are a new site, a filtered queryset that is empty, or a section with no published content.

**Desired behavior:** A sitemap with a callable `lastmod` and no items reports "no latest lastmod" (returns `None`), as it already does when `lastmod` values are not comparable (`TypeError`). The sitemap index then renders successfully. The entry for that sitemap has no `<lastmod>` element.

**Acceptance criteria (user-level):**
- Requesting the sitemap index when one of its sitemaps has a callable `lastmod` and zero items returns HTTP 200, not an error.
- The empty sitemap still appears in the index. Its `lastmod` is treated as absent/`None`.
- Behavior for non-empty sitemaps, sitemaps without `lastmod`, and sitemaps with a non-callable `lastmod` attribute does not change.

**Reported location (from traceback):**
- `django/contrib/sitemaps/__init__.py`, `Sitemap.get_latest_lastmod`, line ~170: `return max([self.lastmod(item) for item in self.items()])`
- Caller: `django/contrib/sitemaps/views.py`, `index` view, line ~76: `site_lastmod = site.get_latest_lastmod()`

**Reporter's suggested fix (recorded, not yet adopted):** widen `except TypeError:` to `except (TypeError, ValueError):`. See Open Questions about whether catching `ValueError` broadly is the right scope.

## Assumptions

1. The target codebase is Django itself (`django.contrib.sitemaps`), not a downstream project. The reporter's Python is 3.10. The exact Django version and branch are unknown.
2. The current `get_latest_lastmod` has the structure shown in the issue. It returns `None` when there is no `lastmod` attribute, catches `TypeError` around `max(...)` for a callable `lastmod`, and otherwise returns the attribute value.
3. `None` is the correct "unknown" result. The index view and template already handle a `None` lastmod, since the `TypeError` path already returns it.
4. Only the base `Sitemap` class needs changing. Subclasses in `django.contrib.sitemaps` (e.g. `GenericSitemap`) either inherit this method or are out of scope unless they have the same pattern. This is unverified; see Open Questions.
5. The fix is a bug fix with no public API change. It needs a regression test and possibly a release note, depending on the target branch.
6. Python's `max()` supports a `default=` keyword (Python 3.4+), so the empty case can be handled without catching exceptions. Which approach to use is a design choice left to the plan.

## Tech Stack

- Language: Python (traceback shows 3.10; the minimum supported version for the target branch is unknown)
- Framework: Django, `django.contrib.sitemaps` app
- Other versions/dependencies: unknown

## Commands

Not visible in the issue; all are unknown.

```
Build: unknown (likely none needed for a pure-Python change)
Test:  unknown (Django's own test runner invocation for the sitemaps tests is not given in the issue)
Lint:  unknown
Dev:   unknown
```

## Project Structure

Only these paths are known from the traceback (installed-package paths, mapped to the source tree by assumption):

```
django/contrib/sitemaps/__init__.py  → Sitemap class, including get_latest_lastmod()
django/contrib/sitemaps/views.py     → index() and sitemap() views; index() calls get_latest_lastmod()
```

Unknown:
- Location of the existing sitemaps test suite and its test sitemap fixtures/URLconfs
- Location of release notes for the target version

## Code Style

Unknown beyond the snippet in the issue. Follow the existing style of `django/contrib/sitemaps/__init__.py`. Do not introduce new conventions. The existing method style, as shown in the issue, is:

```python
def get_latest_lastmod(self):
    if not hasattr(self, "lastmod"):
        return None
    if callable(self.lastmod):
        try:
            return max([self.lastmod(item) for item in self.items()])
        except TypeError:
            return None
    else:
        return self.lastmod
```

## Testing Strategy

- **Framework:** Django's test suite (exact runner command unknown).
- **Regression test (required):** Define a sitemap class with a callable `lastmod(self, item)` method and an `items()` that returns an empty list. Wire it into a sitemap index URL and request the index. The test must:
  - fail on the current code (the error propagates or the response is 500), and
  - pass after the fix: status 200, the sitemap listed, and no `<lastmod>` for that entry.
- **Unit-level check (recommended):** Calling `get_latest_lastmod()` directly on such a sitemap returns `None`.
- **Non-regression:** Existing sitemaps tests stay green, especially those covering:
  - callable `lastmod` with items (returns the max),
  - callable `lastmod` with mixed/non-comparable values (`TypeError` → `None`),
  - non-callable `lastmod` attribute,
  - no `lastmod` attribute.
- **Edge case to consider:** a `lastmod(item)` method that itself raises `ValueError` for a non-empty item list. Whether this should be swallowed or propagate depends on Open Question 1. Add a test pinning whichever behavior is chosen.
- Coverage expectations: unknown; at minimum, the new branch/behavior is exercised.

## Boundaries

- **Always:**
  - Keep the change minimal and confined to the `get_latest_lastmod` logic (plus tests, and a release note if the project requires one).
  - Preserve the existing return contract: a `datetime`/date-like value or `None`.
  - Add a regression test reproducing the reported scenario.
- **Ask first:**
  - Changing the views (`views.py`) or templates instead of, or in addition to, the model method.
  - Changing behavior for non-empty sitemaps (e.g. starting to swallow `ValueError` raised from user `lastmod()` code).
  - Applying the same change to other sitemap subclasses or similar `max()` call sites.
  - Backporting to stable branches.
- **Never:**
  - Change the public signature of `get_latest_lastmod` or `lastmod`.
  - Evaluate `items()` more than the current code does if that changes query counts in existing tests, without flagging it.
  - Remove or weaken existing tests.

## Success Criteria

1. For a sitemap whose `lastmod` is callable and whose `items()` is empty, `get_latest_lastmod()` returns `None` and raises nothing.
2. The sitemap index view returns HTTP 200 for a configuration including such a sitemap. The entry is rendered without a `lastmod` value.
3. For a callable `lastmod` with ≥1 item, the result is unchanged: the maximum of the `lastmod` values.
4. Non-comparable `lastmod` values still return `None` (the existing `TypeError` behavior).
5. The no-`lastmod` and non-callable-`lastmod` paths are unchanged.
6. A new regression test fails before the fix and passes after. All existing sitemaps tests pass.

## Open Questions

1. **Scope of exception handling:** Should the fix catch `ValueError` broadly, as the reporter suggests, or handle only the empty-items case explicitly (e.g. `max(..., default=None)` or an emptiness check)? Catching `ValueError` would also hide `ValueError`s raised inside user-defined `lastmod()` implementations, which may mask real bugs.
2. **Target branch and backport:** Which Django version or branch is this targeted at, and does it qualify for a backport (it is a crash in a contrib view)? This determines whether a release note is needed and where it goes.
3. **Other call sites:** Do other parts of `django.contrib.sitemaps` have the same `max()` pattern over possibly empty sequences (e.g. latest-lastmod computation in the `sitemap` view across sitemaps or pages, or in `GenericSitemap`)? Should they be fixed in the same change?
4. **Expected index output:** Is it confirmed that the index template omits `<lastmod>` when the value is `None`, rather than rendering an empty element? This needs checking against the current template.
5. **Query cost:** Is it acceptable that an emptiness check might evaluate `items()` an extra time, or must the fix evaluate `items()` once, as the current list comprehension does?
6. **Test location and commands:** Where do sitemaps tests and test URLconfs live, and what is the exact command to run them? This is not visible from the issue.