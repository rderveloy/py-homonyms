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
- [ ] Follow the principles of Clean Code and Clean Architecture (Robert C.
      Martin): small focused functions, meaningful names, minimal arguments, no
      side effects/command-query separation, DRY, clear separation of concerns
      and dependency direction (depend on abstractions, not details). Audit the
      codebase against these and refactor where it falls short.
