# Spec: Automatic velocity calculation in `Point.vel()`

## Objective

`Point.vel(frame)` should calculate a point's velocity in a reference frame when it has not been set explicitly but can be derived from known position relationships. This would match `ReferenceFrame.ang_vel_in()`, which already derives angular velocity from orientation relationships.

**Current behavior (from the issue):**

```python
A = me.ReferenceFrame('A')
q = me.dynamicsymbols('q')
P = me.Point('P')
Q = me.Point('Q')
r = q*A.x + 2*q*A.y
Q.set_pos(P, r)
Q.vel(A)
# ValueError: Velocity of point Q has not been defined in ReferenceFrame A
```

The error is raised in `vel()` in `sympy/physics/vector/point.py`, which only reads `self._vel_dict[frame]`.

**Expected behavior:**

```python
Q.vel(A)  # -> q'*A.x + 2*q'*A.y   (equal to r.dt(A))
```

**Users:** people using `sympy.physics.mechanics` / `sympy.physics.vector` to build kinematic models. They expect velocities to follow from positions the same way angular velocities follow from orientations.

**Success looks like:** when a point's velocity in a frame is not stored, `vel()` derives it from the position tree. It is computed as `O.vel(frame) + Q.pos_from(O).dt(frame)`, where `O` is a point whose velocity in `frame` is known or can be assumed. When no such derivation is possible, `vel()` still raises a clear `ValueError`.

## Assumptions

1. The fix is confined to `Point.vel()` in `sympy/physics/vector/point.py`. `sympy.physics.mechanics.Point` is the same class re-exported, based on the traceback path.
2. The derivation uses the standard kinematic relation `v_Q/A = v_O/A + d/dt(r_OQ) in A`, with the time derivative taken in `frame` via `Vector.dt(frame)`.
3. Position relationships are stored per point, in a structure that can be traversed from `Q` to other points (e.g. `_pos_dict`). The exact internal structure has not been inspected.
4. Explicitly set velocities always take precedence over computed ones. `vel()` returns the stored value unchanged when `frame` is already in `_vel_dict`.
5. The issue's expected output `q'*A.x + 2*q'*A.y` implies that `P` is treated as having zero velocity in `A`, even though this was never set. Whether that implicit assumption is acceptable is unresolved (see Open Questions).
6. The existing `ValueError` message and type are kept for the case where the velocity cannot be determined.
7. The public signature of `vel(frame)` does not change.
8. The computed velocity may or may not be cached in `_vel_dict`; this is unresolved (see Open Questions).

## Tech Stack

- Python, SymPy (`sympy.physics.vector`, `sympy.physics.mechanics`)
- Python and SymPy versions supported by the target branch: **unknown**. The issue's traceback shows Python 3.6.

## Commands

- Build: **unknown** (pure-Python package; no build step stated in the issue)
- Test: **unknown**. Presumably the SymPy test runner targeting the `sympy/physics/vector` tests, but the exact command has not been verified.
- Lint: **unknown**
- Dev: **unknown**

## Project Structure

- `sympy/physics/vector/point.py`: `Point` class, including `vel()`, `set_pos()`, `pos_from()` and `set_vel()`. This path is confirmed by the traceback.
- Test location for `Point`: **unknown**. It is likely a `tests/` directory under `sympy/physics/vector/`, but this is not verified.
- Docs or docstring location for `Point.vel`: **unknown**. At minimum, the method's docstring should describe the new behavior.

## Code Style

- Follow existing SymPy conventions in `point.py`. These have not been inspected, so no snippet is provided.
- Include a docstring example for `vel()` that demonstrates automatic calculation, in doctest format like the issue's example.

## Testing Strategy

- **Framework:** SymPy's existing test framework. Exact runner and invocation are **unknown**.
- **Unit tests** for `Point.vel()` should cover:
  - The issue's exact example, with `P`'s velocity behavior decided by the Open Questions.
  - `P.set_vel(A, 0)` followed by `Q.set_pos(P, r)`, so that `Q.vel(A) == r.dt(A)`.
  - A non-zero base velocity: `P.set_vel(A, v)`, so that `Q.vel(A) == v + r.dt(A)`.
  - A multi-hop chain such as `P → Q → R`, where only `P`'s velocity is known.
  - A position vector expressed in a rotating frame `B`, checking that the derivative in `A` includes the ω×r terms.
  - An explicitly set velocity being returned unchanged, even if it disagrees with the position-derived value.
  - A point with no position relationships and no velocity, which must still raise `ValueError`.
  - A position tree containing no point with known velocity in `frame`, with the behavior decided by the Open Questions.
- **Regression:** the existing `sympy.physics.vector` and `sympy.physics.mechanics` test suites must pass, including tests that rely on `ValueError` being raised.
- **Doctests:** the updated `vel()` docstring example must pass.

## Boundaries

- **Always:**
  - Keep an explicitly set velocity authoritative.
  - Raise `ValueError` when the velocity cannot be derived.
  - Add tests for each success criterion.
  - Update the `vel()` docstring.
- **Ask first:**
  - Implicitly treating a point with no velocity as stationary in `frame`.
  - Caching computed velocities in `_vel_dict`.
  - Emitting warnings.
  - Changing `ReferenceFrame` behavior.
  - Changing other `Point` methods (`a2pt_theory`, `v2pt_theory`, `acc`, etc.).
  - Making the same change for accelerations (`Point.acc`).
- **Never:**
  - Change the signature of `vel()`.
  - Silently return a wrong velocity when the position tree is ambiguous or inconsistent.
  - Remove or weaken existing tests.

## Success Criteria

1. If `frame` is in the point's stored velocities, `vel(frame)` returns that stored value. Existing behavior is unchanged.
2. If `Q.set_pos(P, r)` was called and `P.vel(A)` is defined, `Q.vel(A)` returns `P.vel(A) + r.dt(A)` without error.
3. The issue's example produces `q'*A.x + 2*q'*A.y`, subject to resolution of Open Question 1.
4. Velocity is derived through chains of `set_pos` relationships of any length, not just direct neighbours.
5. The derived velocity is correct when the position vector is expressed in a frame that rotates relative to `frame`.
6. When no point with known velocity in `frame` is reachable, `vel()` raises `ValueError` with a message naming the point and the frame.
7. The derivation terminates on position graphs with cycles, if cycles are possible.
8. All existing `sympy.physics.vector` and `sympy.physics.mechanics` tests pass.

## Open Questions

1. **Implicit zero velocity.** In the issue's example, `P` has no velocity defined in `A`, yet the expected result assumes `P` is fixed in `A`. Which behavior is wanted?
   - (a) Require some point in the tree to have an explicitly defined velocity in `frame`, and raise otherwise. The issue's example would then still fail unless `P.set_vel(A, 0)` is added.
   - (b) Treat a root point with no defined velocities as stationary in `frame`.
   - (c) Treat it as stationary in `frame` and emit a warning.
2. **Multiple candidate base points.** If several reachable points have known velocities in `frame`, which one should be used: the nearest, or the first found? Should inconsistent results be detected or warned about?
3. **Caching.** Should the computed velocity be stored in `_vel_dict`? Caching can go stale if positions or velocities change later.
4. **Scope.** Should `Point.acc()` get analogous automatic calculation in the same change, for consistency?
5. **Intentional omission.** Is there a known reason this was not implemented, such as the ambiguity of an "absolute" reference, or interactions with `v2pt_theory` / `v1pt_theory`? Maintainers may want to confirm.
6. **Docs.** Do docs outside the docstring (e.g. the physics/vector kinematics docs) need updating, and where do they live?
7. **Repository details.** The exact test command, test file location, and supported Python versions are unknown.