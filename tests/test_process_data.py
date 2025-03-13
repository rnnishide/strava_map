from strava_map import process_data, data_types


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
