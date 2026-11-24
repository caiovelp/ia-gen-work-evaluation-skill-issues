## Summary
`SimpleLazyObject` does not implement `__radd__`

## Description
`SimpleLazyObject` is missing several magic methods that a complete proxy implementation provides. `wrapt.ObjectProxy` is an example of such a complete proxy. The missing method that causes problems for the reporter right now is `__radd__`. Because `SimpleLazyObject` does not define it, reflected addition does not work when the lazy object is the right-hand operand (`other + lazy_obj`).

The reporter notes that the simple approaches used for other proxied methods do not work here:
- `__radd__ = new_method_proxy(operator.radd)` is not possible because `operator.radd` does not exist.
- `__radd__ = new_method_proxy(operator.attrgetter("__radd__"))` also fails. The wrapped type may not have a `__radd__` attribute, and `attrgetter` does not suppress the resulting exception correctly.

## Product version
Not provided in the original request.

## Rationale
Without `__radd__`, a `SimpleLazyObject` cannot act as a transparent proxy for its wrapped object when it is the right-hand operand of `+`. The gap affects the reporter's code directly. It is also one example of the wider incompleteness of `SimpleLazyObject` compared to a full proxy implementation such as `wrapt.ObjectProxy`.

## Use case or scenario
A value wrapped in `SimpleLazyObject` is used as the right-hand operand of an addition, for example `other + lazy_obj`. The expected behaviour is that the wrapped object is evaluated and the addition works as if the wrapped value had been used directly.

## Possible solution
The reporter suggests the following minimal implementation, which works for them. It sets up the wrapped object if needed and then performs the addition with the wrapped value as the right-hand operand:

```python
def __radd__(self, other):
    if self._wrapped is empty:
        self._setup()
    return other + self._wrapped
```