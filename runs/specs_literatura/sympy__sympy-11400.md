## Summary
`ccode(sinc(x))` does not generate usable C code

## Description
Passing the `sinc` function to `ccode` does not produce valid C code. It outputs a "not supported" comment followed by an unchanged `sinc(x)` call:

```
In [30]: ccode(sinc(x))
Out[30]: '// Not supported in C:\n// sinc\nsinc(x)'
```

The reporter notes that `math.h` probably does not provide a `sinc` function, so the output cannot be used directly as C code.

## Product version
Not provided in the original request.

## Rationale
Because C (`math.h`) has no built-in `sinc`, `ccode` currently marks the function as unsupported and emits a call to a function that does not exist in C. Expressions containing `sinc` therefore cannot be translated into working C code. `sinc` can be written using functions C does support (`sin` and division) plus a special case at zero, so `ccode` could produce valid output instead of failing.

## Use case or scenario
A user has an expression containing `sinc(x)` and calls `ccode` to generate C code from it. The user expects compilable C code, but instead gets a "Not supported in C" comment and a call to an undefined `sinc` function.

## Possible solution
Have `ccode` print `sinc` as its piecewise definition: `sin(x)/x` when `x` is not zero, and `1` otherwise. The reporter shows the output `ccode` currently produces for the equivalent `Piecewise` expression:

```
In [38]: ccode(Piecewise((sin(theta)/theta, Ne(theta, 0)), (1, True)))
Out[38]: '((Ne(theta, 0)) ? (\n   sin(theta)/theta\n)\n: (\n   1\n))'
```