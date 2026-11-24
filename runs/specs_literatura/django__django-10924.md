## Summary
Allow the `path` argument of Django's `FilePathField` to accept a callable.

## Description
A model field of type `FilePathField` stores paths to local files on the server or development machine. The directory holding these files differs from machine to machine, so the field's `path` is built from a setting:

```python
import os
from django.conf import settings
from django.db import models

class LocalFiles(models.Model):
    name = models.CharField(max_length=255)
    file = models.FilePathField(path=os.path.join(settings.LOCAL_FILE_DIR, 'example_dir'))
```

When `manage.py makemigrations` runs, the expression is evaluated on the machine where the command is run. The resulting absolute path is written into the migration file, for example `/home/<username>/server_files/example_dir`. The request is that `FilePathField` accept a callable for `path`, so the path is not fixed at migration-generation time.

## Product version
Not provided in the original request.

## Rationale
- The storage directory differs between machines (development, production, others).
- Because the path is resolved when `makemigrations` runs, the migration contains a machine-specific absolute path.
- That migration breaks when it runs on production or any other machine.
- The current workaround is to edit the generated migration by hand so it contains the `os.path.join()` expression instead of the resolved path. This is manual and easy to get wrong.

## Use case or scenario
1. A developer defines a model with a `FilePathField` whose `path` is built from `settings.LOCAL_FILE_DIR`. That setting has a different value on each machine.
2. The developer runs `manage.py makemigrations` on their own machine. The migration records the resolved path, e.g. `/home/<username>/server_files/example_dir`.
3. The migration is then run on production or another machine, where the path is wrong.
4. Today the developer must edit the migration by hand to restore the `os.path.join()` expression.

## Possible solution
Let `FilePathField`'s `path` argument accept a callable, as the title proposes. No further implementation details are given in the original request.