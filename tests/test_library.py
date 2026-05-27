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
    # whitespace stripped, still a homograph
    assert lib.are_homographs("lead", "lead ")
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
    # A cached word returns exactly its curated homophones, without
    # falling back to cmudict (which adds surname forms like "tew").
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
        # "moped" sounds two ways (the vehicle vs. past tense of mope)
        # but isn't curated here.
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

    def test_add_group_rejects_empty(self):
        lib = HomonymsLibrary()
        with pytest.raises(ValueError):
            lib.add_homophone_group([])
        with pytest.raises(ValueError):
            lib.add_homophone_group(["  "])

    def test_add_group_skips_duplicates(self):
        lib = HomonymsLibrary()
        assert lib.add_homophone_group(["foo", "bar"])
        before = len(lib.homophone_groups)
        assert not lib.add_homophone_group(["bar", "foo"])  # same set, no-op
        assert len(lib.homophone_groups) == before


WORD_PREDICATES = [
    "are_homographs",
    "are_homophones",
    "are_homonyms",
    "classify",
]
WORD_GETTERS = [
    "get_homographs",
    "get_homophones",
    "get_all_homonyms",
    "warm",
]
NON_STR_INPUTS = [123, 3.14, None, b"bytes", ["to"], {"to"}, ("to",), object()]
BLANK_STRINGS = ["", "   ", "\t\n  "]
# Valid str inputs that are unusual but must be handled without error.
WEIRD_VALID_WORDS = [
    "café",                       # accented
    "naïve",
    "Zürich",
    "δοκιμή",                     # non-Latin script
    "ｔｏ",                         # full-width Latin
    "to​o",                  # embedded zero-width space
    "a" * 100_000,                # oversized
    "(a+)+$",                     # regex-pathological-looking
    "a?a?a?a?aaaa",
    "'; DROP TABLE words; --",    # SQL-injection-looking
    "../../etc/passwd",           # path-traversal-looking
]


class TestHostileWordInput:
    @pytest.mark.parametrize("method", WORD_PREDICATES)
    @pytest.mark.parametrize("bad", NON_STR_INPUTS)
    def test_two_arg_rejects_non_str(self, lib, method, bad):
        func = getattr(lib, method)
        with pytest.raises(TypeError):
            func(bad, "two")
        with pytest.raises(TypeError):
            func("two", bad)

    @pytest.mark.parametrize("method", WORD_PREDICATES)
    @pytest.mark.parametrize("blank", BLANK_STRINGS)
    def test_two_arg_rejects_blank(self, lib, method, blank):
        func = getattr(lib, method)
        with pytest.raises(ValueError):
            func(blank, "two")
        with pytest.raises(ValueError):
            func("two", blank)

    @pytest.mark.parametrize("method", WORD_GETTERS)
    @pytest.mark.parametrize("bad", NON_STR_INPUTS)
    def test_one_arg_rejects_non_str(self, lib, method, bad):
        with pytest.raises(TypeError):
            getattr(lib, method)(bad)

    @pytest.mark.parametrize("method", WORD_GETTERS)
    @pytest.mark.parametrize("blank", BLANK_STRINGS)
    def test_one_arg_rejects_blank(self, lib, method, blank):
        with pytest.raises(ValueError):
            getattr(lib, method)(blank)


class TestHostileGroupInput:
    @pytest.mark.parametrize(
        "words",
        [
            "foo",          # a bare str iterates into characters
            b"foo",         # bytes iterate into ints
            123,            # not iterable
            None,           # not iterable
            ["foo", 5],     # non-str member
            ["foo", None],
            [["nested"]],   # nested-list member
            [{"key": 1}],   # dict member
        ],
    )
    def test_rejects_bad_types(self, words):
        lib = HomonymsLibrary()
        with pytest.raises(TypeError):
            lib.add_homophone_group(words)
        with pytest.raises(TypeError):
            lib.add_homograph_group(words)

    @pytest.mark.parametrize(
        "words",
        [[], (), set(), ["  ", "\t"], {"", "   "}],
    )
    def test_rejects_empty_or_blank(self, words):
        lib = HomonymsLibrary()
        with pytest.raises(ValueError):
            lib.add_homophone_group(words)
        with pytest.raises(ValueError):
            lib.add_homograph_group(words)


class TestCleanHelperParameterLabel:
    # The helpers are directly callable methods we authored, so every
    # parameter is validated, including the error-message label.
    @pytest.mark.parametrize("bad", [123, None, b"word", ["word"]])
    def test_clean_word_rejects_non_str_label(self, lib, bad):
        with pytest.raises(TypeError):
            lib._clean_word("to", bad)

    @pytest.mark.parametrize("bad", [123, None, b"words", ["words"]])
    def test_clean_group_rejects_non_str_label(self, lib, bad):
        with pytest.raises(TypeError):
            lib._clean_group(["foo", "bar"], bad)


class TestRobustValidInput:
    @pytest.mark.parametrize("word", WEIRD_VALID_WORDS)
    def test_getters_handle_weird_but_valid(self, lib, word):
        assert isinstance(lib.get_homophones(word), set)
        assert isinstance(lib.get_homographs(word), set)
        assert set(lib.get_all_homonyms(word)) == {
            "homographs",
            "homophones",
            "all",
        }

    @pytest.mark.parametrize("word", WEIRD_VALID_WORDS)
    def test_predicates_handle_weird_but_valid(self, lib, word):
        assert isinstance(lib.are_homophones(word, "to"), bool)
        assert isinstance(lib.are_homographs(word, word), bool)
        assert isinstance(lib.are_homonyms(word, "to"), bool)
        assert isinstance(lib.classify(word, "to"), MatchType)


class TestExecutionPaths:
    def test_are_homographs_different_spelling_is_false(self, lib):
        assert not lib.are_homographs("cat", "dog")

    def test_are_homonyms_unrelated_is_false(self, lib):
        assert not lib.are_homonyms("cat", "dog")

    def test_get_homographs_curated_and_unknown(self, lib):
        assert lib.get_homographs("lead") == {"lead"}
        assert lib.get_homographs("zzqxnonsense") == set()

    def test_get_homophones_unknown_is_empty(self, lib):
        assert lib.get_homophones("zzqxnonsense") == set()

    def test_get_all_homonyms_structure(self, lib):
        result = lib.get_all_homonyms("bat")
        assert result["homographs"] == {"bat"}
        assert "bat" not in result["homophones"]  # excludes self
        assert result["all"] == result["homographs"] | result["homophones"]

    def test_add_homograph_group_duplicate_is_noop(self):
        lib = HomonymsLibrary()
        assert lib.add_homograph_group(["zzz"])
        before = len(lib.homograph_groups)
        assert not lib.add_homograph_group(["ZZZ"])  # same set, no-op
        assert len(lib.homograph_groups) == before

    def test_statistics_has_all_keys(self, lib):
        assert set(lib.get_statistics()) == {
            "homograph_groups",
            "homophone_groups",
            "total_homographic_words",
            "total_homophonic_words",
            "phonetic_fallback_enabled",
        }


class TestEncapsulation:
    def test_get_homographs_returns_defensive_copy(self, lib):
        first = lib.get_homographs("lead")
        first.add("intruder")
        assert "intruder" not in lib.get_homographs("lead")

    def test_get_homophones_returns_defensive_copy(self, lib):
        first = lib.get_homophones("to")
        first.add("intruder")
        assert "intruder" not in lib.get_homophones("to")

    def test_word_index_is_read_only_mapping(self, lib):
        with pytest.raises(TypeError):
            lib.word_to_homographs["lead"] = {"x"}

    def test_word_index_value_is_a_snapshot(self, lib):
        snapshot = lib.word_to_homophones["to"]
        snapshot.add("intruder")
        assert "intruder" not in lib.word_to_homophones["to"]

    def test_groups_snapshot_is_independent(self, lib):
        groups = lib.homophone_groups
        count = len(groups)
        groups.append({"bogus"})
        groups[0].add("bogus")
        assert len(lib.homophone_groups) == count
        assert all("bogus" not in group for group in lib.homophone_groups)

    def test_same_spelling_is_frozen(self, lib):
        with pytest.raises(AttributeError):
            lib.same_spelling_homophones.add("intruder")

    def test_additions_still_work_through_mutators(self, lib):
        # Encapsulation must not block the sanctioned write path.
        local = HomonymsLibrary()
        assert local.add_homophone_group(["foo", "bar"])
        assert local.are_homophones("foo", "bar")


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
