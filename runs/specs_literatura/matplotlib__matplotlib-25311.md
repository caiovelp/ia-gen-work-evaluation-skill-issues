## Summary

A Matplotlib figure cannot be pickled once its legend has been made draggable. `pickle.dumps(fig)` raises `TypeError: cannot pickle 'FigureCanvasQTAgg' object`. Removing the `leg.set_draggable(True)` call makes pickling work. The reporter says draggable annotations cause the same error.

## Steps to reproduce

1. Create a figure and add a subplot: `fig = plt.figure()`, `ax = fig.add_subplot(111)`.
2. Plot data with a label: `ax.plot([0,1,2,3,4], [40,43,45,47,48], label="speed")`.
3. Create a legend: `leg = ax.legend()`.
4. Make the legend draggable: `leg.set_draggable(True)`.
5. Pickle the figure: `pickle.dumps(fig)`.
6. A `TypeError` is raised.

For comparison, skip step 4 and pickling succeeds.

## Observed behavior

`pickle.dumps(fig)` fails with:

```
TypeError: cannot pickle 'FigureCanvasQTAgg' object
```

This happens only when the legend is draggable. The reporter says the same error occurs with draggable annotations.

## Expected behavior

The figure pickles successfully, even with a draggable legend (or draggable annotations).

## Stack trace / error output

Only the final error message was provided:

```
TypeError: cannot pickle 'FigureCanvasQTAgg' object
```

The full traceback was not provided in the original report.

## Test case

A minimal test based on the reproduction code from the report:

```python
import pickle
import matplotlib.pyplot as plt

def test_pickle_figure_with_draggable_legend():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot([0, 1, 2, 3, 4], [40, 43, 45, 47, 48], label="speed")
    leg = ax.legend()
    leg.set_draggable(True)
    pickle.dumps(fig)  # expected to succeed; currently raises TypeError
```

## Code example

```python
import matplotlib.pyplot as plt
import pickle

fig = plt.figure()
ax = fig.add_subplot(111)

time=[0,1,2,3,4]
speed=[40,43,45,47,48]

ax.plot(time,speed,label="speed")

leg=ax.legend()
leg.set_draggable(True) #pickling works after removing this line 

pickle.dumps(fig)
plt.show()
```

## Version and environment

- Operating system: Windows 10
- Matplotlib version: 3.7.0
- Python version: 3.10
- Installation: pip
- Matplotlib backend: Not provided in the original report. The error message mentions `FigureCanvasQTAgg`.
- Jupyter version: Not provided in the original report.