## Summary
Allow the `:inherited-members:` option to accept more than one class.

## Description
The `:inherited-members:` option of `automodule` should accept a list of classes instead of a single class. When `autoclass` documentation is generated and any class in the list appears as a base class, members inherited from that class should be ignored. Members inherited from all other base classes should still be documented.

## Product version
Not provided in the original request.

## Rationale
The current option cannot handle two situations:

1. **Multiple inheritance:** A class inherits from several base classes. The user wants to document members from some of these base classes and ignore members from others.
2. **Modules with mixed base classes:** A module contains several classes that inherit from different built-in classes, such as `list`, `set` or `tuple`. The user wants to ignore members inherited from all of these built-ins while still documenting all other inherited members of the classes in the module.

The only workaround is to drop `automodule` and write a separate `autoclass` block for each class in the module. This has two drawbacks:
- It only solves the second situation, not the first.
- It is tedious for modules that contain many classes.

## Use case or scenario
- A user documents a class that inherits from several base classes. They want inherited members from some base classes to appear in the documentation and members from the other base classes to be left out.
- A user runs `automodule` on a module whose classes inherit from `list`, `set` or `tuple`. They want to exclude members inherited from `list`, `set` and `tuple` but keep every other inherited member of every class in the module, without writing an `autoclass` block for each class.

## Possible solution
Make the `:inherited-members:` option of `automodule` accept a list of classes. When `autoclass` documentation is generated, any base class that appears in this list is ignored, so its members are not documented.