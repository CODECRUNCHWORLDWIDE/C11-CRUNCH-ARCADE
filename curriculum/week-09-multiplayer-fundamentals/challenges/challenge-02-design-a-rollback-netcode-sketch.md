# Challenge 2 — Design a Rollback Netcode Sketch

> **Format:** Paper-design exercise (no code). ~2 hours including reading.
> **Deliverable:** A `rollback-sketch.md` containing your written design plus one hand-drawn or whiteboarded data-flow diagram.
> **Estimated time:** 2 hours.

This challenge is the design counterpart to Lecture 2 §4-5 (prediction and reconciliation). You will *not* implement rollback netcode this week — it is the most sophisticated multiplayer technique in indie game development, and a real implementation is a multi-week project on its own. Instead, you will read enough about it to *design* one on paper, for a hypothetical two-player fighting game, and write up the design at the level of detail you would need to start coding.

The exercise is calibrated to leave you with two things:
1. A clear understanding of how rollback differs from the snapshot-interpolation model we built this week.
2. A design document you could hand to a (hypothetical) collaborator and they could turn into code.

## The setup

You will need:

- ~45 minutes of reading time. The three required sources are below.
- A blank document, pen and paper (or a digital whiteboard), and 90 minutes of design time.
- Your Week 9 Lecture 2 notes open for reference.

### Required reading

- **GGPO — *What is Rollback Netcode?* (free, ggpo.net).** The founding article on rollback by Tony Cannon. Read in full. ~10 minutes.
  <https://www.ggpo.net/>
- **Skullgirls — *Skullgirls' Netcode* by Mike Z (free).** A first-hand account from the developer of a critically-acclaimed fighting game's rollback implementation. Search for the post on the developer's site or YouTube. ~20 minutes.
  <https://www.youtube.com/results?search_query=skullgirls+netcode+mike+z>
- **Infil — *A guide to fighting-game netcode* (free).** The community-canonical write-up for non-developers. Skim for the vocabulary. ~15 minutes.
  <https://words.infil.net/w02-netcode.html>

Plus the relevant section in Week 9 Lecture 2:

- Lecture 2 §4 — Client-side prediction.
- Lecture 2 §5 — Server reconciliation.
- Lecture 2 §6 — Lag compensation (mentioned).

## What rollback is, in two paragraphs

The snapshot-interpolation model we build this week renders the world ~100 ms *in the past*. For fighting games — where moves complete in 4-6 frames at 60 fps (~70-100 ms) — that delay is catastrophic. A 100 ms input delay means most attacks land *before* the defender's reaction is processed by the server.

Rollback flips the trade: every peer runs the *full* simulation locally, with the inputs *they currently believe* every other peer is doing (typically, "the other peer is still pressing whatever they were pressing last frame"). When real inputs arrive (a few frames late, over UDP), the local simulation *rewinds* to the last frame where everyone's inputs were known, re-applies the corrected inputs, and re-simulates forward to the current frame. The visible result: nearly-zero input delay for the local player, with occasional "snaps" when a remote player did something unexpected.

This is *very different* from authoritative-server with prediction. Rollback typically runs *peer-to-peer with deterministic simulation* (the lockstep model from Lecture 1 §1.3, but with rollback added to hide latency). There is no authoritative server. Both peers' simulations are identical because the simulation is deterministic and they both run the same input stream.

## The hypothetical game

You are designing for **CrunchBrawl**, a two-player 2D fighter modelled after early-2000s Capcom fighters:

- 60 Hz simulation tick. Each match round is 99 seconds (~5940 frames).
- Inputs: 8-directional stick + 4 buttons (LP, MP, HP, K). 12 bits per player per frame.
- Two players exactly. Best-of-three rounds.
- Target audience: competitive online play across a continent. RTT 50-150 ms is the design centre.
- Deterministic integer simulation. No floating-point math in the gameplay code.

## The design questions (answer each)

### 1. Frame buffering and rollback window

How many frames of "rollback room" does CrunchBrawl reserve?

- Define `MAX_ROLLBACK_FRAMES` (a small integer, typically 6-10).
- Justify the number: at 60 Hz, `MAX_ROLLBACK_FRAMES = 8` covers up to 133 ms of RTT.
- What does the game do if the other peer's inputs arrive more than `MAX_ROLLBACK_FRAMES` late? (Hint: this is the "freeze" / "wait" branch. Most rollback games freeze briefly.)

Write 100-200 words. Include the formula `MAX_ROLLBACK_FRAMES x (1000 / TICK_HZ) = max latency hidden`.

### 2. Input serialisation

What does CrunchBrawl send over UDP each frame?

- Define the input packet structure. Suggested: `(player_id, frame_number, 12_bit_input)`. Compute the byte size.
- Send rate: every frame (60 Hz), every other frame (30 Hz), or sub-sampled?
- Reliability: are inputs sent with ACKs (reliable-over-UDP), or sent at high redundancy (each packet contains the last *N* frames of input)? Most production rollback uses the latter — explain why.

Write 100-200 words. Show the packet structure as a struct-style diagram (similar to the UDP header diagram in Lecture 1 §4).

### 3. Determinism

What does CrunchBrawl have to do *in its simulation code* to be safely rollback-compatible?

- List four things that *break* determinism if used naively:
  - Floating-point math across compilers.
  - Iteration order over hash maps with random salt.
  - System-time-seeded RNG.
  - Frame-rate-dependent logic (`dt`-based motion).
- For each, name the fix. (Integer fixed-point math; ordered dicts or sorted iteration; explicit seed-and-advance; fixed-timestep simulation.)

Write 100-200 words. This is the section that tells you whether your engine can ever go rollback at all.

### 4. State save and restore

How does CrunchBrawl save and restore frame state?

- Define `FrameState` — every byte of simulation state that affects future frames. List the fields (positions, velocities, animation frame indices, hp, stamina, projectile list, RNG state, ...).
- Size estimate. For a typical 2D fighter, `FrameState` is 4-16 kB.
- Where the buffer lives. Ring buffer of length `MAX_ROLLBACK_FRAMES + 1`, indexed by `frame_number & (BUFFER_LEN - 1)`.
- Restore cost. A `memcpy`-equivalent into the live state. ~10 microseconds.

Write 100-200 words. Include a diagram showing the ring buffer as a circular array with the "current" frame and the "oldest savable" frame marked.

### 5. The rollback loop

Walk through one rollback event step by step.

The setup: at local frame `F`, your local player has just done frame `F-3`'s input as "right". The remote player's input for frame `F-3` arrives now, and it is "left" (you had been predicting "neutral" for them).

Write the sequence of steps the game runs *this frame*. Number them. Aim for 6-10 steps, ending in "render frame `F`."

A correct sketch is roughly:

1. Receive remote's `F-3` input from UDP. Compare to predicted: mismatch.
2. Locate the saved `FrameState` at `F-3` (one before the mismatch).
3. Restore the simulation to that saved state.
4. Re-apply the correct remote input plus the local inputs `F-3, F-2, F-1` (now all known).
5. Re-simulate frames `F-3, F-2, F-1, F` (four ticks of game logic).
6. Save the new `FrameState` for frame `F`.
7. Render frame `F`.

The whole rollback happens in *one render-frame's budget*. At 60 Hz that is 16.6 ms; rollback of 4 frames should cost ~2-5 ms on a modern CPU.

Write this section as numbered steps, then 100 words of prose explaining what the player *sees*.

### 6. Comparison to this week's snapshot model

In ~150 words, contrast rollback netcode (your CrunchBrawl design) with the authoritative-server snapshot model we built in Weeks 9 Exercises 2-3. Touch on:

- Which model has the server? (Snapshot does; rollback typically does not — both peers run the simulation.)
- Which has zero input lag for the local player? (Rollback. Snapshot needs prediction-plus-reconciliation, which we didn't implement this week.)
- Which is more vulnerable to a malicious client? (Rollback. Each peer is its own simulation; cheating is bounded by the determinism of the engine, which a cheater can subvert.)
- Which fits CrunchBrawl better and why? (Rollback. The genre is competitive 1v1; low input lag is more important than cheating prevention — competitive fighting games rely on anti-cheat in other layers.)

### 7. The data-flow diagram

On paper or a whiteboard, draw a one-page diagram showing:

- The two peers as boxes.
- The input packet flow between them (arrow, frame numbers labelled).
- The simulation ring buffer inside each peer (8 cells, labelled with frame numbers).
- The "current frame" pointer.
- The "rollback boundary" pointer (oldest frame still mutable).
- The local input source (controller icon).

Photograph or scan the diagram. Save as `rollback-sketch-dataflow.png` in your repo. The diagram should be legible at thumbnail size; spend the time on neatness.

## Acceptance criteria

- [ ] A file `rollback-sketch.md` exists in your Week 9 repo (or `homework/challenge-02/`).
- [ ] All six numbered sections are answered. Word counts are within ~25% of the targets.
- [ ] At least one `rollback-sketch-*.png` data-flow diagram is committed.
- [ ] The write-up cites Lecture 2 §4 (prediction) and §5 (reconciliation) by name.
- [ ] The write-up cites at least one of the three required external sources (GGPO, Skullgirls/Mike Z, Infil).
- [ ] The packet-size estimate in §2 is shown as a computation, not just a number.
- [ ] The `FrameState` size estimate in §4 is shown as a sum of named fields.

## What this challenge prepares you for

If you ever build a fighting game, a Bomberman-style synced game, a multiplayer puzzler with frame-precise inputs, or *any* genre where 100 ms of input delay is unacceptable — you will need rollback. The implementation effort is real (the GGPO library exists exactly because writing one from scratch is hard). The *design* is what you can do in two hours, and the design is what catches the engine-determinism problems early enough to fix.

## Stretch (optional)

If you finish the paper design and have time:

- Read the **GGPO source code** (open source on GitHub). It is C and ~3000 lines. Identify which lines correspond to which step in your §5 walkthrough.
- Watch a **competitive fighting-game stream on Twitch** and try to spot rollback "snaps" — the moments where the screen briefly jumps because a prediction was wrong. They are rare on good connections; they are visible on bad ones.
- Read the **Unreal Engine GAS prediction documentation**. The Gameplay Ability System has its own prediction model that is closer to rollback than to authoritative-server snapshotting. The vocabulary is different but the patterns are familiar.

Bring `rollback-sketch.md` to the Friday review session.
