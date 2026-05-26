from py_homonyms import pronunciations, sound_alike


def test_classic_homophones():
    assert sound_alike("to", "too")
    assert sound_alike("two", "too")
    assert sound_alike("their", "there")
    assert sound_alike("flour", "flower")


def test_is_case_insensitive():
    assert sound_alike("To", "TWO")


def test_a_word_sounds_like_itself():
    assert sound_alike("bat", "bat")


def test_different_sounding_words():
    assert not sound_alike("cat", "dog")
    assert not sound_alike("bat", "ball")


def test_unknown_words_return_false():
    assert not sound_alike("zzqx", "zzqx")
    assert not sound_alike("cat", "zzqx")


def test_pronunciations_lookup():
    assert ("T", "UW1") in pronunciations("two")
    assert pronunciations("zzqx") == set()
