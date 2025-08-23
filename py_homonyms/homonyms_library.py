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
    A library for working with English homonyms, including:
    - Homographs: words with same spelling but different meanings
    - Homophones: words that sound alike but may have different spellings
    - True homonyms: words that are both homographs and homophones
    """

    def __init__(self):
        self.homograph_groups: List[Set[str]] = self._load_homographs()
        self.homophone_groups: List[Set[str]] = self._load_homophones()
        self.word_to_homographs: Dict[str, Set[str]] = self._build_reverse_index(
            self.homograph_groups
        )
        self.word_to_homophones: Dict[str, Set[str]] = self._build_reverse_index(
            self.homophone_groups
        )

    def _load_homographs(self) -> List[Set[str]]:
        """Load homograph groups (words with same spelling, but different meanings)"""

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
            {"present", "present"},  # gift vs current time vs to show
            {"produce", "produce"},  # to create vs fruits/vegetables
            {"project", "project"},  # plan vs to extend outward
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
        """Load homophone groups (words that sound alike, but are spelled differently)"""

        # Common English homophones
        homophones: List[Set[str]] = [
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

    def _build_reverse_index(self, groups: List[Set[str]]) -> Dict[str, Set[str]]:
        """Build reverse index from word to its homonym group"""
        result: Dict[str, Set[str]] = None
        index = defaultdict(set)

        for group in groups:
            for word in group:
                index[word.lower()].update(
                    w.lower() for w in group if w.lower() != word.lower()
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
        word1, word2 = word1.lower().strip(), word2.lower().strip()

        # TODO: Find out if word lookup is not needed and can be removed for performance:
        result = word1 == word2 and word1 in self.word_to_homographs
        return result

    def are_homophones(self, word1: str, word2: str) -> bool:
        """
        Check if two words are homophones (sound alike, but have different spelling)

        Args:
            word1: First word
            word2: Second word

        Returns:
            True if words are homophones, False otherwise
        """

        result: bool = False

        word1, word2 = word1.lower().strip(), word2.lower().strip()

        if word1 == word2:
            result = False  # Same word, not technically homophones
        else:
            result = word2 in self.word_to_homophones.get(word1, set())

        return result

    def are_homonyms(self, word1: str, word2: str) -> bool:
        """
        Check if two words are homonyms (any type: homographs, homophones, or both)

        Args:
            word1: First word
            word2: Second word

        Returns:
            True if words are homonyms, False otherwise
        """

        result: bool = self.are_homographs(word1, word2) or self.are_homophones(
            word1, word2
        )

        return result

    def get_homographs(self, word: str) -> Set[str]:
        pass

    def get_homophones(self, word: str) -> Set[str]:
        pass

    def get_all_homonyms(self, word: str) -> Dict[str, Set[str]]:
        pass

    def add_homograph_group(self, words: List[str]) -> None:
        pass

    def add_homophone_group(self, words: List[str]) -> None:
        pass

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the loaded homonym data"""

        result: Dict[str, int] = {
            'homograph_groups': len(self.homograph_groups),
            'homophone_groups': len(self.homophone_groups),
            'total_homographic_words': len(self.word_to_homographs),
            'total_homophonic_words': len(self.word_to_homophones)
        }

        return result


def main():
    pass


if __name__ == "__main__":
    main()
