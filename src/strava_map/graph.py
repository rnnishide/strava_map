from __future__ import annotations

from typing import List, Optional, Tuple, Dict
from strava_map import types
import networkx
import heapq

# 1 degrees of latitude is roughly 69 miles
DEG_LAT_LONG = 4
MAX_EDGE_LEN = 0.1 / 69


def _round_coordinates(coord) -> types.GPSCoordinate:
    return (round(coord[0], DEG_LAT_LONG), round(coord[1], DEG_LAT_LONG))


# This code is totally ripped off from https://www.geeksforgeeks.org/uniform-cost-search-ucs-in-ai/
# I copy pasted the example there and edited it to do what I want.
def _reconstruct_path(visited, goal) -> List[types.GPSCoordinate]:
    # Reconstruct the path from start to goal by following the visited nodes
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = visited[current][1]  # Get the parent node
    path.reverse()
    return path


def uniform_cost_search(
    graph: networkx.DiGraph, start: types.GPSCoordinate, goal: types.GPSCoordinate
) -> Tuple[float, List[types.GPSCoordinate]]:
    """Find best path from start node to goal node in graph, based on the lowest cost.

    Raises:
        ValueError: if start or goal node is not in graph

    Returns:
        cost of path, -1 if no path found: [float]
        path: List[types.GPSCoordinate]

    """
    # We want to round the start/goal node coordinates to make sure the have the same precision as the graph.
    # This is mostly for convenience for the user passing coordinates.
    start = _round_coordinates(start)
    goal = _round_coordinates(goal)
    priority_queue = [(0, start)]
    # Dictionary to store the cost of the shortest path to each node
    visited: Dict[types.GPSCoordinate, Tuple[float, Optional[types.GPSCoordinate]]] = {
        start: (0, None)
    }

    # TODO: find nodes closest to start and end node so I don't have to raise here.
    # Sounds like it would probably be slow... not sure the best way to do that.
    if start not in graph.nodes():
        raise ValueError(f"Start node {start} not in graph.")
    if goal not in graph.nodes():
        raise ValueError(f"Goal node {goal} not in graph.")
    while priority_queue:
        # Pop the node with the lowest cost from the priority queue
        current_cost, current_node = heapq.heappop(priority_queue)

        # If we reached the goal, return the total cost and the path
        if current_node == goal:
            return current_cost, _reconstruct_path(visited, goal)

        # Explore the neighbors
        for coord in graph.neighbors(current_node):
            # Coordinate that is closest and most frequently visited will have the cheapest cost.
            total_cost = current_cost + (
                graph.nodes[coord]["weight"]
                * graph.edges[(current_node, coord)].get("weight", 1)
            )
            # Check if this path to the neighbor is better than any previously found.
            if coord not in visited or total_cost < visited[coord][0]:
                visited[coord] = (total_cost, current_node)
                heapq.heappush(priority_queue, (total_cost, coord))

    # If the goal is not reachable, return -1 as cost and no path.
    return -1, []


def _calculate_distance(coord1, coord2) -> float:
    return abs((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2) ** 0.5


def add_activity_to_graph(
    graph: networkx.DiGraph,
    activity: types.Activity,
) -> networkx.DiGraph:
    """Add coordinates from given Activity to a directional graph.

    Coordinates will be rounded to `strava_map.graph.DEG_LAT_LONG` significant figures before being turned into nodes.
    Nodes are weighted by `1/n_times_gps_records_at_node`.
    Edges are directional such that they point from a node recorded at an earlier time to a later one.
    Edges are weighted by distance.
    """
    previous_node = None
    for coord in activity.coordinates:
        # Build up edges in a smarter way by inserting existing nodes into edges for existing nodes
        rounded_coords = _round_coordinates(coord)
        if graph.has_node(rounded_coords):
            node = graph.nodes[rounded_coords]
            # Invert instance count so that nodes that show up more often have lower cost
            node["weight"] = 1 / (1 + node["weight"])
        else:
            # TODO: Add custom data type for node so I can keep metadata attached to points.
            # This would open the door to more complicated analysis.
            graph.add_node(rounded_coords, weight=1)
        if previous_node:
            dist = _calculate_distance(rounded_coords, previous_node)
            # We don't want edges that represent huge distance gaps.
            # These gaps are due to pausing gps tracking (at least in my data...)
            if dist < MAX_EDGE_LEN:
                graph.add_edge(previous_node, rounded_coords, weight=dist)
        previous_node = rounded_coords
    return graph
