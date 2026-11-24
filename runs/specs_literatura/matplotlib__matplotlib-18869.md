## Summary
Add easily comparable version information to Matplotlib's top-level namespace.

## Description
Matplotlib currently exposes only `__version__`, which is a string. Checking the version quickly would be easier with a value that compares correctly. That could be either:
- a `version_info` tuple, which can be compared with other tuples, or
- a `LooseVersion` instance, which can be compared correctly with other version strings.

This would be a small usability improvement.

## Product version
Not provided in the original request.

## Rationale
Plain string comparison of `__version__` is unreliable. In practice it works for now, but it breaks once a version component reaches two digits, such as Matplotlib 3.10 or 4.10. The reporter says that won't happen soon, but relying on string comparison "feels quite dirty." A version object or tuple that compares properly would make version checks correct and simpler.

## Use case or scenario
A user or downstream code needs a quick check of the installed Matplotlib version, for example whether it is at least a given release. With a comparable version attribute, the check works correctly without relying on string comparison of `__version__`.

## Possible solution
Expose one of the following at the top level of Matplotlib:
- **`version_info` tuple:** much more common in other packages and possibly simpler to understand. The original request notes that `version_info` is a common convention elsewhere, without citing specific examples.
- **`LooseVersion` instance:** slightly preferred by the reporter.

The reporter expects the hardest part to be choosing between these two options.