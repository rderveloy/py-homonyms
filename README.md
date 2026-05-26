# py-homonyms
A comprehensive library for checking homonyms, homophones, and homographs in English.

## Installation

```bash
pip install -e .
```

Pronunciation data comes from the [CMU Pronouncing Dictionary](https://github.com/cmusphinx/cmudict) (bundled via the `cmudict` package), so no network access is needed at runtime.

## Usage

```python
from py_homonyms import sound_alike

sound_alike("to", "two")        # True
sound_alike("flour", "flower")  # True
sound_alike("cat", "dog")       # False
```

`sound_alike(word1, word2)` returns `True` when the two words share at least one pronunciation — i.e. they can sound identical, regardless of spelling or meaning. Lookup is case-insensitive, and unknown words return `False`.

### Classifying a pair of words

```python
from py_homonyms import classify, MatchType

classify("to", "two")     # MatchType.HOMOPHONE  (different spelling, same sound)
classify("bat", "bat")    # MatchType.HOMONYM    (same spelling, one sound)
classify("lead", "lead")  # MatchType.HOMOGRAPH  (same spelling, multiple sounds)
classify("cat", "dog")    # MatchType.DIFFERENT
classify("cat", "zzqx")   # MatchType.UNKNOWN    (no pronunciation data)
```

`MatchType` values:

| Value | Spelling | Sound |
|-------|----------|-------|
| `HOMONYM`   | same | same (single pronunciation) |
| `HOMOPHONE` | different | same |
| `HOMOGRAPH` | same | word has more than one pronunciation |
| `DIFFERENT` | different | different |
| `UNKNOWN`   | — | pronunciation data missing for a word |

**Note:** classification works on spelling and sound only — there's no word-sense data. A word with variant pronunciations of the *same* meaning (e.g. `either`) is still reported as `HOMOGRAPH`.

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
