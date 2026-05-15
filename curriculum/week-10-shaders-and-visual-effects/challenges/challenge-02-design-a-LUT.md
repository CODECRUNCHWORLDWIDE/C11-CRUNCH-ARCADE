# Challenge 2 — Design a Colour-Grade LUT

> **Estimated time:** 90-150 minutes.
> **Difficulty:** medium-hard.
> **Deliverable:** one Python script that generates a LUT PNG, one rendered Godot scene with the LUT applied, and a short reflection on the artistic choices.

## The challenge

A colour LUT (look-up table) is the production-grade way to apply a global colour treatment to a scene. The treatment is fully data-driven: the same shader applies any LUT, and the LUT can be designed by an artist using nothing but Python (or Krita, or DaVinci Resolve, or any photo editor that can paint a 256x16 image).

Your task is to design *three distinct* LUTs that transform the same scene into three different moods. Each LUT is a 16-cube (16x16x16 colour mapping) packed into a 256x16 2D texture. You will write a Python script that generates all three from a set of named "grading operations" you implement yourself.

## What is a LUT, precisely

A 16-cube LUT maps every (r, g, b) input — where each channel is one of 16 discrete values 0/15, 1/15, ..., 15/15 — to a graded (r', g', b') output. The cube has 16 * 16 * 16 = 4096 entries.

A *strip-encoded* 16-cube is laid out as 16 horizontal slices of 16x16 each, concatenated horizontally. The texture is 256 pixels wide and 16 pixels tall. Each slice is one fixed blue value; within the slice, x is the red coordinate and y is the green coordinate.

```
+--------------+--------------+--------------+ ... +--------------+
|              |              |              |     |              |
|   slice 0    |   slice 1    |   slice 2    | ... |   slice 15   |
|   (b=0/15)   |   (b=1/15)   |   (b=2/15)   |     |   (b=15/15)  |
|              |              |              |     |              |
+--------------+--------------+--------------+ ... +--------------+
   16x16          16x16          16x16              16x16
```

The shader (Lecture 3 section 6) does the lookup: given an input rgb, it picks the two adjacent blue slices, samples within each at (r, g), and linearly interpolates by the blue's fractional part. The output is a graded rgb.

The *identity LUT* is the LUT where the graded output equals the input. Painting the identity LUT into the strip and applying it gives an unchanged scene. Every interesting LUT is a modification of the identity.

## Step 1: write the identity-LUT generator

```python
"""generate_identity_lut.py

Generates the 256x16 identity LUT. Every grading function below
starts from this base.
"""
import struct
import zlib

LUT_SIZE: int = 16
STRIP_WIDTH: int = LUT_SIZE * LUT_SIZE  # 256
STRIP_HEIGHT: int = LUT_SIZE  # 16


def identity_lut() -> list[tuple[int, int, int, int]]:
    """Return the identity LUT as a list of (r, g, b, a) tuples."""
    pixels: list[tuple[int, int, int, int]] = []
    for y in range(STRIP_HEIGHT):
        for x in range(STRIP_WIDTH):
            slice_index: int = x // LUT_SIZE
            x_in_slice: int = x % LUT_SIZE
            r: int = int(255 * x_in_slice / (LUT_SIZE - 1))
            g: int = int(255 * y / (LUT_SIZE - 1))
            b: int = int(255 * slice_index / (LUT_SIZE - 1))
            pixels.append((r, g, b, 255))
    return pixels
```

Verify: the pixel at strip-coord (0, 0) is rgba (0, 0, 0, 255); the pixel at (255, 15) is rgba (255, 255, 255, 255); the pixel at (128, 8) is roughly mid-grey.

## Step 2: write three grading operations

Each operation takes the identity LUT and returns a new LUT. Implement at least these three (more if you want):

### Operation A: "sunset"

A warm grade. Boost red, dim blue, lift mid-tones.

```python
def grade_sunset(lut: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
    out: list[tuple[int, int, int, int]] = []
    for r, g, b, a in lut:
        # Lift mid-tones with a gamma curve (gamma < 1 lifts; > 1 darkens).
        rf: float = (r / 255.0) ** 0.85
        gf: float = (g / 255.0) ** 0.95
        bf: float = (b / 255.0) ** 1.15
        # Tint toward warm orange.
        rf = min(1.0, rf * 1.10 + 0.05)
        gf = min(1.0, gf * 1.00 + 0.02)
        bf = max(0.0, bf * 0.85 - 0.02)
        out.append((int(rf * 255), int(gf * 255), int(bf * 255), a))
    return out
```

### Operation B: "moonlight"

A cool grade. Crush red, lift blue, lower overall brightness.

```python
def grade_moonlight(lut: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
    out: list[tuple[int, int, int, int]] = []
    for r, g, b, a in lut:
        rf: float = (r / 255.0) ** 1.15 * 0.75
        gf: float = (g / 255.0) ** 1.05 * 0.85
        bf: float = (b / 255.0) ** 0.90 * 1.05
        rf = max(0.0, min(1.0, rf))
        gf = max(0.0, min(1.0, gf))
        bf = max(0.0, min(1.0, bf))
        out.append((int(rf * 255), int(gf * 255), int(bf * 255), a))
    return out
```

### Operation C: "horror"

A high-contrast grade with a green-cyan cast.

```python
def grade_horror(lut: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
    out: list[tuple[int, int, int, int]] = []
    for r, g, b, a in lut:
        rf: float = (r / 255.0) ** 1.6
        gf: float = (g / 255.0) ** 0.85
        bf: float = (b / 255.0) ** 1.2
        # Bias toward sickly green-cyan.
        gf = min(1.0, gf + 0.08)
        bf = min(1.0, bf + 0.04)
        out.append((int(rf * 255), int(gf * 255), int(bf * 255), a))
    return out
```

### Save as PNG

Reuse the `make_png` helper from `SOLUTIONS.md` (the dissolve-noise generator). Three PNG files: `lut_sunset.png`, `lut_moonlight.png`, `lut_horror.png`. Each is ~5 KB.

## Step 3: apply in Godot

1. Import the three PNGs into your Godot project. *Important*: set each one's import settings to disable mipmaps and set filter to *Linear* (not nearest). The shader assumes linear interpolation between slices.
2. Create a scene with a colourful background (a couple of sprites of varied hues).
3. Add a SubViewport + TextureRect post-process setup (see Lecture 3 section 2.1).
4. Assign the LUT shader (from Lecture 3 section 6 — paste it into a `.gdshader` file in your project).
5. Assign one of the three LUTs to the `lut` uniform.
6. Take a screenshot.
7. Swap to the next LUT. Screenshot.
8. Repeat for the third.

## Step 4: the deliverables

1. **`challenge-02-generate-lut.py`** — the Python script that generates all three LUTs. Must compile with `python3 -m py_compile`. Standard library only; no Pillow, no numpy.
2. **`challenge-02-lut-sunset.png`, `-moonlight.png`, `-horror.png`** — the three generated LUT files.
3. **`challenge-02-screenshot-original.png`** — the unaltered scene.
4. **`challenge-02-screenshot-sunset.png`, `-moonlight.png`, `-horror.png`** — the three graded scenes.
5. **`challenge-02-reflection.md`** — 200-word reflection on the artistic choices:
   - Which grade reads most strongly? Why?
   - Which grade would you use for a specific gameplay state (e.g. low health, night-time, boss encounter)? Justify.
   - What would you do differently if you had a real photo editor instead of Python?

## Grading rubric

- 30% — the Python script compiles, runs, and produces three valid PNG files.
- 30% — the three rendered scenes are visually distinct from each other and from the original.
- 25% — the LUTs are technically correct: the identity grade renders the scene unchanged; the graded LUTs do not produce out-of-gamut artefacts (no saturation clipping, no posterisation beyond the LUT's natural quantisation).
- 15% — the reflection demonstrates understanding of *why* a grade reads a particular way, not just *that* it does.

## Stretch goals

1. **Implement a "tonemap" operation**. Real cinema grading often includes a tonemap step — a non-linear remapping of brightness — to compress the highlights. Implement `tonemap_reinhard(x) = x / (1 + x)` or `tonemap_aces(x) = (x*(2.51*x + 0.03)) / (x*(2.43*x + 0.59) + 0.14)` (the ACES Filmic Tone Mapping curve) as a pre-grade step.
2. **Generate a 32-cube LUT instead of 16-cube**. Higher fidelity; eight times more entries (32x32x32 = 32768). The texture becomes 1024x32. The shader needs a small update to `lut_size`.
3. **Author a LUT by hand in Krita**. Open the identity LUT PNG, paint adjustments using only Krita's filters and adjustment layers, save, apply. Compare to your Python-generated LUTs. This is how real artists work.
4. **Animate between two LUTs**. Add a second `sampler2D lut_b` uniform to the LUT shader and a `lut_blend` float. Sample both, mix between them. Tween `lut_blend` to transition between moods (e.g. day -> sunset over 4 seconds).

## A note on real-world LUT workflows

In a shipping studio, LUTs are typically authored by a *colourist* in DaVinci Resolve, Nuke, or a similar high-end colour-grading tool. The tool exports a `.cube` or `.3dl` file; a build script converts it to the strip-encoded PNG your shader can read. The *shader* is identical regardless of who authored the LUT or in what tool; the *data* is what changes.

This data-driven separation is the deepest practical lesson of this challenge. Your shader from Lecture 3 already accepts any LUT. The Python script you write today is one way to author them; in production it would be Resolve. The shipping pipeline is identical. That is what we mean when we say production effects are "data-driven."
