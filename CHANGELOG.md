# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `add_homophone_group()` and `add_homograph_group()` mutators that register
  new groups at runtime, maintaining the reverse indices and the
  same-spelling-homonym set, and skipping empty or duplicate groups.
- `warm()` method: an opt-in path that promotes cmudict fallback results for a
  word into the curated cache so later lookups hit the in-memory groups. The
  read-only getters stay pure (no hidden mutation); promotion is explicit and
  idempotent.
- Substantially expanded curated data: homophone groups 104 -> 227 and
  homograph groups 39 -> 84.

## [0.1]

### Added
- Initial `HomonymsLibrary` with curated homophone and homograph groups.
- `are_homophones()`, `are_homographs()`, `are_homonyms()`, `get_homophones()`,
  `get_homographs()`, `get_all_homonyms()`, and `get_statistics()`.
- `classify()` returning a `MatchType` (`HOMONYM`, `HOMOPHONE`, `HOMOGRAPH`,
  `DIFFERENT`, `UNKNOWN`).
- Optional cmudict phonetic fallback for words not covered by the curated data.
