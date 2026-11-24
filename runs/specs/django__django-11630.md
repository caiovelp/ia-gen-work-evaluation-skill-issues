# Spec: Allow the same `db_table` across models routed to different databases (models.E028 regression)

## Objective

After upgrading from Django 2.0 to 2.2, projects that use several databases now fail the system check:

```
table_name: (models.E028) db_table 'table_name' is used by multiple models: base.ModelName, app2.ModelName.
```

The reporter's setup:
- A `base` app whose models live in a central database.
- Several other apps, each with models in its own database.
- Some models in different apps use the same table name. This is valid because the tables are in different databases.

This worked on Django 2.0. On 2.2 the check blocks startup, so the reporter rolled back to 2.0.

**Users:** Django projects that use multiple databases and database routing, where models in different apps map to identically named tables in different databases.

**Goal:** Projects whose same-named tables are legitimately split across databases can upgrade without being blocked. Real table-name collisions should still be detected in single-database projects.

**Acceptance criteria:**
1. When database routing is configured, two models in different apps that share a `db_table` no longer produce a blocking **error**. Projects in that situation can run management commands such as `runserver` and `migrate`.
2. The duplicate is still reported in some form, such as a non-blocking **warning** with a hint. The check cannot reliably know which database each model will use, so the user should verify the routing.
3. When no database routing is configured, the existing E028 error still fires for duplicate `db_table` values.
4. Existing exemptions in the check still behave as they do today. Examples are unmanaged models and proxy models, if the check already excludes them. (Exact current rules are unknown.)
5. The release notes and the system-check documentation describe the changed behavior for the affected release line(s).

## Assumptions

1. The regression comes from the E028 check (duplicate `db_table`) being new or tightened in Django 2.2. In 2.0 the same duplicate tables passed.
2. The reporter uses `DATABASE_ROUTERS` to send each app's models to its own database. The issue implies this but doesn't state it.
3. The system check framework runs without a database connection and can't fully evaluate router logic per model. So "routers are configured" is the practical signal available, not "these two models really go to different databases."
4. A non-blocking warning, which users can silence through `SILENCED_SYSTEM_CHECKS`, is an acceptable middle ground between keeping the error and removing the check entirely.
5. The fix targets the 2.2 line as a regression and is carried forward to later versions.
6. The models in question are ordinary concrete models. Whether they are managed or unmanaged isn't stated.

## Tech Stack

- Django framework source, Python. Exact supported Python versions for the target branch are **unknown**.
- Django system checks framework (`models.E028`).

## Commands

Not visible in the issue; all **unknown**:
- Test runner invocation for Django's own test suite: unknown
- Lint / style check: unknown
- Build / docs build: unknown

## Project Structure

**Unknown.** The issue gives no file paths. The relevant areas are:
- the module that implements the model-level system checks (where E028 is raised),
- that check's test module,
- the system-check reference documentation,
- the release notes for the patch release that fixes this.

## Code Style

**Unknown.** Follow the existing conventions of the surrounding check code and its tests. No example code is available in the issue.

## Testing Strategy

The framework and test locations are **unknown**. These are the behaviors to cover, as check-level unit tests using isolated model definitions:
- Duplicate `db_table` across two apps, **no** routers configured → E028 error, as today.
- Duplicate `db_table` across two apps, routers configured → warning instead of an error, with a hint about verifying routing. No error is emitted.
- No duplicates, with or without routers → no message.
- Existing exemptions (for example unmanaged or proxy models, if currently exempt) → unchanged.

## Boundaries

- **Always:**
  - Keep E028 behavior unchanged for projects without database routing.
  - Add tests for both the routed and the non-routed cases.
  - Document the change in the check reference and the release notes.
- **Ask first:**
  - Removing the check entirely.
  - Attempting to evaluate router results per model at check time.
  - Changing check IDs beyond adding a new warning ID.
  - Backporting decisions.
- **Never:**
  - Silently drop duplicate-table detection for single-database projects.
  - Require a database connection for this check.
  - Change unrelated system checks.

## Success Criteria

- A project like the reporter's, with routers configured and same-named tables in different apps, passes system checks with at most a warning. It can run on the fixed release without rolling back.
- A single-database project with two models sharing a `db_table` still gets the E028 error.
- New tests for both scenarios pass, and the existing check tests still pass.
- The docs list the new or changed check message and explain when it appears and how to silence it.

## Open Questions

1. Is the intended behavior to downgrade to a warning when routers are configured, or should the check be reverted or removed? Should it instead try harder to determine the target database for each model?
2. Which signal counts as "routing is configured"? Is it a non-empty `DATABASE_ROUTERS`, or multiple entries in `DATABASES`, or both?
3. Should the warning get a new check ID or reuse E028 at a lower level? What is the exact message and hint text?
4. Which release branches receive the fix: only the 2.2 maintenance line, or later versions too?
5. Do the reporter's models with duplicate names use the same model class name, the same `db_table`, or both? Are any of them unmanaged? This affects whether existing exemptions already apply.
6. Should the check also consider models in the *same* database that collide only through routing? (Probably out of scope.)