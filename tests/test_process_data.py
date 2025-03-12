import pytest
import pathlib
from strava_map import process_data


def test_process_file():
    test_file = pathlib.Path.cwd() / "tests" / "data" / "9365674366.gpx"
    activity = process_data.process_file(test_file)
