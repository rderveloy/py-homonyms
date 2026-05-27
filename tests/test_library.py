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


def test_word_is_not_its_own_homophone(lib):
    # A plain curated word is not a homophone of itself; only same-spelling
    # homonyms (e.g. "bat") are.
    assert not lib.are_homophones("flower", "flower")
    assert not lib.are_homophones("to", "to")
    assert lib.are_homophones("bat", "bat")


def test_extended_curated_data(lib):
    assert lib.are_homophones("ant", "aunt")
    assert lib.are_homophones("vain", "vein")
    assert lib.are_homographs("desert", "desert")
    assert lib.classify("desert", "desert") == MatchType.HOMOGRAPH


def test_get_homophones_excludes_self(lib):
    result = lib.get_homophones("to")
    assert "two" in result and "too" in result
    assert "to" not in result


def test_curated_getter_is_clean_and_fast(lib):
    # A cached word returns exactly its curated homophones, without falling back
    # to cmudict (which would add proper-noun/surname forms like "tew").
    assert lib.get_homophones("to") == {"too", "two"}


def test_get_statistics_reports_fallback(lib):
    stats = lib.get_statistics()
    assert "phonetic_fallback_enabled" in stats
    assert stats["homophone_groups"] > 50


@pytest.mark.skipif(not phonetics.available(), reason="cmudict not installed")
class TestCmudictFallback:
    def test_homophone_not_in_cache(self, lib):
        # "moose"/"mousse" are not in the curated homophone groups.
        assert "moose" not in lib.word_to_homophones
        assert lib.are_homophones("moose", "mousse")

    def test_homograph_not_in_cache(self, lib):
        # "moped" sounds two ways (the vehicle vs. past tense of mope) but isn't curated here.
        assert "moped" not in lib.word_to_homographs
        assert lib.are_homographs("moped", "moped")

    def test_fallback_classifies_homophone(self, lib):
        assert lib.classify("moose", "mousse") == MatchType.HOMOPHONE

    def test_getter_uses_fallback(self, lib):
        # "moose" is not curated, but cmudict knows it sounds like "mousse".
        assert "moose" not in lib.word_to_homophones
        assert "mousse" in lib.get_homophones("moose")


class TestMutators:
    def test_add_homophone_group(self):
        lib = HomonymsLibrary()
        assert lib.add_homophone_group(["Foo", " bar "])
        assert lib.are_homophones("foo", "bar")
        assert lib.get_homophones("foo") == {"bar"}

    def test_add_homophone_group_singleton_is_same_spelling(self):
        lib = HomonymsLibrary()
        assert lib.add_homophone_group(["wug", "wug"])
        assert "wug" in lib.same_spelling_homophones
        assert lib.are_homophones("wug", "wug")

    def test_add_homograph_group(self):
        lib = HomonymsLibrary()
        assert lib.add_homograph_group(["Wug"])
        assert lib.are_homographs("wug", "wug")

    def test_add_group_rejects_empty_and_duplicates(self):
        lib = HomonymsLibrary()
        assert not lib.add_homophone_group([])
        assert not lib.add_homophone_group(["  "])
        assert lib.add_homophone_group(["foo", "bar"])
        before = len(lib.homophone_groups)
        assert not lib.add_homophone_group(["bar", "foo"])  # same set, no-op
        assert len(lib.homophone_groups) == before


@pytest.mark.skipif(not phonetics.available(), reason="cmudict not installed")
class TestWarm:
    def test_warm_promotes_homophones_into_cache(self):
        lib = HomonymsLibrary()
        assert "moose" not in lib.word_to_homophones
        promoted = lib.warm("moose")
        assert "mousse" in promoted["homophones"]
        # Now served from the curated path, not the fallback.
        assert "moose" in lib.word_to_homophones
        assert "mousse" in lib.get_homophones("moose")

    def test_warm_promotes_heteronym_homograph(self):
        lib = HomonymsLibrary()
        assert "moped" not in lib.word_to_homographs
        promoted = lib.warm("moped")
        assert promoted["homographs"] == {"moped"}
        assert "moped" in lib.word_to_homographs

    def test_warm_is_idempotent(self):
        lib = HomonymsLibrary()
        lib.warm("moose")
        groups_after_first = len(lib.homophone_groups)
        second = lib.warm("moose")
        assert second["homophones"] == set()
        assert len(lib.homophone_groups) == groups_after_first

    def test_warm_leaves_curated_word_untouched(self):
        lib = HomonymsLibrary()
        groups_before = len(lib.homophone_groups)
        promoted = lib.warm("to")  # already curated
        assert promoted["homophones"] == set()
        assert len(lib.homophone_groups) == groups_before
