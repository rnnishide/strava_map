from strava_map import process_activities, types


def test_process_gpx_file(test_data):
    test_file = test_data / "test_data_0.gpx"
    activity = process_activities.parse_activity_file(test_file)

    expected_activity = types.Activity(
        coordinates=((0, 1), (2, 3), (4, 5)),
        start_time="2023-07-01T01:32:21Z",
        elevation=[52.7, 53.7, 54.7],
        name="test data",
        type="cycling",
    )

    assert activity == expected_activity


def test_process_fit_file(test_data):
    test_file = test_data / "test_fit_file.fit"
    # Test is basically just checking that parser doesn't error, and spot checking last 3 data points
    # TODO: Write a smaller fit file with test data (smaller dataset, lower precision floats)
    activity = process_activities.parse_activity_file(test_file)
    assert activity.coordinates[-3:] == (
        (34.02329723350704, -118.49337819032371),
        (34.023278038948774, -118.49339839071035),
        (34.023265801370144, -118.49340819753706),
    )
    assert activity.name == "test_fit_file"


# TODO: test figure creation by checking figure dict stuff, without showing
