## Summary

In seaborn 0.11.1, `sns.pairplot` raises a `TypeError` when `hue_order` contains only some of the values in the `hue` column. In seaborn versions before 0.11, this call worked: only the listed hue values were plotted, and points with other hue values were omitted.

## Steps to reproduce

1. Install seaborn 0.11.1 (matplotlib 3.3.2 was used in the report).
2. Load the iris dataset: `iris = sns.load_dataset("iris")`. Its `species` column has three distinct values.
3. Call `pairplot` with `hue="species"` and a `hue_order` listing only two of those values:
   `sns.pairplot(iris, hue="species", hue_order=["setosa", "versicolor"])`
4. Observe that an exception is raised.

## Observed behavior

The call fails with a long error traceback. The first exception is raised in `seaborn/_core.py` and is a `TypeError` from `isnan` (see below).

## Expected behavior

As in seaborn < 0.11, the pair plot should be drawn using only the hue levels listed in `hue_order` (`setosa` and `versicolor`). Points whose hue value is not in the list (here, `virginica`) should not be plotted.

## Stack trace / error output

Only the first exception was included in the report. It arises in `seaborn/_core.py`:

```
TypeError: ufunc 'isnan' not supported for the input types, and the inputs could not be safely coerced to any supported types according to the casting rule ''safe''
```

The full traceback was not provided in the original report.

## Test case

Minimal test derived from the reproduction snippet. It currently fails with the `TypeError` above and should pass once the regression is resolved:

```python
import seaborn as sns

def test_pairplot_hue_order_subset_of_hue_values():
    iris = sns.load_dataset("iris")
    # "species" has three values; hue_order lists only two of them
    sns.pairplot(iris, hue="species", hue_order=["setosa", "versicolor"])
```

## Code example

From the original report (a stray trailing backtick after the first line has been removed):

```python
iris = sns.load_dataset("iris")
# The hue column contains three different species; here we want to plot two
sns.pairplot(iris, hue="species", hue_order=["setosa", "versicolor"])
```

## Version and environment

- seaborn: 0.11.1 (worked in seaborn < 0.11)
- matplotlib: 3.3.2
- matplotlib backends: MacOSX, Agg, or Jupyter notebook inline (the report lists all three)
- Python version, OS, numpy/pandas versions: Not provided in the original report.