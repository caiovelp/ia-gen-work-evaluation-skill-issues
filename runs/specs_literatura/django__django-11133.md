## Summary
`HttpResponse` does not handle `memoryview` content correctly. If a `memoryview` object is passed as content, `response.content` holds the object's string representation (for example `b'<memory at 0x7fcc47ab2648>'`) rather than the underlying bytes. This comes up when writing a `BinaryField` value from the database into an `HttpResponse`. SQLite returns the field contents in a form that works. PostgreSQL returns them as a `memoryview` object, which triggers the problem.

## Steps to reproduce
1. Import `HttpResponse` from `django.http`.
2. Create a response with string content: `HttpResponse("My Content")`, then read `response.content`. The result is `b'My Content'`, which is correct.
3. Create a response with bytes content: `HttpResponse(b"My Content")`, then read `response.content`. The result is `b'My Content'`, which is correct.
4. Create a response with memoryview content: `HttpResponse(memoryview(b"My Content"))`, then read `response.content`.

In practice, the same happens when you:
1. Store data in a model's `BinaryField` on a PostgreSQL database.
2. Retrieve the field value (PostgreSQL returns it as a `memoryview`).
3. Pass that value as the content of an `HttpResponse`.

## Observed behavior
With `memoryview` content, `response.content` is the string representation of the memoryview object:
```
b'<memory at 0x7fcc47ab2648>'
```
The same `BinaryField` workflow works on SQLite but fails on PostgreSQL, because PostgreSQL returns a `memoryview`.

## Expected behavior
`HttpResponse(memoryview(b"My Content")).content` should return the underlying bytes:
```
b'My Content'
```
This matches the behavior for `str` and `bytes` content.

## Stack trace / error output
Not provided in the original report. No exception is raised. The content is incorrect, as shown under "Observed behavior".

## Test case
Minimal test case derived from the report's snippet:
```python
from django.http import HttpResponse

def test_httpresponse_memoryview_content():
    response = HttpResponse(memoryview(b"My Content"))
    assert response.content == b"My Content"
```

## Code example
```python
from django.http import HttpResponse

# String content
response = HttpResponse("My Content")
response.content
# Out: b'My Content'
# This is correct

# Bytes content
response = HttpResponse(b"My Content")
response.content
# Out: b'My Content'
# This is also correct

# memoryview content
response = HttpResponse(memoryview(b"My Content"))
response.content
# Out: b'<memory at 0x7fcc47ab2648>'
# This is not correct, I am expecting b'My Content'
```

## Version and environment
- Django version: Not provided in the original report (described only as "current Django").
- Database: The issue happens with PostgreSQL, which returns `BinaryField` contents as `memoryview`. It does not happen with SQLite.
- Python version, OS, database driver version: Not provided in the original report.