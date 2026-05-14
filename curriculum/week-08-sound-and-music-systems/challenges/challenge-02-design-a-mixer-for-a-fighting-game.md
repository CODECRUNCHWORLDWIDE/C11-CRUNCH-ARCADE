# Challenge 2 — Design a Mixer for a Fighting Game

> **Format:** Paper design only. No code. ~2 hours.
> **Deliverable:** A 600-900 word `mixer-design.md` plus a bus-tree diagram (hand-drawn photo or any tool).
> **Estimated time:** 2 hours.

This challenge is a *design exercise*. You will not implement the mixer in code — Lecture 2 already shows you how — but you will *design* the bus topology for a complete fighting game, defend the design against three concrete mix scenarios, and write the ducking rules in pseudocode. The pedagogy is in the audit, not the implementation.

Fighting games have the densest audio in any genre. Two characters, each with ~40 unique attack sounds. A constantly-playing dramatic music track. Crowd-noise ambient layer. Round-bell and commentary voice-over. A menu pause that needs its own UI sound bus. Pop the lid on a typical fighting-game mix and you find six to ten buses with deliberate routing.

You will design the bus tree and the ducking rules for a fictional fighting game called *Crunch Combat*.

## The setup

*Crunch Combat* has the following sound categories:

1. **Background music.** One 3-minute looping track per stage. Always playing at moderate volume.
2. **Crowd ambient.** A continuous murmur/cheer loop layered under the music. Quieter than music. Lights up during big moments.
3. **Character SFX.** Per-attack hit sounds, voice grunts, footsteps, jumps, blocks. Two characters, ~40 SFX each.
4. **Impact emphasis.** A "boom" or low-frequency thump on big hits. Distinct from per-attack SFX because it is *post-hit emphasis*, mixed louder, often pitch-shifted by hit strength.
5. **Round announcer.** A voice line ("ROUND ONE / FIGHT / K.O.") that plays at round transitions. Loudest thing on screen when it fires.
6. **Commentary voice-over.** Optional. Plays opinionated commentary during fights at random intervals. ~15 different lines per fight.
7. **UI sounds.** Menu hover, button click, modal pop, settings adjust. Plays in menus and the pause screen.
8. **Cinematic intro.** Pre-fight character intros (~5 seconds). Has its own music and SFX.

Your task: design a bus tree that lets the player mute or independently adjust the *important* categories, and write the ducking rules for the *interactions* between categories.

## Part A — Design the bus tree (40 min, ~250 words)

In your `mixer-design.md`, draw the bus tree with these properties:

- **Root:** master.
- **Leaves:** every distinct sound category that the player should be able to slider independently.
- **Depth:** 2 or 3 levels. Use a third level only when you need to slide an *intermediate group* (e.g. "all character sound" rather than "footsteps only").

Constraints:

- Every sound category from the eight above must route through *some* leaf bus.
- The player must be able to mute music while keeping SFX. Standard.
- The player must be able to mute the *commentary voice-over* without losing the round announcer. Critical — players hate forced commentary.
- The player must be able to silence the *crowd* without losing music. The crowd can become grating in long sessions.

For each bus, write one line: name, default volume, default mute state, parent bus.

## Part B — The three mix scenarios (60 min, ~400 words)

For each scenario, write a paragraph (~120 words each) explaining what the mix sounds like and which buses are doing what.

### Scenario 1 — Mid-round, big hit lands

The combatants are mid-fight. The music plays at normal volume. The crowd is at ambient murmur level. Player A lands a heavy attack on Player B. Three sounds fire simultaneously: a high-frequency *hit* SFX, a low-frequency *impact emphasis*, and Player B's *grunt* voice line.

Questions to answer:

- Which bus does each sound route through?
- Are any sounds ducked by any others?
- What is the relative volume of the three sounds in the mix?
- If the player is moving fast, are SFX still loud enough to feel like impact?

### Scenario 2 — Round transition

The round timer expires. The announcer fires "ROUND TWO!" — this is the loudest moment in the game. The crowd erupts (the ambient layer briefly raises). Music ducks under the announcer.

Questions to answer:

- Which buses duck while the announcer plays?
- How much do they duck (in dB or linear)?
- Does the crowd's "erupt" event ride above its own bus volume, or is the crowd bus itself raised?
- Does the round announcer's bus return to its previous level after the line ends, or does it remain elevated for a while?

### Scenario 3 — Player opens the pause menu

The player presses pause mid-fight. The combat-fight visual freezes; the audio behaviour is a *design choice*.

Questions to answer:

- Does the music keep playing or pause?
- Does the crowd keep playing or pause?
- Do UI sounds (menu hover, button click) play through the *pause* or are they audible at all?
- What ducks while the menu is open?

There is no single correct answer; defend yours.

## Part C — Ducking rules in pseudocode (40 min, ~200 words)

Write the ducking rules as pseudocode. A duck rule has the shape:

```
WHEN <sound on bus X> starts:
    duck bus Y by Z dB over T ms
WHEN <sound on bus X> ends:
    restore bus Y by Z dB over T ms
```

You must write rules for at least these interactions:

1. **Round announcer ducks music.** How much? How fast?
2. **Round announcer ducks commentary.** How much? How fast?
3. **Round announcer ducks crowd?** Yes/no — defend your choice.
4. **Character voice ducks music.** During grunts/shouts, ducking would be excessive (40 per fight); you may choose to *not* duck on character voice. Defend it.
5. **Commentary voice ducks music.** How much? How does it interact with the existing announcer duck?
6. **UI sounds duck anything?** Usually no. Defend.

The pseudocode does not need to be runnable; the *rules* are the artefact.

## Part D — Optional stretches (in your bonus time)

These are not required for acceptance; do them if you finish Parts A-C early.

- **Add an accessibility layer.** "Reduce sudden volume changes" toggle that makes the round-announcer duck less aggressive. Specify the numeric difference.
- **Add a "training mode" mix.** Music quieter, SFX louder, commentary off. Specify the volume offsets per bus.
- **Add a "spectator mode" mix.** Crowd louder, music quieter, commentary on. Specify the offsets.
- **Spec a sidechain compressor on the music bus.** Modern audio middleware (Wwise, FMOD) uses sidechain ducks more nuanced than the on/off pattern. Sketch what it would look like.

## Acceptance criteria

- [ ] A file `mixer-design.md` exists at the challenge's `loop-authoring/` (or your week-08 working folder).
- [ ] Part A produces a bus tree with at least six leaves and a sensible depth-2 or depth-3 structure.
- [ ] Part B answers all three scenarios with concrete bus names and volume reasoning.
- [ ] Part C writes ducking rules in pseudocode for all six interactions (1-6 above).
- [ ] The total word count is 600-900 words. Shorter does not show the work; longer is padding.
- [ ] At least one diagram of the bus tree is included as `bus-tree.png` or inline ASCII art.
- [ ] The reasoning cites either Lecture 2 (*Mixing, buses, and dynamic music*) or the *AudioServer* tutorial by name at least twice.

## Worked partial example (do not copy literally)

Here is what *one corner* of the design might look like. Use as a structural template; do not lift the content.

### Bus tree (excerpt)

```
master                vol 0.80
├── music             vol 0.60
│   ├── stage         vol 1.00
│   └── intro         vol 0.90
├── ambient
│   └── crowd         vol 0.40
├── sfx
│   ├── character     vol 1.00
│   └── impact        vol 0.85
├── voice
│   ├── announcer     vol 1.00
│   ├── commentary    vol 0.85
│   └── grunt         vol 0.80
└── ui                vol 0.70
```

### Scenario 1 excerpt

The hit SFX routes through `sfx.character`. The impact emphasis routes through `sfx.impact`. The grunt routes through `voice.grunt`. The mix is dominated by the impact (loudest because it carries the most low-frequency energy), with the hit SFX riding 6 dB above the impact in the high frequencies, and the grunt cutting through both because the human ear preferentially attends to voice frequencies. No ducking fires; the three sounds are short (<200 ms) and the duck-fade times would last longer than the sound itself.

### Pseudocode excerpt

```
WHEN announcer starts:
    duck music    by -12 dB over 300 ms
    duck commentary by -24 dB over 100 ms   # hard duck; commentary mustn't compete
WHEN announcer ends:
    restore music     to default over 600 ms
    restore commentary to default over 600 ms
```

The asymmetric fade times (100 ms duck-down, 600 ms duck-up) are deliberate: the duck-down is fast because the announcer must cut through immediately; the duck-up is slow because returning to full music abruptly after the announcer feels jarring.

---

## Why this matters

Designing the bus tree *before* writing code is the discipline that separates a one-bus "everything is the same volume" mix from a shippable game. The fighting-game scenario is the dense end of the design space; doing it on paper for a fictional fighting game makes the simpler trees you will design for the mini-project and Week-11 capstone obvious by comparison.

The pseudocode rules are the same shape your eventual `audio.py` will hold. The act of writing them in English first — naming the buses, picking the dB numbers, choosing fast-down/slow-up asymmetry — is the design work that the code expresses.

---

## References

- **Lecture 2 — *Mixing, buses, and dynamic music*.** Three-bus design, ducking, layered music. `../lecture-notes/02-mixing-buses-and-dynamic-music.md`
- **Lecture 3 §5 — *The Godot 4.x AudioServer bridge*.** The bus topology you design here ports to Godot's editor-driven bus panel almost directly. `../lecture-notes/03-authoring-loops-formats-and-the-godot-bridge.md`
- **Godot — *Audio buses* tutorial.** The editor-driven equivalent. <https://docs.godotengine.org/en/stable/tutorials/audio/audio_buses.html>
- **Wikipedia — *Sidechain compression*.** Industry-standard explanation of the ducking pattern. <https://en.wikipedia.org/wiki/Dynamic_range_compression#Side-chaining>

---

*If you find errors in this challenge, please open an issue.*
