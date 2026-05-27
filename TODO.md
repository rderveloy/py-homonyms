# TODO

- [ ] Add JSON persistence for warmed/curated groups: `to_json()` / `from_json()`
      built on the homophone/homograph groups, so a session's `warm()`
      promotions can be saved and reloaded across runs.

## Queued (do not implement yet — waiting on go-ahead)

- [ ] CLAUDE.md: add a rule on accidental-mistake prevention — design APIs so a
      caller's honest mistake cannot silently corrupt state (defensive copies of
      returned data, read-only views of internals, mutation only through
      sanctioned methods).
- [ ] CLAUDE.md: add/clarify a documentation rule — every comment must at least
      explain the *why* (rationale); the why is the floor and is never optional.
      Explaining the *what* in addition is welcome, but a comment that gives
      only the what, with no why, is insufficient.
- [ ] Make the mutator-managed backing fields name-mangled (double underscore,
      e.g. `__word_to_homophones`, `__word_to_homographs`, `__homophone_groups`,
      `__homograph_groups`, `__same_spelling_homophones`) so they are not
      accidentally inherited/overridden by subclasses. Notes for implementation:
      double underscore => name mangling (`_HomonymsLibrary__x`); this prevents
      subclass collisions but is not true privacy (still reachable via the
      mangled name). Update all internal references; keep the existing public
      read-only properties as the access surface; check no tests rely on the
      single-underscore private names.
- [ ] Discourage direct access to those fields via documentation: rely on the
      read-only property docstrings (the real mechanism), optionally add PEP 224
      attribute docstrings (string literal after each assignment; surfaced by
      Sphinx/IDEs though ignored at runtime), and a one-line note in the class
      docstring pointing callers to the properties + mutators.
- [ ] CLAUDE.md: add a rule to follow the principles of *Clean Code* by Robert
      C. Martin. Non-exhaustive examples: small functions that do one thing at a
      single level of abstraction; meaningful, intention-revealing names;
      minimal arguments (prefer 0-3, avoid flag args); command-query separation;
      no side effects; DRY; prefer exceptions to error codes; no dead code;
      leave code cleaner than you found it (boy-scout rule).
- [ ] CLAUDE.md: add a separate rule to follow the principles of *Clean
      Architecture* by Robert C. Martin. Non-exhaustive examples: separation of
      concerns across boundaries; the dependency rule — source dependencies
      point inward toward higher-level policy/abstractions, never toward
      details; business logic independent of frameworks, UI, DB, and IO; depend
      on abstractions via interfaces; the SOLID principles.
