"""Core phonetic comparison logic for py-homonyms."""

from __future__ import annotations

import enum
from functools import lru_cache

import cmudict

Pronunciation = tuple[str, ...]


class MatchType(enum.Enum):
    """How two words relate by spelling and sound.

    ``HOMONYM``    - same spelling, same sound (e.g. ``bat`` the animal vs. the bat you swing).
    ``HOMOPHONE``  - different spelling, same sound (e.g. ``to`` / ``two``).
    ``HOMOGRAPH``  - same spelling but more than one pronunciation (e.g. ``lead``, ``bass``).
    ``DIFFERENT``  - neither spelling nor sound match.
    ``UNKNOWN``    - pronunciation data is missing, so sound cannot be judged.
    """

    HOMONYM = "homonym"
    HOMOPHONE = "homophone"
    HOMOGRAPH = "homograph"
    DIFFERENT = "different"
    UNKNOWN = "unknown"


def _normalize(word: str) -> str:
    return word.strip().lower()


@lru_cache(maxsize=1)
def _dictionary() -> dict[str, list[list[str]]]:
    """The CMU Pronouncing Dictionary, loaded once on first use."""
    return cmudict.dict()


def pronunciations(word: str) -> set[Pronunciation]:
    """Return the set of known pronunciations for ``word``.

    Each pronunciation is a tuple of ARPAbet phonemes (vowels carry a
    trailing stress digit, e.g. ``UW1``). An unknown word yields an empty set.
    Lookup is case-insensitive.
    """
    entries = _dictionary().get(_normalize(word), [])
    return {tuple(phonemes) for phonemes in entries}


def sound_alike(word1: str, word2: str) -> bool:
    """Return ``True`` if the two words can be pronounced identically.

    Words are homophones when they share at least one pronunciation,
    regardless of spelling or meaning (e.g. ``to``/``too``/``two``).
    Returns ``False`` if either word is absent from the dictionary.
    """
    p1 = pronunciations(word1)
    if not p1:
        return False
    return bool(p1 & pronunciations(word2))


def same_spelling(word1: str, word2: str) -> bool:
    """Return ``True`` if the two words are spelled identically (case-insensitive)."""
    return _normalize(word1) == _normalize(word2)


def classify(word1: str, word2: str) -> MatchType:
    """Classify how two words relate by spelling and sound.

    See :class:`MatchType` for the possible results. A same-spelling word with
    more than one pronunciation is reported as ``HOMOGRAPH`` even when both
    spellings are identical, since it can be read in more than one way.
    """
    p1 = pronunciations(word1)
    p2 = pronunciations(word2)

    if same_spelling(word1, word2):
        if not p1:
            return MatchType.UNKNOWN
        if len(p1) > 1:
            return MatchType.HOMOGRAPH
        return MatchType.HOMONYM

    if not p1 or not p2:
        return MatchType.UNKNOWN
    if p1 & p2:
        return MatchType.HOMOPHONE
    return MatchType.DIFFERENT
