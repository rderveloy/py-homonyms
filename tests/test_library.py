import pytest

from py_homonyms import HomonymsLibrary, MatchType
from py_homonyms import phonetics


@pytest.fixture(scope="module")
def lib():
    return HomonymsLibrary()


def test_curated_homophones(lib):
    assert lib.are_homophones("to", "two")
    assert lib.are_homophones("there", "their")
    assert not lib.are_homophones("cat", "dog")


def test_curated_homographs(lib):
    assert lib.are_homographs("lead", "lead")
    assert lib.are_homographs("lead", "lead ")  # whitespace stripped, still a homograph
    assert not lib.are_homographs("cat", "cat")  # same word, not a homograph


def test_homonyms_compose(lib):
    assert lib.are_homonyms("bat", "bat")  # both homograph and homophone
    assert lib.are_homonyms("to", "two")  # homophone only


def test_case_and_whitespace_insensitive(lib):
    assert lib.are_homophones("  To ", "TWO")


def test_classify(lib):
    assert lib.classify("to", "two") == MatchType.HOMOPHONE
    assert lib.classify("bat", "bat") == MatchType.HOMONYM
    assert lib.classify("lead", "lead") == MatchType.HOMOGRAPH
    assert lib.classify("cat", "dog") == MatchType.DIFFERENT
    assert lib.classify("zzqx", "qxzz") == MatchType.UNKNOWN


@pytest.mark.skipif(not phonetics.available(), reason="cmudict not installed")
class TestCmudictFallback:
    def test_homophone_not_in_cache(self, lib):
        # "knew"/"new" are not in the curated homophone groups.
        assert "knew" not in lib.word_to_homophones
        assert lib.are_homophones("knew", "new")

    def test_homograph_not_in_cache(self, lib):
        # "bass" sounds two ways (fish vs. the instrument) but isn't curated here.
        assert "bass" not in lib.word_to_homographs
        assert lib.are_homographs("bass", "bass")

    def test_fallback_classifies_homophone(self, lib):
        assert lib.classify("knew", "new") == MatchType.HOMOPHONE
