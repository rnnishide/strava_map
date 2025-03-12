import pathlib

from strava_map import data_types

METADATA_TAG = "metadata"
TIME_TAG = "time"
TRACKING_DATA_TAG = "trk"
DATA_PT_TAG = "trkpt"
TYPE_TAG = "type"
ELEVATION_TAG = "ele"
NAME_TAG = "name"


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
            elevation.append(extract_data(next(lines)))
    return data_types.Activity(
        start_time=start_time,
        elevation=tuple(elevation),
        type=activity_type,
        coordinates=tuple(coords),
        name=name,
    )
