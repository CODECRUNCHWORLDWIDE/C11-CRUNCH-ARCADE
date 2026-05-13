# Week 2 — Resources

Every resource on this page is **free** and **publicly accessible**. No paywalled books, no proprietary PDFs. If a link breaks, please open an issue.

## Required reading (work it into your week)

- **Pygame — `pygame.Rect`** (the entire reference; you'll bounce here a hundred times this term): <https://www.pygame.org/docs/ref/rect.html>
- **Pygame — `pygame.sprite`** (`Sprite`, `Group`, and the `spritecollide*` helpers — skim only): <https://www.pygame.org/docs/ref/sprite.html>
- **Pygame — `pygame.math.Vector2`** (revisit; we lean on it for velocity and acceleration): <https://www.pygame.org/docs/ref/math.html>
- **Pygame — `pygame.draw`** (`rect`, `circle`, `line`): <https://www.pygame.org/docs/ref/draw.html>

## The classic essays — physics and collision

- **Glenn Fiedler — Fix Your Timestep!** — re-read it this week. Last week it was theoretical; this week it explains a bug you've felt:
  <https://gafferongames.com/post/fix_your_timestep/>
- **Glenn Fiedler — Integration Basics** — Euler vs RK4 vs Verlet, explained plainly:
  <https://gafferongames.com/post/integration_basics/>
- **Bob Nystrom — *Game Programming Patterns* — Object Pool** (free online; useful once you have lots of bullets / bricks):
  <https://gameprogrammingpatterns.com/object-pool.html>
- **Erin Catto — Box2D Lite** (the original 2D physics-engine paper; free PDF, deeply worth a skim even if the math goes over your head):
  <https://box2d.org/files/ErinCatto_PhysicsForGameProgrammers_GDC2006.pdf>

## The Nature of Code

Daniel Shiffman's free book is the single best intuition primer for game physics. It's in p5.js (JavaScript), but the math translates directly. Chapters 1–3 are mandatory reading this week.

- **The Nature of Code (book + videos)**: <https://natureofcode.com/>
- **Chapter 1 — Vectors**: <https://natureofcode.com/book/chapter-1-vectors/>
- **Chapter 2 — Forces**: <https://natureofcode.com/book/chapter-2-forces/>
- **Chapter 3 — Oscillation**: <https://natureofcode.com/book/chapter-3-oscillation/>

## Collision-detection deep dives (free articles)

- **Jeffrey Thompson — Collision Detection** (a free interactive book; the AABB-vs-AABB and circle-vs-rect chapters are the ones you want this week):
  <http://www.jeffreythompson.org/collision-detection/table_of_contents.php>
- **Christer Ericson — *Real-Time Collision Detection*** (the bible; the book itself is not free, but Christer's site has free sample chapters and slides):
  <http://realtimecollisiondetection.net/>
- **Amit Patel — *Red Blob Games* — Line of Sight, Movement** (free articles; the diagrams are worth the visit alone):
  <https://www.redblobgames.com/>

## YouTube channels worth your time

- **DaFluffyPotato** — "platformer physics" video series; the closest you'll get to a real indie's collision setup in 30 minutes:
  <https://www.youtube.com/@DaFluffyPotato>
- **Coding Math** by Keith Peters — short videos on the math behind games (vectors, reflection, rotation):
  <https://www.youtube.com/@codingmath>
- **The Coding Train** (Shiffman) — *Nature of Code* episode list (free, JS but the ideas are universal):
  <https://thecodingtrain.com/tracks/the-nature-of-code-2>

## Official Python docs (you'll bounce here from time to time)

- **`math` module** (`copysign`, `sqrt`, `hypot` — useful for distance work): <https://docs.python.org/3/library/math.html>
- **`random` module** (for spawning bricks in random patterns): <https://docs.python.org/3/library/random.html>
- **`dataclasses` module** (your `Ball` and `Brick` want to be dataclasses): <https://docs.python.org/3/library/dataclasses.html>

## Other engines — same collision, different syntax

In Week 8 you'll switch to Godot. The collision primitives are the same; the names change. Bookmark these now.

- **Godot — `Area2D` and `CollisionShape2D`**:
  <https://docs.godotengine.org/en/stable/tutorials/physics/collision_shapes_2d.html>
- **Godot — `KinematicBody2D.move_and_slide()`** (the canonical "push-out-and-keep-going" call): now `CharacterBody2D` in Godot 4:
  <https://docs.godotengine.org/en/stable/tutorials/physics/using_character_body_2d.html>
- **Box2D's `b2World`** (for context; you don't need this for brick-breaker but it's where the industry standard lives): <https://box2d.org/documentation/>

## Free books (chapter-level, not whole books)

- **Al Sweigart — *Making Games With Python & Pygame*** — chapters on collision and "Squirrel Eat Squirrel":
  <https://inventwithpython.com/pygame/>
- **The Nature of Code** (already linked above).

## Asset libraries

- **Kenney.nl — Breakout Pack** (CC0; you won't use sprites this week but bookmark for Week 6):
  <https://kenney.nl/assets/category:2D?sort=update>
- **OpenGameArt.org — Breakout-style assets**: <https://opengameart.org/art-search?keys=breakout>
- **Freesound.org — short SFX** (search "bounce", "brick", "thud"; check CC0 / CC-BY):
  <https://freesound.org/>

## Glossary cheat sheet

Keep this open in a tab.

| Term | Plain English |
|------|---------------|
| **AABB** | Axis-Aligned Bounding Box. A rectangle whose sides are parallel to the X and Y axes. The simplest collision primitive. |
| **Overlap test** | "Do these two shapes share any pixels?" For AABBs: four comparisons. |
| **Penetration** | The distance one body is *inside* another after a frame's movement. Resolution pushes it out by this amount. |
| **Restitution** | The "bounciness" coefficient. 1.0 = perfect bounce. 0.0 = stick. Most rubber balls are around 0.7. |
| **Reflection** | Flipping the perpendicular component of velocity on impact. Simplest form: `vel.x = -vel.x` on a vertical wall. |
| **Tunneling** | A fast-moving object passes *through* a thin wall in one frame because we only sampled the endpoints. |
| **Swept test** | A collision check along the *path* between two frames, not just at the endpoints. The fix for tunneling. |
| **Euler integration** | The simplest way to update position from velocity: `pos += vel * dt`. Accurate enough for games. |
| **Verlet integration** | A more numerically stable integrator. Out of scope this week; covered briefly in Week 11. |
| **Fixed timestep** | Running the simulation at a constant `dt` regardless of render rate. Preview this week, deep dive in Week 4. |
| **Separating axis** | If you can find an axis on which two shapes don't overlap, they don't collide. The basis of SAT for arbitrary polygons. |

---

*If a link 404s, please [open an issue](https://github.com/CODE-CRUNCH-CLUB) so we can replace it.*
