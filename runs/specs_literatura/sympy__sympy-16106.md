## Summary
Add MathML printer support for `IndexedBase` / `Indexed` objects

## Description
Converting an `Indexed` object (created by indexing an `IndexedBase`) to MathML with `sympy.printing.mathml` fails with `TypeError: 'Indexed' object is not iterable`.

The MathML printer has no specific print method for `Indexed`, so it falls back to `_print_Basic`, which tries to iterate over the expression (`for arg in e:`). Because `Indexed` objects are not iterable, this raises the exception.

The failure also occurs for more complex expressions in which at least one element is `Indexed`.

**Steps to reproduce:**

```
In [340]: sympy.__version__
Out[340]: '1.0.1.dev'

In [341]: from sympy.abc import (a, b)

In [342]: sympy.printing.mathml(sympy.IndexedBase(a)[b])
```

**Actual result:**

```
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-342-b32e493b70d3> in <module>()
----> 1 sympy.printing.mathml(sympy.IndexedBase(a)[b])

/dev/shm/gerrit/venv/stable-3.5/lib/python3.5/site-packages/sympy/printing/mathml.py in mathml(expr, **settings)
    442 def mathml(expr, **settings):
    443     """Returns the MathML representation of expr"""
--> 444     return MathMLPrinter(settings).doprint(expr)
    445 
    446 

/dev/shm/gerrit/venv/stable-3.5/lib/python3.5/site-packages/sympy/printing/mathml.py in doprint(self, expr)
     36         Prints the expression as MathML.
     37         """
---> 38         mathML = Printer._print(self, expr)
     39         unistr = mathML.toxml()
     40         xmlbstr = unistr.encode('ascii', 'xmlcharrefreplace')

/dev/shm/gerrit/venv/stable-3.5/lib/python3.5/site-packages/sympy/printing/printer.py in _print(self, expr, *args, **kwargs)
    255                 printmethod = '_print_' + cls.__name__
    256                 if hasattr(self, printmethod):
--> 257                     return getattr(self, printmethod)(expr, *args, **kwargs)
    258             # Unknown object, fall back to the emptyPrinter.
    259             return self.emptyPrinter(expr)

/dev/shm/gerrit/venv/stable-3.5/lib/python3.5/site-packages/sympy/printing/mathml.py in _print_Basic(self, e)
    356     def _print_Basic(self, e):
    357         x = self.dom.createElement(self.mathml_tag(e))
--> 358         for arg in e:
    359             x.appendChild(self._print(arg))
    360         return x

TypeError: 'Indexed' object is not iterable
```

**Expected result:**
A MathML representation of the indexed expression, without an exception.

## Product version
SymPy `1.0.1.dev` (Python 3.5)

## Rationale
At present, no expression that contains an `Indexed` element can be exported to MathML. This applies both to a single indexed object and to any larger expression that contains one. Users who work with indexed quantities therefore cannot use the MathML printer at all for those expressions.

## Use case or scenario
A user builds an expression with an indexed symbol, such as `IndexedBase(a)[b]`, either alone or inside a more complex expression. The user then wants to convert it to MathML with `sympy.printing.mathml(...)`.

## Possible solution
The title of the request suggests adding a dedicated MathML printer for `IndexedBase` (and its `Indexed` objects). The printer would then no longer fall back to the generic `_print_Basic` method, which fails. No further implementation details were provided in the original request.