from strava_map import graph, types

import networkx


def test_add_activity_to_graph():
    g = networkx.DiGraph()
    coords = (
        (34.0263, -118.4798040),
        (34.0265, -118.4797040),
        (34.0264, -118.4797040),
        (34.0264, -118.4797040),
    )
    activity = types.Activity(
        coordinates=coords,
        start_time="2023-07-01T01:32:21Z",
        elevation=[-1] * 4,
        name="test data",
        type="cycling",
    )
    g = graph.add_activity_to_graph(g, activity)
    assert set(g.nodes) == set(
        (
            round(c[0], graph.DEG_LAT_LONG),
            round(c[1], graph.DEG_LAT_LONG),
        )
        for c in coords
    )
    assert list(data[1] for data in g.nodes(data="weight")) == [1, 1, 0.5]


def test_find_route():
    """
    (0, 0) -- (0, 1)
    |           |
    (1, 0) -- (1, 1) -- (1, 2) -- (1, 3)
    """
    # Test that making (1,0) cheaper makes path go through it.
    g = networkx.DiGraph()
    graph.MAX_EDGE_LEN = 999
    g.add_node((0, 0), weight=1)
    g.add_node((0, 1), weight=1)
    g.add_node((1, 0), weight=0.5)
    g.add_node((1, 1), weight=1)
    g.add_node((1, 2), weight=1)
    g.add_node((1, 3), weight=1)

    g.add_edge((0, 0), (0, 1))
    g.add_edge((0, 0), (1, 0))
    g.add_edge((0, 1), (1, 1))
    g.add_edge((1, 0), (1, 1))
    g.add_edge((1, 1), (1, 2))
    g.add_edge((1, 2), (1, 3))

    _, path = graph.find_route(g, (0, 0), (1, 3))
    assert path == [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3)]

    # Test that making (0,1) cheaper makes path go through it.
    g = networkx.DiGraph()
    g.add_node((0, 0), weight=1)
    g.add_node((0, 1), weight=0.5)
    g.add_node((1, 0), weight=1)
    g.add_node((1, 1), weight=1)
    g.add_node((1, 2), weight=1)
    g.add_node((1, 3), weight=1)

    g.add_edge((0, 0), (0, 1))
    g.add_edge((0, 0), (1, 0))
    g.add_edge((0, 1), (1, 1))
    g.add_edge((1, 0), (1, 1))
    g.add_edge((1, 1), (1, 2))
    g.add_edge((1, 2), (1, 3))

    _, path = graph.find_route(g, (0, 0), (1, 3))
    assert path == [(0, 0), (0, 1), (1, 1), (1, 2), (1, 3)]

    # Test that a really short edge length tips favor back to (1,0) path
    g = networkx.DiGraph()
    g.add_node((0, 0), weight=1)
    g.add_node((0, 1), weight=0.5)
    g.add_node((1, 0), weight=1)
    g.add_node((1, 1), weight=1)
    g.add_node((1, 2), weight=1)
    g.add_node((1, 3), weight=1)

    g.add_edge((0, 0), (0, 1))
    g.add_edge((0, 0), (1, 0), weight=0.01)
    g.add_edge((0, 1), (1, 1))
    g.add_edge((1, 0), (1, 1))
    g.add_edge((1, 1), (1, 2))
    g.add_edge((1, 2), (1, 3))

    _, path = graph.find_route(g, (0, 0), (1, 3))
    assert path == [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3)]
