"""Phonetic fallback backed by the CMU Pronouncing Dictionary.

This module is an optional enhancement. The curated cache in
``homonyms_library`` works with no dependencies; when ``cmudict`` is
installed it extends coverage to words the cache does not list. If
``cmudict`` is unavailable, every lookup here degrades to "no data" and
the library falls back to curated results only.
"""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache

try:
    import cmudict as _cmudict
except ImportError:  # pragma: no cover - only without the optional dep
    _cmudict = None

Pronunciation = tuple[str, ...]


def available() -> bool:
    """Return ``True`` if the cmudict fallback can be used."""
    return _cmudict is not None


@lru_cache(maxsize=1)
def _dictionary() -> dict[str, list[list[str]]]:
    return _cmudict.dict() if _cmudict is not None else {}


def pronunciations(word: str) -> set[Pronunciation]:
    """Return the set of known pronunciations for ``word`` (empty if unknown).

    Each pronunciation is a tuple of ARPAbet phonemes; vowels carry a trailing
    stress digit (e.g. ``UW1``). Lookup is case-insensitive.
    """
    entries = _dictionary().get(word.strip().lower(), [])
    return {tuple(phonemes) for phonemes in entries}


def sound_alike(word1: str, word2: str) -> bool:
    """Return ``True`` if the two words share at least one pronunciation."""
    first_pronunciations = pronunciations(word1)
    if not first_pronunciations:
        return False
    return bool(first_pronunciations & pronunciations(word2))


@lru_cache(maxsize=1)
def _reverse_index() -> dict[Pronunciation, set[str]]:
    """Map each pronunciation to the set of words that have it (built once)."""
    index: dict[Pronunciation, set[str]] = defaultdict(set)
    for word, entries in _dictionary().items():
        for phonemes in entries:
            index[tuple(phonemes)].add(word)
    return index


def homophones(word: str) -> set[str]:
    """Return words sharing a pronunciation with ``word`` (excluding it).

    Empty if ``word`` is unknown or cmudict is unavailable.
    """
    cleaned = word.strip().lower()
    index = _reverse_index()
    result: set[str] = set()
    for pron in pronunciations(cleaned):
        result |= index.get(pron, set())
    result.discard(cleaned)
    return result
