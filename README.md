# What does this package do

This codebase parses gpx and fit files downloaded from strava. The data will be used to populate a dataclass called `process_activities.Activity`. That dataclass can then be used to plot coordinates, or added to a `networkx.DiGraph` using `process_activites.add_activity_to_graph`. Once you have a graph, you can use to to calculate the best route between two points, based on frequency of records at each coordinate and distance. 

Here is an example of a plot with a route generated in red:

![example](./example_plot.png)

Currently, this package does not support interfacing with Strava or other fitness tracker's API. It is a TODO - for now I reccomend using [strava docs on bulk exporting.](https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export)


See the [guide](/docs/guide.md)] for more details on how to use the package.
# Installing and Developing
## Build

Make sure `build` package is installed, then build package:

```
python3 -m build
```

and install:

```
python3 -m pip install ./dist/strava_map*tar.gz
```

## Running tests

To run tests:

```
pytest .

```

## Reccomended Devtools

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

# TODO: 

- Hook into strava, garmin, wahoo, etc API's to automate data downloads.
- Setup CI to run mypy, pytest, and ruff.
- Package as CLI app
- jupyter notebook demo
- Add logging.
- Update to python 3.12.
- Build docs with sphinx.
- Include options to package more data (power, heart rate) and use to filter plots and support more interesting fitness related analysis.
- Web front end to make plotting interactive.