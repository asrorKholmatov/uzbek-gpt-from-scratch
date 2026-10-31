from uz_text import cyr_to_lat, normalize_apostrophes, to_uzbek_latin


def test_cyr_to_lat():
    assert cyr_to_lat("Ўзбекистон") == "Oʻzbekiston"
    assert cyr_to_lat("Ер юзи") == "Yer yuzi"
    assert cyr_to_lat("тоғ") == "togʻ"
    assert cyr_to_lat("Қўшиқ") == "Qoʻshiq"
    assert cyr_to_lat("маъно") == "maʼno"
    assert cyr_to_lat("келди") == "keldi"


def test_apostrophes():
    for a in ["'", "‘", "’", "`", "ʻ"]:
        assert normalize_apostrophes(f"O{a}zbek tog{a}") == "Oʻzbek togʻ"
    assert normalize_apostrophes("ma'no") == "maʼno"


def test_russian_dropped():
    assert to_uzbek_latin("Это русский текст про город") is None
    assert to_uzbek_latin("Бу ўзбекча матн") == "Bu oʻzbekcha matn"
