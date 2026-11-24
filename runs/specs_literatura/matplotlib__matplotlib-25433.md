## Summary

In Matplotlib, a `RangeSlider` `on_changed` callback that calls `pyplot.clf()`, adds new widgets and then calls `pyplot.draw()` leaves every widget in the figure unable to receive input. The same sequence in a `Button` `on_clicked` callback works fine.

## Steps to reproduce

1. Run the script in the "Code example" section. It creates a figure with a `RangeSlider` and a `Button`. Each widget's callback clears the figure (`pyplot.clf()`), re-creates both widgets (`addElements()`) and redraws (`pyplot.draw()`).
2. Click the **Button**. The figure is cleared and redrawn, and the widgets still respond to mouse input.
3. Drag or click the **RangeSlider** so its `on_changed` callback fires. The figure is cleared and redrawn.
4. Try to click either of the newly created widgets (slider or button).

## Observed behavior

After the figure is redrawn from the `RangeSlider` `on_changed` callback, no widget in the figure receives mouse clicks.

When the figure is redrawn from the `Button` `on_clicked` callback, there is no problem.

## Expected behavior

The `RangeSlider` `on_changed` callback should behave the same as the `Button` `on_clicked` callback. After clearing and redrawing the figure, the newly created widgets should keep responding to mouse input.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report. The reproduction script under "Code example" serves as a manual (interactive) reproduction.

## Code example

```python
import matplotlib.pyplot as pyplot
import matplotlib.widgets as widgets

def onchanged(values):
    print("on changed")
    print(values)
    pyplot.clf()
    addElements()
    pyplot.draw()

def onclick(e):
    print("on click")
    pyplot.clf()
    addElements()
    pyplot.draw()

def addElements():
    ax = pyplot.axes([0.1, 0.45, 0.8, 0.1])
    global slider
    slider = widgets.RangeSlider(ax, "Test", valmin=1, valmax=10, valinit=(1, 10))
    slider.on_changed(onchanged)
    ax = pyplot.axes([0.1, 0.30, 0.8, 0.1])
    global button
    button = widgets.Button(ax, "Test")
    button.on_clicked(onclick)

addElements()

pyplot.show()
```

## Version and environment

**Primary environment:**
- Operating system: Windows 10
- Matplotlib version: 3.6.2
- Matplotlib backend: TkAgg
- Python version: 3.11.0
- Installation: pip
- Jupyter version: not provided

**Also reproduced on:**
- Operating system: Manjaro Linux
- Matplotlib version: 3.6.2
- Matplotlib backend: QtAgg
- Python version: 3.10.9
- Installation: Linux package manager

The bug therefore occurs with both the TkAgg and QtAgg backends.