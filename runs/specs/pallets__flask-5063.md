# Spec: Show Domain/Subdomain Information in `flask routes`

## Objective

The `flask routes` CLI command lists every URL rule with its endpoint, methods and path. It does not show which domain or subdomain a rule belongs to. When blueprints are registered with `subdomain=...`, routes on different subdomains can share the same path, and the output cannot tell them apart:

```
admin_blueprint.home            GET   /home
test_subdomain_blueprint.home   GET   /home
```

Users currently have to read the app configuration to work out which `/home` serves `admin.test.local` and which serves `test.test.local`.

**Who it's for:** Developers debugging or auditing routing in Flask apps that use subdomain routing (blueprint or route `subdomain=`) or host matching.

**What we're building:** An extension to `flask routes` that shows each rule's domain or subdomain whenever that information is relevant. It must not change the output for apps that don't use subdomains or host matching.

**Secondary need from the issue:** "If it is not possible to fix routes, can you add or tell which method(s) should be used to get below information." The documentation should therefore point users to the public attributes that carry this information (the `subdomain` / `host` attributes of rules in `app.url_map`), so they can get it programmatically.

### User stories

1. As a developer whose app sets `SERVER_NAME='test.local'` and registers blueprints with `subdomain='admin'` and `subdomain='test'`, I run `flask routes` and see which domain each rule is served on. That is `admin.test.local`, `test.test.local` or `test.local`.
2. As a developer whose app has no subdomain routing, I run `flask routes` and get the same output as today, with no new empty column.
3. As a developer using host matching (`host_matching=True`), I see the host each rule is bound to.
4. As a developer, I can sort the routes output by domain.

## Assumptions

1. The scope is the built-in `flask routes` command in the Flask project itself, not a third-party extension.
2. Each Werkzeug `Rule` object exposes its subdomain and host bindings as attributes (`rule.subdomain`, `rule.host`). Flask sets these when a blueprint or route is registered with `subdomain=`, or when `host_matching` is enabled. This is based on the issue's blueprint usage and general Werkzeug knowledge, not verified against the repo.
3. The domain displayed is built as follows:
   - With host matching, it is the rule's host.
   - Otherwise, a rule with a non-empty subdomain shows `<subdomain>.<SERVER_NAME>`.
   - A rule with an empty subdomain shows `SERVER_NAME`.
   This matches the issue's expected output.
4. The column only appears when at least one rule has a non-empty subdomain, or when host matching is enabled. Output for apps that don't use either stays byte-for-byte unchanged.
5. The existing options of `flask routes` (believed to be `--sort` and `--all-methods`) keep working. Sorting gains a domain-based option.
6. Column order follows the issue's example: the domain column comes first, before Endpoint.
7. No new dependencies are needed.

## Tech Stack

- Python, Flask, Werkzeug (routing), Click (CLI). Supported version ranges: **unknown**, so use the project's existing ones.

## Commands

All unknown, because there is no repository access. They must be taken from the project's contributor docs or CI config.

```
Build: unknown
Test:  unknown (project test runner, likely pytest; verify)
Lint:  unknown
Dev:   flask --app <app> routes   # manual verification of the feature
```

## Project Structure

Unknown. Expected locations to confirm:

- The module that implements the `routes` CLI command (believed to be the Flask CLI module; exact path unverified)
- The test module covering CLI commands (unverified)
- CLI documentation page and changelog (unverified)

## Code Style

Unknown. Follow the existing conventions of the CLI module: Click option declarations, the table formatting already used by `flask routes`, type hints if present, and the project's formatter/linter config. No snippet is provided because none is visible in the issue.

## Testing Strategy

- **Framework:** The project's existing test framework and CLI test helpers (e.g. Click's `CliRunner` or Flask's CLI runner). Exact framework is unknown.
- **Level:** Unit/CLI tests that build small apps in-test, invoke `routes`, and assert on the output.
- **Cases to cover:**
  - App without subdomains or host matching: no domain column, and output unchanged from current behavior.
  - App with `SERVER_NAME` and blueprints on `admin` and `test` subdomains: column present, values are `admin.test.local`, `test.test.local` and `test.local` (the last for `static` and other non-subdomain rules).
  - App with `host_matching=True` and rules bound to hosts: column shows each rule's host.
  - Sorting by domain orders rows by the displayed domain.
  - Existing options (`--sort` values, `--all-methods`) still behave as before, with and without the new column.
  - Edge: subdomain set but `SERVER_NAME` unset. Expected behavior depends on an open question.
- **Coverage:** Match project norms. Every new branch, column shown or hidden and host versus subdomain, must be covered.

## Boundaries

- **Always:**
  - Keep `flask routes` output unchanged for apps without subdomains or host matching.
  - Add tests for every new display branch.
  - Update the CLI docs and changelog.
  - Run the full test suite before committing.
- **Ask first:**
  - Changing column order or headers of the existing output.
  - Adding new CLI flags beyond the sort option.
  - Changing anything in Werkzeug.
  - Adding any dependency.
- **Never:**
  - Change routing or matching behavior.
  - Remove or rename existing `--sort` values.
  - Modify or delete existing tests to make new ones pass without approval.

## Success Criteria

1. For the issue's example app, `flask routes` prints a domain column whose values are `admin.test.local` for `admin_blueprint.home`, `test.test.local` for `test_subdomain_blueprint.home`, and `test.local` for `static`.
2. For an app with no subdomain rules and no host matching, the output is identical to the current output. An existing or new snapshot-style test asserts this.
3. With `host_matching=True`, the column shows each rule's host. The header wording is to be decided (see Open Questions).
4. A sort option orders rows by the domain column.
5. `--all-methods` and all existing `--sort` values work unchanged.
6. The docs describe the new column and show how to read the information programmatically from `app.url_map.iter_rules()` via the rule's `subdomain` / `host`.
7. All tests and lint pass.

## Open Questions

1. **Column header:** Should it be a single `Domain` header as in the issue? Or should the header change by mode, e.g. `Host` when host matching is on and `Subdomain` / `Domain` otherwise?
2. **Displayed value:** Should the column show the full domain (`admin.test.local`, as the issue requests) or only the raw subdomain (`admin`)? A full domain depends on `SERVER_NAME`. A raw subdomain does not, but is less readable.
3. **`SERVER_NAME` unset:** If a rule has a subdomain but `SERVER_NAME` is not configured, what should be displayed? Options: the raw subdomain, a placeholder, or a warning.
4. **Empty-subdomain rules:** When the column is shown, should rules with no subdomain display `SERVER_NAME`, as in the issue, or stay blank?
5. **Subdomain matching config:** How should `subdomain_matching` / `default_subdomain` settings (if applicable in the target Flask version) affect what is displayed for rules without an explicit subdomain?
6. **Variable subdomains** (e.g. `subdomain='<user>'`): Should they be shown literally as `<user>.test.local`?
7. **Column visibility:** Should it be automatic (only when relevant) or controlled by an explicit flag? An automatic column changes output for subdomain users. Is that acceptable for anyone parsing this output?
8. **Sort option name:** What should the new sort option be called, e.g. `domain`, or `host` / `subdomain`?
9. **Target version:** Which Flask release should this land in, and does it count as a feature that needs a changelog entry under "Unreleased"?