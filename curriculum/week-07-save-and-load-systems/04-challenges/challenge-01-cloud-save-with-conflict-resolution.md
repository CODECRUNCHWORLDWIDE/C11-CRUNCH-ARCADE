# Challenge 1 — Cloud Save with Conflict Resolution

> **Format:** Paper design only. No code. ~2 hours.
> **Deliverable:** A 600-800 word `cloud-save-design.md` plus a sequence diagram (hand-drawn photo or any tool).
> **Estimated time:** 2 hours.

This challenge is a *design exercise*. You will not implement a cloud save this week — the plumbing belongs to a Week-17 stretch topic — but you will *design* the protocol on paper, defend the design against three concrete failure modes, and pick one of three conflict-resolution strategies with reasoning.

Cloud saves are the most-shipped, most-broken feature in indie games. Steam Cloud, GOG Galaxy, and Apple iCloud each provide the *transport*; the *protocol* — what to sync, when to sync, and how to resolve conflicts — is the developer's responsibility. Most indie cloud saves fail in one of three places, and you will name all three by the end of this challenge.

## The setup

You ship a single-player RPG on Steam. The player plays on a laptop and a desktop. Steam Cloud syncs the save folder between the two machines whenever the game launches or quits. Your save folder is the one from this week's mini-project:

```
saves/
├── slot1.json
├── slot1.json.bak
├── slot1.json.sha256
├── slot2.json
├── slot2.json.bak
├── slot2.json.sha256
├── slot3.json
├── slot3.json.bak
├── slot3.json.sha256
├── autosave.json
├── autosave.json.bak
└── autosave.json.sha256
```

## The three failure modes

Your protocol must handle each of these. Write a paragraph per failure mode explaining how your design handles it, with the *exact sequence of events* between the two machines.

### Failure A — Concurrent edits

Player plays on the laptop for an hour, saves to slot 1, quits. Steam Cloud syncs the laptop save up.

Meanwhile, the desktop has been *offline* the whole time. Player walks over to the desktop, opens the game *before* Steam Cloud has had a chance to sync down, and plays for another hour on slot 1 (overwriting the *desktop's* older version). They save and quit.

Steam Cloud now sees two versions of `slot1.json` — one from the laptop, one from the desktop — both newer than the last synced version. **Which one wins?**

### Failure B — Save during sync

Player is on the laptop. Steam Cloud starts a download in the background. Halfway through replacing `slot1.json` with the cloud version, the player presses Save in-game. The game writes its own version of `slot1.json`. Steam Cloud finishes its download a moment later and overwrites the *just-written* save with the cloud version.

The player loses the save they just made and does not know it. **How does your protocol prevent this?**

### Failure C — Cross-version corruption

Player plays v1 of your game on the desktop, saves a v1 file, quits. Cloud syncs.

Player later updates the desktop to v2 of your game, plays for two hours, saves a v2 file. Cloud syncs.

Player walks to the laptop, which has *not* been updated. The laptop is still on v1. Steam Cloud syncs the v2 save *down to the v1 game*. The v1 game tries to load the v2 save. **What happens, and how does your protocol gracefully handle it?**

## The three conflict-resolution strategies

Pick *one* and defend it. The other two should be discussed and ruled out with one paragraph each.

### Strategy 1 — Last-write-wins

The save with the most recent `timestamp_iso` wins. Older save is discarded.

**Pros:** trivial to implement. One line of comparison logic. No UI required.
**Cons:** the older save's progress is *gone*. If the player saved a major milestone on the desktop two days ago and then briefly opened the game on the laptop yesterday (advancing nothing but updating the timestamp on `autosave.json`), the laptop's stale autosave can overwrite the desktop's milestone.

### Strategy 2 — Newest-by-content (vector clocks)

Each save carries a *vector clock* — a small `{laptop: 12, desktop: 9}` counter that increments on each machine independently. Two saves are concurrent if neither's vector dominates the other's. On conflict, the user is prompted: "we found two saves; pick one."

**Pros:** detects *true* concurrent edits and prompts the user instead of silently dropping data. Correct for the failure-A scenario.
**Cons:** the UX is heavier. The user must understand "you have two saves" and make a choice. Most users do not understand vector clocks (and should not have to).

### Strategy 3 — Three-way merge

Each save carries a `parent_save_id` pointing to the save it descended from. On conflict, the protocol locates the common ancestor and tries to merge the two divergent saves field-by-field. Inventory adds, flags OR together, hp prefers the maximum, position prefers the most-recently-edited save.

**Pros:** the user never sees a conflict UI; the system just merges.
**Cons:** *very* easy to get wrong. The "merge" semantics for an inventory are not obvious — does picking up a sword on the desktop and selling a sword on the laptop result in zero swords or one? The complexity is *enormous*; the bug surface is enormous.

## What to deliver

A markdown file `cloud-save-design.md` at the root of your Week-7 repo (or in `challenges/`), containing:

1. **A title and your handle.**
2. **The chosen strategy** (one of 1, 2, or 3) with a one-paragraph defence.
3. **The two strategies you did NOT choose**, with one paragraph each explaining why.
4. **Failure-mode walkthroughs.** Three paragraphs, one per failure mode (A, B, C), naming the sequence of events your protocol produces and the final state on disk.
5. **A sequence diagram** — pen-and-paper photo, [draw.io](https://draw.io), [excalidraw.com](https://excalidraw.com), or any whiteboard — for failure mode A. The diagram shows two timelines (laptop, desktop) with the Steam Cloud middle channel and the save reads/writes.
6. **One paragraph on what you would still need to implement** (locking? a "uploading..." UI? offline-mode behaviour?) if you were actually shipping this.

Word count: 600-800 words excluding code blocks and the diagram caption. Aim for prose density, not length.

## Acceptance criteria

- [ ] `cloud-save-design.md` exists at the agreed path.
- [ ] The chosen strategy is named and defended in one paragraph.
- [ ] The two rejected strategies each get a paragraph of "why not."
- [ ] All three failure modes (A, B, C) are walked through in detail.
- [ ] A sequence diagram for failure mode A is included (image or link).
- [ ] Total length is 600-800 words.
- [ ] The document cites *at least one* of the resources from `resources.md` — typically Gaffer On Games or one of the Godot/Steam Cloud docs.

## Hints

- Most shipping indie games use **last-write-wins** (Strategy 1) and accept the data-loss risk. This is *correct for most indie projects* — the engineering hours to do better are better spent on game design. If you choose this, defend it on those grounds.
- *Stardew Valley*, *Hollow Knight*, and *Celeste* all use Strategy 1 with a "last-played date" timestamp shown in the slot UI so the player can see *which* save just synced.
- Failure mode B (save during sync) is solved by either (a) **only syncing on launch/quit, never mid-session**, which most Steam-integrated games do, or (b) **a file lock** that the game holds while writing. Steam Cloud does (a).
- Failure mode C (cross-version) is solved by your *migration ladder from Lecture 3*. If your v1 game tries to load a v2 save, the migration framework should detect the unknown version and refuse to load, falling back to `.bak` or the local autosave. This connects this challenge directly to the lecture material.
- The Steam Cloud docs are not free in the technical-protocol sense (Steam is closed-source), but Valve's Steamworks developer documentation is freely readable: <https://partner.steamgames.com/doc/features/cloud>. You may cite it.

## Why this matters

The save bugs you read about in indie post-mortems — the *Hollow Knight* save-corruption thread, the *Stardew Valley* multi-day sync confusion, the *Celeste* "I lost my speedrun" reports — are almost all variations of failure modes A, B, and C above. You are not going to solve these definitively. You *are* going to internalise that "cloud sync" is a *protocol design problem*, not a "Steam handles it" problem, and bring that vocabulary forward into Week 17 if/when you actually wire one up.

The discipline this challenge teaches is **defensive design under uncertainty**. Save systems are the place where uncertainty is highest (network, two machines, varying versions, varying user actions) and the cost of a bug is highest (a player loses irreplaceable progress and never opens your game again). Designing on paper *before* writing code is the only way through.

---

*Submit your `cloud-save-design.md` as part of your Week-7 push. The mini-project does not require this challenge; it is an independent design artefact.*
