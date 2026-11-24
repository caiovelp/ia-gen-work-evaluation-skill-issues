## Summary

In Matplotlib 3.5.0, a 3D line plot fails with `AttributeError: 'Line3D' object has no attribute '_verts3d'` after a previous failed plot call in the same IPython session.

The sequence is:

1. The plotting code works with integer inputs.
2. The reporter passes a NumPy array as one coordinate value (`x_s_0[n]`). This fails with `input operand has more dimensions than allowed by the axis remapping`.
3. The reporter goes back to integer inputs. Every later run now fails at `plt.show()` with the `AttributeError`.

The error continues whatever the variables are changed to, and even after they are deleted. Only restarting the IPython console kernel clears it.

## Steps to reproduce

1. Start an IPython console. The reporter used PyCharm on Windows, connected to a remote Ubuntu 20.04 interpreter, with the `module://backend_interagg` backend.
2. Fill the six arrays `x_s_0`, `x_e_0`, `y_s_0`, `y_e_0`, `z_s_0`, `z_e_0` with integer values. The actual values are not given in the report.
3. Run the code from the Code example section. **Result:** the 3D lines are drawn correctly.
4. Run the code again, but make `x_s_0[n]` a NumPy array instead of an int. The exact array is not given in the report. **Result:** an error occurs: `input operand has more dimensions than allowed by the axis remapping`.
5. Set `x_s_0[n]` and the other variables back to int values and run the code again. **Result:** `AttributeError: 'Line3D' object has no attribute '_verts3d'` is raised from `plt.show()`.
6. Change or delete the variables and run again. **Result:** the same `AttributeError` occurs every time until the IPython kernel is restarted.

## Observed behavior

- After a failed call with array-valued input, every later attempt to draw the figure fails during `plt.show()`. The failure happens in `mpl_toolkits/mplot3d/art3d.py`, `Line3D.draw`, with `AttributeError: 'Line3D' object has no attribute '_verts3d'`.
- The error survives changes to the variables and deleting them. Only a kernel restart clears it.

## Expected behavior

Once valid integer inputs are supplied again, the code should draw the 3D lines, as it did on the first run.

## Stack trace / error output

Error at step 4 (only the message was reported, with no full traceback):

```
input operand has more dimensions than allowed by the axis remapping
```

Error at steps 5 and 6:

```
Traceback (most recent call last):
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/IPython/core/interactiveshell.py", line 3444, in run_code
    exec(code_obj, self.user_global_ns, self.user_ns)
  File "<ipython-input-80-e04907066a16>", line 20, in <module>
    plt.show()
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/matplotlib/pyplot.py", line 368, in show
    return _backend_mod.show(*args, **kwargs)
  File "/home/hanyaning/.pycharm_helpers/pycharm_matplotlib_backend/backend_interagg.py", line 29, in __call__
    manager.show(**kwargs)
  File "/home/hanyaning/.pycharm_helpers/pycharm_matplotlib_backend/backend_interagg.py", line 112, in show
    self.canvas.show()
  File "/home/hanyaning/.pycharm_helpers/pycharm_matplotlib_backend/backend_interagg.py", line 68, in show
    FigureCanvasAgg.draw(self)
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/matplotlib/backends/backend_agg.py", line 436, in draw
    self.figure.draw(self.renderer)
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/matplotlib/artist.py", line 73, in draw_wrapper
    result = draw(artist, renderer, *args, **kwargs)
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/matplotlib/artist.py", line 50, in draw_wrapper
    return draw(artist, renderer)
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/matplotlib/figure.py", line 2803, in draw
    mimage._draw_list_compositing_images(
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/matplotlib/image.py", line 132, in _draw_list_compositing_images
    a.draw(renderer)
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/matplotlib/artist.py", line 50, in draw_wrapper
    return draw(artist, renderer)
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/mpl_toolkits/mplot3d/axes3d.py", line 469, in draw
    super().draw(renderer)
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/matplotlib/artist.py", line 50, in draw_wrapper
    return draw(artist, renderer)
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/matplotlib/axes/_base.py", line 3082, in draw
    mimage._draw_list_compositing_images(
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/matplotlib/image.py", line 132, in _draw_list_compositing_images
    a.draw(renderer)
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/matplotlib/artist.py", line 50, in draw_wrapper
    return draw(artist, renderer)
  File "/home/hanyaning/anaconda3/envs/SBeA/lib/python3.8/site-packages/mpl_toolkits/mplot3d/art3d.py", line 215, in draw
    xs3d, ys3d, zs3d = self._verts3d
AttributeError: 'Line3D' object has no attribute '_verts3d'
```

## Test case

Not provided in the original report. The reproduction code uses placeholders (`'my int number list'`) instead of real data. The report also does not give the NumPy array that was assigned to `x_s_0[n]` in step 4, so a self-contained test case cannot be built from it.

## Code example

This is the code from the report. Indentation is normalized, and the placeholder data is kept as written. The imports (`numpy as np`, `matplotlib.pyplot as plt`, and mplot3d) are not shown in the original.

```python
x_s_0 = np.array(['my int number list'])
x_e_0 = np.array(['my int number list'])
y_s_0 = np.array(['my int number list'])
y_e_0 = np.array(['my int number list'])
z_s_0 = np.array(['my int number list'])
z_e_0 = np.array(['my int number list'])

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=90, azim=0)
ax.set_zlim3d(-10, 10)
clr_list = 'r-'

for n in range(np.size(z_s_0, axis=0)):
    ax.plot([int(x_s_0[n]), int(x_e_0[n])],
            [int(y_s_0[n]), int(y_e_0[n])],
            [int(z_s_0[n]), int(z_e_0[n])], clr_list)

plt.xlabel('x')
plt.ylabel('y')
# ax.zlabel('z')
plt.title('90-0')
plt.show()
```

## Version and environment

- **Matplotlib:** 3.5.0
- **Python:** 3.8.12
- **Backend:** `module://backend_interagg` (PyCharm's matplotlib backend)
- **Operating system:** local Windows running PyCharm; remote Ubuntu 20.04 interpreter (Anaconda environment `SBeA`)
- **Execution context:** IPython console
- **Installation:** pip
- **Jupyter version:** Not provided in the original report.