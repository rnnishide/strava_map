# First things first

Make sure `build` package is installed, then build package:

```
python3 -m build
```

and install:

```
python3 -m pip install .
```

# Running tests

To run tests:

```
pytest .

```

# Reccomended Devtools

Formatting:
```
ruff format
```

Linting and fixing things in place:
```
ruff check --fix
```

Static type checking:
```
mypy src
```

and

```
mypy tests
```

### TODO: 

- automate data scraping
- setup CI to run mypy, pytest, and ruff
