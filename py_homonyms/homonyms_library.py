"""
English Homonyms Library
A comprehensive library for checking homonyms, homophones, and
homographs in English.
"""

from __future__ import annotations

import enum
from collections import defaultdict
from collections.abc import Iterable, Mapping
from types import MappingProxyType

from . import phonetics


class MatchType(enum.Enum):
    """How two words relate.

    ``HOMONYM``   - both a homograph and a homophone (e.g. ``bat`` the
                    animal vs. the bat you swing).
    ``HOMOPHONE`` - sound alike but not the same spelling
                    (e.g. ``to`` / ``two``).
    ``HOMOGRAPH`` - same spelling, different meaning/pronunciation
                    (e.g. ``lead``).
    ``DIFFERENT`` - unrelated by spelling and sound.
    ``UNKNOWN``   - no curated or phonetic data was available to judge
                    the pair.
    """

    HOMONYM = "homonym"
    HOMOPHONE = "homophone"
    HOMOGRAPH = "homograph"
    DIFFERENT = "different"
    UNKNOWN = "unknown"


class HomonymsLibrary:
    """
    A local library for working with English homonyms, including:
    - Homophones: words that sound the same, but are different in meaning
      (baseball bat vs animal bat) or spelling (sea vs see).
    - Homographs: words that are spelled the same, but different in
      meaning and/or pronunciation (lead weight vs lead the team).
    - Homonyms: words that are homographs, homophones, or both.
    See:
    https://www.merriam-webster.com/grammar/homophones-vs-homographs-vs-homonyms
    """

    def __init__(self) -> None:
        # The backing store is private and mutable: only our own methods (the
        # mutators and warm) write to it. External callers reach it through the
        # read-only properties below, which hand out independent snapshots so a
        # caller's mistake cannot corrupt the library's state.
        self._homograph_groups: list[set[str]] = self._load_homographs()
        self._homophone_groups: list[set[str]] = self._load_homophones()
        self._word_to_homographs: dict[str, set[str]] = (
            self._build_reverse_index(
                self._homograph_groups, keep_identical=True
            )
        )
        self._word_to_homophones: dict[str, set[str]] = (
            self._build_reverse_index(
                self._homophone_groups, keep_identical=True
            )
        )
        # Words that are homophones of themselves: same spelling, same sound,
        # different meaning (e.g. "bat"). These appear as single-member groups.
        self._same_spelling_homophones: set[str] = {
            word.lower()
            for group in self._homophone_groups
            if len({member.lower() for member in group}) == 1
            for word in group
        }

    @property
    def homograph_groups(self) -> list[set[str]]:
        """Read-only snapshot of the homograph groups."""
        return [set(group) for group in self._homograph_groups]

    @property
    def homophone_groups(self) -> list[set[str]]:
        """Read-only snapshot of the homophone groups."""
        return [set(group) for group in self._homophone_groups]

    @property
    def word_to_homographs(self) -> Mapping[str, set[str]]:
        """Read-only snapshot mapping each word to its homograph group."""
        return MappingProxyType(
            {
                word: set(group)
                for word, group in self._word_to_homographs.items()
            }
        )

    @property
    def word_to_homophones(self) -> Mapping[str, set[str]]:
        """Read-only snapshot mapping each word to its homophone group."""
        return MappingProxyType(
            {
                word: set(group)
                for word, group in self._word_to_homophones.items()
            }
        )

    @property
    def same_spelling_homophones(self) -> frozenset[str]:
        """Read-only snapshot of the same-spelling homonyms."""
        return frozenset(self._same_spelling_homophones)

    def _load_homographs(self) -> list[set[str]]:
        """Load homograph groups (words with the same spelling but
        different meanings). They can have the same or different
        pronunciations.

        See:
        https://www.merriam-webster.com/grammar/homophones-vs-homographs-vs-homonyms
        """

        homographs: list[set[str]] = [
            {"bank", "bank"},  # financial institution vs river bank
            {"bark", "bark"},  # dog sound vs tree covering
            {"bat", "bat"},  # animal vs sports equipment
            {"bear", "bear"},  # animal vs to carry
            {"bow", "bow"},  # weapon vs to bend
            {"close", "close"},  # near vs to shut
            {"dove", "dove"},  # bird vs past tense of dive
            {"fair", "fair"},  # just vs carnival
            {"lead", "lead"},  # metal vs to guide
            {"live", "live"},  # to exist vs in real time
            {"minute", "minute"},  # time unit vs very small
            {"object", "object"},  # thing vs to protest
            {"perfect", "perfect"},  # flawless vs to make perfect
            {"present", "present", "present"},  # gift vs now vs to show
            {"produce", "produce"},  # to create vs fruits/vegetables
            {"project", "project"},  # plan vs to extend outward
            {"quail", "quail"},  # cower vs bird
            {"read", "read"},  # present vs past tense
            {"record", "record"},  # to capture vs a disc/document
            {"refuse", "refuse"},  # to decline vs garbage
            {"subject", "subject"},  # topic vs to cause to experience
            {"tear", "tear"},  # to rip vs from crying
            {"wind", "wind"},  # air movement vs to turn
            {"wound", "wound"},  # injury vs past tense of wind
            {"address", "address"},  # location vs to speak to
            {"console", "console"},  # to comfort vs a control panel
            {"content", "content"},  # satisfied vs subject matter
            {"contract", "contract"},  # agreement vs to shrink
            {"convict", "convict"},  # to find guilty vs a prisoner
            {"desert", "desert"},  # arid land vs to abandon
            {"does", "does"},  # verb vs plural of doe
            {"entrance", "entrance"},  # doorway vs to delight
            {"insult", "insult"},  # to offend vs an offense
            {"invalid", "invalid"},  # not valid vs a sick person
            {"permit", "permit"},  # to allow vs a license
            {"polish", "polish"},  # to shine vs from Poland
            {"rebel", "rebel"},  # to resist vs a resister
            {"row", "row"},  # to paddle vs an argument
            {"sow", "sow"},  # to plant vs a female pig
            {"bass", "bass"},  # fish vs the instrument
            {"abuse", "abuse"},  # noun vs verb
            {"attribute", "attribute"},  # a quality vs to ascribe
            {"buffet", "buffet"},  # a meal vs to strike
            {"compound", "compound"},  # an enclosure vs to combine
            {"conduct", "conduct"},  # behavior vs to lead
            {"conflict", "conflict"},  # a dispute vs to clash
            {"contest", "contest"},  # a competition vs to dispute
            {"contrast", "contrast"},  # a difference vs to differ
            {"converse", "converse"},  # the opposite vs to talk
            {"convert", "convert"},  # a believer vs to change
            {"digest", "digest"},  # a summary vs to break down
            {"escort", "escort"},  # a companion vs to accompany
            {"excuse", "excuse"},  # a reason vs to forgive
            {"export", "export"},  # a good shipped vs to ship out
            {"extract", "extract"},  # an excerpt vs to remove
            {"import", "import"},  # a good brought in vs to bring in
            {"incline", "incline"},  # a slope vs to lean
            {"increase", "increase"},  # a rise vs to grow
            {"insert", "insert"},  # an addition vs to put in
            {"intern", "intern"},  # a trainee vs to confine
            {"misuse", "misuse"},  # wrong use vs to use wrongly
            {"number", "number"},  # a numeral vs more numb
            {"progress", "progress"},  # advancement vs to advance
            {"protest", "protest"},  # a demonstration vs to object
            {"recall", "recall"},  # memory vs to remember
            {"refund", "refund"},  # money returned vs to return money
            {"reject", "reject"},  # a discard vs to refuse
            {"sewer", "sewer"},  # a drain vs one who sews
            {"survey", "survey"},  # a poll vs to examine
            {"suspect", "suspect"},  # a person vs to doubt
            {"transfer", "transfer"},  # a move vs to move
            {"transport", "transport"},  # conveyance vs to carry
            {"upset", "upset"},  # a disturbance vs to overturn
            {"use", "use"},  # a purpose vs to employ
            {"moderate", "moderate"},  # not extreme vs to chair
            {"separate", "separate"},  # apart vs to divide
            {"estimate", "estimate"},  # a guess vs to approximate
            {"graduate", "graduate"},  # an alum vs to complete a degree
            {"associate", "associate"},  # a colleague vs to connect
            {"alternate", "alternate"},  # every other vs to take turns
            {"duplicate", "duplicate"},  # a copy vs to copy
            {"delegate", "delegate"},  # a representative vs to assign
            {"deliberate", "deliberate"},  # intentional vs to ponder
            {"intimate", "intimate"},  # close vs to hint
        ]
        return homographs

    def _load_homophones(self) -> list[set[str]]:
        """Load homophone groups (words that sound alike but have
        different meanings). Spelling can be the same or different.

        See:
        https://www.merriam-webster.com/grammar/homophones-vs-homographs-vs-homonyms
        """

        # Common English homophones
        homophones: list[set[str]] = [
            {"bank", "bank"},  # financial institution vs river bank
            {"bark", "bark"},  # dog sound vs tree covering
            {"bat", "bat"},  # animal vs sports equipment
            {"bear", "bear"},  # animal vs to carry
            {"fair", "fair"},  # just vs carnival
            {"present", "present"},  # a gift vs in the current time
            {"subject", "subject"},  # topic vs to cause to experience
            {"tear", "tear"},  # to rip vs from crying
            {"to", "too", "two"},
            {"there", "their", "they're"},
            {"hear", "here"},
            {"see", "sea", "c"},
            {"right", "write", "rite"},
            {"know", "no"},
            {"one", "won"},
            {"four", "for", "fore"},
            {"eight", "ate"},
            {"buy", "by", "bye"},
            {"cell", "sell"},
            {"dear", "deer"},
            {"flour", "flower"},
            {"hole", "whole"},
            {"knight", "night"},
            {"mail", "male"},
            {"pale", "pail"},
            {"peace", "piece"},
            {"plain", "plane"},
            {"quail", "quail"},  # cower vs bird
            {"rain", "reign", "rein"},
            {"road", "rode"},
            {"sail", "sale"},
            {"son", "sun"},
            {"tail", "tale"},
            {"wait", "weight"},
            {"weak", "week"},
            {"wear", "where"},
            {"wood", "would"},
            {"your", "you're"},
            {"break", "brake"},
            {"cent", "scent", "sent"},
            {"cite", "sight", "site"},
            {"fair", "fare"},
            {"flea", "flee"},
            {"grown", "groan"},
            {"heal", "heel"},
            {"meat", "meet"},
            {"pair", "pear"},
            {"principal", "principle"},
            {"roll", "role"},
            {"steal", "steel"},
            {"threw", "through"},
            {"tied", "tide"},
            {"waste", "waist"},
            {"aloud", "allowed"},
            {"ant", "aunt"},
            {"bare", "bear"},
            {"beat", "beet"},
            {"berry", "bury"},
            {"blew", "blue"},
            {"board", "bored"},
            {"bread", "bred"},
            {"capital", "capitol"},
            {"cereal", "serial"},
            {"chord", "cord"},
            {"coarse", "course"},
            {"creak", "creek"},
            {"die", "dye"},
            {"fairy", "ferry"},
            {"feat", "feet"},
            {"find", "fined"},
            {"flew", "flu", "flue"},
            {"gene", "jean"},
            {"hair", "hare"},
            {"hall", "haul"},
            {"heard", "herd"},
            {"hoarse", "horse"},
            {"hour", "our"},
            {"idle", "idol"},
            {"knot", "not"},
            {"lessen", "lesson"},
            {"loan", "lone"},
            {"made", "maid"},
            {"main", "mane"},
            {"medal", "meddle"},
            {"morning", "mourning"},
            {"none", "nun"},
            {"oar", "or", "ore"},
            {"pause", "paws"},
            {"peak", "peek"},
            {"pedal", "peddle"},
            {"pray", "prey"},
            {"profit", "prophet"},
            {"rap", "wrap"},
            {"real", "reel"},
            {"seam", "seem"},
            {"sole", "soul"},
            {"stair", "stare"},
            {"stationary", "stationery"},
            {"toad", "towed"},
            {"vain", "vein", "vane"},
            {"way", "weigh"},
            {"which", "witch"},
            {"whine", "wine"},
            {"who's", "whose"},
            {"ad", "add"},
            {"ail", "ale"},
            {"air", "heir"},
            {"aisle", "isle", "i'll"},
            {"altar", "alter"},
            {"arc", "ark"},
            {"ascent", "assent"},
            {"aye", "eye", "i"},
            {"bail", "bale"},
            {"ball", "bawl"},
            {"band", "banned"},
            {"baron", "barren"},
            {"base", "bass"},
            {"be", "bee"},
            {"beach", "beech"},
            {"berth", "birth"},
            {"billed", "build"},
            {"boar", "bore"},
            {"bold", "bowled"},
            {"bolder", "boulder"},
            {"born", "borne"},
            {"bough", "bow"},
            {"bridal", "bridle"},
            {"but", "butt"},
            {"cache", "cash"},
            {"ceiling", "sealing"},
            {"cellar", "seller"},
            {"chili", "chilly"},
            {"choral", "coral"},
            {"chews", "choose"},
            {"complement", "compliment"},
            {"council", "counsel"},
            {"cue", "queue"},
            {"currant", "current"},
            {"cymbal", "symbol"},
            {"days", "daze"},
            {"dew", "do", "due"},
            {"discreet", "discrete"},
            {"doe", "dough"},
            {"done", "dun"},
            {"dual", "duel"},
            {"earn", "urn"},
            {"ewe", "you", "yew"},
            {"faint", "feint"},
            {"fir", "fur"},
            {"flair", "flare"},
            {"foul", "fowl"},
            {"gait", "gate"},
            {"gilt", "guilt"},
            {"gorilla", "guerrilla"},
            {"great", "grate"},
            {"guessed", "guest"},
            {"hangar", "hanger"},
            {"hay", "hey"},
            {"higher", "hire"},
            {"him", "hymn"},
            {"hoard", "horde"},
            {"holey", "holy", "wholly"},
            {"in", "inn"},
            {"its", "it's"},
            {"knead", "need"},
            {"knew", "new", "gnu"},
            {"knows", "nose"},
            {"leak", "leek"},
            {"lie", "lye"},
            {"links", "lynx"},
            {"load", "lode"},
            {"loot", "lute"},
            {"maize", "maze"},
            {"mall", "maul"},
            {"mantel", "mantle"},
            {"marshal", "martial"},
            {"might", "mite"},
            {"miner", "minor"},
            {"missed", "mist"},
            {"mustard", "mustered"},
            {"naval", "navel"},
            {"nay", "neigh"},
            {"overdo", "overdue"},
            {"paced", "paste"},
            {"packed", "pact"},
            {"patience", "patients"},
            {"plum", "plumb"},
            {"pole", "poll"},
            {"poor", "pour", "pore"},
            {"praise", "prays", "preys"},
            {"presence", "presents"},
            {"rack", "wrack"},
            {"raise", "rays", "raze"},
            {"read", "reed"},
            {"read", "red"},
            {"ring", "wring"},
            {"rose", "rows"},
            {"rote", "wrote"},
            {"rye", "wry"},
            {"scene", "seen"},
            {"seas", "sees", "seize"},
            {"sew", "so", "sow"},
            {"side", "sighed"},
            {"slay", "sleigh"},
            {"soar", "sore"},
            {"some", "sum"},
            {"staid", "stayed"},
            {"steak", "stake"},
            {"straight", "strait"},
            {"suite", "sweet"},
            {"tacks", "tax"},
            {"team", "teem"},
            {"throne", "thrown"},
            {"thyme", "time"},
            {"toe", "tow"},
            {"told", "tolled"},
            {"tracked", "tract"},
            {"wail", "wale", "whale"},
            {"waive", "wave"},
            {"ware", "wear", "where"},
            {"warn", "worn"},
            {"weather", "whether"},
            {"weave", "we've"},
            {"wet", "whet"},
            {"yoke", "yolk"},
            {"yore", "your", "you're"},
            {"you'll", "yule"},
        ]

        return homophones

    def _build_reverse_index(
        self, groups: list[set[str]], keep_identical: bool = False
    ) -> dict[str, set[str]]:
        """Build a reverse index from each word to its homonym group.

        Raises:
            TypeError: If ``keep_identical`` is not a ``bool``, ``groups`` is a
                ``str``/``bytes``, or a group contains a non-``str``.
        """
        if not isinstance(keep_identical, bool):
            raise TypeError(
                "keep_identical must be a bool, got %r" % (keep_identical,)
            )
        if isinstance(groups, (str, bytes)):
            raise TypeError(
                "groups must be an iterable of sets of str, got %r"
                % (groups,)
            )
        index: dict[str, set[str]] = defaultdict(set)
        for group in groups:
            lowered_group: set[str] = set()
            for word in group:
                if not isinstance(word, str):
                    raise TypeError(
                        "groups must contain only str, got %r" % (word,)
                    )
                lowered_group.add(word.lower())
            for lowered_word in lowered_group:
                index[lowered_word].update(
                    member
                    for member in lowered_group
                    if keep_identical or member != lowered_word
                )
        return dict(index)

    def _clean_word(self, word: str, parameter: str = "word") -> str:
        """Normalize and validate a single word argument.

        Raises:
            TypeError: If ``parameter`` or ``word`` is not a ``str``.
            ValueError: If ``word`` has no non-whitespace characters.
        """
        if not isinstance(parameter, str):
            raise TypeError(
                "parameter must be a str, got %r" % (parameter,)
            )
        if not isinstance(word, str):
            raise TypeError("%s must be a str, got %r" % (parameter, word))
        cleaned_word = word.lower().strip()
        if not cleaned_word:
            raise ValueError(
                "%s must contain a non-whitespace character, got %r"
                % (parameter, word)
            )
        return cleaned_word

    def _clean_group(
        self, words: Iterable[str], parameter: str = "words"
    ) -> set[str]:
        """Normalize and validate a group of words.

        Raises:
            TypeError: If ``parameter`` is not a ``str``, or ``words`` is a
                ``str`` or contains a non-``str``.
            ValueError: If no word has a non-whitespace character.
        """
        if not isinstance(parameter, str):
            raise TypeError(
                "parameter must be a str, got %r" % (parameter,)
            )
        if isinstance(words, str):
            raise TypeError(
                "%s must be an iterable of str, not a str, got %r"
                % (parameter, words)
            )
        cleaned_group: set[str] = set()
        for word in words:
            if not isinstance(word, str):
                raise TypeError(
                    "%s must contain only str, got %r" % (parameter, word)
                )
            cleaned_word = word.lower().strip()
            if cleaned_word:
                cleaned_group.add(cleaned_word)
        if not cleaned_group:
            raise ValueError(
                "%s must contain at least one non-whitespace word, got %r"
                % (parameter, words)
            )
        return cleaned_group

    def are_homographs(self, word1: str, word2: str) -> bool:
        """Check if two words are homographs (same spelling, different
        meanings).

        Args:
            word1: First word.
            word2: Second word.

        Returns:
            True if the words are homographs, False otherwise.

        Raises:
            TypeError: If either argument is not a ``str``.
            ValueError: If either argument has no non-whitespace characters.
        """
        cleaned_word1 = self._clean_word(word1, "word1")
        cleaned_word2 = self._clean_word(word2, "word2")
        # A word spelled like another could simply be the same word, so equal
        # spelling is required but not sufficient.
        if cleaned_word1 != cleaned_word2:
            return False
        if cleaned_word1 in self._word_to_homographs:
            return True
        # Fallback: a word with more than one pronunciation (a heteronym, e.g.
        # "lead"/"read") is a homograph even when not in the curated cache.
        return len(phonetics.pronunciations(cleaned_word1)) > 1

    def are_homophones(self, word1: str, word2: str) -> bool:
        """Check if two words are homophones (sound alike, but differ in
        meaning, derivation, or spelling).

        Args:
            word1: First word.
            word2: Second word.

        Returns:
            True if the words are homophones, False otherwise.

        Raises:
            TypeError: If either argument is not a ``str``.
            ValueError: If either argument has no non-whitespace characters.
        """
        cleaned_word1 = self._clean_word(word1, "word1")
        cleaned_word2 = self._clean_word(word2, "word2")
        # Same spelling is only a homophone relationship for curated
        # same-spelling homonyms (e.g. "bat"); a word is not otherwise a
        # homophone of itself, and phonetics alone cannot tell two meanings of
        # one spelling apart.
        if cleaned_word1 == cleaned_word2:
            return cleaned_word1 in self._same_spelling_homophones
        if cleaned_word2 in self._word_to_homophones.get(cleaned_word1, set()):
            return True
        # Fallback: different-spelled words that share a pronunciation.
        return phonetics.sound_alike(cleaned_word1, cleaned_word2)

    def are_homonyms(self, word1: str, word2: str) -> bool:
        """Check if two words are homonyms (homographs, homophones, or both).

        Args:
            word1: First word.
            word2: Second word.

        Returns:
            True if the words are homonyms, False otherwise.

        Raises:
            TypeError: If either argument is not a ``str``.
            ValueError: If either argument has no non-whitespace characters.
        """
        # Validate this function's own parameters; never rely solely on the
        # delegated calls having done so.
        self._clean_word(word1, "word1")
        self._clean_word(word2, "word2")
        return self.are_homographs(word1, word2) or self.are_homophones(
            word1, word2
        )

    def classify(self, word1: str, word2: str) -> MatchType:
        """Classify how two words relate, returning a :class:`MatchType`.

        A pair that is both a homograph and a homophone is reported as
        ``HOMONYM``. When neither curated data nor cmudict can speak to the
        pair, the result is ``UNKNOWN`` rather than ``DIFFERENT``.

        Args:
            word1: First word.
            word2: Second word.

        Returns:
            The :class:`MatchType` describing the relationship.

        Raises:
            TypeError: If either argument is not a ``str``.
            ValueError: If either argument has no non-whitespace characters.
        """
        cleaned_word1 = self._clean_word(word1, "word1")
        cleaned_word2 = self._clean_word(word2, "word2")

        is_homograph: bool = self.are_homographs(word1, word2)
        is_homophone: bool = self.are_homophones(word1, word2)

        if is_homograph and is_homophone:
            return MatchType.HOMONYM
        if is_homograph:
            return MatchType.HOMOGRAPH
        if is_homophone:
            return MatchType.HOMOPHONE

        first_is_known: bool = (
            cleaned_word1 in self._word_to_homophones
            or cleaned_word1 in self._word_to_homographs
            or bool(phonetics.pronunciations(cleaned_word1))
        )
        second_is_known: bool = (
            cleaned_word2 in self._word_to_homophones
            or cleaned_word2 in self._word_to_homographs
            or bool(phonetics.pronunciations(cleaned_word2))
        )
        if first_is_known and second_is_known:
            return MatchType.DIFFERENT
        return MatchType.UNKNOWN

    def get_homographs(self, word: str) -> set[str]:
        """Get all homographs for a given word.

        Args:
            word: Input word.

        Returns:
            Set of homographs (empty set if none found).

        Raises:
            TypeError: If ``word`` is not a ``str``.
            ValueError: If ``word`` has no non-whitespace characters.
        """
        cleaned_word = self._clean_word(word)
        # Return a copy, never the live internal set: a caller mutating the
        # result must not be able to corrupt the reverse index.
        return set(self._word_to_homographs.get(cleaned_word, set()))

    def get_homophones(self, word: str) -> set[str]:
        """Get all homophones for a given word.

        Args:
            word: Input word.

        Returns:
            Set of homophones (empty set if none found).

        Raises:
            TypeError: If ``word`` is not a ``str``.
            ValueError: If ``word`` has no non-whitespace characters.
        """
        cleaned_word = self._clean_word(word)
        curated: set[str] = self._word_to_homophones.get(cleaned_word, set())
        # Curated cache is authoritative and fast; only fall back to cmudict
        # (which loads its dictionary) for words the cache does not cover.
        result: set[str] = (
            set(curated) if curated else phonetics.homophones(cleaned_word)
        )
        result.discard(cleaned_word)
        return result

    def get_all_homonyms(self, word: str) -> dict[str, set[str]]:
        """Get all types of homonyms for a given word.

        Args:
            word: Input word.

        Returns:
            Dictionary with ``homographs``, ``homophones``, and ``all`` keys.
            Value sets are empty if none exist.

        Raises:
            TypeError: If ``word`` is not a ``str``.
            ValueError: If ``word`` has no non-whitespace characters.
        """
        self._clean_word(word)  # validate this function's own parameter
        homographs: set[str] = self.get_homographs(word)
        homophones: set[str] = self.get_homophones(word)
        combined: set[str] = homographs.union(homophones)
        return {
            "homographs": homographs,
            "homophones": homophones,
            "all": combined,
        }

    def _index_group(
        self, index: dict[str, set[str]], group: set[str]
    ) -> None:
        """Add one group to a reverse index in place.

        Raises:
            TypeError: If ``index`` is not a ``dict``, ``group`` is a
                ``str``/``bytes``, or ``group`` contains a non-``str``.
        """
        if not isinstance(index, dict):
            raise TypeError("index must be a dict, got %r" % (index,))
        if isinstance(group, (str, bytes)):
            raise TypeError(
                "group must be an iterable of str, not a str, got %r"
                % (group,)
            )
        members: set[str] = set()
        for word in group:
            if not isinstance(word, str):
                raise TypeError(
                    "group must contain only str, got %r" % (word,)
                )
            members.add(word)
        for word in members:
            index.setdefault(word, set()).update(members)

    def add_homophone_group(self, words: Iterable[str]) -> bool:
        """Register a new homophone group (words that sound alike).

        Words are lower-cased and stripped. A group that collapses to a single
        spelling is treated as a same-spelling homonym (like the curated
        ``{"bat"}``).

        Args:
            words: The words that share a pronunciation.

        Returns:
            True if the group was added, False if an identical group already
            exists.

        Raises:
            TypeError: If ``words`` is a ``str`` or contains a non-``str``.
            ValueError: If no word has a non-whitespace character.
        """
        group = self._clean_group(words)
        if group in self._homophone_groups:
            return False
        self._homophone_groups.append(group)
        self._index_group(self._word_to_homophones, group)
        if len(group) == 1:
            self._same_spelling_homophones.update(group)
        return True

    def add_homograph_group(self, words: Iterable[str]) -> bool:
        """Register a new homograph group (words spelled the same).

        Args:
            words: The words that share a spelling.

        Returns:
            True if the group was added, False if an identical group already
            exists.

        Raises:
            TypeError: If ``words`` is a ``str`` or contains a non-``str``.
            ValueError: If no word has a non-whitespace character.
        """
        group = self._clean_group(words)
        if group in self._homograph_groups:
            return False
        self._homograph_groups.append(group)
        self._index_group(self._word_to_homographs, group)
        return True

    def warm(self, word: str) -> dict[str, set[str]]:
        """Promote cmudict fallback results for ``word`` into the cache.

        This is the opt-in counterpart to the read-only getters: rather than
        having a lookup silently mutate shared state, callers ask for promotion
        explicitly. After warming, future lookups for ``word`` (and any newly
        linked homophones) hit the in-memory groups instead of the phonetic
        fallback, and the pairs show up in :meth:`get_statistics`.

        Args:
            word: The word to promote into the curated cache.

        Returns:
            The homophones/homographs that were newly promoted (empty sets if
            the word was already cached or cmudict had nothing to add).

        Raises:
            TypeError: If ``word`` is not a ``str``.
            ValueError: If ``word`` has no non-whitespace characters.
        """
        cleaned_word = self._clean_word(word)
        promoted: dict[str, set[str]] = {
            "homophones": set(),
            "homographs": set(),
        }

        if cleaned_word not in self._word_to_homophones:
            partners = phonetics.homophones(cleaned_word)
            # Only multi-spelling groups are valid homophones; a lone word
            # would be wrongly recorded as a same-spelling homonym.
            if partners and self.add_homophone_group(
                partners | {cleaned_word}
            ):
                promoted["homophones"] = partners

        if cleaned_word not in self._word_to_homographs:
            has_multiple_pronunciations = (
                len(phonetics.pronunciations(cleaned_word)) > 1
            )
            if has_multiple_pronunciations and self.add_homograph_group(
                {cleaned_word}
            ):
                promoted["homographs"] = {cleaned_word}

        return promoted

    def get_statistics(self) -> dict[str, int]:
        """Get statistics about the loaded homonym data."""
        return {
            "homograph_groups": len(self._homograph_groups),
            "homophone_groups": len(self._homophone_groups),
            "total_homographic_words": len(self._word_to_homographs),
            "total_homophonic_words": len(self._word_to_homophones),
            "phonetic_fallback_enabled": int(phonetics.available()),
        }


def main() -> None:
    HomonymsLibrary()


if __name__ == "__main__":
    main()
