## Summary

`django.utils.http.parse_http_date` interprets two-digit years in RFC 850-format dates with a hard-coded rule rather than relative to the current year. RFC 7231 requires the latter, and RFC 2822 has a similar rule.

## Steps to reproduce

1. Call `django.utils.http.parse_http_date` with a timestamp in RFC 850 date format, which uses a two-digit year.
2. Use a two-digit year between 0 and 69 that, read as 20xx, would be more than 50 years in the future relative to the current year.
3. Look at the year the parsed result uses.

(The original report describes the faulty logic but gives no concrete input values.)

## Observed behavior

The two-digit year is mapped with a fixed rule:
- Years 0–69 become 2000–2069.
- Years 70–99 become 1970–1999.

The current year plays no part in this, so a timestamp can be read as more than 50 years in the future.

## Expected behavior

The current year should decide how a two-digit year is read. RFC 7231 says:

> Recipients of a timestamp value in rfc850-date format, which uses a two-digit year, MUST interpret a timestamp that appears to be more than 50 years in the future as representing the most recent year in the past that had the same last two digits.

RFC 850 itself does not mention this rule.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report.

## Code example

Not provided in the original report.

## Version and environment

Not provided in the original report.