from strava_map import process_data


def test_process_file(test_data):
    test_file = test_data / "9365674366.gpx"
    activity = process_data.process_file(test_file)
