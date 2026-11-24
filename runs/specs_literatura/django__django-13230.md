## Summary
Add support for `item_comments` to the syndication framework.

## Description
In `syndication.views`, `feed.add_item()` should accept a `comments` argument. This lets a feed define `item_comments` directly, without the workaround of `item_extra_kwargs`.

The feed generator ("feedparser") already lists `comments` explicitly, but the syndication view does not pass it through.

## Product version
Not provided in the original request.

## Rationale
- Today, the only way to set comments for a feed item is the indirect route through `item_extra_kwargs`.
- The feed generator already lists `comments` explicitly, so the view and the generator are inconsistent.
- Supporting `item_comments` directly would make the view match what the feed generator already offers and make the feature easier to use.

## Use case or scenario
A developer building a feed with the syndication framework wants each feed item to include a comments reference. Today they must provide it through `item_extra_kwargs`. With this change, they could define `item_comments` on the feed directly, the same way as other item attributes.

## Possible solution
Add a `comments` argument to the `feed.add_item()` call in `syndication.views`, filled from `item_comments`. Feeds could then define `item_comments` directly instead of going through `item_extra_kwargs`.