"""Phonetic fallback backed by the CMU Pronouncing Dictionary.

This module is an optional enhancement. The curated cache in
``homonyms_library`` works with no dependencies; when ``cmudict`` is
installed it extends coverage to words the cache does not list. If
``cmudict`` is unavailable, every lookup here degrades to "no data" and
the library falls back to curated results only.
"""

from __future__ import annotations

from functools import lru_cache

try:
    import cmudict as _cmudict
except ImportError:  # pragma: no cover - exercised only without the optional dep
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
    p1 = pronunciations(word1)
    if not p1:
        return False
    return bool(p1 & pronunciations(word2))
