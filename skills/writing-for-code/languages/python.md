# Python docstrings

Sources, checked on 2026-11-06:

- PEP 257: <https://peps.python.org/pep-0257/>
- Google Python Style Guide, section 3.8:
  <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>
- numpydoc style guide: <https://numpydoc.readthedocs.io/en/latest/format.html>

## Pick the style of the repo

Python has three common section styles: Google, NumPy, and reST
(`:param name:`). Read three docstrings in the repo and use their style. If
the repo has none, use Google style.

## PEP 257 applies to all of them

- Use `"""triple double quotes"""`. Use `r"""` if the docstring has a
  backslash.
- A one-line docstring has its closing quotes on the same line.
- A multi-line docstring has a summary line, a blank line, then the body.
  Put the closing quotes on a line of their own.
- Write the summary of a function in the imperative: "Return the path", not
  "Returns the path". (Google style also allows "Returns". Use one style in
  a file.)
- Do not repeat the signature.
- A function docstring covers the arguments, the return value, side
  effects, exceptions, and limits on when to call it.

## Google style

```python
def route(start: Stop, end: Stop) -> Route | None:
    """Return the route between two stops.

    Args:
        start: The first stop.
        end: The last stop. Must differ from `start`.

    Returns:
        The route, or None if no road connects the stops.

    Raises:
        OfflineError: The device has no network.
    """
```

- The summary is one line of 80 characters or fewer. It ends with `.`,
  `?`, or `!`.
- Sections: `Args:`, `Returns:` or `Yields:`, `Raises:`, and `Attributes:`
  for a class.
- A method with `@override` needs no docstring unless it changes the
  contract.

## NumPy style

Each section heading has a line of hyphens under it. The order is
`Parameters`, `Returns`, `Yields`, `Raises`, `Warns`, `See Also`, `Notes`,
`References`, `Examples`. Read the numpydoc guide before you use a section
that is not in this list.

## Do not

- Do not write the types in the docstring when the signature has type
  hints.
