import connectwise.connect as cw



def test_convert_duration():
    duration = 3600;
    converted_duration = {"hours":1,"minutes": 0}
    assert cw.convert_duration(duration) == converted_duration 


def test_format_duration_single_hour():
    duration = 3600;
    assert cw.format_duration(duration) == "1 hour"


def test_format_duration1():
    duration = 5400;
    assert cw.format_duration(duration) == "1 hour 30 minutes"


def test_format_duration2():
    duration = 8100;
    assert cw.format_duration(duration) == "2 hours 15 minutes"
