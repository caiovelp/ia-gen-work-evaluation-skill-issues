## Summary
Add a check that ensures `Field.max_length` is large enough to fit the longest value in `Field.choices`.

## Description
There is currently no check that verifies whether a field's `max_length` can hold the longest value defined in its `choices`. So a field can be declared with choice values longer than its `max_length`, and nothing reports the mismatch.

## Product version
Not provided in the original request.

## Rationale
This mistake often goes unnoticed until someone tries to save a record using one of the choice values that is too long. A check would surface the problem early, before it causes an error at save time.

## Use case or scenario
A developer defines a field with a `max_length` and a set of `choices`, where at least one choice value is longer than `max_length`. Right now nothing flags this. The problem only shows up later, when a record with one of the too-long values is saved.

## Possible solution
Add a check that compares `Field.max_length` with the length of the longest value in `Field.choices` and reports when `max_length` is too small.