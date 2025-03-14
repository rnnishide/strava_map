import pathlib

from typing import List
from strava_map import data_types
import plotly.graph_objects as go
import networkx
import fitparse
import heapq


# 1 degrees of latitude is roughly 69 miles
DEG_LAT_LONG = 4
MAX_EDGE_LEN = 0.1 / 69

### NOTE: The parsing part of this code leaves much to be desired...
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


def process_strava_gpx_file(path_to_file: pathlib.Path):
    METADATA_TAG = "metadata"
    TRACKING_DATA_TAG = "trk"
    DATA_PT_TAG = "trkpt"
    NAME_TAG = "name"

    f = open(path_to_file, "r")
    lines = iter(f.readlines())

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
            activity_type = data_types.ActivityTypes(
                _extract_html_style_data(next(lines))
            )
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

    return data_types.Activity(
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


def process_fit_file(path_to_file: pathlib.Path):
    fitfile = fitparse.FitFile(str(path_to_file))
    coords = []
    records = fitfile.get_messages("record")
    for record in records:
        lat = _extract_field_data("position_lat", record)
        long = _extract_field_data("position_long", record)
        if lat and long:
            # TODO: I should really be checking units here, but all the data i'm messing with is in semicircle.
            coords.append((_semicircle_to_deg(lat), _semicircle_to_deg(long)))

    return data_types.Activity(
        start_time="",  # TODO: Extract from fit file.
        type=data_types.ActivityTypes.UNKNOWN,  # TODO: Extract from fit file.
        elevation=(-1,) * len(coords),  # TODO: Extract from fit file.
        coordinates=tuple(coords),
        name=path_to_file.root,  # TODO: Extract from fit file.
    )


# This code is totally ripped off from https://www.geeksforgeeks.org/uniform-cost-search-ucs-in-ai/
# I copy pasted the example there and edited it to do what I want.
def reconstruct_path(visited, goal):
    # Reconstruct the path from start to goal by following the visited nodes
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = visited[current][1]  # Get the parent node
    path.reverse()
    return path


def uniform_cost_search(graph, start, goal):
    # Priority queue to store the frontier nodes, initialized with the start node
    start = tuple(round(val, DEG_LAT_LONG) for val in start)
    goal = tuple(round(val, DEG_LAT_LONG) for val in goal)
    priority_queue = [(0, start)]
    weights = {data[0]: data[1] for data in graph.nodes(data="weight")}
    # Dictionary to store the cost of the shortest path to each node
    visited = {start: (0, None)}
    if start not in graph.nodes():
        raise ValueError(f"Start node {start} not in graph.")
    if goal not in graph.nodes():
        raise ValueError(f"Goal node {goal} not in graph.")
    while priority_queue:
        # Pop the node with the lowest cost from the priority queue
        current_cost, current_node = heapq.heappop(priority_queue)

        # If we reached the goal, return the total cost and the path
        if current_node == goal:
            return current_cost, reconstruct_path(visited, goal)

        # Explore the neighbors
        for coord in graph.neighbors(current_node):
            total_cost = current_cost + weights[coord]
            # Check if this path to the neighbor is better than any previously found
            # NOTE: I'm not using the weight of the edges anywhere cause I prefer routes i know.
            if coord not in visited or total_cost < visited[coord][0]:
                visited[coord] = (total_cost, current_node)
                heapq.heappush(priority_queue, (total_cost, coord))

    # If the goal is not reachable, return None
    return None, []


# TODO: Make a node that has all the data in it
def add_activity_to_graph(
    graph: networkx.Graph,
    activity: data_types.Activity,
) -> networkx.Graph:
    previous_node = None
    for coord in activity.coordinates:
        # Build up edges in a smarter way by inserting existing nodes into edges for existing nodes
        rounded_coords = tuple(round(i, DEG_LAT_LONG) for i in coord)
        if graph.has_node(rounded_coords):
            print(rounded_coords, graph.nodes[rounded_coords]["weight"])
            # Invert instance count so that nodes that show up more often have lower cost
            graph.nodes[rounded_coords]["weight"] = 1 / (
                1 + graph.nodes[rounded_coords]["weight"]
            )
        else:
            # TODO: Add custom data type for node so i can keep metadata attached to points.
            # This would open the door to more complicated analysis.
            graph.add_node(rounded_coords, weight=1)
        if previous_node:
            dist = (
                (rounded_coords[0] - previous_node[0]) ** 2
                + (rounded_coords[1] - previous_node[1]) ** 2
            ) ** 0.5
            # We don't want edges that represent huge distance gaps.
            # These gaps are due to pausing gps tracking (at least in my data...)
            if dist < MAX_EDGE_LEN:
                graph.add_edge(previous_node, rounded_coords, weight=dist)
        previous_node = rounded_coords
    return graph


def plot_activities(activities: List[data_types.Activity]) -> go.Figure:
    # TODO: Add plotting options based on other data in Activity
    # Like color gradient based on elevation.
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
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        plot_bgcolor="black",
    )
    return fig


# TODO: Move demo from script to jupyter notebook, add to repo
if __name__ == "__main__":
    print("Input path to data folder.")
    # data_path = pathlib.Path(input()).expanduser()
    data_path = pathlib.Path("~/Downloads/export_120164743/activities").expanduser()
    activities = []
    for f in data_path.iterdir():
        if f.suffix == ".gpx":
            try:
                activities.append(process_strava_gpx_file(f))
            except StopIteration:
                print(
                    f"Failed to process {f}, omitting from summary. Data may be corrupted."
                )
        elif f.suffix == ".fit":
            activities.append(process_fit_file(f))
    fig = plot_activities(activities)
    g: networkx.Graph = networkx.Graph()
    for activity in activities:
        add_activity_to_graph(g, activity)

    cost, path = uniform_cost_search(g, (34.0234, -118.4603), (34.1262, -118.5095))
    if cost and path:
        x, y = [], []
        for coord in path:
            x.append(coord[1])
            y.append(coord[0])
        fig.add_trace(
            go.Scatter(
                x=x, y=y, marker={"color": "red"}, mode="lines", line={"width": 2}
            )
        )
    fig.update_yaxes(range=[33.57, 34.92])
    fig.update_xaxes(range=[-120.4, -117.7])

    fig.show()


# TODO: Update to python 3.12, i really want to use match statements...
# TODO: add ability to filter out activities by name, type, and date.
# TODO
# TODO: package as cli app
# TODO: logging
