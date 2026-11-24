## Summary

Saving a figure with the PostScript backend (`.eps`) raises `TypeError: cannot unpack non-iterable NoneType object` when the figure contains a multi-line text label that has an empty line, such as text starting with `\n`. This affects annotations and titles. The same figure saves without error with other backends (PNG, PDF, SVG, Qt). According to the reporter, this is a regression: it works with matplotlib <= 3.5.3 and fails with 3.6.0.

## Steps to reproduce

1. Create a `Figure` and add a subplot.
2. Add a text element whose string contains an empty line, for example:
   - `ax.annotate(text='\nLower label', xy=(0, 0))`, or
   - `ax.set_title('\nLower title')` (the reporter says this also triggers the error).
3. Save the figure with the PostScript backend: `figure.savefig('figure.eps')`.
4. Observe the `TypeError`.

## Observed behavior

`savefig` raises `TypeError: cannot unpack non-iterable NoneType object` from `backend_ps.py` in `draw_text`, and the `.eps` file is not saved successfully.

## Expected behavior

The figure is saved as `figure.eps` without error, as it is with the PNG, PDF, SVG and Qt backends and with matplotlib <= 3.5.3.

## Stack trace / error output

```
$ ./venv/Scripts/python save_ps.py
Traceback (most recent call last):
  File "C:\temp\matplotlib_save_ps\save_ps.py", line 7, in <module>
    figure.savefig('figure.eps')
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\figure.py", line 3272, in savefig
    self.canvas.print_figure(fname, **kwargs)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\backend_bases.py", line 2338, in print_figure
    result = print_method(
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\backend_bases.py", line 2204, in <lambda>
    print_method = functools.wraps(meth)(lambda *args, **kwargs: meth(
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\_api\deprecation.py", line 410, in wrapper
    return func(*inner_args, **inner_kwargs)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\backends\backend_ps.py", line 869, in _print_ps
    printer(fmt, outfile, dpi=dpi, dsc_comments=dsc_comments,
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\backends\backend_ps.py", line 927, in _print_figure
    self.figure.draw(renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\artist.py", line 74, in draw_wrapper
    result = draw(artist, renderer, *args, **kwargs)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\artist.py", line 51, in draw_wrapper
    return draw(artist, renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\figure.py", line 3069, in draw
    mimage._draw_list_compositing_images(
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\image.py", line 131, in _draw_list_compositing_images
    a.draw(renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\artist.py", line 51, in draw_wrapper
    return draw(artist, renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\axes\_base.py", line 3106, in draw
    mimage._draw_list_compositing_images(
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\image.py", line 131, in _draw_list_compositing_images
    a.draw(renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\artist.py", line 51, in draw_wrapper
    return draw(artist, renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\text.py", line 1995, in draw
    Text.draw(self, renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\artist.py", line 51, in draw_wrapper
    return draw(artist, renderer)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\text.py", line 736, in draw
    textrenderer.draw_text(gc, x, y, clean_line,
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\backends\backend_ps.py", line 248, in wrapper
    return meth(self, *args, **kwargs)
  File "C:\temp\matplotlib_save_ps\venv\lib\site-packages\matplotlib\backends\backend_ps.py", line 673, in draw_text
    for ps_name, xs_names in stream:
TypeError: cannot unpack non-iterable NoneType object
```

## Test case

This is a minimal test derived from the reproduction snippet in the report. It should pass, meaning no exception is raised:

```python
from matplotlib.figure import Figure

def test_eps_text_with_empty_line():
    figure = Figure()
    ax = figure.add_subplot(111)
    ax.annotate(text='\nLower label', xy=(0, 0))
    figure.savefig('figure.eps')

def test_eps_title_with_empty_line():
    figure = Figure()
    ax = figure.add_subplot(111)
    ax.set_title('\nLower title')
    figure.savefig('figure.eps')
```

## Code example

```python
from matplotlib.figure import Figure

figure = Figure()
ax = figure.add_subplot(111)
# ax.set_title('\nLower title')  # this would cause an error as well
ax.annotate(text='\nLower label', xy=(0, 0))
figure.savefig('figure.eps')
```

## Version and environment

- Matplotlib version: 3.6.0 (works with matplotlib <= 3.5.3)
- Python version: 3.9.13
- Operating system: Windows
- Installation: pip (virtual environment)
- Backend: PostScript, via saving to `.eps`. PNG, PDF, SVG and Qt backends are reported to work.