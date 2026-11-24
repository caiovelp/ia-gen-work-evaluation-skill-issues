# Spec: Preserve Per-Hop Request State Across Redirect Chains in `Session.resolve_redirects`

## Objective

`Session.resolve_redirects` copies the **original** request at the start of every redirect iteration. Changes made at earlier hops are lost, and later hops are built from stale state.

The issue's example:

1. `POST /do_something` → `303 See Other`, `Location: /new_thing_1513`. Requests correctly converts the request to `GET`.
2. `GET /new_thing_1513` → `307 Temporary Redirect`, `Location: //failover.example.com/new_thing_1513`.
3. **Expected:** `GET //failover.example.com/new_thing_1513`. A 307 must preserve the method of the request that received it.
4. **Actual:** `POST`. The third request is rebuilt from the original POST.

**Who is affected:** Users of the Requests library who follow redirects (the default for most methods) and hit chains that mix method-changing redirects (301/302/303) with method-preserving ones (307, possibly 308).

**What we're building:** A behavioral fix. Each redirect hop must be derived from the request that was actually sent at the previous hop, not from the original request. Method selection then follows HTTP semantics across the whole chain.

**Acceptance criteria (user-visible):**
- After a 303 turns a POST into a GET, any later 307 in the same chain issues a GET.
- Any request state changed by an earlier hop stays changed at later hops. This includes the method and the body that was dropped when the method became GET.
- Single-hop redirect behavior is unchanged.

## Assumptions

1. The affected code is `Session.resolve_redirects` in the Requests library. Its module path is assumed to be `requests/sessions.py`, which is not verified because the repository is not visible.
2. The 303→GET conversion is already correct for a single hop. Only state propagation across multiple hops is broken.
3. The intended semantics are:
   - 303: change the method to GET, except for HEAD.
   - 301/302 with POST: change to GET (current Requests convention, assumed unchanged).
   - 307 (and 308, if supported in this codebase version): preserve the method and body of the *immediately preceding* request.
4. When a hop converts to GET, the body and body-related headers (for example `Content-Length`, `Content-Type`, `Transfer-Encoding`) are stripped. That stripping should also persist to later hops. Whether the current code strips them at all is unknown.
5. Other per-hop state should also come from the previous hop, not the original request. This includes the URL being resolved relative to the previous URL, auth headers removed on host change, and cookies.
6. The fix must not change the public signature of `resolve_redirects` beyond what is needed. That signature is not visible here.
7. Redirect history (`response.history`) and `max_redirects` enforcement keep their current behavior.
8. A scheme-relative `Location` (`//failover.example.com/...`) is already resolved correctly using the previous request's scheme. It appears in the example but is not the bug.

## Tech Stack

- Python, Requests library. The supported Python versions and the library version this targets are **unknown**.
- HTTP semantics reference: RFC 7231 (303, 307) and RFC 7538 (308). Which RFCs the project follows is assumed, not verified.

## Commands

All **unknown**. The repository's build, test, and lint tooling is not visible.

```
Build: unknown
Test:  unknown
Lint:  unknown
Dev:   unknown
```

## Project Structure

**Unknown.** The only path inferred from the issue is the location of `Session.resolve_redirects`, likely in a `sessions` module of the `requests` package. This is not verified. The test directory location is also unknown.

## Code Style

**Unknown.** Follow the existing style of the module that contains `Session.resolve_redirects`. No snippet is available.

## Testing Strategy

- **Framework:** unknown. Use whatever the existing test suite uses.
- **Primary test level:** unit or integration tests that simulate a multi-hop redirect chain without real network access. Whether the suite has a mock adapter or local HTTP server fixture is unknown.
- **Required test cases:**
  1. `POST` → 303 → `GET` → 307 → final request is `GET`. This is the issue's exact scenario.
  2. Same chain, and the final request has no body and no body-related headers left over from the original POST.
  3. `POST` → 307 → 307 → final request is still `POST` with the original body. This is a regression guard showing 307 preservation still works when no conversion happened.
  4. `POST` → 302 → 307 → final request is `GET`. This covers the same propagation bug via 301/302 conversion.
  5. `HEAD` → 303 → 307 → final request is `HEAD`, if 303-preserves-HEAD is current behavior.
  6. Single-hop 301/302/303/307 behavior is unchanged.
  7. `response.history` length and order are correct for multi-hop chains.
- **Coverage expectation:** unknown project threshold. Every new branch in redirect method and body handling should be covered.

## Boundaries

- **Always:**
  - Derive each hop from the previously sent request.
  - Add regression tests for the issue's exact chain.
  - Run the full existing test suite before committing.
  - Keep `response.history` semantics intact.
- **Ask first:**
  - Changing the public signature or return type of `resolve_redirects`.
  - Changing the 301/302 POST→GET convention.
  - Adding or changing 308 support.
  - Adding test dependencies.
- **Never:**
  - Make tests depend on real external hosts.
  - Remove or weaken existing redirect tests without approval.
  - Change unrelated session behavior, such as connection pooling or retries.

## Success Criteria

- [ ] A chain `POST` → 303 → 307 results in a `GET` for the third request (issue scenario reproduced in a test, failing before and passing after).
- [ ] The body and body headers dropped at a method-converting hop do not reappear at later hops.
- [ ] Method-preserving redirects (307) preserve the method of the immediately preceding request, verified across at least 3 hops.
- [ ] All existing redirect and session tests pass unchanged.
- [ ] No change to the observable behavior of single-hop redirects.

## Open Questions

1. Should 308 Permanent Redirect be handled by this fix? Is 308 supported in the target version?
2. Should other per-hop mutations also persist across hops, beyond the method and body? Examples are auth header stripping on cross-host redirects, cookie updates, and the resolved URL. Is there an existing expectation or test that relies on copying the original?
3. Does `resolve_redirects` copy the original request on purpose for some caller, for example to re-apply original hooks or auth? Would deriving from the previous hop break that caller?
4. Is `resolve_redirects` considered public API? Is it called directly by third parties with an explicit request argument whose semantics must be preserved?
5. Which Python and Requests versions must the fix support? Should it be backported?
6. What are the project's test, lint, and build commands, and the test directory layout?
7. Is the 301/302 POST→GET conversion intended to remain? It deviates from strict RFC wording but matches browser behavior.