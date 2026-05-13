# Challenge 1 — Juice-Comparison Video

**Time estimate:** ~120 minutes (record, edit, write-up).

## Problem statement

Capture a 30-second side-by-side "before juice / after juice" video of your Week 2 brick-breaker. Both clips show the same gameplay sequence at the same window size with audio. Stack them horizontally (preferred) or stack them vertically. Add minimal labels: "before" on the left, "after" on the right. Publish it.

This is the single most-replicated game-feel demo on the internet, and for good reason — the side-by-side does an enormous amount of work that words cannot. If you have built three juice touches in your mini-project but you cannot *show the difference*, you can't argue for the value of what you built. The video is the argument.

You will produce three artefacts:

1. A 30-second comparison video (`.mp4` or `.webm`, ≤ 50 MB).
2. The "before" build of your game preserved as a separate Git tag or branch (`pre-juice`).
3. A 200-word written write-up in `challenges/challenge-01/WRITEUP.md` using vocabulary from Lectures 1 and 2 to explain what the viewer is seeing.

The write-up is what graduates this from "neat clip" to "design artefact."

## Acceptance criteria

- [ ] A `.mp4` or `.webm` file in your portfolio repo at `challenges/challenge-01/comparison.mp4` (or `.webm`). ≤ 50 MB total. If larger, host externally (YouTube/Vimeo/Imgur) and link from `WRITEUP.md`.
- [ ] The clip is **between 25 and 40 seconds long.** Anything shorter is not enough to evaluate; anything longer loses the viewer.
- [ ] Both halves of the video play **simultaneously** and show **the same gameplay sequence** (same paddle motion, same ball trajectory, same brick destructions, ideally same final score). You'll need to either play it twice and hand-sync, or use the same recording but with juice toggled by a feature flag at build time. (Either is fine; the second is harder but cleaner.)
- [ ] Audio is preserved in the "after" half. The "before" half can be muted or silent.
- [ ] Minimal labels: "before" and "after" overlaid on the appropriate half. Font and colour clearly readable.
- [ ] A Git tag or branch `pre-juice` exists in your brick-breaker repo, pointing to the commit where the juice has not yet been added. (This proves the "before" is real, not faked.)
- [ ] A 200-word write-up at `challenges/challenge-01/WRITEUP.md` that:
  - Names at least three specific juice techniques present in the "after" clip.
  - Uses at least two terms from Lecture 2 (Church's four lenses OR MDA's three layers) correctly.
  - States what aesthetic (per the eight aesthetics in Lecture 2 §3.3) the juiced version more clearly delivers.
  - Cites Steve Swink at least once.
  - Does NOT say "feels better" without naming what feels better.
- [ ] The video file is committed AND the repo's `README.md` links to it from the root.

## Stretch (any of these for extra polish)

- **An A/B player.** Build a single web page (a single HTML file with two `<video>` elements is fine) where the viewer can swap between A and B with a key. This is the format Vlambeer uses for their game-feel showcases.
- **A frame-by-frame walkthrough.** Pick the moment of one brick destruction. Export 5 frames from the "before" clip and 5 from the "after." Annotate each pair with what's changed visually. 1-2 paragraphs. Add to `WRITEUP.md`.
- **A second comparison: tuning.** Add a third clip showing your *over-juiced* version (every effect cranked to 3x). The "too much" version is often more instructive than the "before."
- **Capture a tester's reaction.** Sit one person down, show them "before," then "after." Record their voice (with permission). Embed the 10-second clip in `WRITEUP.md`. This is real playtest data.

## Recording tooling — short list

You don't need a paid screen recorder. Free options on each platform:

- **macOS:** `Cmd-Shift-5` (built-in). Or [OBS Studio](https://obsproject.com/) (free, cross-platform) for the side-by-side compositing.
- **Linux:** `OBS Studio`. `peek` for short GIF-style captures.
- **Windows:** `Win-G` (Xbox Game Bar, built-in) for the basic capture. `OBS Studio` for compositing.

For the side-by-side merge:

- **OBS Studio** can record two sources side-by-side directly. Set scene resolution to 1920×540 (two stacked 960×540 captures), and add two source crops.
- **ffmpeg** if you prefer the command line:

  ```bash
  ffmpeg -i before.mp4 -i after.mp4 \
      -filter_complex "[0:v][1:v]hstack=inputs=2[v]; [1:a]anull[a]" \
      -map "[v]" -map "[a]" comparison.mp4
  ```

  This stacks horizontally and keeps only the audio from the "after" track. Crops and resizes can be added if the source clips have different sizes.

## Hints

<details>
<summary>How to capture the same gameplay sequence twice</summary>

The cleanest approach: add a boolean `JUICE = True` (or read it from a CLI flag) at the top of your game and gate every juice trigger on it.

```python
JUICE = "--juice" in sys.argv

# ...

if JUICE:
    shake.trigger(6.0, duration=0.2)
    particles.extend(spawn_burst(brick_centre, count=12))
    hit_sound.play()
```

Then record twice with the same controller input. If you can use a deterministic random seed (`random.seed(42)`) and identical key timings, the two takes will be identical. If you can't, "close enough" beats "perfectly synced" — viewers focus on the difference in feel, not in trajectory.

</details>

<details>
<summary>How long is "30 seconds, including labels"?</summary>

Aim for the structure:

- 0–2 s: black title card. "Brick Breaker — before / after juice."
- 2–28 s: actual side-by-side gameplay.
- 28–30 s: short fade-out.

26 seconds of gameplay shows roughly 3-5 brick destructions, one paddle bounce series, and (ideally) one ball-loss event. That's enough for the viewer to see each juice technique fire at least twice.

</details>

<details>
<summary>What the write-up should NOT do</summary>

- "It feels punchier" without explaining what *punchy* names.
- "I added screen shake, particles, and sound" without naming what each one *communicates*.
- "Steve Swink says juice is great" — vague. Cite a specific claim. E.g., "Swink defines game feel as real-time control of a virtual object in a simulated space with polish; the 'after' clip strengthens the polish dimension without changing the underlying simulation."

The point of the write-up is not to flatter your video. It's to *defend* a design choice in vocabulary the field agrees on.

</details>

<details>
<summary>If your repo's storage is limited</summary>

Compress aggressively. 30 seconds of 720p game footage compresses to well under 10 MB at a reasonable bitrate:

```bash
ffmpeg -i comparison.mp4 -vcodec libx264 -crf 28 -preset slow -acodec aac -b:a 96k comparison_small.mp4
```

If still too big, host externally and link. Hosting is allowed; the link in `README.md` is what matters.

</details>

## What "great" looks like

A viewer who has never seen your game watches the 30-second clip and, without you saying a word, can tell:

1. Both halves are the same game.
2. Something has been *added* to the right half (not just stylised).
3. The right half "lands" hits in a way the left doesn't.

They then read the 200-word write-up and learn the names of the things they noticed.

That is the goal. That is the artefact you'll point to in a portfolio for the next two years.
