## Summary

Passing `domain='RR[y,z]'` explicitly to `Poly` raises `OptionError`. Yet when no domain is given, `Poly` infers `RR[y,z]` for the same expression, so the domain is valid. The reporter also says the wording of the error message could be improved.

## Steps to reproduce

1. Start an interactive SymPy session (the report uses IPython). Define symbols `x`, `y` and `z`. The report does not show how they were defined.
2. Run `Poly(1.2*x*y*z, x)` without a domain. This works, and the result shows `domain='RR[y,z]'`.
3. Run `Poly(1.2*x*y*z, x, domain='RR[y,z]')`, passing the domain that step 2 inferred.
4. An `OptionError` is raised.

## Observed behavior

Without an explicit domain, construction works and infers `RR[y,z]`:

```py
In [14]: Poly(1.2*x*y*z, x)
Out[14]: Poly(1.2*y*z*x, x, domain='RR[y,z]')
```

With `domain='RR[y,z]'` given explicitly, construction fails:

```
OptionError: expected a valid domain specification, got RR[y,z]
```

The error comes from the domain preprocessing step in `sympy/polys/polyoptions.py`, which does not accept the string `'RR[y,z]'`.

## Expected behavior

`Poly(1.2*x*y*z, x, domain='RR[y,z]')` should succeed. It should create a polynomial over `RR[y,z]`, the same domain `Poly` infers automatically for this expression, as in `Out[14]`.

The reporter also says the wording of the `OptionError` message ("expected a valid domain specification, got ...") could be improved. The report gives no specific alternative wording.

## Stack trace / error output

```
---------------------------------------------------------------------------
OptionError                               Traceback (most recent call last)
<ipython-input-15-d83389519ae1> in <module>()
----> 1 Poly(1.2*x*y*z, x, domain='RR[y,z]')

/Users/aaronmeurer/Documents/Python/sympy/sympy-scratch/sympy/polys/polytools.py in __new__(cls, rep, *gens, **args)
     69     def __new__(cls, rep, *gens, **args):
     70         """Create a new polynomial instance out of something useful. """
---> 71         opt = options.build_options(gens, args)
     72
     73         if 'order' in opt:

/Users/aaronmeurer/Documents/Python/sympy/sympy-scratch/sympy/polys/polyoptions.py in build_options(gens, args)
    718
    719     if len(args) != 1 or 'opt' not in args or gens:
--> 720         return Options(gens, args)
    721     else:
    722         return args['opt']

/Users/aaronmeurer/Documents/Python/sympy/sympy-scratch/sympy/polys/polyoptions.py in __init__(self, gens, args, flags, strict)
    151                     self[option] = cls.preprocess(value)
    152
--> 153         preprocess_options(args)
    154
    155         for key, value in dict(defaults).items():

/Users/aaronmeurer/Documents/Python/sympy/sympy-scratch/sympy/polys/polyoptions.py in preprocess_options(args)
    149
    150                 if value is not None:
--> 151                     self[option] = cls.preprocess(value)
    152
    153         preprocess_options(args)

/Users/aaronmeurer/Documents/Python/sympy/sympy-scratch/sympy/polys/polyoptions.py in preprocess(cls, domain)
    480                 return sympy.polys.domains.QQ.algebraic_field(*gens)
    481
--> 482         raise OptionError('expected a valid domain specification, got %s' % domain)
    483
    484     @classmethod

OptionError: expected a valid domain specification, got RR[y,z]
```

## Test case

This minimal test is derived from the report's snippet. It checks that an explicit `RR[y,z]` domain is accepted and matches the inferred one:

```py
from sympy import Poly, symbols

x, y, z = symbols('x y z')

def test_poly_explicit_RR_polynomial_ring_domain():
    inferred = Poly(1.2*x*y*z, x)            # works; domain shown as RR[y,z]
    explicit = Poly(1.2*x*y*z, x, domain='RR[y,z]')  # currently raises OptionError
    assert explicit == inferred
```

## Code example

```py
Poly(1.2*x*y*z, x)                    # OK -> Poly(1.2*y*z*x, x, domain='RR[y,z]')
Poly(1.2*x*y*z, x, domain='RR[y,z]')  # OptionError: expected a valid domain specification, got RR[y,z]
```

## Version and environment

- SymPy run from a local source checkout (`.../sympy/sympy-scratch/`). The report gives no version number or commit.
- The session is IPython. The file paths (`/Users/...`) suggest macOS.
- Python version: Not provided in the original report.