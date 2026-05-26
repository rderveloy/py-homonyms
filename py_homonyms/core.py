"""Core phonetic comparison logic for py-homonyms."""

from __future__ import annotations

from functools import lru_cache

import cmudict

Pronunciation = tuple[str, ...]


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
    entries = _dictionary().get(word.strip().lower(), [])
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
