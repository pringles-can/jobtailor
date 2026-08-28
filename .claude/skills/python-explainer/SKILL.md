---
name: python-explainer
description: The author is fluent in C#/.NET and new to Python. Use any time you explain Python behavior or write a non-obvious Python construct in this project — apply the C#-to-Python translation table and explain Python-specific idioms, not general programming.
---

# Python for a C#/.NET developer

The author of this project knows C#/.NET well and is new to Python. When you
explain Python or write non-obvious code here, translate to C# concepts where
the analogy is accurate, and explain *Python-specific* constructs — not general
programming.

## C# to Python translation table

| C# / .NET                         | Python                                    |
|-----------------------------------|-------------------------------------------|
| dotnet CLI                        | `uv` (project + deps + run)               |
| `.csproj`                         | `pyproject.toml`                          |
| records + annotations             | `pydantic` models                         |
| System.CommandLine                | `typer`                                   |
| `this`                            | `self` (explicit first arg on methods)    |
| `null`                            | `None`                                    |
| `throw`                           | `raise`                                   |
| interfaces / access modifiers     | none — convention: `_name` = "internal"   |
| `$"{x}"` interpolation            | f-string: `f"{x}"`                         |
| `List<string>`                    | `list[str]`                               |
| `using (var x = ...)`             | `with ... as x:` (context manager)        |
| namespaces / assemblies           | packages / modules (`__init__.py` marks a package) |
| compile step                      | none — it runs straight from source       |
| braces for blocks                 | indentation *is* the block syntax         |

## Python idioms worth flagging when they appear

- **`with` (context manager):** `with open(p) as f:` acquires and *always*
  releases a resource, like `using`. `__enter__`/`__exit__` are the hooks.
- **Decorators (`@app.command()`):** a function that wraps another to add
  behavior — like an attribute + interception, applied at definition time.
- **Dunder methods (`__init__`, `__call__`):** "double underscore" hooks Python
  calls implicitly. `__init__` is the constructor; `__call__` makes an instance
  callable like a function (that's why a `typer.Typer()` app can be a script
  entry point).
- **`__init__.py`:** presence of this file makes a folder an importable package.
- **Type hints (`x: int`):** annotations only — not enforced at runtime by the
  language (pydantic *does* enforce them for its models).
- **Mutable default arguments:** `def f(x=[])` reuses the *same* list across
  calls — a real bug. Use `Field(default_factory=list)` on models, or `None` +
  create inside the function.
- **Truthiness:** empty string/list/dict and `0` are falsy; `if not source:`
  covers both `None` and `""`.
- **Slicing:** `lines[1:]` = all but the first; `lines[:-1]` = all but the last.

## House style for this project

Prefer boring, explicit code over clever idioms — the author needs to reread it
in six months. Comment where a Python-specific construct first appears; don't
comment general programming ("loop over the items" is noise). See `CLAUDE.md`.
