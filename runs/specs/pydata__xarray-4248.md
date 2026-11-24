# Spec: Show Units in the `Dataset` Text Repr

## Objective

Show the units of each coordinate and data variable in the plain-text `xarray.Dataset` repr. Users can then read the physical meaning of each variable (metres, mm, deg C) from the overview, without inspecting `.attrs` one variable at a time.

**User:** Someone working interactively in a REPL or notebook who prints a `Dataset` to get an overview of its contents.

**User story:** As an xarray user, when I print a `Dataset`, I want each coordinate and data variable line to show its units, if it has any, so I can understand the data at a glance.

**Requested output (from the issue):**

```
<xarray.Dataset>
Dimensions:  (time: 3, x: 988, y: 822)
Coordinates:
  * x, in metres         (x)            float64 ...
  * y, in metres         (y)            float64 ...
  * time                 (time)         datetime64[ns] ...
Data variables:
    rainfall, in mm      (time, y, x)   float32 ...
    max_temp, in deg C   (time, y, x)   float32 ...
```

Notable properties of this example:
- Units follow the variable name in the form `<name>, in <units>`.
- A variable without units (`time`) shows only its name. It gets no placeholder.
- The dims, dtype and values columns stay aligned across all lines after the name is made longer.

## Assumptions

1. A variable's units come from its `attrs["units"]` entry, following the CF conventions. The issue does not say where units come from.
2. Only the plain-text `__repr__` of `Dataset` is in scope. Whether the HTML notebook repr, the `DataArray` repr, or `Dataset.info()` should change is an open question.
3. A variable with no `units` attribute is rendered exactly as it is today, apart from any column-alignment changes caused by other lines.
4. The `<name>, in <units>` format in the issue is a suggestion, not a fixed requirement. The final format is an open question.
5. Units are shown as their string form. They are not parsed, validated or normalised: `"m"` stays `"m"` and is not expanded to `"metres"`.
6. Behaviour is the same for coordinates (indexed `*` and non-indexed) and data variables.
7. Showing units must not load lazy or backend-backed data. Reading `attrs` is assumed to be cheap and not to trigger computation.
8. The change is to existing repr/formatting code. No new dependency (for example, a units library) is introduced.

## Tech Stack

- Python library: xarray.
- Python version, supported dependency versions and the formatting module location: **unknown** (not visible in the issue).

## Commands

All **unknown**. The repository is not visible. To be filled in from the project's contributor docs:

```
Install (dev): unknown
Test:          unknown
Lint/format:   unknown
Docs build:    unknown
```

## Project Structure

**Unknown.** The issue does not show the repository layout. The spec only assumes that:
- Some source module produces the `Dataset` text repr (location unknown).
- An existing test suite covers repr output (location unknown).
- Documentation and a changelog/"what's new" file may exist (locations unknown).

## Code Style

Unknown. Follow the existing conventions of the repr/formatting code and the project's configured linters. No style example is available from the issue.

## Testing Strategy

- **Framework:** unknown (to be confirmed from the repo).
- **Unit tests on repr output.** Build small in-memory `Dataset`s and assert the exact repr strings for:
  - A coordinate with units, a coordinate without units, and an indexed (`*`) coordinate with units.
  - A data variable with units and one without.
  - Column alignment when names and units have different lengths.
  - A long units string, checking the agreed truncation or width behaviour.
  - A non-string `units` value (for example a number or list), checking the agreed behaviour.
  - An empty-string `units` attribute.
  - Unicode units (for example `°C`, `µm`).
  - A `Dataset` with no variables or coordinates, which must render unchanged.
- **Regression:** existing repr tests either pass unchanged (variables without units) or are updated deliberately, with each update explained.
- **Laziness:** a test confirming that printing a `Dataset` backed by lazy data does not trigger computation or loading.
- **Coverage expectation:** unknown project threshold. All new branches in the formatting logic are covered.

## Boundaries

- **Always:**
  - Keep the repr of variables without units visually identical, except where alignment requires a change.
  - Keep the dims/dtype/values columns aligned.
  - Respect any existing repr width limits and truncation rules.
  - Add or adjust tests for every repr change.
  - Add a changelog entry if the project keeps one.
- **Ask first:**
  - Changing the output format away from the issue's suggestion.
  - Extending the change to the HTML repr, `DataArray` repr or `info()`.
  - Adding a configuration option, for example in `xr.set_options`, to turn the feature on or off.
  - Changing existing repr snapshots that have no units, for example because of alignment shifts.
  - Reading units from any source other than `attrs["units"]`.
- **Never:**
  - Load or compute lazy data to build the repr.
  - Add a units library dependency.
  - Modify `attrs` or any data as a side effect of printing.
  - Delete or weaken existing repr tests to make them pass.

## Success Criteria

1. Printing a `Dataset` whose coordinates and data variables carry `attrs["units"]` shows each variable's units on its line, in the agreed format.
2. Variables without a `units` attribute show only their name, with no placeholder text.
3. The dims, dtype and values columns stay aligned across all coordinate and data-variable lines.
4. Using the example in the issue, the output matches the agreed target string exactly. If the format proposed in the issue is accepted, that means the issue's example.
5. Printing a lazily backed `Dataset` triggers no data loading.
6. Non-string, empty and very long `units` values render according to the agreed rules and never raise an exception during repr.
7. All existing tests pass, and any updated repr expectations are justified in review.

## Open Questions

1. **Format.** Is `name, in units` the desired format? Alternatives include `name [units]`, `name (units)`, or a separate aligned units column. A separate column might read better and would not overload the name column.
2. **Source of units.** Should only `attrs["units"]` be used? Should units from duck arrays that carry units (for example pint-wrapped data) also be shown, and which wins if both are present?
3. **Scope.** Should the same change apply to the HTML notebook repr, the `DataArray` repr (its coordinates and the array itself), and `Dataset.info()`?
4. **Opt-in or default.** Should this be on by default, or controlled by a display option? Turning it on by default changes the output for many users and many downstream doctests.
5. **Width and truncation.** How should very long units strings be handled? Should they be truncated with an ellipsis, and is there a maximum width for the name-plus-units column?
6. **Non-string units.** How should numbers, lists, `None` or an empty string in `attrs["units"]` be displayed? Should they be stringified, skipped, or shown as-is?
7. **Alignment cost.** Is it acceptable that adding units to one variable widens the name column for all lines, including lines that have no units?
8. **Other attributes.** Should other common attributes such as `long_name` or `standard_name` be considered, or is this strictly limited to units?
9. **Repository details.** What are the formatting module location, the test/lint/build commands and the changelog location? These are all unknown from the issue.