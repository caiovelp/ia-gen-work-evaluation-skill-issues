## Summary
Generate man page section directories (e.g., `man/man1/`, `man/man3/`) in Sphinx's man page output.

## Description
Sphinx currently puts all generated man pages into a single directory: `<build-dir>/man`.

The Unix `man` program looks for man pages in section subdirectories such as `man/man1`, `man/man3`, and so on. Because of this, the flat output directory cannot be used with the `MANPATH` environment variable.

The request is for Sphinx to create the section directories automatically and to place each generated man page in the directory for its section.

## Product version
Not provided in the original request.

## Rationale
- The current flat layout does not work with the `MANPATH` search mechanism. The `man` program only finds man pages that are in section directories.
- The problem can be worked around in a project's own build system, by installing the built man pages in the correct location. However, it would be better if the build directory already had the proper layout, so that the output can be used directly.

## Use case or scenario
A project generates man pages with Sphinx and wants to use the build output directly. The user adds `<build-dir>/man` to the `MANPATH` environment variable so that `man` can find the pages. This fails today because the pages are not in section subdirectories such as `man1` or `man3`.

## Possible solution
- **Suggested solution:** Sphinx automatically creates section directories (e.g., `man/man1/`, `man/man3/`) and places each generated man page in the directory for its section.
- **Alternative considered:** Handle the problem in each project's build system by installing the built man pages in the correct location. The reporter finds this less desirable than having the correct layout in the build directory.
- **Compatibility concern:** Changing this behavior may break setups that expect all man pages to be directly inside the `man/` directory.
- The reporter is willing to try implementing a fix.