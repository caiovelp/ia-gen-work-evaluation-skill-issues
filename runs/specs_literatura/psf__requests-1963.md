## Summary

`Session.resolve_redirects` starts each iteration of a redirect chain by copying the *original* request, not the most recent one. If an earlier redirect changed the method, a later redirect can bring the original method back. For example, a 303 See Other turns a POST into a GET, but a following 307 Temporary Redirect makes Requests issue a POST again.

## Steps to reproduce

1. Send a `POST` request to `/do_something` on `server.example.com` using a Requests `Session`.
2. The server responds with `303 See Other` and `Location: /new_thing_1513`.
3. Requests follows the redirect and sends a `GET` to `/new_thing_1513`. The 303 has correctly converted the POST to a GET.
4. The server responds with `307 Temporary Redirect` and `Location: //failover.example.com/new_thing_1513`.
5. Check which HTTP method Requests uses for the request to `failover.example.com/new_thing_1513`.

## Observed behavior

Requests sends a **POST** to `//failover.example.com/new_thing_1513`. This happens because each iteration of `Session.resolve_redirects` starts from a copy of the original request, which was a POST. The GET produced by the 303 is not carried forward.

## Expected behavior

The 307 Temporary Redirect should keep the method of the request it redirects, which is the **GET** produced by the earlier 303. Requests should send a **GET** to `//failover.example.com/new_thing_1513`.

## Stack trace / error output

Not provided in the original report.

## Test case

No test code is provided in the original report. A test could be built from the redirect chain in the report:

- Initial request: `POST /do_something` to `server.example.com`
- Response 1: `303 See Other`, `Location: /new_thing_1513` → next request should be `GET /new_thing_1513`
- Response 2: `307 Temporary Redirect`, `Location: //failover.example.com/new_thing_1513` → next request should be `GET`. Currently it is `POST`.

## Code example

Redirect chain from the original report:

```
POST /do_something HTTP/1.1
Host: server.example.com
...

HTTP/1.1 303 See Other
Location: /new_thing_1513

GET /new_thing_1513
Host: server.example.com
...

HTTP/1.1 307 Temporary Redirect
Location: //failover.example.com/new_thing_1513
```

## Version and environment

Not provided in the original report.