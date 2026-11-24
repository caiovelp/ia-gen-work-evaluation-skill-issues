## Summary

When the primary key field of a model is renamed, the auto-generated migration for a `ForeignKey` pointing to that model sets the `to_field` parameter to the **old** field name instead of the new one.

## Steps to reproduce

1. Define these two models in an app (`app1`), where `ModelA` has a `CharField` primary key and `ModelB` has a `ForeignKey` to `ModelA`:
   ```python
   class ModelA(models.Model):
       field_wrong = models.CharField('field1', max_length=50, primary_key=True)  # I'm a Primary key.

   class ModelB(models.Model):
       field_fk = models.ForeignKey(ModelA, blank=True, null=True, on_delete=models.CASCADE)
   ```
2. Create and apply the migrations (resulting in `0001_initial`).
3. Rename the primary key field `ModelA.field_wrong` to `field_fixed`:
   ```python
   class ModelA(models.Model):
       field_fixed = models.CharField('field1', max_length=50, primary_key=True)  # I'm a Primary key.
   ```
4. Generate a new migration. Django detects the rename.
5. Inspect the generated migration.

## Observed behavior

The generated migration contains a `RenameField` operation for `modela` (`field_wrong` → `field_fixed`). It also contains an `AlterField` operation for the foreign key on `modelb`. In that operation, `to_field` is set to the old name `'field_wrong'` and not to the new name `'field_fixed'`. The generated migration is reproduced under "Code example" below.

Note: the original report has some inconsistencies. The text says the `to_field` points to "field_typo", but the migration shows `'field_wrong'`. The migration also shows `name='modela'` and `to='app1.ModelB'`, but the model definitions use `field_fk` and `ModelA`.

## Expected behavior

The `to_field` parameter of the `ForeignKey` should reference the new primary key name, `'field_fixed'`.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report.

## Code example

Migration generated after the rename, as given in the original report:

```python
class Migration(migrations.Migration):
    dependencies = [
        ('app1', '0001_initial'),
    ]
    operations = [
        migrations.RenameField(
            model_name='modela',
            old_name='field_wrong',
            new_name='field_fixed',
        ),
        migrations.AlterField(
            model_name='modelb',
            name='modela',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app1.ModelB', to_field='field_wrong'),
        ),
    ]
```

## Version and environment

Not provided in the original report.