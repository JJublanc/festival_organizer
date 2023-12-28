import pytest

from data_gathering.scrap_etrange_festival import (
    convert_duration_to_minutes,
    extract_date_time_location,
)


@pytest.mark.parametrize(
    "duration_text, expected_minutes",
    [
        ("2h30mn", 150),
        ("1h", 60),
        ("45mn", 45),
        ("3h15m", 195),
        ("1H30MIN", 90),
        ("0h", 0),
        ("", 0),  # Edge case: empty duration text
    ],
)
def test_convert_duration_to_minutes(duration_text, expected_minutes):
    assert convert_duration_to_minutes(duration_text) == expected_minutes


@pytest.mark.parametrize(
    "text, expected_date, expected_time, expected_location",
    [
        ("Date: 12/31 Time: 08h30 Location: Salle 101", "12/31", "08h30", "Salle 101"),
        ("Date: 01/15 Time: 14h45 Location: Salle 202", "01/15", "14h45", "Salle 202"),
        ("Date: 07/20 Time: 10h00 Location: Salle 303", "07/20", "10h00", "Salle 303"),
        ("No date, time, or location information", None, None, None),
    ],
)
def test_extract_date_time_location(
    text, expected_date, expected_time, expected_location
):
    result_date, result_time, result_location = extract_date_time_location(text)
    assert result_date == expected_date
    assert result_time == expected_time
    assert result_location == expected_location
