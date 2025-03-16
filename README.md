# First things first

Make sure `build` package is installed, then build package:

```
python3 -m build
```

and install:

```
python3 -m pip install ./dist/strava_map*tar.gz
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
- package as CLI app
- jupyter notebook demo
- logging
- Update to python 3.12