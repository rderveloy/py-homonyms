"""
English Homonyms Library
A comprehensive library for checking homonyms, homophones, and homographs in English.
"""

import enum
import json
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import re

from . import phonetics


class MatchType(enum.Enum):
    """How two words relate.

    ``HOMONYM``   - both a homograph and a homophone (e.g. ``bat`` the animal vs. the bat you swing).
    ``HOMOPHONE`` - sound alike but not the same spelling (e.g. ``to`` / ``two``).
    ``HOMOGRAPH`` - same spelling, different meaning/pronunciation (e.g. ``lead``).
    ``DIFFERENT`` - unrelated by spelling and sound.
    ``UNKNOWN``   - no curated or phonetic data was available to judge the pair.
    """

    HOMONYM = "homonym"
    HOMOPHONE = "homophone"
    HOMOGRAPH = "homograph"
    DIFFERENT = "different"
    UNKNOWN = "unknown"


class HomonymsLibrary:
    """
    A local library for working with English homonyms, including:
    - Homophones: words that sound the same, but are different in meaning (baseball bat vs animal bat) or spelling (sea vs see).
    - Homographs: words that are spelled the same, but different in meaning and/or pronounciation (lead weight vs lead the team).
    - Homonyms: words that are homographs, homophones, or both.
    See: https://www.merriam-webster.com/grammar/homophones-vs-homographs-vs-homonyms
    """

    def __init__(self):
        self.homograph_groups: List[Set[str]] = self._load_homographs()
        self.homophone_groups: List[Set[str]] = self._load_homophones()
        self.word_to_homographs: Dict[str, Set[str]] = self._build_reverse_index(
            self.homograph_groups, keep_identical=True
        )
        self.word_to_homophones: Dict[str, Set[str]] = self._build_reverse_index(
            self.homophone_groups, keep_identical=True
        )
        # Words that are homophones of themselves: same spelling, same sound,
        # different meaning (e.g. "bat"). These appear as single-member groups.
        self.same_spelling_homophones: Set[str] = {
            word.lower()
            for group in self.homophone_groups
            if len({w.lower() for w in group}) == 1
            for word in group
        }

    def _load_homographs(self) -> List[Set[str]]:
        """
        Load homograph groups (words with same spelling, but different meanings).  Can have same or different pronounciations.
        See: https://www.merriam-webster.com/grammar/homophones-vs-homographs-vs-homonyms
        """

        homographs: List[Set[str]] = [
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
            {"present", "present", "present"},  # gift vs current time vs to show
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

    def _load_homophones(self) -> List[Set[str]]:
        """
        Load homophone groups (words that sound alike, but have different meanings).  Spelling can be the same or different.
        See: https://www.merriam-webster.com/grammar/homophones-vs-homographs-vs-homonyms
        """

        # Common English homophones
        homophones: List[Set[str]] = [
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
        self, groups: List[Set[str]], keep_identical=False
    ) -> Dict[str, Set[str]]:
        """Build reverse index from word to its homonym group"""
        result: Dict[str, Set[str]] = None
        index = defaultdict(set)

        for group in groups:
            for word in group:
                index[word.lower()].update(
                    w.lower()
                    for w in group
                    if keep_identical or w.lower() != word.lower()
                )

        result = dict(index)
        return result

    def are_homographs(self, word1: str, word2: str) -> bool:
        """
        Check if two words are homographs (same spelling, different meanings)

        Args:
            word1: First word
            word2: Second word

        Returns:
            True if words are homographs, False otherwise
        """
        cleaned_word1, cleaned_word2 = word1.lower().strip(), word2.lower().strip()

        # Word lookup is needed since two strings spelled the same could just be the same word and not a homograph:
        if cleaned_word1 != cleaned_word2:
            return False
        if cleaned_word1 in self.word_to_homographs:
            return True

        # Fallback: a word with more than one pronunciation (a heteronym, e.g.
        # "lead"/"read") is a homograph even when it is not in the curated cache.
        return len(phonetics.pronunciations(cleaned_word1)) > 1

    def are_homophones(self, word1: str, word2: str) -> bool:
        """
        Check if two words are homophones (sound alike, but differ in meaning, derivation, or spelling).

        Args:
            word1: First word.
            word2: Second word.

        Returns:
            True if words are homophones, False otherwise.
        """

        cleaned_word1, cleaned_word2 = word1.lower().strip(), word2.lower().strip()

        # Same spelling is only a homophone relationship for curated same-spelling
        # homonyms (e.g. "bat"); a word is not otherwise a homophone of itself, and
        # phonetics alone cannot tell two meanings of one spelling apart.
        if cleaned_word1 == cleaned_word2:
            return cleaned_word1 in self.same_spelling_homophones

        if cleaned_word2 in self.word_to_homophones.get(cleaned_word1, set()):
            return True

        # Fallback: different-spelled words that share a pronunciation are homophones.
        return phonetics.sound_alike(cleaned_word1, cleaned_word2)

    def are_homonyms(self, word1: str, word2: str) -> bool:
        """
        Check if two words are homonyms (any type: homographs, homophones, or both).

        Args:
            word1: First word.
            word2: Second word.

        Returns:
            True if words are homonyms, False otherwise.
        """

        result: bool = self.are_homographs(word1, word2) or self.are_homophones(
            word1, word2
        )

        return result

    def classify(self, word1: str, word2: str) -> "MatchType":
        """Classify how two words relate, returning a :class:`MatchType`.

        A pair that is both a homograph and a homophone is reported as
        ``HOMONYM``. When neither curated data nor cmudict can speak to the
        pair, the result is ``UNKNOWN`` rather than ``DIFFERENT``.
        """
        homograph: bool = self.are_homographs(word1, word2)
        homophone: bool = self.are_homophones(word1, word2)

        if homograph and homophone:
            return MatchType.HOMONYM
        if homograph:
            return MatchType.HOMOGRAPH
        if homophone:
            return MatchType.HOMOPHONE

        cleaned_word1, cleaned_word2 = word1.lower().strip(), word2.lower().strip()
        known = (
            cleaned_word1 in self.word_to_homophones
            or cleaned_word1 in self.word_to_homographs
            or bool(phonetics.pronunciations(cleaned_word1))
        ) and (
            cleaned_word2 in self.word_to_homophones
            or cleaned_word2 in self.word_to_homographs
            or bool(phonetics.pronunciations(cleaned_word2))
        )
        return MatchType.DIFFERENT if known else MatchType.UNKNOWN

    def get_homographs(self, word: str) -> Set[str]:
        """
        Get all homographs for a given word.

        Args:
            word: Input word

        Returns:
            Set of homographs (empty set if none found)
        """
        cleaned_word: str = word.lower().strip()
        result: Set[str] = self.word_to_homographs.get(cleaned_word, set())
        return result

    def get_homophones(self, word: str) -> Set[str]:
        """
        Get all homophones for a given word.

        Args:
            word: Input word

        Returns:
            Set of homophones (empty set if none found)
        """
        cleaned_word = word.lower().strip()
        curated: Set[str] = self.word_to_homophones.get(cleaned_word, set())

        # Curated cache is authoritative and fast; only fall back to cmudict
        # (which loads its dictionary) for words the cache does not cover.
        result: Set[str] = set(curated) if curated else phonetics.homophones(cleaned_word)

        result.discard(cleaned_word)
        return result

    def get_all_homonyms(self, word: str) -> Dict[str, Set[str]]:
        """
        Get all types of homonyms for a given word.

        Args:
            word: Input word

        Returns:
            Dictionary with 'homographs', 'homophones', and 'all keys.  Value sets will be empty if none exist.
        """

        homographs: Set[str] = self.get_homographs(word)
        homophones: Set[str] = self.get_homophones(word)
        all: Set[str] = homographs.union(homophones)

        result: Dict[str, Set[str]] = {
            "homographs": homographs,
            "homophones": homophones,
            "all": all,
        }

        return result

    # def add_homograph_group(self, words: List[str]) -> None:
    #     pass

    # def add_homophone_group(self, words: List[str]) -> None:
    #     pass

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the loaded homonym data"""

        result: Dict[str, int] = {
            "homograph_groups": len(self.homograph_groups),
            "homophone_groups": len(self.homophone_groups),
            "total_homographic_words": len(self.word_to_homographs),
            "total_homophonic_words": len(self.word_to_homophones),
            "phonetic_fallback_enabled": int(phonetics.available()),
        }

        return result


def main():
    test = HomonymsLibrary()


if __name__ == "__main__":
    main()
