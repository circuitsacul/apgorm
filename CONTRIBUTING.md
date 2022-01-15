# Contribution Guidelines
These guidelines must be followed before any pull request will be accepted. If your not sure about something, just do your best.

## General Style
 - CI must pass; `black` and `isort` issues will be automaticly fixed, but `mypy`, `flake8`, and `pytest` issues must be resolved manually.
 - Code should have static type hints (don't just use `Any` for everything). If a function or method returns `None` (either with `return None` or no return at all), that function should still be typed to return None (otherwise mypy will assume Any).
 - Avoid using `# pragma: no cover`, `# noqa`, and `# type: ignore` unless you have a very good reason for it.

## Naming
Functions, methods, classes, variables (constants and properties), and classvars that are meant for public use should have docstrings (use `google` style for functions & methods). Non-public API should start with `_` (`_some_function`).

If you edit a function/method/class that already has a docstring, make sure to update the docstring to match.
