# Lecture 2 — Camera and Off-Screen Culling

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can implement a camera with snap / lerp / dead-zone follow modes, clamp it to the level bounds, and cull off-screen tiles with integer math so a 2000-tile level draws in ~1 ms instead of ~9 ms.

If you only remember one thing from this lecture, remember this:

> **A camera is an offset, and culling is integer math.** "Camera" sounds like an entire subsystem; it is actually two floats — `cam_x` and `cam_y` — and you subtract them from every world coordinate before drawing. "Culling" sounds expensive; for tilemaps it costs four `int()` calls per frame and saves you 95% of your draw time. The dragon is much smaller than its name suggests.

---

## 1. What is a camera?

In Pygame, there is no "camera" object built in. The screen always draws at `(0, 0)`. If you want the world to appear to scroll, *you move every world object the other way*. Pressing right doesn't move the player; pressing right moves the *world* leftward, and the player stays in the centre of the screen.

That sounds backwards, but it's the only way it works in a fixed-window 2D renderer. The trick is to maintain a single value — the **camera offset** — that represents "what world point currently sits at the top-left of the screen." Then for every world-space drawable, you subtract the camera offset before blitting.

```python
@dataclass
class Camera:
    x: float = 0.0   # world x at the top-left of the screen
    y: float = 0.0
    viewport_w: int = 960
    viewport_h: int = 540

    def world_to_screen(self, wx: float, wy: float) -> tuple[int, int]:
        return (int(wx - self.x), int(wy - self.y))
```

Two fields. One method. That's a camera.

To render a tile in row `r`, column `c`, with the world top-left at `(0, 0)`:

```python
sx, sy = camera.world_to_screen(c * TILE, r * TILE)
screen.blit(tile_surf, (sx, sy))
```

Every entity in the world does the same dance: compute its world position, subtract the camera offset, blit. The HUD (score, lives, level number) does *not* use the camera — it lives in screen space directly. That distinction is why you can shake the world while the score stays still, and why we kept the HUD un-shaken in Week 3.

---

## 2. Follow modes

Now the camera *does* something. The point of having a camera is that it tracks the player as they move through a level larger than the window. There are three follow modes you should know, in increasing order of feel quality.

### 2.1 Snap (the placeholder)

The camera centres on the player every frame, instantly.

```python
def follow_snap(cam: Camera, target_x: float, target_y: float) -> None:
    cam.x = target_x - cam.viewport_w / 2
    cam.y = target_y - cam.viewport_h / 2
```

This is the right starting point. It will work. It will also feel *robotic* — every player input snaps the camera in lock-step. You'll feel motion sick after thirty seconds. Use snap for prototyping; never ship it.

### 2.2 Lerp (smooth follow)

The camera moves toward the target by a fraction of the distance every frame. This is **linear interpolation**, or *lerp*.

```python
def follow_lerp(cam: Camera, target_x: float, target_y: float, dt: float, speed: float = 6.0) -> None:
    """speed is roughly 'how many screen-widths per second the camera can travel'."""
    desired_x = target_x - cam.viewport_w / 2
    desired_y = target_y - cam.viewport_h / 2
    t = 1.0 - pow(0.001, dt * speed)   # frame-rate-independent lerp factor
    cam.x += (desired_x - cam.x) * t
    cam.y += (desired_y - cam.y) * t
```

The funky `1 - 0.001 ** (dt * speed)` is the **frame-rate-independent lerp factor**. It is mathematically equivalent to "approach the target by `speed` fractional units per second, regardless of the timestep." Memorise the pattern; we'll use it in Week 6 for animation easing too.

At `speed=6.0`, the camera covers about 6 units of "remaining distance per second." On the player's first step, the camera lags slightly and accelerates. The player feels *led*, not *snapped*. This is the default for most 2D platformers.

### 2.3 Dead-zone (the platformer classic)

The camera doesn't move at all *until* the player exits a central rectangle. This is what *Super Mario World* uses, and *Hollow Knight*, and most action-platformers that don't want a constantly-floating camera.

```python
@dataclass
class DeadZoneCamera(Camera):
    dz_w: int = 200   # dead-zone width
    dz_h: int = 120   # dead-zone height

    def follow_dead_zone(self, target_x: float, target_y: float) -> None:
        # Centre of the dead-zone in screen space.
        cx = self.viewport_w / 2
        cy = self.viewport_h / 2
        # Target in screen space.
        tx = target_x - self.x
        ty = target_y - self.y
        # Dead-zone bounds.
        left   = cx - self.dz_w / 2
        right  = cx + self.dz_w / 2
        top    = cy - self.dz_h / 2
        bottom = cy + self.dz_h / 2
        if tx < left:    self.x += tx - left
        if tx > right:   self.x += tx - right
        if ty < top:     self.y += ty - top
        if ty > bottom:  self.y += ty - bottom
```

The camera moves only the *minimum* amount needed to keep the target inside the dead-zone. While the player walks back and forth in the middle of the window, the camera is perfectly still. As soon as the player walks past the right edge of the dead-zone, the camera starts to pan right. This feels stable and deliberate. Players don't notice the camera unless you do something wrong.

Combine dead-zone and lerp for the deluxe version: the dead-zone defines *when* the camera should move, and a lerp toward the dead-zone boundary defines *how fast*. We do this in Exercise 3 and the mini-project.

---

## 3. Clamping to the level bounds

A camera that follows without bounds will happily pan past the edge of the level, showing the player a void of cleared-screen black to the right of the last tile. That looks broken. The fix:

```python
def clamp_camera_to_bounds(cam: Camera, level_w: int, level_h: int) -> None:
    """level_w and level_h are the level dimensions in pixels."""
    cam.x = max(0.0, min(cam.x, level_w - cam.viewport_w))
    cam.y = max(0.0, min(cam.y, level_h - cam.viewport_h))
```

Call this *after* the follow update, every frame. If the level is smaller than the viewport on either axis (a small intro level), the clamp will pin the camera to `(0, 0)` on that axis, which is exactly what you want — the player walks around inside a fixed view.

Edge case: if `level_w < cam.viewport_w`, the upper bound becomes negative, which the `min` resolves to "less than 0," and then `max(0, ...)` resolves to `0`. The level just centres against the top-left and the rest of the window stays as your clear colour. If you want it horizontally centred instead, special-case that branch — but for this week, top-left pinning is fine.

---

## 4. Off-screen culling

Now the headline. Drawing every tile every frame is wasteful even when the wasted cost is "low." A 200×100 tile level has 20,000 cells. Drawing 20,000 `blit` calls per frame is 333 µs of pure Python overhead per `blit × 20000`, which on a modern CPU is somewhere between 2 ms and 8 ms depending on Python version and Pygame build. You don't have that budget.

The fix is one of the oldest tricks in computer graphics: **don't draw what you can't see.** This is called **culling** (or, more specifically here, *frustum culling* — the frustum being the camera's viewport rectangle).

For arbitrary objects, culling means "AABB-test each object against the viewport rect and skip the ones that don't intersect." That's `O(n)` and helps with overdraw but doesn't help with *iteration cost*. For tilemaps, we can do better. Because tiles are a regular grid, **we can compute the range of grid cells inside the viewport directly**, without iterating over any cell outside it.

### The integer-math cull

```python
def visible_tile_range(cam: Camera, tile_w: int, tile_h: int,
                       grid_w: int, grid_h: int) -> tuple[int, int, int, int]:
    """Return (col_start, col_end, row_start, row_end) bounding the visible tiles."""
    col_start = max(0, int(cam.x) // tile_w)
    row_start = max(0, int(cam.y) // tile_h)
    col_end   = min(grid_w, (int(cam.x) + cam.viewport_w) // tile_w + 1)
    row_end   = min(grid_h, (int(cam.y) + cam.viewport_h) // tile_h + 1)
    return (col_start, col_end, row_start, row_end)
```

Four `int()` casts. Four divisions. Two `max`/`min` calls each. That's the entire cull. With a 960×540 viewport and 32×32 tiles, the visible range is at most `(960/32 + 1) * (540/32 + 1) = 31 * 17 = 527` tiles. Walking that range is roughly 25× cheaper than walking 20,000 cells. The numbers work out the same on any reasonable laptop: ~9 ms uncalled to ~1.2 ms culled. That's the difference between fitting in your 16.6 ms frame budget and not.

### The culled draw loop

```python
def draw_layer(screen: pygame.Surface, layer: TileLayer,
               tile_surfaces: list[pygame.Surface],
               cam: Camera, tile_w: int, tile_h: int) -> None:
    c0, c1, r0, r1 = visible_tile_range(cam, tile_w, tile_h, layer.width, layer.height)
    for row in range(r0, r1):
        base = row * layer.width
        for col in range(c0, c1):
            gid = layer.data[base + col]
            if gid == 0:
                continue
            sx = col * tile_w - int(cam.x)
            sy = row * tile_h - int(cam.y)
            screen.blit(tile_surfaces[gid - 1], (sx, sy))
```

Note `base = row * layer.width` once per row. Trivial constant-folding, but it shaves a couple of µs off the inner loop. In a 30-fps tight game you'd care; in a 60-fps casual platformer you don't. Either way, keep it.

### Why `colliderect` per tile is wrong

A common beginner version of "cull" looks like this:

```python
# WRONG. Don't do this.
viewport_rect = pygame.Rect(int(cam.x), int(cam.y), cam.viewport_w, cam.viewport_h)
for row in range(layer.height):
    for col in range(layer.width):
        tile_rect = pygame.Rect(col * tile_w, row * tile_h, tile_w, tile_h)
        if not viewport_rect.colliderect(tile_rect):
            continue
        # ... draw tile ...
```

This *works*. It also *iterates over all 20,000 cells every frame*. The `colliderect` test itself is O(1), but you still pay the loop overhead for every cell, plus the cost of constructing 20,000 `pygame.Rect` instances per frame, which is roughly 4 ms of pure Python garbage. Integer-math culling skips all of that. **The cull is in the range, not in the test.**

---

## 5. Frame budget for the culled tilemap

Here is what the frame budget looks like on a real Week-4 platformer. (Numbers measured on an M1 MacBook Air, 60 fps, Python 3.11 + Pygame 2.5. Your numbers will differ; the *ratio* is what matters.)

```
┌─────────────────────────────────────────────────────────┐
│  FRAME BUDGET — 60 fps target, with culled tilemap      │
│                                                         │
│  Input poll:       ~0.2 ms                              │
│  Update (sim):     ~1.5 ms                              │
│  Tilemap collide:  ~0.6 ms (AABB-vs-grid, integer math) │
│  Particles:        ~0.5 ms                              │
│  Camera follow:    ~0.05 ms                             │
│  Tilemap draw:     ~1.2 ms  (~600 tiles, culled)        │
│  Entity draw:      ~1.5 ms                              │
│  HUD draw:         ~0.4 ms                              │
│  Audio mix:        ~0.3 ms                              │
│  GPU + present:    ~4.0 ms                              │
│  Headroom:         ~6.4 ms                              │
│  ─────────────────────                                  │
│  Total:           ~16.6 ms / frame                      │
└─────────────────────────────────────────────────────────┘
```

Two rows are new this week: **Tilemap collide** (0.6 ms) and **Tilemap draw** (1.2 ms). Both are cheap *because* you implemented them with grid math, not Python objects. The same level with naive `Rect.colliderect` everywhere would burn 4-8 ms and squeeze your budget. From Week 5 onward, every additional system (state machines, animation, audio events) has to fit inside the ~6.4 ms of headroom above. Spending 4 ms on a naive tilemap now means you have 2 ms left for the rest of the game. *Not* fine.

A practical rule: **profile your tilemap draw on the largest level you plan to ship, on the slowest machine you plan to support, with the rest of the game disabled.** If draw alone is above 3 ms, you have a budget problem you need to solve before adding any other feature. Most of the time, the solution is "you forgot to cull."

---

## 6. Parallax for nearly free

Once the camera is an offset, parallax is one line. Draw a background layer using a *fraction* of the camera's position. The background appears to move slower than the foreground, which the brain reads as "the background is far away."

```python
# Foreground layer: full camera offset.
draw_layer(screen, level.tile_layers[1], tile_surfaces, cam, TILE_W, TILE_H)

# Background layer: half camera offset (twice as far away).
# Build a "parallax camera" with half the x and y.
bg_cam = Camera(x=cam.x * 0.5, y=cam.y * 0.5,
                viewport_w=cam.viewport_w, viewport_h=cam.viewport_h)
draw_layer(screen, level.tile_layers[0], tile_surfaces, bg_cam, TILE_W, TILE_H)
```

Three multiplications per frame for a *huge* visual win. Tile your background layer wide enough that the slower scroll doesn't reveal the right edge before the foreground does, and you have a parallax background for the cost of one extra `Camera` instance per frame.

A note on order: draw the background *first*, then the foreground. The foreground overlaps the background, not the other way. Pygame is a painter's-algorithm renderer; back-to-front.

---

## 7. AABB-vs-tilemap collision (preview)

The mini-project needs collisions between the player and the world tiles. We are not turning this into a Week-5 lecture on collision (that's next week) but here's the technique you'll use, because it's the natural pair to the culled draw.

For a player AABB at `(px, py, pw, ph)`:

1. Convert the AABB's corners to tile coordinates: `world_to_tile(px, py)` (top-left), `world_to_tile(px + pw - 1, py + ph - 1)` (bottom-right).
2. Iterate the cells in that range. For each cell that is solid (`grid[r][c] != 0`), construct that one tile's rect and test `colliderect` against the player.
3. Resolve the overlap: split into a horizontal pass and a vertical pass. Move the player by the velocity's x first, check for x-collisions, snap; then move by y, check for y-collisions, snap.

The total cost is `O(tiles_under_player)`, which for a 32×32 player on a 32×32 grid is at most 4 cells. Per frame. That's an order of magnitude cheaper than "test against every wall" and the technique you'll see in *Super Meat Boy*, *Celeste*, *Hollow Knight*, and every other platformer.

The starter code for the mini-project gives you this collision routine pre-written; your job this week is the data and the camera. Week 5 returns to this.

---

## 8. Common camera bugs (and how to find them)

- **"The level shakes/jitters as I walk."** You're not rounding the camera position before blitting. Pygame's `Surface.blit` takes a pair of floats and rounds inconsistently. Cast to `int()` before blit. Always.
- **"My player walks off-screen and the camera doesn't follow."** You set `cam.x = target.x` but never subtracted the half-viewport, so the camera centres on the *top-left corner* of the player. Centre on `target_x - viewport_w / 2`.
- **"The camera goes past the level edge."** You forgot to clamp after the follow update. Order matters: follow first, clamp second.
- **"Everything except the HUD shakes correctly."** This is correct, actually — but only if the HUD is in screen space and the world is in world space. Make sure your `screen.blit(score_text, (10, 10))` does *not* go through `world_to_screen`. The HUD is the anchor.
- **"My parallax background looks weird at the level edges."** Your parallax layer is the same pixel-width as the foreground, but the slower scroll means it can't reach the right edge in time. Tile the parallax layer wider, or repeat it modulo its width.
- **"60 fps drops to 20 when the camera moves."** You're not culling, or your cull is the `colliderect`-per-tile mistake from §4. Re-read the integer-math cull and replace.

---

## 9. Mini-glossary recap

| Term | Recall |
|------|--------|
| Camera | Two floats: x and y. The world point at the top-left of the screen. |
| `world_to_screen` | `(int(wx - cam.x), int(wy - cam.y))`. Two integer subtractions. |
| Snap follow | `cam.x = target.x - viewport_w/2`. The placeholder. |
| Lerp follow | `cam.x += (desired - cam.x) * t`. The default for most 2D games. |
| Dead-zone | A central rect the target can move freely inside without the camera moving. |
| Clamp to bounds | `cam.x = max(0, min(cam.x, level_w - viewport_w))`. Two lines. |
| Cull (tilemap) | Compute `(c0, c1, r0, r1)` from the viewport. Iterate only that. |
| Parallax | Draw a second layer with `cam_x * fraction`. |

---

## 10. Re-read checklist

Before you move to Exercise 3 and the mini-project, you should be able to:

1. Explain why "camera" in Pygame is just two floats and a subtraction.
2. Implement snap, lerp, and dead-zone follow without checking the lecture.
3. Recall the frame-rate-independent lerp formula and explain why it's preferred over `cam.x += (desired - cam.x) * 0.1`.
4. Write the four-line integer-math culling formula from memory.
5. Explain why `Rect.colliderect`-per-tile is wrong, even though it gives the same visual result.
6. State the rough frame-budget split for a culled tilemap (tilemap draw ~1.2 ms vs ~9 ms uncalled).
7. Implement parallax in two extra lines on top of the existing draw loop.

If any of those are shaky, re-read the section in question before continuing. Exercise 3 and the mini-project assume all seven.

---

*Previous:* [Lecture 1 — The Tilemap Data Format](./01-the-tilemap-data-format.md). *Continue to* [Exercise 1 — CSV Tilemap](../exercises/exercise-01-csv-tilemap.py).
