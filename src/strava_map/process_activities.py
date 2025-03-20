"""Process raw data downloaded from strava."""

from __future__ import annotations
import pathlib
import traceback
import warnings
from typing import List, Callable, Dict, Any, Optional
from strava_map import types
import plotly.graph_objects as go
import fitparse


### NOTE: This code is probably kind of brittle.
# Generally I am assuming a lot about file structure, units, and data available.
# I could get a lot more data out of these files if I made my parsers smarter so they could handle optional data.
# Right now i'm just lazily scraping out the bare minumum, in a way that works with all my own data.


def _extract_html_style_data(line: str) -> str:
    """Extract data from a line marked with tags.

    For example, given a string that follows the format:
    >>> test_data = "  <my_tag>my data!</my_tag>"
    >>> _extract_html_style_data(test_data)
    'my data!'
    """
    iter_line = iter(line)
    current_char = ""
    data = ""
    while current_char != ">":
        current_char = next(iter_line)
    while True:
        try:
            current_char = next(iter_line)
        except StopIteration:
            raise RuntimeError(
                f"Data corrupted, failed to find end tag in line:\n    {line}"
            )
        if current_char == "<":
            break
        data += current_char
    assert next(iter_line) == "/", "Tag should end with '</'."
    return data


def _process_strava_gpx_file(path_to_file: pathlib.Path):
    METADATA_TAG = "metadata"
    TRACKING_DATA_TAG = "trk"
    DATA_PT_TAG = "trkpt"
    NAME_TAG = "name"

    f = open(path_to_file, "r")
    lines = iter(f)

    # Start time is always first
    start_time = ""
    while start_time == "":
        if f"<{METADATA_TAG}>" in next(lines):
            start_time = _extract_html_style_data(next(lines))
            if f"</{METADATA_TAG}>" not in next(lines):
                raise TypeError(
                    "Data not in expected format, {path_to_file} is corrupted."
                )

    # Next is name, and it is always in one line and it is always followed by type.
    name = ""
    while name == "":
        line = next(lines)
        if NAME_TAG in line:
            name = _extract_html_style_data(line)
            activity_type = types.ActivityTypes(_extract_html_style_data(next(lines)))
    elevation = []
    coords = []
    while f"</{TRACKING_DATA_TAG}>" not in line:
        line = next(lines)
        if f"<{DATA_PT_TAG} " in line:
            coords_line = line.split('"')
            coords.append((float(coords_line[1]), float(coords_line[3])))
            # elevation always follows coordinates.
            elevation.append(float(_extract_html_style_data(next(lines))))
        if len(coords) != len(elevation):
            raise RuntimeError(f"Error parsing {path_to_file}.")

    return types.Activity(
        start_time=start_time,
        elevation=tuple(elevation),
        type=activity_type,
        coordinates=tuple(coords),
        name=name,
    )


def _extract_field_data(field_name, record):
    return next((f.value for f in record.fields if f.name is field_name), None)


def _semicircle_to_deg(val) -> float:
    return val * (180 / 2**31)


def _process_fit_file(path_to_file: pathlib.Path):
    fitfile = fitparse.FitFile(str(path_to_file))
    coords = []
    records = fitfile.get_messages("record")
    for record in records:
        lat = _extract_field_data("position_lat", record)
        long = _extract_field_data("position_long", record)
        if lat and long:
            # TODO: I should really be checking units here, but all the data i'm messing with is in semicircle.
            coords.append((_semicircle_to_deg(lat), _semicircle_to_deg(long)))

    return types.Activity(
        start_time="",  # TODO: Extract from fit file.
        type=types.ActivityTypes.UNKNOWN,  # TODO: Extract from fit file.
        elevation=(-1,) * len(coords),  # TODO: Extract from fit file.
        coordinates=tuple(coords),
        name=path_to_file.stem,  # TODO: Extract from fit file.
    )


DISPATCH_PARSERS: Dict[str, Callable[[pathlib.Path], types.Activity]] = {
    ".gpx": _process_strava_gpx_file,
    ".fit": _process_fit_file,
}


def parse_activity_file(path_to_file: pathlib.Path) -> types.Activity:
    """Create a new `Activity` by reading data from a file.

    By default, gpx and fit files are supported.

    To add a support for a new parser at runtime:
    >>> def my_parser(path_to_file):
    ...     print("executing my parser")

    >>> DISPATCH_PARSERS[".myfileformat"] = my_parser
    >>> parse_activity_file(pathlib.Path("./some_file.myfileformat"))
    executing my parser

    """
    parser = DISPATCH_PARSERS.get(path_to_file.suffix, None)
    if parser is None:
        raise TypeError(
            f"Parsing file with extension {path_to_file.suffix} is not supported."
        )
    return parser(path_to_file)


def parse_all_files_in_dir(path_to_dir: pathlib.Path) -> List[types.Activity]:
    """Attempt to read every file in a directory into an `Activity` class.

    If processing a file fails, a warning will be presented with the error's stacktrace,
    and we will move onto the next file."""
    activities = []
    for f in path_to_dir.iterdir():
        try:
            activities.append(parse_activity_file(f))
        except Exception:
            warnings.warn(f"Failed to process file {f}.)")
            print("\n    ")
            traceback.print_exc()

    return activities


def plot_activities(
    activities: List[types.Activity], fig_style: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """Plot all activities on a graph.

    Figure can be customized by passing style specifiers in `fig_style` dictionary.
    See https://plotly.com/python/styling-plotly-express/
    """
    # TODO: Add plotting options based on other data in Activity
    # Like color gradient based on elevation.
    # TODO: Add filtering to only plot activities by type, date, etc
    fig = go.Figure()
    for activity in activities:
        x, y = [], []
        for coord in activity.coordinates:
            x.append(coord[1])
            y.append(coord[0])
        fig.add_trace(
            go.Scatter(
                x=x, y=y, marker={"color": "white"}, mode="lines", line={"width": 1}
            )
        )
    _fig_style = {
        "xaxis": dict(showgrid=False, zeroline=False),
        "yaxis": dict(showgrid=False, zeroline=False),
        "plot_bgcolor": "black",
    }
    if fig_style:
        _fig_style.update(fig_style)

    fig.update_layout(**_fig_style)
    return fig


def plot_path(fig: go.Figure, path: List[types.GPSCoordinate]) -> go.Figure:
    """Plot path as a red trace on existing figure."""
    x, y = [], []
    for coord in path:
        x.append(coord[1])
        y.append(coord[0])
    fig.add_trace(
        go.Scatter(x=x, y=y, marker={"color": "red"}, mode="lines", line={"width": 2})
    )
    return fig
