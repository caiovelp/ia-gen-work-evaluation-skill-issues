# Spec: Cross-version (Python 2 → Python 3) unpickling of Float-containing SymPy expressions

## Objective

**Problem.** A SymPy expression that contains a `Float`, pickled under Python 2, cannot be unpickled under Python 3. Loading fails inside `Float.__new__` (`sympy/core/numbers.py`, line 1045 at commit `3546ac7`):

```
num[1] = long(num[1], 16)
ValueError: invalid literal for int() with base 16: '1L'
```

The Python 2 pickle stores the Float's mantissa as a hexadecimal string. That string ends in a trailing `L` (here `'1L'`), and Python 3's `int(..., 16)` rejects it. The suffix most likely comes from Python 2's `hex()` on a `long`; see the Assumptions section.

**Who is affected.** Users who serialize SymPy expressions with `pickle` in Python 2 and deserialize them in Python 3, for example to migrate stored data or caches during a 2→3 transition.

**What success looks like.** Python 3 loads Python 2 pickles of Float-containing expressions and gets values equal to the originals. All existing pickling behaviour stays the same (Py3→Py3, Py2→Py2, and the current pickle output format).

**Reproduction (from the issue):**
```bash
python2 -c 'import pickle; import sympy; x = sympy.symbols("x"); print pickle.dumps(x + 1.0, 2)' \
  | python3 -c 'import pickle; import sys; print(pickle.loads(sys.stdin.buffer.read()))'
```
- Expected: prints `x + 1.0`
- Actual: the `ValueError` shown above.

**Acceptance criteria**
1. Running the reproduction command above in Python 3 prints an expression equal to `x + 1.0` and raises no error.
2. `Float` construction from the tuple form used during unpickling accepts a hex mantissa string with a trailing `L` and gives the same value as the same string without the `L`.
3. Pickles produced and loaded in the same Python version (2→2, 3→3) still round-trip unchanged for Floats, including large mantissas, negative values, zero, and special values (`inf`, `-inf`, `nan`) where those are currently supported.
4. The format of newly produced pickles does not change, unless a change is explicitly approved (see Open Questions).

## Assumptions

1. The pickled state of a `Float` includes a tuple whose second element is the mantissa, written as a hex string. On Python 2 this string comes from `hex()` on a `long`, which appends `L`. This is inferred from the traceback and the value `'1L'`; I have not verified it in the source.
2. The fix belongs on the **load** side, in the `Float.__new__` tuple/string handling, so that existing Python 2 pickles already on disk can be read. Changing only the dump side would not help pickles that already exist.
3. Only the trailing `L` suffix is incompatible. Other parts of the tuple (sign, exponent, bit count) load correctly across versions. This is unverified.
4. The supported Python versions at this commit include both Python 2.7 and Python 3.x. Compatibility helpers such as `long` are already in use; the traceback calls `long(...)` under Python 3.
5. Pickle protocol 2 is the protocol of interest. Other protocols may hit the same code path and should behave the same way.
6. Other number classes (`Integer`, `Rational`) are not affected, because their pickled state does not use `hex()` strings. This is unverified.

## Tech Stack

- Language: Python 2.7 and Python 3.x (3.6 confirmed in the issue). Exact supported versions are unknown.
- Library: SymPy at commit `3546ac7`.
- Relevant dependency: mpmath, whose mpf tuple representation `Float` wraps. The version is unknown.

## Commands

Unknown. The repository is not visible. Build, test, and lint commands must be confirmed from the project. The only command known from the issue is the reproduction command above.

## Project Structure

Known from the traceback:
- `sympy/core/numbers.py` contains `Float.__new__`, the failure site.

Unknown:
- Exact location of core-number tests. A `sympy/core/tests/` directory is likely but unconfirmed.
- Whether pickling tests live in a dedicated module, e.g. `sympy/utilities/tests/test_pickling.py`. This is unconfirmed.

## Code Style

Unknown beyond what the traceback shows. Follow existing conventions in `sympy/core/numbers.py`, including its existing Py2/Py3 compatibility helpers such as `long`. No new dependencies.

## Testing Strategy

- **Framework:** unknown. Use whatever the project's existing test runner is.
- **Unit test (Python 3 and Python 2):** build a `Float` from the tuple form that unpickling uses, with a mantissa string carrying a trailing `L` (e.g. `'1L'`). Assert it equals the corresponding Float.
- **Regression test with a fixed byte string:** embed a pickle of a Float-containing expression produced by Python 2 (e.g. of `x + 1.0`, protocol 2) as a literal in the test. Assert that `pickle.loads` gives the expected expression. This tests the cross-version path without needing two interpreters in CI.
- **Round-trip tests:** same-version pickle/unpickle for Floats with several precisions and magnitudes, and for special values, to confirm nothing regresses.
- **Manual check:** run the reproduction command from the issue with both interpreters available.

## Boundaries

- **Always:**
  - Keep loading of existing Python 3 pickles and existing Python 2 pickles working.
  - Add a regression test that reproduces the issue.
  - Run the existing test suite for core numbers and pickling before committing.
- **Ask first:**
  - Changing the format of newly produced pickles, e.g. stripping `L` on dump or changing `__getnewargs__`/`__getstate__`.
  - Broadening the change to other number classes.
  - Dropping support for any Python version.
- **Never:**
  - Change Float's numeric semantics or precision handling as a side effect.
  - Remove or weaken existing pickling tests.
  - Add new third-party dependencies.

## Success Criteria

- [ ] The issue's reproduction command prints `x + 1.0` under Python 3 with no exception.
- [ ] `Float` built from a tuple whose hex mantissa string ends in `L` equals the same Float without the suffix.
- [ ] A regression test with an embedded Python 2 pickle byte string passes under Python 3. If the test suite runs under Python 2, it passes there too.
- [ ] Existing same-version Float pickling tests pass unchanged.
- [ ] Newly produced pickles are byte-identical to before, unless an approved decision says otherwise.

## Open Questions

1. Should the fix be load-side only (accept a trailing `L`), or should the dump side also stop emitting `L` on Python 2, so that new Py2 pickles are clean? A dump-side change alters pickle output.
2. Should loading also accept a lowercase `l` suffix, or other variants? Python 2's `hex()` emits uppercase `L`.
3. Are there other places in SymPy where Python 2 `hex()`/`long` string representations end up in pickled state? The fix could be generalized, or limited to `Float`.
4. What is the exact pickled state structure of `Float` at this commit (`__getnewargs__`/`__getstate__`)? The answer confirms Assumption 1.
5. Which test file should hold cross-version pickle regression tests, and what are the project's test commands?
6. Is Python 2 → Python 3 pickle compatibility a stated support guarantee for SymPy? If it is, should other types be audited for similar issues?