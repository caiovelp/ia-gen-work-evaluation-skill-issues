## Summary

The `join` template filter escapes the joining string (the filter argument) even inside an `{% autoescape off %}` block. The list items are correctly left unescaped, but the separator is always escaped. The reporter found nothing in the documentation for `autoescape` or `join` that suggests this is intended.

## Steps to reproduce

1. Create a template that applies `join` to a list inside an `{% autoescape off %}` block, with the separator passed as a variable:
   ```django
   {% autoescape off %}{{ some_list|join:some_var }}{% endautoescape %}
   ```
2. Render it with this context:
   - `some_list = ["<p>Hello World!</p>", "beta & me", "<script>Hi!</script>"]`
   - `some_var = "<br/>"`
3. Inspect the rendered output.

## Observed behavior

The list items are output unescaped, but the joining string `<br/>` is escaped to `&lt;br/&gt;`:

```
<p>Hello World!</p>&lt;br/&gt;beta & me&lt;br/&gt;<script>Hi!</script>
```

## Expected behavior

With `autoescape` off, neither the list items nor the joining string should be escaped. The output should equal `some_var.join(some_list)`:

```
<p>Hello World!</p><br/>beta & me<br/><script>Hi!</script>
```

With autoescape on (the default), the existing behavior of escaping both the items and the separator should remain. The test `test_join01` below checks this case and passes.

## Stack trace / error output

```
.F
======================================================================
FAIL: test_join02 (template_tests.filter_tests.test_regression.RegressionTests.test_join02)
----------------------------------------------------------------------
Traceback (most recent call last):
 File "/home/nessita/fellowship/django/django/test/utils.py", line 443, in inner
	return func(*args, **kwargs)
		 ^^^^^^^^^^^^^^^^^^^^^
 File "/home/nessita/fellowship/django/tests/template_tests/utils.py", line 58, in inner
	func(self)
 File "/home/nessita/fellowship/django/tests/template_tests/filter_tests/test_regression.py", line 21, in test_join02
	self.assertEqual(output, some_var.join(some_list))
AssertionError: '<p>Hello World!</p>&lt;br/&gt;beta & me&lt;br/&gt;<script>Hi!</script>' != '<p>Hello World!</p><br/>beta & me<br/><script>Hi!</script>'
----------------------------------------------------------------------
Ran 2 tests in 0.007s
```

## Test case

Run this from inside the `template_tests/filter_tests` folder (for example, as `test_regression.py`). `test_join01` (autoescape on) passes. `test_join02` (autoescape off) fails.

```python
from django.template.defaultfilters import escape
from django.test import SimpleTestCase
from ..utils import setup


class RegressionTests(SimpleTestCase):
    @setup({"join01": '{{ some_list|join:some_var }}'})
    def test_join01(self):
        some_list = ["<p>Hello World!</p>", "beta & me", "<script>Hi!</script>"]
        some_var = "<br/>"
        output = self.engine.render_to_string("join01", {"some_list": some_list, "some_var": some_var})
        self.assertEqual(output, escape(some_var.join(some_list)))

    @setup({"join02": '{% autoescape off %}{{ some_list|join:some_var }}{% endautoescape %}'})
    def test_join02(self):
        some_list = ["<p>Hello World!</p>", "beta & me", "<script>Hi!</script>"]
        some_var = "<br/>"
        output = self.engine.render_to_string("join02", {"some_list": some_list, "some_var": some_var})
        self.assertEqual(output, some_var.join(some_list))
```

## Code example

```django
{% autoescape off %}
{{ some_list|join:some_var }}
{% endautoescape %}
```

## Version and environment

- Django: current `main` branch (exact commit not given)
- Python version and OS: Not provided in the original report.