# Spec: Do not raise models.W042 for models whose primary key is inherited from a parent model

## Objective

**Problem.** In Django 3.2 alpha, the system check `models.W042` ("Auto-created primary key used when not defining a primary key type…") fires for models that do not declare a primary key themselves but inherit one from an ancestor model. The reporter defines the primary key once on an ancestor (e.g. `Entity`), and descendants such as `accounts.User` inherit it. Django 3.1 did not report this, because W042 is new in 3.2.

**Why it matters.** W042 tells users to set `DEFAULT_AUTO_FIELD` or `AppConfig.default_auto_field`. For a model whose primary key is inherited, the child's key type comes from the parent, so that advice does not apply to the child. False positives:

- add noise to `makemigrations` and `check` output;
- push users to change settings for no reason;
- make the genuine warnings harder to spot.

**Users.** Django developers who use model inheritance and upgrade to 3.2.

**Desired behaviour.**

- W042 is raised only where Django actually auto-creates a primary key using the default auto-field type, i.e. a concrete model with no explicitly declared primary key anywhere in its inheritance chain.
- A model whose primary key comes from a parent must not get W042 on its own account. A parent may have declared its key explicitly, or the child may have a parent-link `OneToOneField` that serves as its pk. If the root ancestor itself relies on an auto-created pk, the root model is the one that should receive W042.

### Acceptance criteria / user stories

1. As a developer with a concrete parent that declares an explicit pk (e.g. `id = models.BigAutoField(primary_key=True)` or a non-auto pk), and a multi-table-inheritance child that declares no pk, `manage.py check` reports no W042 for the child.
2. As a developer whose child model has an explicit parent link (`OneToOneField(Parent, parent_link=True, primary_key=True)`), I get no W042 for the child.
3. As a developer with an abstract base that declares an explicit pk, I get no W042 for concrete subclasses. This should already work; it is a regression guard.
4. As a developer with a concrete root model that declares no pk and no `DEFAULT_AUTO_FIELD` / `default_auto_field` configured:
   - W042 is still raised for the root model;
   - the multi-table-inheritance child is not additionally flagged. This is an assumption; see Open Questions.
5. As a developer with a model that has no parents and no explicit pk, and no default auto field configured, I still get W042. This behaviour is unchanged.
6. W042 continues to be suppressed when `DEFAULT_AUTO_FIELD` is set or `AppConfig.default_auto_field` is overridden. This behaviour is unchanged.

## Assumptions

1. The reporter's models (e.g. `accounts.User` inheriting from `Entity`) use **multi-table (concrete) inheritance**, where the child's pk is the auto-created parent-link `OneToOneField`. The issue does not say whether `Entity` is abstract or concrete.
2. The false positive happens because the check treats the auto-created parent-link field as an "auto-created primary key". This is a hypothesis, not verified against source.
3. Some flagged models come from third-party apps, e.g. `friendship.*` and possibly `likes.UserLike`. Those models may genuinely lack an explicit pk, so their warnings may be legitimate. This spec only covers models whose pk is inherited.
4. The fix belongs in Django core (model system checks and/or model `Options` pk setup), targeted at the 3.2 release branch. It is not a documentation-only change.
5. Proxy models are not separately affected. They inherit the concrete model's pk and are presumably already excluded or handled; to be confirmed.
6. No change is intended to the wording, ID, or hint text of W042.

## Tech Stack

- Python, Django (3.2 alpha / main branch at the time of the report).
- Affected area: Django's model system checks (W042) and model metadata / primary-key setup for inherited models. Exact files and functions are **unknown** (no repository access).

## Commands

Unknown; no repository access. Django's test suite is conventionally run via its own test runner, but the exact invocation and the relevant test labels for this repo/environment are **unknown**.

```
Build: unknown (pure Python; likely none)
Test:  unknown — to be confirmed (Django's own test runner, targeting check-framework / model-inheritance tests)
Lint:  unknown
Dev:   n/a
```

## Project Structure

Unknown. Expected (unverified) areas of interest:

- Model base / system-check logic that emits `models.W042`: location unknown.
- Model `Options` / metadata where an inherited pk or parent link is promoted to pk: location unknown.
- Existing tests for the default-pk check and for model inheritance: locations unknown.

## Code Style

Follow the existing Django code style in the touched modules. No snippet is available from the issue. Tests should follow the existing pattern for system-check tests: define isolated models and assert the exact list of returned `checks.Warning` objects. File and fixture names are unknown.

## Testing Strategy

- **Level.** Unit tests for the system check, using models defined in isolated test apps. No database interaction is required beyond model definition.
- **Cases** (one per acceptance criterion 1–6):
  - concrete parent with explicit pk → child has no W042;
  - explicit `parent_link=True, primary_key=True` → no W042;
  - abstract parent with explicit pk → no W042;
  - concrete parent with auto pk → W042 on parent only (pending Open Question 1);
  - standalone model without pk → W042;
  - `DEFAULT_AUTO_FIELD` overridden or `AppConfig.default_auto_field` set → no W042.
- **Regression.** The existing W042 tests must still pass unchanged.
- **Coverage.** Every branch of the W042 condition is exercised.
- Framework, test locations and run commands: **unknown**.

## Boundaries

- **Always:**
  - add regression tests reproducing the false positive before changing behaviour;
  - keep the W042 ID, message and hint unchanged;
  - preserve W042 for genuinely auto-created default pks.
- **Ask first:**
  - changing how parent-link fields are flagged (e.g. altering `auto_created` semantics), since other code may depend on it;
  - changing which model (root vs. child) receives the warning;
  - backporting decisions;
  - adding release notes.
- **Never:**
  - silence W042 globally;
  - change the default value of `DEFAULT_AUTO_FIELD`;
  - alter migration autodetector output for inherited models;
  - remove or weaken existing check tests.

## Success Criteria

- With the reporter's pattern (concrete ancestor with explicit pk plus multi-table-inheritance descendants without their own pk), `check` and `makemigrations` emit no W042 for the descendants.
- W042 still fires for concrete models whose pk is genuinely auto-created with the implicit default type, and only for those.
- No changes to generated migrations for inherited models.
- All new tests (acceptance criteria 1–6) pass. The existing check-framework and model-inheritance test suites pass.

## Open Questions

1. **Root without explicit pk.** In multi-table inheritance where the root ancestor has an auto-created pk, should the child also receive W042, or only the root? This spec assumes only the root.
2. **Inheritance type.** Is the reporter's `Entity` abstract or concrete? If it is abstract with an explicit pk and W042 still fires, there is a second bug path.
3. **Third-party models.** Are the warnings on third-party models (`friendship.Block`, `friendship.Follow`, etc.) also inherited-pk false positives, or genuine models without a pk? A minimal reproduction from the reporter would help.
4. **Indirect inheritance.** Should a model that inherits from a parent which itself inherits its pk (multi-level inheritance) be covered explicitly? This spec assumes yes, with the same rule.
5. **Multiple concrete parents.** Should a model with more than one concrete parent behave the same as single inheritance (no W042 on the child)?
6. **Release process.** Is a release note required for 3.2, and should the fix be backported to the 3.2 alpha/beta branch?
7. **Logistics.** The exact code locations, test locations and test commands are unknown and must be confirmed against the repository.