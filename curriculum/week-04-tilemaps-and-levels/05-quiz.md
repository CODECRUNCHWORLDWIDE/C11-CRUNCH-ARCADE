# Week 4 — Quiz

Ten multiple-choice questions. Take it with your lecture notes closed. Aim for 9/10 before moving to Week 5. Answer key at the bottom — don't peek.

---

**Q1.** Lecture 1 names three pieces of "the tilemap abstraction." Which set is correct?

- A) Tileset, grid, renderer.
- B) Background, foreground, HUD.
- C) Tiled, PyTMX, Pygame.
- D) GID, firstgid, tile-index.

---

**Q2.** In a Tiled-exported JSON map, what does GID `0` mean?

- A) The first tile in the first tileset.
- B) An empty cell — nothing is drawn there.
- C) The player spawn.
- D) An error code that means the file is corrupt.

---

**Q3.** You load a Tiled map and the tiles all appear shifted by one — every cell is drawing the *previous* tile from your tileset. What's the most likely cause?

- A) The map was exported at the wrong tile size.
- B) You indexed your tileset array as `tile_surfaces[gid]` instead of `tile_surfaces[gid - 1]`. GID `1` is the first tile, which is index `0`.
- C) The map has two tilesets and you only loaded the first.
- D) Pygame's `subsurface` is broken on your version.

---

**Q4.** Lecture 1 gives four coordinate conversion functions. Which line correctly converts a world-space pixel position to its containing tile cell?

- A) `(int(wx / TILE), int(wy / TILE))`
- B) `(int(wx // TILE), int(wy // TILE))`
- C) `(int(wx) // TILE_W, int(wy) // TILE_H)` where TILE_W and TILE_H come from the map file.
- D) Both B and C are correct.

---

**Q5.** A camera in pure Pygame is, fundamentally:

- A) A subclass of `pygame.sprite.Sprite` that follows the player.
- B) A `pygame.Rect` you subtract from every world-space draw.
- C) Two floats (x and y) representing the world point at the top-left of the screen; the screen draws at `world - cam`.
- D) A separate render target you blit the whole world into and then scroll.

---

**Q6.** The frame-rate-independent lerp factor for a smooth camera is `t = 1 - 0.001 ** (dt * speed)`. Why is the naive `cam.x += (desired - cam.x) * 0.1` wrong?

- A) It isn't wrong; both are equivalent.
- B) The naive version's "0.1" is a per-frame factor, which ties the follow speed to the frame rate. At 30 fps the camera lags; at 144 fps it overshoots. The exponential form is dt-correct.
- C) `pow` is faster than multiplication, so the exponential is preferred for performance.
- D) Floating-point precision; the multiplication accumulates error.

---

**Q7.** Lecture 2 argues that for tilemap culling, `Rect.colliderect`-per-tile is the *wrong* approach even though it produces the same visual result. Why?

- A) `colliderect` is a buggy method on some Pygame versions.
- B) It still iterates every cell (O(n_tiles)) and constructs a `pygame.Rect` per cell — the per-cell loop and per-cell allocation are the cost, not the test itself. Integer-math range culling skips all of that and is O(visible_tiles).
- C) `colliderect` returns the wrong answer for tile-aligned rectangles.
- D) It doesn't handle edge tiles correctly.

---

**Q8.** A 200×100 tile world (20,000 cells) renders naively at ~9 ms / frame. After integer-math culling (viewport ~600 tiles), the same render is closest to:

- A) ~9 ms (culling doesn't matter at this scale).
- B) ~6 ms.
- C) ~1.2 ms.
- D) ~0 ms (culling is free).

---

**Q9.** Which of the following is the canonical platformer camera follow mode that *only moves when the player exits a central window*?

- A) Snap follow.
- B) Lerp follow.
- C) Dead-zone follow.
- D) Parallax follow.

---

**Q10.** Per Lecture 1, you have a friend who is comfortable in spreadsheets but doesn't program. Which file format would you choose for them to edit your level layout?

- A) `.tmx` (Tiled's XML format) — it's the indie standard.
- B) `.json` — it's a programmer format.
- C) `.csv` — every spreadsheet exports it; no editor install required.
- D) A `.py` file with a Python list literal — easiest to read.

---

## Answer key

<details>
<summary>Click to reveal answers</summary>

1. **A** — Tileset (the image), grid (the array of indices), renderer (the code that walks the grid and blits). (Lecture 1 §1.)
2. **B** — GID 0 means empty. Always. Across every Tiled map ever exported. The first non-empty tile in the first tileset is GID 1. (Lecture 1 §4.)
3. **B** — The off-by-one between GID space (1-indexed for "real" tiles, 0 reserved for empty) and Python list space (0-indexed). Use `gid - 1` when looking up the tile surface. (Lecture 1 §7.)
4. **D** — Both B and C are correct. `//` is floor division. Pulling `TILE_W`/`TILE_H` from the file is the production-correct version because Tiled supports non-square tiles. (Lecture 1 §2.)
5. **C** — Two floats and a subtraction. That is the whole camera abstraction. (Lecture 2 §1.)
6. **B** — The naive form is frame-rate-dependent. The exponential form converges to the same fractional approach regardless of dt. This is the same trick you'll use for animation easing in Week 6. (Lecture 2 §2.2.)
7. **B** — The cull is in the *range*, not in the *test*. Iterating every cell and testing each one is `O(n_total)`; computing the visible range upfront is `O(n_visible)`. The latter is 25× faster on a 200×100 world. (Lecture 2 §4.)
8. **C** — ~1.2 ms. ~25× speedup is the realistic number on modern Python+Pygame. (Lecture 2 §5, frame-budget tile.)
9. **C** — Dead-zone. The camera doesn't move at all while the player wanders inside the centre window; it only catches up when they exit. (Lecture 2 §2.3.)
10. **C** — CSV. The level designer doesn't need Tiled or your IDE; they edit in LibreOffice or Google Sheets. (Lecture 1 §3.)

</details>

---

If you scored under 7, re-read the lecture sections cited in the answers you missed. If you scored 9 or 10, you're ready for the [homework](./06-homework.md).
