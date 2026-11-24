## Summary
Display fixture scope in the output of `pytest --fixtures`

## Description
The `pytest --fixtures` command lists available fixtures but does not show their scope. This request proposes including each fixture's scope in that listing.

## Product version
Not provided in the original request.

## Rationale
Right now the only ways to find a fixture's scope are:
- reading the documentation, which works only when the scope is documented, or
- reading the source code.

Showing the scope in `pytest --fixtures` would make this information available directly from the command line.

## Use case or scenario
A user runs `pytest --fixtures` to see the available fixtures and wants to know each fixture's scope. Today they must look in the documentation or the source code to find it.

## Possible solution
Show each fixture's scope as part of the output of `pytest --fixtures`.