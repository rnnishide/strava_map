from strava_map import process_data, data_types

import networkx


def test_process_file(test_data):
    test_file = test_data / "test_data_0.gpx"
    activity = process_data.process_file(test_file)

    expected_activity = data_types.Activity(
        coordinates=((0, 1), (2, 3), (4, 5)),
        start_time="2023-07-01T01:32:21Z",
        name="test data",
        type="cycling",
        elevation=(52.7, 53.7, 54.7),
    )

    assert activity == expected_activity


def test_add_activity_to_graph():
    g = networkx.Graph()
    coords = (
        (34.0264080, -118.4797040),
        (34.0263760, -118.4797420),
        (34.0264080, -118.4797040),
        (34.0263600, -118.4797730),
    )
    activity = data_types.Activity(
        coordinates=coords,
        start_time="2023-07-01T01:32:21Z",
        name="test data",
        type="cycling",
        elevation=(52.7, 53.7, 54.7),
    )
    g = process_data.add_activity_to_graph(g, activity)
    assert set(g.nodes) == set(
        (round(c[0], process_data.DEG_LAT_LONG), round(c[1], process_data.DEG_LAT_LONG))
        for c in coords
    )
    assert list(data[1] for data in g.nodes(data="weight")) == [0.5, 1, 1]
    assert list(e[2] for e in g.edges(data="weight")) == [0.003, 0.005, 0.002]
