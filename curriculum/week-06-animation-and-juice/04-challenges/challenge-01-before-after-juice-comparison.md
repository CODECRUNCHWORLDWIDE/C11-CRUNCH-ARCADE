# Challenge 1 — Before/After Juice Comparison

**Time estimate:** ~90-120 minutes (setup, recording two takes, side-by-side edit, writing).

## Problem statement

Produce a *side-by-side before-and-after comparison video* of your Week-5 character (no juice) running alongside your Week-6 Exercise-3 character (full juice pass), performing the same input sequence. Then write a 200-word teardown that ranks the six juice tricks by perceived impact and identifies the one trick that was *noise* — i.e. that you could have left out and nobody would have noticed.

This is the canonical artefact of game-feel work. It is the format Jan Willem Nijman uses in *The Art of Screenshake* and Martin Jonasson and Petri Purho use in *Juice it or lose it*. Watching twenty seconds of side-by-side is worth a paragraph of "it feels better." Internalising the format now means you have the template forever.

You will produce three artefacts:

1. **One MP4 video** at `challenges/challenge-01/before-after.mp4`, 25-40 seconds long, side-by-side composition (two windows running simultaneously, or two clips composited spatially). Both sides perform the same input sequence: walk right, jump twice, fall, walk into a spike, recover, walk back. Label the left side "Week 5: bones" and the right side "Week 6: juice."
2. **A 200-word teardown** at `challenges/challenge-01/TEARDOWN.md` that:
   - Ranks the six juice tricks by perceived impact (1 = biggest impact, 6 = smallest).
   - Names the one trick that was noise.
   - Cites at least one tick from Nijman's *Screenshake* talk or Swink's *Game Feel* by name.
3. **A `manifest.json`** at `challenges/challenge-01/manifest.json` listing the six tricks, their default knobs, and the knob values you ended up shipping after tuning. This is the design artefact for future-you.

## Acceptance criteria

- [ ] A folder `challenges/challenge-01/` exists in your repo.
- [ ] `before-after.mp4` is committed (or, if file size is an issue, uploaded externally and linked from `TEARDOWN.md`).
- [ ] The video is **25-40 seconds**. Shorter than 25 and the player can't read the comparison. Longer than 40 and the audience checks out.
- [ ] The video is **side-by-side**, not before-then-after. The eye compares spatially better than temporally; both halves must be visible at once.
- [ ] **Both sides perform the same input sequence.** Same path, same jumps, same spike hit. If a viewer can't see the same inputs producing the same world-state with different *feel*, the comparison is invalid.
- [ ] Both sides are **labelled in-video**: "Week 5: bones" on the left; "Week 6: juice" on the right. Font readable at 720p; placement out of the way of the action.
- [ ] **`TEARDOWN.md` exists** and contains:
  - 200 words (give or take 25).
  - A ranked list of the six juice tricks (1 = biggest perceived impact, 6 = smallest).
  - The single trick that was *noise* — the one you'd cut from the pass if you had to ship at 20% effort.
  - A citation of Nijman's *Screenshake* talk or Swink's *Game Feel* by name.
  - A sentence on which tuning knob was the hardest to settle on, and why.
- [ ] **`manifest.json` exists** and contains an array of six entries. Each entry has `name`, `default_knob`, `shipped_knob`, and a 1-sentence `notes`. Example structure in the hints below.

## Suggested order of operations

Build incrementally. Each phase ends with a commit.

### Phase 1 — Stage the two runs (~15 min)

1. Take your Week-5 Exercise-2 (or your Week-5 mini-project, whichever is cleaner). Verify it runs. Move the player to (100, 348) at startup; this is the canonical start position.
2. Take your Week-6 Exercise-3. Verify it runs. Move the player to the same canonical start position. Verify all six juice tricks fire.
3. Decide on the input sequence. Suggested: walk right for 1 s, jump, walk right for 1 s, jump, walk into the spike at x=360, recover, jump, walk right past the second spike at x=540, jump over it, land, walk left back to start, jump, land. About 22 seconds. Practice it three times so the recording is clean.
4. Commit: `Stage canonical start positions; document input sequence.`

### Phase 2 — Record both runs (~20 min)

1. Open OBS Studio (download free at obsproject.com). Create a scene capturing the Pygame window.
2. Record the Week-5 run. One take. If you mess up, retake — but don't try to be perfect; one or two stumbles are fine if the *juice diff* is still clearly visible.
3. Quit Week-5; start Week-6 Exercise-3. Record the same input sequence on it. One take.
4. Save both files as `week05-take.mp4` and `week06-take.mp4`.
5. Commit: `Record both takes.`

### Phase 3 — Side-by-side composition (~25 min)

1. Open DaVinci Resolve (or Shotcut, or any free editor that supports side-by-side composition).
2. Place `week05-take.mp4` on the left half of the timeline; `week06-take.mp4` on the right half. Scale each to 50% horizontal so both fit at the original aspect ratio.
3. Align the start of jump 1 on both clips. Use the SPACE-keypress sound (or a visual cue like the player's first jump-launch frame) as the sync point.
4. Add two text overlays: "Week 5: bones" (left, top-left corner) and "Week 6: juice" (right, top-left corner of the right half).
5. Export at 1080p or 720p, H.264, ≤ 25 MB. Name it `before-after.mp4`.
6. Commit: `Side-by-side comparison edit complete.`

### Phase 4 — Write the teardown (~25 min)

1. Watch the side-by-side video three times. Each pass, note in a draft document which juice trick stood out. Don't analyse yet — react.
2. After three passes, rank the six tricks by perceived impact. Yours might disagree with the canonical ranking (most students rank screen-shake-on-land as #1; some rank squash-and-stretch as #1; both are defensible).
3. Identify the noise trick. Be honest. Most students find that *one* of the six was redundant in their tuning. Naming it is the engineering work.
4. Write the 200 words. Use the structure: paragraph 1 (ranking), paragraph 2 (noise trick + justification), paragraph 3 (the hardest knob to tune + the value you settled on). Cite Nijman or Swink by name.
5. Commit: `Add TEARDOWN.md.`

### Phase 5 — manifest.json + final commit (~15 min)

1. Write `manifest.json`. Six entries, one per trick. Example structure in the hints.
2. Final commit: `Add manifest.json; comparison complete.`
3. Verify the repo: `before-after.mp4` is committed (or linked), `TEARDOWN.md` is 200 words, `manifest.json` is valid JSON.

## Hints

<details>
<summary>How do I record two takes with the same input sequence?</summary>

Two options. One: practice the sequence five times before you hit record so muscle memory carries you through both takes. Two: use a simple input recorder. The cleanest no-dependency version is to copy your Exercise-3 main loop and add a `recorded_inputs.json` log that captures every keypress's frame number; load the same log into the Week-5 version and replay it deterministically. The second option is engineering you don't have time for in a 90-minute challenge; the first is what 90% of students do.

If your two takes diverge slightly (one jump goes a frame higher), the comparison is *still valid* as long as the same six events fire on both sides. The viewer is comparing feel, not pixel positions.

</details>

<details>
<summary>What does manifest.json look like?</summary>

```json
[
  {
    "name": "squash_and_stretch",
    "default_knob": {"from": 0.65, "to": 1.0, "dur": 0.20, "ease": "ease_out_back"},
    "shipped_knob": {"from": 0.70, "to": 1.0, "dur": 0.18, "ease": "ease_out_back"},
    "notes": "Lowered the squash from 0.65 -> 0.70 because the cartoonier flatten distracted from the FSM transitions."
  },
  {
    "name": "screen_shake_land",
    "default_knob": {"amp": 4.0, "dur": 0.10},
    "shipped_knob": {"amp": 5.0, "dur": 0.08},
    "notes": "Raised amplitude, shortened duration. Made landings feel impactful without losing screen-readability."
  },
  {"name": "particles_dust_land", "default_knob": {"count": 8}, "shipped_knob": {"count": 10}, "notes": "..."},
  {"name": "particles_footstep", "default_knob": {"count": 3}, "shipped_knob": {"count": 2}, "notes": "..."},
  {"name": "particles_hit", "default_knob": {"count": 12}, "shipped_knob": {"count": 14}, "notes": "..."},
  {"name": "hit_flash", "default_knob": {"dur": 0.08, "color": "white"}, "shipped_knob": {"dur": 0.10, "color": "white"}, "notes": "..."}
]
```

Six entries, hand-written, version-controlled. Future-you will look at it and remember the tuning *thinking*, not just the values.

</details>

<details>
<summary>What if my video is over 25 MB after export?</summary>

Two options. One: drop the export bit-rate. 720p at 2 Mbps H.264 is ~3 MB for 30 seconds; entirely sufficient for a portfolio piece. Two: upload externally to YouTube as unlisted and link from `TEARDOWN.md`. Either works for the rubric.

</details>

<details>
<summary>How do I rank the tricks without bias?</summary>

The honest method: watch the side-by-side with the audio MUTED, three times. Rank by visual impact alone. Then watch with audio. The audio cues (jump SFX, land thud, hit) almost always shift the ranking, because audio is *cheap juice* with a huge payoff. Most students discover that the SFX cues outrank one of the visual tricks they thought was important. That's a real finding; report it.

</details>

<details>
<summary>Is "the noise trick" always the same one?</summary>

No. Different students at different tuning settings will identify different tricks. The most common candidates: the footstep particles (often too subtle to notice), the hit-flash (overshadowed by the screen-shake + particles), the squash-and-stretch (if the duration is too short to read). The point is not to *find the canonical noise trick* — it is to *identify which one in your project was noise*. Honesty is the engineering skill.

</details>

## What "great" looks like

A reviewer who has never seen your project sits down. They open the README, click the side-by-side video. Twenty-five seconds in, they grin — the diff is unmistakable. They read the teardown: the six tricks are ranked, the noise trick is identified, Nijman is cited. They open `manifest.json`: six entries, each with a sentence of design history. Five minutes later they say "okay, this is a portfolio piece" and they screenshot the side-by-side for their own internal review deck. That is the artefact this challenge is shaped to produce. The video is forty seconds of viewing time; the discipline of producing it carries the rest of the course.
