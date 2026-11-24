# Spec: `inspectdb` generates `related_name` when one table has several relations to the same model

## Objective

`inspectdb` reads an existing database and writes Django model source code. If one table has two or more foreign-key columns that point to the same table, the generated model has several `ForeignKey`/`OneToOneField` fields that target the same model. Django then gives each of them the same default reverse accessor (`<model>_set`). The system check reports:

```
module.Model.field1: (fields.E304) Reverse accessor for 'module.Model.field1' clashes with reverse accessor for 'module.Model.field2'.
HINT: Add or change a related_name argument to the definition for 'module.Model.field1' or 'module.Model.field2'.
```

The generated models therefore fail system checks until a developer adds `related_name` to each field by hand.

**User:** a developer running `inspectdb` against a legacy database to bootstrap Django models.

**Goal:** when a generated model has more than one relation field targeting the same model, `inspectdb` adds a `related_name` to those fields automatically. Each generated reverse accessor must be unique, so the output passes these checks without manual edits.

**User stories / acceptance**
- As a developer, when my table `message` has `sender_id → user.id` and `recipient_id → user.id`, the generated `Message` model has two `ForeignKey(User, ...)` fields with distinct `related_name` values. `fields.E304` and `fields.E305` are not raised for them.
- As a developer, when a table has only one relation to a given target, the generated code for that field looks exactly as it does today, with no `related_name` added.
- As a developer, when a table has several foreign keys to itself, the self-referential fields also get distinct `related_name` values.

## Assumptions

1. This is the Django project, and the change is in the `inspectdb` management command. The exact source file path is **unknown** because the repository was not visible. It is probably the command module under Django's core management commands.
2. "Same relation target" is decided per generated model. It means two or more relation fields (`ForeignKey` or `OneToOneField`) in one table whose referenced table maps to the same model class name, including `'self'`.
3. `related_name` is added **only** to relation fields that share a target with another field in the same model. Fields whose target is unique keep today's output, so existing output changes as little as possible.
4. The generated `related_name` is derived from the attribute (field) name. It must be unique across all models that point at the target, not only within the source model. For that reason, the naming scheme probably needs the source model name as well as the attribute name (for example `<model>_<attname>_set`). The issue's literal suggestion, `related_name='attribute_name'`, could clash across models and with real fields on the target model. The final format is an open question.
5. This fixes only the reverse-accessor and reverse-query-name clashes (E304/E305) that come from several relations to the same target. Other clashes are out of scope. One example is a reverse accessor that collides with an existing field name on the target model (E302/E303).
6. The behaviour applies to tables and to views and partitions if those are introspected. It applies on every database backend, since it depends only on introspected relations and not on backend-specific SQL.
7. There is no new command-line flag. The behaviour is always on.
8. The change ships with tests in Django's existing `inspectdb` test suite, with test models that create the multi-FK situation. The test location and models are **unknown** and need confirming.

## Tech Stack

- Python and Django. The versions are **unknown**, so target the current development branch.
- Database introspection goes through each backend's introspection API, specifically the relations and constraints information that `inspectdb` already uses.

## Commands

All commands are **unknown** because the repo was not visible. Expected shape, to be confirmed:

```
Build: n/a (pure Python)
Test:  <Django test runner> inspectdb       # exact invocation unknown
Lint:  unknown (project linters/formatters to be confirmed)
Dev:   python manage.py inspectdb            # manual verification in a sample project
```

## Project Structure

**Unknown.** Two locations need confirming:
- `inspectdb` command source: unknown path
- `inspectdb` tests and their test models: unknown path

## Code Style

Follow the existing style of the `inspectdb` command:
- Generated field kwargs are emitted the same way the command already emits them, for example as an extra-params mapping rendered into the field call.
- Use the same quoting and ordering conventions as the existing generated output.

No code snippet is given, because the source is not visible.

Illustrative **expected generated output** (exact `related_name` format to be confirmed):

```python
class Message(models.Model):
    sender = models.ForeignKey('User', models.DO_NOTHING, related_name='<unique name derived from "sender">')
    recipient = models.ForeignKey('User', models.DO_NOTHING, related_name='<unique name derived from "recipient">')
```

## Testing Strategy

- **Framework:** Django's own test suite. The runner invocation is unknown.
- **Level:** integration tests for `inspectdb`. They introspect real test tables and assert on the generated source text.
- **Cases:**
  1. A table with two FKs to the same other table. Both fields contain `related_name=...` and the values differ.
  2. A table with two FKs to itself (`'self'`). Both fields contain distinct `related_name` values.
  3. A table with a single FK to a target. No `related_name` in the output (regression guard).
  4. A table with one FK to target A and two FKs to target B. Only the two B fields get `related_name`.
  5. Optional but preferred: generated models load and pass `check()` with no E304/E305. This might be done by executing the generated code, but feasibility in the suite is unknown.
- **Coverage:** every new branch in the related-name generation logic is exercised.

## Boundaries

- **Always:**
  - Keep output identical for relation fields whose target is unique within the model.
  - Produce valid Python identifiers for `related_name`.
  - Add tests covering both the multi-FK case and the self-referential case.
- **Ask first:**
  - Choosing the `related_name` naming format.
  - Applying `related_name` to *all* relation fields, not only duplicates.
  - Adding a command-line option to toggle the behaviour.
  - Adding `related_query_name`.
  - Changing test models or schema shared with other tests.
  - Adding release notes or docs changes.
- **Never:**
  - Change how non-relation fields are generated.
  - Alter introspection backends' public APIs.
  - Silence the system check instead of generating unique names.
  - Remove or weaken existing `inspectdb` tests.

## Success Criteria

- [ ] For any introspected table with ≥2 relation fields to the same target model (including self), every such field in the generated output has a `related_name`.
- [ ] All generated `related_name` values pointing at a given target are unique across all generated models, so no E304/E305 clash is introduced between them.
- [ ] Relation fields with a unique target in their model are generated exactly as before.
- [ ] The new tests pass, and the existing `inspectdb` tests pass unchanged.
- [ ] Each `related_name` is a valid Python identifier.

## Open Questions

1. **Naming format:** should it be the attribute name only, as the issue suggests? Or something like `<model_lower>_<attname>_set`, which is unique across models? The attribute name alone can clash when two different models both have, for example, a `created_by` FK to `User`.
2. **Scope of application:** should `related_name` go only on duplicated targets, as assumed? Or on every relation field, as the issue's "to all fields in model" might suggest?
3. Should `related_query_name` also be set? Without it, the default query name, which is based on the model name, could still clash (E305).
4. Should reverse-accessor clashes with existing field names on the target model (E302/E303) be handled here or left out of scope?
5. Does this need a release note or a documentation update for `inspectdb`?
6. What are the exact source path, test path, and test-runner command? (Unknown.)
7. If the target table is not introspected (the target model is generated as a string reference or is missing), should duplicate detection still use the referenced table name?