# Lecture 1 — When and What to Save

> **Duration:** ~2 hours of reading plus design exercise.
> **Outcome:** You can name the four save-point patterns shipped games actually use, choose the right pattern for a given game's loop, distinguish *meta* state from *run* state, and state what should never go into a save file at all.

If you only remember one thing from this lecture, remember this:

> **A save file is a contract between your current self and your future self. The format you pick today is the format you have to migrate forever. Pick the smallest format that captures the player's progression and intent, not the largest format that captures the engine's current state.**

The lecture begins with the taxonomy of save points (manual, autosave, quicksave, checkpoint), narrows to the question of *what* a save should contain, separates *meta* state from *run* state, and ends with a short list of things that should never be in a save file regardless of game.

We lean on the Godot 4.x "Saving games" tutorial throughout. The tutorial's "What to save" subsection is short on words and long on judgement; this lecture expands it.

---

## 1. The four save-point patterns, with shipped examples

The taxonomy below is a designer's vocabulary, not a programmer's. The patterns determine the write cadence and the player's trust contract; the implementation is the same in all four cases (it is the code in Lecture 3). Pick the pattern first; write the code last.

### 1.1 Manual save

The player chooses when to save. The classic JRPG implementation: the player walks to an inn or a save crystal, opens a menu, picks "Save," chooses a slot. The save fires exactly when requested.

The contract with the player: *the game's progression state is exactly as it was at the moment you pressed the button, no earlier and no later.* The cost to the player: they have to remember to do it. The cost to the developer: nothing — manual save is the lowest-friction pattern to implement.

Shipped examples:

- *Final Fantasy VI* (1994) — save crystals on the world map.
- *Resident Evil 1* (1996) — typewriters in fixed locations, consuming an ink-ribbon item per save. (The item consumption is a *design* choice, not a *technology* one.)
- *Persona 5* (2016) — save anywhere outside combat.
- *Hollow Knight* (2017) — benches in fixed locations. Players sit on a bench; the game writes.

### 1.2 Autosave on transition

The engine chooses when to save: every time the player crosses a boundary the designer marks as "interesting." Common boundaries: level transitions, dialogue trees, boss fight starts, scene loads, sleep cycles.

The contract with the player: *progress made since the last transition is in danger; progress made before the last transition is safe.* The cost to the player: surprise — the player learns the cadence by playing. The cost to the developer: every transition needs a `SaveManager.autosave()` call and a small busy indicator in the corner of the screen.

Shipped examples:

- *Stardew Valley* (2016) — autosaves at the end of every in-game day, when the player goes to sleep.
- *The Legend of Zelda: Breath of the Wild* (2017) — autosaves on Shrine entry / exit and on warping.
- *Dark Souls* (2011) — autosaves on every meaningful event; you cannot opt out. The bonfire-rest is technically a manual transition that triggers an autosave write.
- *Hades* (2020) — autosaves on room transitions; combined with the death-resets-the-run roguelike loop, the cadence is "every 30 seconds."

### 1.3 Quicksave

A key binding (typically F5 or F9) that saves to a dedicated `quicksave` slot. The quicksave is conceptually a manual save, but with a single hard-coded slot and zero menu navigation.

The contract with the player: *the player is power-using the save system to rewind half a second when they made a mistake.* The cost: the same as manual save plus one extra slot to manage.

Shipped examples:

- *The Elder Scrolls V: Skyrim* (2011) — F5 quicksave, F9 quickload. Heavy use by players who treat the game as a roguelike with a rewind button.
- Most strategy games — *XCOM 2*, *Civilization VI* — bind both keys by default.
- *Doom Eternal* (2020) — explicitly no quicksave; the design choice removes the "save before every encounter" pattern.

### 1.4 Checkpoint (designer-placed)

A hybrid: the designer places a checkpoint trigger in the level; when the player crosses the trigger, the game autosaves. The cadence is the designer's, not the engine's.

The contract with the player: *between checkpoints you are in the same danger as in autosave-on-transition mode; the difference is that the designer chose the cadence rather than the engine.* The cost: someone (a designer, a level designer, often both) has to place the triggers and confirm they do not skip over needed state.

Shipped examples:

- *Halo: Combat Evolved* (2001) — invisible checkpoint triggers throughout each level.
- *Celeste* (2018) — every screen transition is a checkpoint; deaths return to the most recent.
- Most modern AAA games — *God of War (2018)*, *Marvel's Spider-Man* — combine designer checkpoints with autosaves on major story beats.

### 1.5 Comparison table

The four patterns line up like this:

| Pattern              | Player chooses *when*? | Player chooses *where*? | Designer chooses *where*? | Engine chooses *when*? | Typical files / day |
|----------------------|:----------------------:|:-----------------------:|:-------------------------:|:----------------------:|--------------------:|
| Manual save          |          Yes           |       Yes (slot)        |             —             |           —            |               1–10  |
| Autosave (transition)|          No            |           No            |             —             |          Yes           |              30–100 |
| Quicksave            |       Yes (key)        |     No (one slot)       |             —             |           —            |             50–500  |
| Checkpoint           |          No            |           No            |            Yes            |          —             |              20–80  |

Most modern games ship at least two of the four patterns. *Stardew Valley* ships autosave-on-transition and manual save. *Dark Souls* ships checkpoint and autosave-on-event but disables manual save deliberately. *Skyrim* ships all four.

### 1.6 Implications for write cadence

If you ship manual save only, the save subsystem is invoked a few times per hour at most. The write can take 100 ms and the player will not notice. You can write synchronously on the main thread.

If you ship autosave at transitions, the save subsystem fires on every loading screen. The write happens while a loading screen is already drawn; again, the player does not notice 100 ms. Synchronous is fine.

If you ship quicksave, the save subsystem fires on a key press during gameplay. A 100 ms stall *is* visible. You must either:

- Make the save fast enough to fit in one frame's slack budget (<5 ms is safe), or
- Move the save off the main thread.

For the size of the saves we will write this week (a few kilobytes, JSON-formatted), option (a) is achievable. A JSON serialise and a synchronous write of 5 KB completes in under a millisecond on any modern SSD. The temp-file-plus-rename pattern (Lecture 3) keeps that to ~3 ms in the worst case.

For a 100 MB *Skyrim*-style save with thousands of entity references, option (b) is mandatory and the write becomes a multi-frame, multi-thread coordinated dance. We do not cover that case this week; the prerequisites (worker threads in Godot, double-buffered game state, frozen-snapshot serialisation) are a full course of their own.

---

## 2. What to actually save

The hardest question in save design is not *how* but *what*. The answer is informed by a single principle:

> **Save the minimum data needed to reconstruct the player's progression and intent. Everything else is reconstructible from that minimum at load time, by re-running deterministic engine code.**

We work through the principle in four directions.

### 2.1 What goes in: player progression and intent

These are the artefacts of *time the player has spent*. Losing them is what makes a save corruption catastrophic.

- **Character identity and stats.** Name, class, level, experience, learned skills, allocated stat points. Every choice the player made about who their character is.
- **Inventory.** Item IDs and counts. Not the rendered icons; not the cached descriptions; just the IDs.
- **Quest state.** Quest IDs and their progress markers ("talked to NPC", "delivered the package"). Not the dialogue trees themselves; those are static data in the game build.
- **World-progression flags.** Doors unlocked, NPCs killed permanently, keys collected. Booleans, mostly.
- **Position and orientation at the last save point.** Where the player physically stood. A single `Vector3` and a quaternion, or `Vector2` and a rotation for 2D.
- **The current level / map / scene.** A single identifier; everything else about the scene is loaded fresh.
- **Time-tracking values.** In-game day count, achievement timers. Real-world wall-clock playtime if the game reports it.

That is the entire run-state bucket. For a 40-hour RPG, it should fit in 50 KB of JSON or 15 KB of MessagePack. If your save is larger, something else got in by accident.

### 2.2 What goes out: anything reconstructible

The temptation, when implementing a save system, is to serialise *every node in the scene tree*. This works in a week-one prototype and breaks in week six when an engine update changes how a node serialises. The reconstructible items below should never be in the save:

- **Engine-internal state.** Render buffers. Audio mix levels (the meta bucket has the user's *settings*; the *current* mix is computed from settings). Physics broadphase indices.
- **Cached or computed values.** The character's *current* damage if it is derived from base damage + equipped weapon + active buffs; save the inputs, recompute the output.
- **Object references.** A pointer to a *specific instance* of a node. Save the *identity* — the node's ID — and look the instance up on load.
- **The currently loaded scene's geometry.** It is in the game build. Load it from the build.
- **Particle system state.** Particles in mid-flight are not progression. Drop them.
- **Animation playback positions.** The character is in an idle animation when you save? Load them in an idle animation. The frame within the idle does not matter.

The principle has a tidy name: *save the inputs, not the outputs*. Every game-engine save that has aged poorly aged poorly because it saved an output the developer later wanted to change the function of.

### 2.3 Meta state vs run state: the two-bucket model

Player-facing data splits cleanly into two buckets, and they want different storage:

| Bucket   | What is in it                                              | Write cadence              | Typical size | File suggestion          |
|----------|------------------------------------------------------------|----------------------------|--------------|--------------------------|
| **Meta** | Settings, key bindings, audio levels, accessibility flags, achievements, run history, total playtime, last-played-version | On settings panel close    | 1–5 KB       | `meta.json` (always JSON)|
| **Run**  | Active playthrough — character, inventory, world flags, position, scene ID | On save / autosave / checkpoint | 5–50 KB | `slot_0.save`, `slot_1.save`, ... |

The two buckets live in separate files for one reason: **failure isolation**. A corrupted run file should not delete the player's audio settings. A corrupted meta file should not delete their playthrough. Two files, two atomic writes, two independent integrity checks. The cost is twenty lines of code; the win is the difference between "I lost my settings" and "I lost my game."

The two buckets also write at different cadences. Meta writes only when the player closes the settings panel — once or twice per session. Run writes on every save event — many times per session. Different cadences mean different optimisation budgets; meta can afford to be a slow synchronous write, run cannot.

### 2.4 Slots and free saves

A *slot* is a named container for a run-state save. The game might expose ten slots (Final Fantasy style), three slots (modern AAA), or one slot per character (roguelike-ish).

A *free save* is the autosave that the game keeps independent of the slot system: typically one file, written on every autosave event, used for crash recovery and rapid-rewind.

The two interact as follows: a manual save writes to the chosen slot AND to the free-save file. An autosave writes only to the free-save file. On load, the game presents the slot list to the player and a "Continue" button that picks the free save.

The pattern keeps the slot count finite (so the UI is sane) while not losing autosave granularity (so the player who forgot to save manually does not lose an hour). Most modern games ship some version of it.

---

## 3. What should never be in a save file

A short, opinionated list of things that should not be in any save file regardless of the game.

### 3.1 Anything in the game build

The build is on disk already. Saving a copy of static data doubles the disk usage, doubles the parse time, and creates a synchronisation problem the day you patch the build. Save the *identity* of static data; look it up on load.

### 3.2 Engine objects in their entirety

Saving "a `Node`" in its entirety means saving the engine's internal layout of `Node`. The internal layout changes between engine versions; the save breaks. Save *what you, the game programmer, mean by the node*: its position, its state-machine state, its inventory. Not its `_internal_render_token`.

### 3.3 References to things that can be deleted

A save that contains `weapon_id = 0xDEADBEEF` and the weapon table no longer contains an entry for `0xDEADBEEF` is a broken save. Either commit to never deleting an ID once shipped, or design the loader to handle missing IDs gracefully (fall back to a sentinel item, log a warning, continue). The first is the safer policy; once an ID ships, it lives forever.

### 3.4 Anything the player can use to cheat in multiplayer

If the game has a multiplayer mode where saves are shared or progression matters competitively, the save is a *capability*: anything in it can be edited and re-loaded. Either move the cheat-sensitive state to a server-authoritative store (the right answer for any game with leaderboards or paid items) or accept that local saves are local and design the multiplayer around player-vs-player consent.

This is the only place this week where we mention the *signed save* pattern (HMAC-SHA-256 of the payload with a per-install key). It does not stop a determined cheater — the key is on the machine — but it stops casual save editors and the most common copy-a-friend's-save attack. The signed-save pattern is the topic of `challenges/challenge-01-hmac-signed-saves.md`.

### 3.5 Personally identifying information

Real names, email addresses, IP addresses, geographic coordinates from a GPS-equipped device. The save file is, in general, *not* encrypted on disk and *is* uploaded to cloud-save services. Anything in it is, at minimum, visible to anyone with file-system access. PII in a save file is a privacy bug.

The only PII-adjacent value most games legitimately need is a *user display name* (the player typed it in). Treat that name as ordinary string data, the same as a character name; do not separately associate it with an email or a real identity. If the game has accounts, the account ID is on a server, not in the save.

### 3.6 Anything that the player would object to losing if the file became corrupted

This is the corollary of the principle in 2.1. If the player would file a bug ticket on losing the value, it is *run* or *meta* state and goes into the appropriate bucket. If the player would not care, it is not save data; it is engine state. The line is the difference between a 50 KB save and a 50 MB save.

---

## 4. A concrete example: the cursor demo from Week 9

The Week 9 multiplayer-cursor demo persists very little. As a small worked example, the cursor demo's complete save manifest, in the two-bucket model:

**Meta bucket** (`meta.json`):

```json
{
  "version": 1,
  "settings": {
    "master_volume": 0.8,
    "music_volume": 0.6,
    "fullscreen": false
  },
  "last_used_player_name": "Player 1"
}
```

**Run bucket** (`slot_0.save`, but written as JSON for the dev build):

```json
{
  "version": 2,
  "player_name": "Player 1",
  "current_score": 1240,
  "session_start_timestamp": 1715000000,
  "highest_score_this_session": 1240,
  "current_level": "level_03"
}
```

The dev build serialises both as JSON. The shipped build serialises both as MessagePack. The schema migration from v1 to v2 added the `current_level` field; v1 saves loaded into the v2 codebase get a default `current_level = "level_01"`.

In Week 11's mini-project, you take this cursor demo (or a comparable prior-week game) and implement exactly this manifest.

---

## 5. Recap

We covered, in this lecture:

- The four save-point patterns (manual, autosave-on-transition, quicksave, checkpoint), with shipped examples and player-trust contracts.
- The implication of each pattern on write cadence and on whether the save needs to be off-thread.
- The two-bucket model (meta vs run) and its failure-isolation rationale.
- A six-item checklist of what should never be in a save file.
- A concrete two-file manifest for the cursor demo we will save in the mini-project.

Lecture 2 picks up the *format* question. Given that we know *what* to save and *when*, what bytes on disk should it become? JSON, MessagePack, Protobuf, Godot resources — each has a use case. And two formats we will refuse to use: pickle in Python and BinaryFormatter in .NET, both for the same reason.
