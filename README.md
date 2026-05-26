# py-homonyms
A comprehensive local library for checking homonyms, homophones, and homographs in English.  
Intentionally designed to not require an internet connection.

## Usage

```python
from py_homonyms import HomonymsLibrary, MatchType

lib = HomonymsLibrary()

lib.are_homophones("to", "two")    # True
lib.are_homographs("lead", "lead") # True
lib.are_homonyms("bat", "bat")     # True

lib.classify("to", "two")    # MatchType.HOMOPHONE
lib.classify("bat", "bat")   # MatchType.HOMONYM
lib.classify("lead", "lead") # MatchType.HOMOGRAPH
lib.classify("cat", "dog")   # MatchType.DIFFERENT
lib.classify("zzqx", "qxzz") # MatchType.UNKNOWN
```

`classify(word1, word2)` returns a `MatchType`:

| Value | Meaning |
|-------|---------|
| `HOMONYM`   | both a homograph and a homophone |
| `HOMOPHONE` | sound alike, different spelling |
| `HOMOGRAPH` | same spelling, different meaning/pronunciation |
| `DIFFERENT` | unrelated by spelling and sound |
| `UNKNOWN`   | no curated or phonetic data available for the pair |

## Phonetic fallback (optional)

Lookups are served first from the bundled **offline curated cache** of homophone
and homograph groups — no dependencies, no network. For word pairs the cache
doesn't cover, the library can fall back to the
[CMU Pronouncing Dictionary](https://github.com/cmusphinx/cmudict):

```bash
pip install -e ".[phonetics]"
```

`cmudict` bundles its data, so the fallback still works fully offline. Without
it installed, the library transparently uses curated results only.

For non-commercial use only CC BY-NC-SA 4.0.