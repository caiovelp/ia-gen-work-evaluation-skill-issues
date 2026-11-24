## Summary
Add a `draggable` keyword argument to the `Legend` constructor so a legend can be made draggable when it is created.

## Description
There is currently no keyword that makes a legend draggable at creation time. To get a draggable legend, the user must first create the legend and then make it draggable with a separate call.

The request asks whether there is a technical (code) reason why a `draggable=True` keyword cannot be added to the `__init__` function of `Legend`. The reporter thinks this looks simple to implement but acknowledges there may be a reason it would not work.

## Product version
Not provided in the original request.

## Rationale
Setting draggability at creation would be more convenient than making a separate call after the legend has been created.

## Use case or scenario
A user creating a legend who wants it to be draggable. Today they must create the legend and then make it draggable in a second step. With the proposed keyword, they could set this in a single step when creating the legend.

## Possible solution
Add a `draggable` keyword argument (e.g., `draggable=True`) to the `Legend.__init__` function so that draggability can be enabled at creation time. The reporter asks maintainers to confirm whether there is a technical reason this would not work.