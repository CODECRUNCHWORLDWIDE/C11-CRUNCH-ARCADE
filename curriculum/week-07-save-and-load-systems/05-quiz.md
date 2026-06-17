# Week 7 — Quiz

Ten multiple-choice questions. Take it with your lecture notes closed. Aim for 9/10 before moving to Week 8. Answer key at the bottom — don't peek.

---

**Q1.** Lecture 1 sorts every field of a running game into one of four categories. Which of these is the *persistent* category?

- A) The player's current velocity (`vx`, `vy`).
- B) The player's `pygame.Surface` sprite reference.
- C) The player's inventory items and the world flags.
- D) The screen-shake remaining duration from Week 6.

---

**Q2.** Why does Lecture 1 §7 reject `pickle` as a save format?

- A) Pickle is slower than JSON.
- B) Pickle executes Python code on load, is brittle to refactoring, and is Python-only.
- C) Pickle files are larger than JSON files.
- D) Pickle is not in the Python standard library.

---

**Q3.** The `GameState` dataclass from Lecture 1 has `schema_version: int = 1` as its first field. Why is that field so important?

- A) It makes the file slightly smaller.
- B) It is required by `json.dump`; the function rejects dicts without a version key.
- C) It allows old saves to be detected and routed through a migration ladder when the code's expected schema changes.
- D) It is a Python convention; all dataclasses start with a `version` field.

---

**Q4.** Lecture 2's decision rule (§10) says JSON is the default for game saves. When does the rule recommend switching to MessagePack?

- A) Whenever a third-party package is available.
- B) When the JSON save grows past a few megabytes *and* a profiler shows the save call as a measurable bump.
- C) When the player asks for it in a settings menu.
- D) Whenever the game runs on Windows.

---

**Q5.** Lecture 2 §7 observes that JSON + gzip is competitive with MessagePack on *size*. The reason JSON compresses so well is:

- A) JSON files are sorted alphabetically.
- B) JSON repeats key names and uses ASCII digits for numbers, which gzip exploits as redundancy.
- C) JSON is already compressed internally.
- D) Gzip detects JSON syntax and uses a JSON-specific encoder.

---

**Q6.** The atomic-write pattern from Lecture 3 §4 has three operations in this order. Pick the correct order.

- A) `os.replace` → `f.flush` → `json.dump`.
- B) `json.dump` → `f.flush` + `os.fsync` → `os.replace`.
- C) `json.dump` → `os.replace` → `os.fsync`.
- D) `os.fsync` → `json.dump` → `os.replace`.

---

**Q7.** The migration ladder pattern (Lecture 3 §2) composes one-step functions like `migrate_v1_to_v2` and `migrate_v2_to_v3`. What discipline does each individual migration follow?

- A) It steps *exactly one* version forward and updates `schema_version` to the new value before returning.
- B) It walks the dict to the *current* version in one shot, calling all later migrations internally.
- C) It deletes obsolete fields from the dict on every step.
- D) It writes the migrated dict to disk as a side effect.

---

**Q8.** Lecture 3 §6 stores a SHA-256 digest in a sidecar `.sha256` file next to the save. What problem does this digest solve?

- A) It prevents a determined player from editing the save by hand.
- B) It detects accidental corruption — bit-flips on disk, incomplete writes, or a hand-edit that broke the JSON — by comparing the recomputed digest against the stored value on load.
- C) It encrypts the save so it cannot be read without a key.
- D) It compresses the save by replacing it with the digest.

---

**Q9.** Lecture 3 §7 argues against shipping anti-cheat for *local* saves. The argument rests on which observation?

- A) The Python stdlib has no anti-cheat library.
- B) Anti-cheat is illegal under EU consumer-protection law.
- C) A local save lives on a machine the player controls; any obfuscation a developer ships in the binary can be reversed by the player, so engineering hours are better spent elsewhere.
- D) Anti-cheat slows the save by ~10 ms, exceeding the frame budget.

---

**Q10.** The mini-project ships **three save slots** plus an **autosave slot**. The lecture's recommended cadence for autosave is:

- A) Every frame.
- B) Every five seconds of wall-clock time.
- C) On a level boundary (or another safe checkpoint like death / game-over), with an optional N-minute wall-clock fallback. Never every frame.
- D) Only when the player explicitly requests it.

---

## Answer key (do not peek until you have committed answers)

1. **C** — Persistent state is what the player has earned; the others are session (velocity), presentation (`pygame.Surface`), and session (screen-shake timer). See Lecture 1 §2.
2. **B** — All three. The code-execution-on-load point alone disqualifies pickle for any cross-machine context; the refactoring brittleness disqualifies it across game versions; the Python-only constraint disqualifies it for any out-of-process tool. Lecture 1 §7.
3. **C** — The first byte of every save is the version stamp; without it, evolving the schema in v2 cannot read v1 saves without breaking them. Lecture 3 §1.
4. **B** — JSON is the default. MessagePack is the answer when JSON shows up on a profiler. Lecture 2 §10.
5. **B** — JSON has high lexical redundancy (key names repeated per record, numbers as ASCII digits) and gzip exploits exactly this kind of pattern. Lecture 2 §7.
6. **B** — Write, flush+fsync, rename. The fsync ensures the temp file is durable before the rename commits it; the rename is atomic. Lecture 3 §4.
7. **A** — One step at a time, update the version, return. The composer chains them. Lecture 3 §2.
8. **B** — Integrity against accident, not security against malice. SHA-256 is a checksum, not a signature; a tampered file with a recomputed hash will pass the check. Lecture 3 §6.
9. **C** — The player controls the machine; any obfuscation can be reversed. Local-save anti-cheat is theatre. The exception is multiplayer leaderboards (server-side authority), which is a Week-12 topic. Lecture 3 §7.
10. **C** — Level boundary is the safe cadence; the autosave slot is dedicated and cannot trample manual saves. Lecture 3 §8.

---

*Score yourself. 9-10 is a pass; 7-8 means re-read the lecture for any question you missed; below 7 means re-read all three lectures before starting the mini-project.*
