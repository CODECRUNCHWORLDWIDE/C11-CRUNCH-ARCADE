# Challenge 1 — Author a Seamless Loop in Audacity

> **Format:** Hands-on Audacity exercise. ~2 hours including download time.
> **Deliverable:** A `loop-authoring.md` walkthrough plus the source asset, the trimmed asset, and a 10-second Pygame test script.
> **Estimated time:** 2 hours.

This challenge is the *content* counterpart to Lecture 3 §1-2. You will download one free CC-licensed ambient loop from OpenGameArt, identify its loop region, trim to a zero-crossing on a beat boundary, remove any DC offset, export as 44.1 kHz / 16-bit stereo OGG at quality 5, and verify that Pygame's `pygame.mixer.music.play(-1)` plays the result seamlessly. By the end you have an artefact you can drop into the mini-project.

## The setup

You will need:

- A working installation of Audacity (free, cross-platform): <https://www.audacityteam.org/>.
- A working Pygame environment from this week's `pip install pygame numpy` step.
- A pair of headphones. *Required.* The defect you are listening for is a 1-2 sample click at the seam; laptop speakers will not reveal it.
- ~30 minutes of focused listening time. Loop authoring rewards careful attention.

## Step-by-step

### Step 1 — Download a free ambient loop

Go to OpenGameArt and search for "ambient loop CC-BY" (or filter on CC0 if you prefer no attribution requirement). Pick a track 30-90 seconds long that has a clear cyclic structure — pads, drones, ostinato bass lines all work well. The track does *not* need to be already loop-clean; making it loop-clean is the whole challenge.

Suggested search URL:

```
https://opengameart.org/art-search?keys=loop+ambient&field_art_licenses_tid%5B%5D=2
```

Pick one. Download the audio file (OGG, WAV, or MP3). Save it as `source.ogg` (or whatever extension it came as) in a working folder `loop-authoring/`.

Record the metadata immediately in `loop-authoring/CREDITS.md`:

```
Source file:  source.ogg
URL:          https://opengameart.org/content/<asset-slug>
Creator:      <creator name>
Licence:      CC-BY 3.0 (or whatever it says)
Date:         <today>
```

### Step 2 — Open the file in Audacity

`File → Open → source.ogg`. Audacity shows a stereo waveform. Listen through with the transport (`Space` to play, `Space` to pause). Find the moment where the music's pattern "comes back to the beginning." This is usually the end of a 4-bar or 8-bar phrase. Click that moment.

### Step 3 — Identify a zero-crossing near the loop point

With the cursor placed at the end-of-phrase moment, press `Z`. Audacity moves the cursor to the nearest zero-crossing (a sample where the waveform crosses zero on both channels). The status bar in the bottom-left of Audacity shows the exact sample number. Note it down in `loop-authoring.md`.

Zoom in on the waveform (`Ctrl++` repeatedly) until you can see individual samples. The cursor should now sit exactly between a positive sample and a negative sample, or right on a zero-amplitude sample.

### Step 4 — Cut everything after the loop point

`Edit → Select → Cursor to End of Track`. Then `Edit → Delete`. The file is now trimmed to your loop length.

### Step 5 — Trim the start to a zero-crossing

Click at sample 0 (the very start of the track). Press `Z`. Most files start at a zero-crossing already, but if there is leading silence or a non-zero initial sample, Audacity will move the cursor a few samples in. Trim everything *before* the cursor (`Edit → Select → Start of Track to Cursor`, then `Edit → Delete`).

### Step 6 — Remove DC offset and normalise

`Effect → Normalize`. In the dialog:

- Check "Remove DC offset (centre on 0.0 vertically)."
- Check "Normalize peak amplitude to:" and set the value to `-1.0 dB` (one dB of headroom for safety).
- Click OK.

The DC removal corrects any consistent vertical bias in the recording. The normalisation lifts the loudest peak to -1 dB, leaving headroom for the bus structure to sum multiple sounds without clipping.

### Step 7 — Preview the loop in Audacity

`Transport → Loop Play On/Off` (or `Shift+Space`). Audacity now loops the selection. Listen for 30 seconds. Pay close attention to the seam (the moment where the file ends and starts over). With headphones you should hear no click, no pop, no audible discontinuity.

If you do hear a click:

1. The cut point is not at a zero-crossing. Go back to step 3 with a slightly different end-of-phrase moment.
2. There is a low-frequency rumble at the seam. Use `Effect → High Pass Filter` at 60 Hz to remove sub-audible bass that could be causing a phase discontinuity.
3. The end and start are *fundamentally* incompatible (one ends on a sustained note, the other starts with silence). You will need the cross-fade-the-seam technique in step 7b.

### Step 7b — (If needed) Cross-fade the seam

If the natural seam is unfixable, you can render an artificial cross-fade. The technique:

1. Duplicate the track (`Edit → Duplicate`).
2. Move the duplicate to start ~100 ms before the end of the original.
3. `Effect → Cross Fade Tracks` with the default 50 ms overlap.
4. Mix and render (`Tracks → Mix → Mix and Render to New Track`).
5. Save and re-test the seam.

The cross-fade trades a perfect-loop seam for a moment of audio that is the average of "the end" and "the start." If the two sound similar, the result is imperceptible. If they sound different, the cross-fade is the lesser evil compared to a click.

### Step 8 — Export as 44.1 kHz / 16-bit stereo OGG at quality 5

`File → Export → Export as OGG`. Settings:

- Filename: `loop-clean.ogg`.
- Quality: 5 (the slider's middle position). Yields ~128 kbps.
- Channels: stereo (preserve the source).
- (Do not bother filling in metadata tags for this exercise; the asset is for the mini-project.)

Click Export.

### Step 9 — Test in Pygame

Write `loop-authoring/test_loop.py`:

```python
"""test_loop.py — verify the loop is seam-clean.

Run with: python test_loop.py
"""

from __future__ import annotations

import sys
import time

import pygame


def main() -> int:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.music.load("loop-clean.ogg")
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.play(loops=-1)
    print("Looping. Listen for 30 seconds.")
    start: float = time.time()
    while time.time() - start < 30.0:
        time.sleep(0.5)
    pygame.mixer.music.fadeout(500)
    time.sleep(0.6)
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Run it: `python test_loop.py`. Listen for 30 seconds with headphones. The loop should pass through the seam at least 1-2 times during the test. Confirm no click.

### Step 10 — Write the deliverable

Create `loop-authoring/loop-authoring.md` with these sections:

1. **The source asset.** Filename, URL, creator, licence. (Copied from `CREDITS.md`.)
2. **The loop length you targeted and why.** Beat count, BPM if known, total seconds.
3. **The trim points.** Start sample (probably 0), end sample.
4. **Cross-fade applied?** Yes/no, and why if yes.
5. **The Pygame test result.** Pass/fail. If "fail," what you heard and what you changed.
6. **One screenshot of the Audacity waveform with the cursor on the loop point.** A PNG saved in the folder.

The whole `loop-authoring.md` is 400-600 words. The point is the *thinking*, not the prose.

## Acceptance criteria

- [ ] A folder `loop-authoring/` exists with the following files:
  - `source.ogg` (or original extension)
  - `loop-clean.ogg`
  - `test_loop.py`
  - `loop-authoring.md`
  - `CREDITS.md`
  - `screenshot.png` (the Audacity zoom on the loop point)
- [ ] `python -m py_compile test_loop.py` succeeds with no output.
- [ ] `python test_loop.py` runs for 30 seconds with no audible click at the seam.
- [ ] The OGG file is 44.1 kHz / 16-bit / stereo / Vorbis quality ~5. Confirm with `ffprobe loop-clean.ogg` if `ffmpeg` is installed, or with Audacity's `File Info` panel.
- [ ] `CREDITS.md` names the creator, URL, and licence. If the licence is CC-BY, the credit string is the canonical four-part string (name, asset name, URL, licence URL).
- [ ] `loop-authoring.md` answers all six sections.

## Common failure modes

**The loop has a perceptible click but you cannot place it.**

Open `loop-clean.ogg` back in Audacity. Switch the track view to *spectrogram* (`View → Track View → Spectrogram`). The seam will show as a vertical line. Note the exact frequency of the line — if it is below 100 Hz, you have a DC step you missed (return to `Effect → Normalize`). If it is above 1 kHz, the cut point is not at a zero-crossing (return to step 3).

**The OGG file is much larger than expected.**

Quality 7 produces ~190 kbps files; quality 9 produces ~280 kbps; quality 10 is near-lossless and ~500 kbps. The exercise targets quality 5 (~128 kbps). Re-export at the lower quality; the audible difference is imperceptible for ambient loops.

**Audacity's normalisation makes the loop quieter, not louder.**

Check the "Normalize peak amplitude to" value — if you typed `-10 dB` instead of `-1 dB`, the file is now ~9 dB quieter. Undo and renormalise to -1 dB.

**Pygame plays the loop at half speed.**

Sample rate mismatch. Confirm `pygame.mixer.pre_init(44100, ...)` and the exported file is 44.1 kHz. If you exported at 48 kHz by accident, Pygame will play it at ~91% speed.

## Why this matters

Loop authoring is a skill you only learn by doing. The discipline you exercised here — zero-crossings, beat boundaries, DC removal, OGG export, in-engine test — is the discipline every shipping game's audio engineer applies to every music track. Doing it once on a 30-second loop is enough to internalise the pattern; you will recognise loop-clean vs loop-dirty files on first listen for the rest of your career.

The asset you produced is shippable. Drop `loop-clean.ogg` into the mini-project's `assets/audio/` folder and credit the creator. The same discipline applied to a second OGG gives you the combat layer for the layered-music subsystem.

---

## References

- **Audacity manual — Edit menu.** Where `Z` (snap-to-zero) lives. <https://manual.audacityteam.org/man/edit_menu.html>
- **Audacity manual — Effect menu.** Where Normalize and Cross Fade Tracks live. <https://manual.audacityteam.org/man/effect_menu.html>
- **Audacity manual — Exporting audio.** The OGG export dialog. <https://manual.audacityteam.org/man/exporting_audio_files.html>
- **OpenGameArt — search filtered to CC-BY.** Your asset source. <https://opengameart.org/>
- **Lecture 3 §1-2.** The loop-point problem and the cross-fade technique, in writing. `../lecture-notes/03-authoring-loops-formats-and-the-godot-bridge.md`

---

*If you find errors in this challenge, please open an issue.*
