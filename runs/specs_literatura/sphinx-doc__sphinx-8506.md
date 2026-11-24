## Summary

Sphinx 3.2 rejects an `option::` directive whose argument is `[enable=]PATTERN`, reporting it as a "Malformed option description". Earlier Sphinx versions accepted the same markup without complaint. This breaks documentation builds that previously worked, such as the QEMU documentation. Projects that must build with whatever `sphinx-build` the Linux distribution ships are particularly affected.

## Steps to reproduce

1. In a Sphinx project, add a reStructuredText file containing the following `option::` directive. In QEMU it is in `docs/qemu-option-trace.rst.inc`:
   ```rst
   .. option:: [enable=]PATTERN

      Immediately enable events matching *PATTERN*
   ```
2. Build the documentation with Sphinx 3.2, with warnings treated as errors, as in the reporter's build.
3. Observe the warning or error for the `option::` directive.
4. For comparison, build the same documentation with an earlier Sphinx version. It builds without complaint.

## Observed behavior

Sphinx 3.2 emits a "Malformed option description" warning for `[enable=]PATTERN`. Because warnings are treated as errors, the documentation build fails. Earlier Sphinx versions built the same source without any warning.

## Expected behavior

The `option::` directive with the description `[enable=]PATTERN` should be accepted as it was in earlier Sphinx versions, without a warning or error. The documentation should keep building after upgrading to Sphinx 3.2.

The reporter's view is that the directive should accept any string as an option description. The forms listed in the error message (`opt`, `-opt args`, `--opt args`, `/opt args`, `+opt args`) don't cover the option syntax of all programs and operating systems.

## Stack trace / error output

```
Warning, treated as error:
../../docs/qemu-option-trace.rst.inc:4:Malformed option description '[enable=]PATTERN', should look like "opt", "-opt args", "--opt args", "/opt args" or "+opt args"
```

No stack trace was provided.

## Test case

Minimal reStructuredText input derived from the report:

```rst
.. option:: [enable=]PATTERN

   Immediately enable events matching *PATTERN*
```

- **Pass:** building with Sphinx 3.2 and warnings treated as errors succeeds, with no "Malformed option description" warning.
- **Fail (current behavior):** the build fails with the warning shown above.

## Code example

From the QEMU documentation, where it documents the command-line options of one of QEMU's programs:

```rst
.. option:: [enable=]PATTERN

   Immediately enable events matching *PATTERN*
```

## Version and environment

- **Failing version:** Sphinx 3.2
- **Working versions:** earlier Sphinx versions. The exact versions were not specified.
- **Context:** the QEMU documentation build, with warnings treated as errors. The reporter mentions building with the Linux distribution's `sphinx-build`.
- **Python version, OS and distribution:** Not provided in the original report.