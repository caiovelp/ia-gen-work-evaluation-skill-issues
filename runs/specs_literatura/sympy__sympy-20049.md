## Summary

`Point.vel()` should calculate a point's velocity automatically when it can be derived, the same way `ReferenceFrame.ang_vel_in()` calculates angular velocity.

## Description

In `sympy.physics.mechanics`, if you define the orientation of one reference frame relative to another, you can then ask for the angular velocity between them and it is calculated automatically. Positions and velocities do not work the same way. If you define a point's position relative to another point with `set_pos()` and then call `vel()`, you get a `ValueError` because the velocity has not been set explicitly.

**Steps to reproduce:**

```python
In [1]: import sympy as sm

In [2]: import sympy.physics.mechanics as me

In [3]: A = me.ReferenceFrame('A')

In [5]: q = me.dynamicsymbols('q')

In [6]: B = A.orientnew('B', 'Axis', (q, A.x))

In [7]: B.ang_vel_in(A)
Out[7]: q'*A.x

In [9]: P = me.Point('P')

In [10]: Q = me.Point('Q')

In [11]: r = q*A.x + 2*q*A.y

In [12]: Q.set_pos(P, r)

In [13]: Q.vel(A)
```

**Actual result:**

```
ValueError                                Traceback (most recent call last)
<ipython-input-13-0fc8041904cc> in <module>
----> 1 Q.vel(A)

~/miniconda3/lib/python3.6/site-packages/sympy/physics/vector/point.py in vel(self, frame)
    453         if not (frame in self._vel_dict):
    454             raise ValueError('Velocity of point ' + self.name + ' has not been'
--> 455                              ' defined in ReferenceFrame ' + frame.name)
    456         return self._vel_dict[frame]
    457 

ValueError: Velocity of point Q has not been defined in ReferenceFrame A
```

**Expected result:**

`Q.vel(A)` should return the same value as the time derivative of the position vector in frame `A`:

```python
In [14]: r.dt(A)
Out[14]: q'*A.x + 2*q'*A.y
```

## Product version

Not provided in the original request. The SymPy version is not stated. The traceback shows SymPy installed in a Python 3.6 Miniconda environment (`~/miniconda3/lib/python3.6/site-packages/sympy/`).

## Rationale

The current behavior is inconsistent and confusing. Angular velocity is derived automatically from orientations, but linear velocity is not derived from positions. The author believes the calculation is possible. They acknowledge there may be a reason it was not implemented, but think it should be attempted.

## Use case or scenario

A user models a system with `sympy.physics.mechanics`:

1. They define the position of point `Q` relative to point `P` with a vector that depends on a dynamic symbol `q`.
2. They want the velocity of `Q` in reference frame `A`.

They expect `Q.vel(A)` to return the derived velocity, just as `B.ang_vel_in(A)` returns the derived angular velocity. Today they must set the velocity explicitly or compute it by hand, for example with `r.dt(A)`.

## Possible solution

The request suggests that when a velocity has not been set explicitly but can be determined, `Point.vel()` should calculate it instead of raising a `ValueError`. In the example, the result would be the time derivative of the position vector in the requested frame (`r.dt(A)`), mirroring how angular velocity is calculated from orientation. No specific implementation is proposed.