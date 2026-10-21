from app.ingest.cities import city_name


def test_code_maps_to_name():
    assert city_name("3000") == "ירושלים"
    assert city_name("874") == "מגדל העמק"


def test_text_city_is_trimmed():
    assert city_name("  רמת גן ") == "רמת גן"


def test_zero_means_unknown():
    assert city_name("0") == ""


def test_unknown_code_is_kept():
    assert city_name("99999") == "99999"
