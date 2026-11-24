# Spec: `item_comments` Support in the Syndication Framework

## Objective

Let feed authors set an item's comments URL by defining an `item_comments` hook on their feed class. Today they must work around this by overriding `item_extra_kwargs`.

**Problem (from the issue):**
- `feed.add_item()` in `syndication.views` is not passed a `comments` argument.
- The feed generator (the issue calls it the "feedparser") already accepts and handles `comments` explicitly.
- So the only way to set an item's comments value is the detour through `item_extra_kwargs`.

**Users:** Developers who build RSS/Atom feeds with the syndication framework's `Feed` view class.

**User story:**
> As a developer defining a feed, I want to declare `item_comments` on my `Feed` subclass, the same way as `item_link` or `item_author_name`, so that each item's comments URL appears in the generated feed without overriding `item_extra_kwargs`.

**Acceptance criteria:**
1. A `Feed` subclass can define `item_comments`, and its value for each item is passed to `feed.add_item()` as `comments`.
2. `item_comments` resolves the same way as the other `item_*` hooks, in each of these forms:
   - a method that takes the item
   - a method that takes no arguments
   - a plain attribute
3. If `item_comments` is not defined, `comments` is passed as `None` and existing feed output is unchanged.
4. For feed formats that support comments, the value appears in the output. RSS 2.0 is assumed to support it via `<comments>`.
5. Existing code that sets `comments` through `item_extra_kwargs` keeps working. How a conflict between the two sources is resolved must be defined (see Open Questions).
6. The documentation for the syndication framework lists `item_comments` alongside the other item hooks.

## Assumptions

1. This is the Django project:
   - "syndication framework" = `django.contrib.syndication`
   - "feedparser" = the feed generator module, assumed to be `django.utils.feedgenerator`
2. `SyndicationFeed.add_item()` already accepts a `comments` keyword argument. The RSS 2.0 writer emits a `<comments>` element when it is set. The issue implies this but the code has not been seen.
3. The `Feed` view resolves `item_*` hooks through an existing helper, assumed to be `_get_dynamic_attr`. `item_comments` should use the same helper rather than new lookup logic.
4. `item_extra_kwargs` is merged into the `add_item()` call as keyword arguments. If `comments` is now passed explicitly as well, a naive merge could raise a duplicate-keyword error. That must be avoided.
5. Atom output does not need a comments element. Only formats that already handle `comments` in the generator are affected.
6. No changes to the generator itself are needed. This is a view-layer change plus tests and docs.
7. No new dependencies are needed and there is no database or schema impact.

## Tech Stack

- Python, Django (version/branch **unknown**)
- Modules involved (assumed names, not verified):
  - `django.contrib.syndication.views`
  - `django.utils.feedgenerator`

## Commands

- Build: **unknown** (not applicable / not visible in the issue)
- Test: **unknown**. Presumably the project's standard test runner targeting the syndication tests. Exact command not visible.
- Lint: **unknown**
- Docs build: **unknown**

## Project Structure

**Unknown.** No repository access. Expected touch points, all of which need verification:

| Area | What changes |
|---|---|
| Syndication view module (`syndication.views`) | Pass `comments` to `feed.add_item()` |
| Syndication tests | Add test feeds/cases for `item_comments` |
| Syndication framework reference docs | Document `item_comments` |
| Release notes for the target version | Mention the new hook |

## Code Style

**Unknown.** No code snippet is visible. Follow the conventions of the surrounding `item_*` hook handling in `syndication.views`. The new hook should mirror how hooks such as `item_link` and `item_author_name` are resolved and passed through.

## Testing Strategy

- **Framework:** **unknown**. Presumably the project's existing test suite for the syndication app.
- **Levels:** Integration-style tests that render a feed through the view and inspect the generated XML, consistent with existing syndication tests (assumed).
- **Cases to cover:**
  1. `item_comments` defined as a method taking `item`: the RSS 2.0 output contains the `<comments>` element with the expected value per item.
  2. `item_comments` defined as a no-argument method or a plain attribute: resolves correctly. This should hold if the shared helper is used.
  3. `item_comments` not defined: no `<comments>` element appears and existing feed outputs are unchanged. Run the existing tests as a regression check.
  4. `comments` supplied via `item_extra_kwargs`: still works, with no duplicate-keyword error. Conflict behaviour matches whatever is decided under Open Questions.
  5. Atom feed with `item_comments` defined: renders without error and is otherwise unchanged.
- **Coverage expectation:** **unknown**. Every new branch should be exercised.

## Boundaries

- **Always:**
  - Resolve `item_comments` through the same mechanism as the other `item_*` hooks.
  - Keep default behaviour unchanged when the hook is absent.
  - Add tests and documentation together with the code change.
- **Ask first:**
  - Changing the feed generator's `add_item()` signature or output.
  - Adding comments output to Atom.
  - Changing how `item_extra_kwargs` is merged beyond what is needed to avoid conflicts.
  - Deprecating the `item_extra_kwargs` route for `comments`.
- **Never:**
  - Break existing feeds that pass `comments` via `item_extra_kwargs`.
  - Remove or weaken existing syndication tests.
  - Change the output of feeds that don't use the new hook.

## Success Criteria

- [ ] A `Feed` subclass that defines only `item_comments` (no `item_extra_kwargs` override) produces RSS 2.0 output with a correct `<comments>` element for each item.
- [ ] Feeds without `item_comments` produce output identical to before the change. All existing syndication tests pass.
- [ ] Feeds that already set `comments` via `item_extra_kwargs` still render without errors, and the result matches the documented precedence rule.
- [ ] New tests for `item_comments` exist and pass.
- [ ] The syndication docs list `item_comments` with its three supported forms (method with item, method without args, attribute), matching how the other hooks are documented.
- [ ] A release note entry describes the new hook.

## Open Questions

1. **Precedence:** If a feed defines both `item_comments` and `comments` inside `item_extra_kwargs`, which wins? Should `item_extra_kwargs` override, consistent with it being the "escape hatch"? Or should it raise an error?
2. **Target version:** Which Django version or branch does this target? This decides where the release note and any `versionadded` doc annotation go.
3. **Generator support:** Is it confirmed that the feed generator's `add_item()` already accepts `comments`, and which formats render it? Is RSS 2.0 the only one?
4. **Atom:** Should anything be emitted for Atom, or is ignoring `comments` there acceptable?
5. **Docs example:** Should the docs show `item_extra_kwargs` usage for comments as an example to replace, or just add the new hook?
6. **Commands and layout:** What are the exact test command, file locations, and lint tooling for this repository? These were not visible in the issue.