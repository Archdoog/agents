# Python Documentation

Fetch the official [PEP 257: Docstring Conventions](https://peps.python.org/pep-0257/) once per session before documenting a public API.
PEP 257 is the stable numbered reference. It defines structure, not one required section-markup style.
Check the repository's Python version and documentation generator.

Use a string literal as the first statement of the documented object, normally with triple double quotes.
Start with a concise imperative summary, such as "Return the elapsed time in seconds."
Separate a longer description from the summary with a blank line.
Use the repository's Google, NumPy, reStructuredText, or other established section format.
Do not mix section formats or repeat the function signature.

Document argument meaning, return values, relevant exceptions, side effects, and call restrictions.
Include `None` behavior, units, accepted ranges, ownership, and concurrency limits where callers need them.
For generators, describe yielded values and resource lifetime. For async APIs, describe cancellation when it affects the contract.

Document modules with module docstrings and packages through their existing package documentation, commonly `__init__.py`.
Explain the public entry points and relationships needed to use the package without inspecting its implementation.
Keep examples valid with their imports and setup. Report whether doctests or documentation builds actually ran.
