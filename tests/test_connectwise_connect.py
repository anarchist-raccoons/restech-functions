import connectwise.connect as cw



def test_convert_duration():
    duration = 3600;
    converted_duration = {"hours":1,"minutes": 0}
    assert cw.convert_duration(duration) == converted_duration 
