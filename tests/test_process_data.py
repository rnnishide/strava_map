from strava_map import process_data, data_types

import networkx


def test_process_file(test_data):
    test_file = test_data / "test_data_0.gpx"
    activity = process_data.process_strava_gpx_file(test_file)

    expected_activity = data_types.Activity(
        coordinates=((0, 1), (2, 3), (4, 5)),
        start_time="2023-07-01T01:32:21Z",
        elevation=[52.7, 53.7, 54.7],
        name="test data",
        type="cycling",
    )

    assert activity == expected_activity


def test_add_activity_to_graph():
    g = networkx.Graph()
    coords = (
        (34.0263, -118.4798040),
        (34.0265, -118.4797040),
        (34.0264, -118.4797040),
        (34.0264, -118.4797040),
    )
    activity = data_types.Activity(
        coordinates=coords,
        start_time="2023-07-01T01:32:21Z",
        elevation=[-1] * 4,
        name="test data",
        type="cycling",
    )
    g = process_data.add_activity_to_graph(g, activity)
    assert set(g.nodes) == set(
        (round(c[0], process_data.DEG_LAT_LONG), round(c[1], process_data.DEG_LAT_LONG))
        for c in coords
    )
    print(list(g.nodes))
    assert list(data[1] for data in g.nodes(data="weight")) == [1, 1, 0.5]


def test_uniform_cost_search():
    """
    (0, 0) -- (0, 1)
    |           |
    (1, 0) -- (1, 1) -- (1, 2) -- (1, 3)
    """
    g = networkx.Graph()
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

    _, path = process_data.uniform_cost_search(g, (0, 0), (1, 3))
    assert path == [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3)]

    g = networkx.Graph()
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

    _, path = process_data.uniform_cost_search(g, (0, 0), (1, 3))
    assert path == [(0, 0), (0, 1), (1, 1), (1, 2), (1, 3)]


# TODO: fit file parsing test, just spot check some stuff

# TODO: test figure creation by checking figure dict stuff, without showing


# TODO: add test to make sure search is working correctly.
# Particularly that if given two equal paths, path with nodes of lower weight is chosen.
