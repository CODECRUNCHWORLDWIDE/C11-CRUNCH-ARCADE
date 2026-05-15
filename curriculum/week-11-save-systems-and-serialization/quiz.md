# Week 11 Quiz — Save Systems and Serialization

**Twenty questions.** Mix of multiple choice and short-answer. Closed-book in spirit; in practice, an honest open-book attempt is more useful than a guessing closed-book one. Time budget: ~45 minutes.

The answers are in `SOLUTIONS.md` at the bottom of this file, but try the quiz before reading them.

---

## Section A — Save-point design (5 questions)

**A1.** A roguelike with permadeath autosaves on every action. Which save-point pattern is this?

- (a) Manual save
- (b) Quicksave
- (c) Autosave on transition
- (d) Checkpoint
- (e) None of the above; permadeath autosaves are their own pattern.

---

**A2.** Which of the following is *not* part of the "what to actually save" minimum?

- (a) The player's name and level.
- (b) Quest progress flags.
- (c) The current animation frame the character is rendering.
- (d) The player's last-saved position.

---

**A3.** Short-answer (one sentence). State the *failure isolation* rationale for keeping meta state and run state in separate files.

---

**A4.** A game's save grows from 50 KB at launch to 500 MB after a year of patches and DLC. The most likely root cause is:

- (a) The player has more inventory.
- (b) The save started persisting the entire scene tree, including engine-internal node state, instead of just the player's progression.
- (c) The JSON format is too verbose.
- (d) The hash field is too long.

---

**A5.** True or false: a manual save is faster to implement than an autosave-on-transition system. Defend your answer in one sentence.

---

## Section B — Formats and schemas (5 questions)

**B1.** Why is `pickle.load` on a save file unsafe even if you wrote the save yourself?

- (a) Because pickle is slow.
- (b) Because pickle's output is larger than JSON.
- (c) Because the player or an attacker can replace the file on disk; pickle's `REDUCE` opcode executes any callable named by the bytes, so loading attacker bytes is executing attacker code.
- (d) Because pickle does not support nested objects.

---

**B2.** MessagePack vs JSON, on a typical 50 KB save: roughly how much smaller is the MessagePack version?

- (a) 10%
- (b) 50% to 70%
- (c) 95%
- (d) Same size; the formats encode the same data.

---

**B3.** Short-answer. Name three reasons to choose JSON over MessagePack for a dev build.

---

**B4.** In Pydantic v2, which call validates a parsed dictionary against a `BaseModel`?

- (a) `Model.parse_obj(d)` (Pydantic v1 API)
- (b) `Model.model_validate(d)`
- (c) `Model.from_dict(d)`
- (d) `Model(d)` directly with the dict as a positional argument.

---

**B5.** True or false: a `migrate_v1_to_v3` function is a reasonable optimisation when most users are on v1 and you have just released v3. Defend in one sentence.

---

## Section C — Atomicity and integrity (5 questions)

**C1.** The temp-file-plus-rename pattern protects against two specific failure modes. Name both in one sentence each.

---

**C2.** Which Python call is the *cross-platform* "atomic rename and replace"?

- (a) `os.rename`
- (b) `os.replace`
- (c) `shutil.move`
- (d) `pathlib.Path.rename`

---

**C3.** Why is `sort_keys=True` essential when hashing a JSON payload for an integrity check?

- (a) Performance: sorted keys parse faster.
- (b) Security: unsorted keys are easier to attack.
- (c) Determinism: without sorting, the same logical payload produces different bytes on different runs, and the integrity check fails on a re-save.
- (d) Compatibility: JSON parsers reject unsorted keys.

---

**C4.** The backup-rotation scheme described in Lecture 3 keeps how many save files per slot in steady state?

- (a) One.
- (b) Two: `save.latest` and `save.previous`.
- (c) Three: `save.latest`, `save.previous`, plus the in-flight `save.tmp`.
- (d) Ten.

---

**C5.** Short-answer. The simple SHA-256 integrity check catches accidental corruption but not deliberate tampering. State the *one* primitive that would close the deliberate-tampering gap (for casual attackers) and *one* threat it does not close.

---

## Section D — Cloud and edge cases (5 questions)

**D1.** Steam Cloud's default conflict-resolution behaviour, when the same save is modified on two machines, is:

- (a) Surface a conflict dialog to the player.
- (b) Last-writer-wins by file mtime.
- (c) Keep both versions in a `conflicts/` subfolder.
- (d) Refuse to sync.

---

**D2.** Apple iCloud Key-Value Storage has a per-user total quota of:

- (a) 100 KB.
- (b) 1 MB.
- (c) 10 MB.
- (d) 1 GB.

---

**D3.** Short-answer. Name one *legitimate* reason a save file on disk would fail to load that is *not* deliberate tampering and *not* a programming bug in the loader.

---

**D4.** The cursor-demo save's `version` field is missing because the save was written by a pre-versioning prototype. What should the loader do?

- (a) Refuse the file.
- (b) Crash with a `KeyError`.
- (c) Treat the missing version as v1 by convention (`if "version" not in parsed: parsed["version"] = 1`).
- (d) Skip the migration step entirely.

---

**D5.** True or false: the save system implemented in Week 11's mini-project is *ready* to integrate against Steam Cloud's Auto-Cloud feature without code changes. Defend in one sentence.

---

## Answer key

A1: (c) Autosave on transition (every action is a transition in the roguelike loop). A2: (c) The animation frame is engine state, not progression. A3: A corrupted run file should not delete settings; a corrupted meta file should not delete the playthrough. Two files, two atomic writes, two independent integrity checks. A4: (b) Persisting the scene tree is the root cause; the principle is *save the inputs, not the outputs*. A5: True. Manual save is the lowest-friction pattern: a single function the player invokes; autosave requires hooking every transition.

B1: (c). Pickle's deserialiser invokes any callable the bytes name, so loading attacker bytes is code execution. B2: (b). Typical ratios are 2x to 3x smaller for MessagePack. B3: Debuggability (the file is human-readable); modding (players can hand-edit); QA productivity (writing a save by hand to repro a bug). B4: (b). `model_validate` is v2; the rest are v1 or wrong. B5: False. The chained single-step migration is the maintainable form; the shortcut breaks the day v4 ships.

C1: Crash before any write (the open-for-write call truncates the file). Crash mid-write (leaves a half-populated file). The temp-file-plus-rename pattern eliminates both by writing to a sibling temp and only publishing via the atomic rename. C2: (b). `os.replace` works on every supported Python version on every supported OS. C3: (c) Determinism. The hash is over the canonicalised bytes; sort_keys=True is one component of canonicalisation. C4: (b) Two in steady state, plus a third briefly during a save operation. C5: HMAC-SHA-256 with a per-install secret key closes the casual-tampering gap. It does not close binary-patching the game to skip the check, extracting the key from process memory, or a determined reverse-engineering attack.

D1: (b) Last-writer-wins by file mtime; the conflict callback exists but must be opted into. D2: (b) 1 MB total; larger saves use iCloud Documents instead. D3: Disk-level corruption (a bad sector flips a bit), an interrupted cloud sync that uploaded truncated bytes, a filesystem rename failure mid-write, a player's antivirus quarantining the save. D4: (c) The convention is to treat missing version as v1 and run the chain. D5: True. The save system writes to a stable path under `OS.get_user_data_dir()`; Steam Cloud Auto-Cloud syncs by glob; declaring the glob in the Steamworks portal is the only configuration change needed.

## Scoring

| Score      | Outcome                                                     |
|------------|-------------------------------------------------------------|
| 18–20      | Excellent. You are ready to ship a save system in your next project. |
| 15–17      | Good. Re-read the section you missed most questions in.     |
| 12–14      | Pass. Read Lecture 2 and Lecture 3 again before the mini-project. |
| 0–11       | Did not pass. Re-attempt after re-reading all three lectures. |

The quiz is 15% of the week's grade.
