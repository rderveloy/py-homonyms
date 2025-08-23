"""
English Homonyms Library
A comprehensive library for checking homonyms, homophones, and homographs in English.
"""

import json
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import re


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
        result: bool = False
        cleaned_word1, cleaned_word2 = word1.lower().strip(), word2.lower().strip()

        # Word lookup is needed since two strings spelled the same could just be the same word and not a homograph:
        result = (
            cleaned_word1 == cleaned_word2 and cleaned_word1 in self.word_to_homographs
        )
        return result

    def are_homophones(self, word1: str, word2: str) -> bool:
        """
        Check if two words are homophones (sound alike, but differ in meaning, derivation, or spelling).

        Args:
            word1: First word.
            word2: Second word.

        Returns:
            True if words are homophones, False otherwise.
        """

        result: bool = False

        cleaned_word1, cleaned_word2 = word1.lower().strip(), word2.lower().strip()

        result = cleaned_word2 in self.word_to_homophones.get(cleaned_word1, set())

        return result

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
        result: Set[str] = self.word_to_homophones.get(cleaned_word, set())
        return result

    def get_all_homonyms(self, word: str) -> Dict[str, Set[str]]:
        """
        Get all types of homonyms for a given word.

        Args:
            word: Input word

        Returns:
            Dictionary with 'homographs', 'homophones', and 'all keys.  Value sets will be empty if no homonyms exist.
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
        }

        return result


def main():
    test = HomonymsLibrary()


if __name__ == "__main__":
    main()
