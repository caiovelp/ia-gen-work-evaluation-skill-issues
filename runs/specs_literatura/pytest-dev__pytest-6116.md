## Summary
Add a single-character short option for `pytest --collect-only`.

## Description
The `--collect-only` command-line option of pytest is long to type. This request proposes adding a one-character short alias for it.

The author has not chosen which character should be used. They invite others to vote (thumbs up/down) on whether the feature would be useful and to suggest a character. The author notes that the change itself should be easy to implement. Before that, they want to find out whether other users would find it useful.

## Product version
Not provided in the original request.

## Rationale
The author runs `pytest --collect-only` very often, and the long option name is tedious to type each time. A one-character shortcut would make this frequently used command faster to enter.

## Use case or scenario
A user runs `pytest --collect-only` many times during their work, for example to see which tests pytest collects. Each time they must type the full `--collect-only` argument. With a one-character short option, they could run the same command with much less typing.

## Possible solution
Assign a one-character short option (for example `-X`, where the actual character is still to be decided) as an alias for `--collect-only`. The original request does not specify which character to use and leaves that choice to community suggestions.