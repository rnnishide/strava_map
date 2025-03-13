import pathlib
from typing import List
from strava_map import data_types
import plotly.graph_objects as go
import networkx
from geopy.distance import geodesic

METADATA_TAG = "metadata"
TRACKING_DATA_TAG = "trk"
DATA_PT_TAG = "trkpt"
NAME_TAG = "name"

# 4 degrees of latitude is very roughly 0.1 miles
DEG_LAT_LONG = 5
DEG_DISTANCE = 3
MAX_ALLOWED_EDGE = 0.1


def extract_data(line: str) -> str:
    """Extract data from a line marked with tags.

    For example, given a string that follows the format:
    >>> test_data = "  <my_tag>my data!</my_tag>"
    >>> extract_data(test_data)
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


def process_file(path_to_file: pathlib.Path):
    f = open(path_to_file, "r")
    lines = iter(f.readlines())

    # Start time is always first
    start_time = ""
    while start_time == "":
        if f"<{METADATA_TAG}>" in next(lines):
            start_time = extract_data(next(lines))
            if f"</{METADATA_TAG}>" not in next(lines):
                raise TypeError(
                    "Data not in expected format, {path_to_file} is corrupted."
                )

    # Next is name, and it is always in one line and it is always followed by type.
    name = ""
    while name == "":
        line = next(lines)
        if NAME_TAG in line:
            name = extract_data(line)
            activity_type = data_types.ActivityTypes(extract_data(next(lines)))

    elevation = []
    coords = []
    while f"</{TRACKING_DATA_TAG}>" not in line:
        line = next(lines)
        if f"<{DATA_PT_TAG} " in line:
            coords_line = line.split('"')
            coords.append((float(coords_line[1]), float(coords_line[3])))
            # elevation always follows coordinates.
            elevation.append(float(extract_data(next(lines))))
    return data_types.Activity(
        start_time=start_time,
        elevation=tuple(elevation),
        type=activity_type,
        coordinates=tuple(coords),
        name=name,
    )


def plot_activities(activities: List[data_types.Activity]) -> go.Figure:
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
    fig.update_yaxes(range=[33.7, 34.2])
    fig.update_xaxes(range=[-119.25, -118.05])

    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        plot_bgcolor="black",
    )
    fig.show()


def add_activity_to_graph(
    graph: networkx.Graph,
    activity: data_types.Activity,
) -> networkx.Graph:
    for coord in activity.coordinates:
        rounded_coords = tuple(round(i, DEG_LAT_LONG) for i in coord)
        if graph.has_node(rounded_coords):
            # Invert so that nodes that show up more often have lower cost
            graph.nodes[rounded_coords]["weight"] = 1 / (
                1 + graph.nodes[rounded_coords]["weight"]
            )
        else:
            graph.add_node(rounded_coords, weight=1)
    for coord1 in graph.nodes():
        for coord2 in graph.nodes():
            if coord1 != coord2:
                dist = round(geodesic(coord1, coord2).miles, DEG_DISTANCE)
                if dist < MAX_ALLOWED_EDGE:
                    graph.add_edge(coord1, coord2, weight=dist)
    return graph


if __name__ == "__main__":
    print("Input path to data folder.")
    data_path = pathlib.Path(input()).expanduser()
    activities = []
    for f in data_path.iterdir():
        if f.suffix == ".gpx":
            try:
                activities.append(process_file(f))
            except StopIteration:
                print(
                    f"Failed to process {f}, omitting from summary. Data may be corrupted."
                )
    plot_activities(activities)


# TODO: add in filtering for location to make the plot look nice
# TODO: Use elevation to add color gradient
# TODO: add ability to filter out activities by name, type, and date
# TODO: package as cli app


# THINK ABOUT:
# Is the data type really justified?
# Ways to speed up?
# Ways to make this more impressive, add more complex features?

# Greedy alg to make route between two points on a graph
