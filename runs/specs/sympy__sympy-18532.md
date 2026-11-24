# Spec: `expr.atoms()` returns leaf nodes (no `.args`) instead of `Atom` subclasses

## Objective

**Problem.** When `expr.atoms()` is called with no arguments, it returns the objects in `expr` that are instances of subclasses of `Atom`. The issue says this is the wrong definition of a leaf. A leaf node is an object with no `.args`.

**Goal.** Change the no-argument behavior of `atoms()` so it returns every object in the expression tree whose `.args` is empty. Performance must not regress in a meaningful way.

**Users.** Library users and internal callers that use `atoms()` with no arguments to get the leaves of an expression tree.

**User stories / acceptance criteria**

- As a user, when I call `expr.atoms()` with no arguments, I get the set of all subexpressions of `expr` (including `expr` itself) that have empty `.args`.
- As a user, when I call `expr.atoms(SomeType, ...)` with explicit types, the behavior is the same as today.
- As a maintainer, I can see benchmark evidence that the new no-argument `atoms()` is not meaningfully slower than the current one.

## Assumptions

1. The project is SymPy, or a codebase built the same way. Expressions are `Basic` objects, each with a `.args` tuple, and `Atom` is a base class for leaf types.
2. "Has no args" means `not node.args` (an empty tuple). It is evaluated on each node reached while traversing the expression tree.
3. Only the **no-argument** form changes. The `atoms(*types)` form keeps its current semantics, which are based on `isinstance`.
4. The return type stays the same: a `set` of the matching objects.
5. The traversal stays the same as today (the full expression tree, including the root). Only the selection predicate changes.
6. Today, every `Atom` instance has empty `.args`. So the new result should be a **superset** of the old result. The new items would be non-`Atom` objects with empty args, for example an empty container-type node.
7. The performance concern is runtime only. Memory is not expected to change significantly.
8. Some existing tests or doctests may assert the old result. If such a test depends on non-`Atom` nodes being excluded, it may need updating. That counts as a behavior change and must be reviewed.

## Tech Stack

- Language: Python (version unknown).
- Library: SymPy or similar (version unknown).
- Relevant components named in the issue: the `atoms()` method, the `Atom` class, and the `.args` attribute. File locations are unknown.
- Benchmarking tool: unknown. The project may have a benchmark suite, but its existence and location are unconfirmed.

## Commands

| Purpose | Command |
|---|---|
| Build | Unknown (not stated in the issue) |
| Test (full) | Unknown |
| Test (targeted, `atoms`-related) | Unknown |
| Doctests | Unknown |
| Lint | Unknown |
| Benchmark | Unknown |

## Project Structure

Unknown. The issue does not give the location of:

- the definition of `atoms()`
- the definition of `Atom`
- the existing tests for `atoms()`
- any benchmark suite

## Code Style

Unknown. Follow the existing style of the module that defines `atoms()`. No code snippet is available from the issue.

## Testing Strategy

Framework and test locations are unknown. These test levels are required:

**Unit tests for the new no-argument behavior:**
- A simple expression returns the same leaves as before when all leaves are `Atom` instances. This guards against regression.
- An expression containing a non-`Atom` node with empty `.args` includes that node in `atoms()`.
- An expression whose root itself has no args returns a set containing only the root.
- Duplicate leaves appear once, because the result is a set.

**Unit tests for unchanged typed behavior:**
- `atoms(T)` and `atoms(T1, T2)` return the same results as before.

**Existing suite:**
- All existing tests and doctests that touch `atoms()` pass. Any that need changes are listed explicitly with a justification.

**Performance check:**
- Benchmark no-argument `atoms()` before and after the change on representative inputs:
  - small expressions
  - large and deep expressions
  - expressions with many repeated subtrees
- Report the results. The acceptance threshold is an open question.

## Boundaries

**Always:**
- Keep the `atoms(*types)` semantics unchanged.
- Run the existing `atoms`-related tests and doctests.
- Record before/after benchmark numbers.
- Document the changed definition in the `atoms()` docstring.

**Ask first:**
- Changing any existing test or doctest expectation.
- Changing the traversal strategy, for example to optimize performance.
- Changing the behavior of other methods that rely on the `Atom` definition.
- Adding a deprecation path or an opt-out flag.

**Never:**
- Change the return type of `atoms()`.
- Remove or weaken existing tests without approval.
- Merge a measurable slowdown without the maintainers explicitly accepting it.

## Success Criteria

1. For any expression `expr`, `expr.atoms()` equals the set of all nodes `n` in `expr`'s tree (root included) with `not n.args`.
2. For every type tuple `T`, `expr.atoms(*T)` returns the same result as before the change.
3. Every node previously returned by no-argument `atoms()` is still returned. Only empty-args non-`Atom` nodes may be added.
4. The full existing test suite passes. Any changed expectations are listed and approved.
5. The `atoms()` docstring describes the "no `.args`" definition for the no-argument case.
6. Benchmarks of no-argument `atoms()` show no slowdown beyond the agreed threshold (TBD) on the agreed inputs.

## Open Questions

1. **Performance threshold.** What counts as an acceptable slowdown (for example, ≤5%, or no statistically significant difference)? Which benchmark inputs and which suite should be used?
2. **`Atom` subclasses with non-empty args.** Can such a node exist? If so, should it still be returned by no-argument `atoms()`? The new definition would exclude it.
3. **Traversal into non-`Basic` args.** Does the current traversal descend into args that are not expression objects? How should those be treated: as leaves, or ignored?
4. **Compatibility.** Is this considered a breaking change? Does it need a release note or deprecation, given that callers may currently receive only `Atom` instances?
5. **Should `Atom` change too?** Should `Atom` itself be redefined or documented in terms of "no args"? Or does this change apply only to `atoms()`?
6. **Other callers.** Should other methods that use the "leaf = `Atom`" definition, such as free-symbol or traversal helpers, be updated for consistency? Or is that out of scope?
7. **Environment.** What are the build, test, lint and benchmark commands, the file locations, and the supported Python versions?