# Week 6 — Quiz

Ten multiple-choice questions. Take it with your lecture notes closed. Aim for 9/10 before moving to Week 7. Answer key at the bottom — don't peek.

---

**Q1.** Steve Swink's *Game Feel* (2009) defines game feel using three pillars. Which set is correct?

- A) Story, art, music.
- B) Real-time control, simulated physical space, polish.
- C) Mechanics, dynamics, aesthetics.
- D) FPS, latency, throughput.

---

**Q2.** A sprite sheet is a single PNG containing a grid of frames. In Pygame, the right way to extract one frame is:

- A) `pygame.image.load(path)` once per frame, with a different rectangle each time.
- B) `pygame.transform.scale(surface, (frame_w, frame_h))` returning a smaller copy.
- C) `surface.subsurface(rect)` — a no-copy view into the parent surface.
- D) `pygame.draw.rect(surface, color, rect)` and trust the pixel layout.

---

**Q3.** Frame-rate-independent animation: the current frame index of a 12-fps clip whose `elapsed_t = 0.5 s` is computed how?

- A) `frame_count += 1` every render frame; modulo total frames.
- B) `int(elapsed_t * fps) % len(frames)` — six frames have passed at 12 fps after 0.5 s.
- C) `int(elapsed_t / fps) % len(frames)` — using elapsed divided by fps.
- D) The display's refresh rate divided by the animation's fps.

---

**Q4.** The two-line `lerp(a, b, t)` function returns `a + (b - a) * t`. Which value of `t` returns the midpoint between `a` and `b`?

- A) `t = 0.0`.
- B) `t = 0.5`.
- C) `t = 1.0`.
- D) `t = 2.0`.

---

**Q5.** Lecture 2 §2 names five easing curves. The "overshoot and settle" curve — the one used for score-counter pops and button presses — is called:

- A) `ease_in_out`.
- B) `linear`.
- C) `ease_out_back`.
- D) `ease_quadratic`.

---

**Q6.** Squash-and-stretch on a jumping character is applied to:

- A) The character's collision rectangle, so the hitbox deforms with the art.
- B) The character's `vx` and `vy`, so the physics scales with the animation.
- C) The character's drawn frame only, via `pygame.transform.scale_by`. The hitbox does not deform; the art does.
- D) The screen-shake amplitude, indirectly.

---

**Q7.** A screen shake of `amplitude = 24 px, duration = 400 ms` would be appropriate for:

- A) Every footstep.
- B) A standard player hit.
- C) A boss-scale explosion. Player hits should use ~6 px; landings ~4 px. 24 px is the maximum; past this, screen readability suffers.
- D) Never; 24 px is always too much.

---

**Q8.** A particle emitter spawning dust on a hard landing should be triggered:

- A) Every frame the player is grounded, from `RunState.update`.
- B) From the input handler, when SPACE is pressed.
- C) From the `enter()` hook of the state the character arrives in (here, `IdleState` or `RunState`, with a "just arrived from airborne" flag). Presentation is bound to state transitions, not physics or input.
- D) From the collision-resolution code, immediately after the AABB-vs-grid pass sets `grounded = True`.

---

**Q9.** Per Lecture 2 §7, a footstep sound played as a loop while running should be:

- A) Started in `RunState.enter` with `play(name, loop=True)` and stopped in `RunState.exit` with `stop(name)`.
- B) Started in `IdleState.exit`, because that's the state being left.
- C) Played one-shot on every frame the character is in `RunState`.
- D) Mixed in the audio system as an ambient track, independent of state.

---

**Q10.** Nijman's *The Art of Screenshake* enumerates ~20 cheap juice tricks. Week 6's exercises and mini-project implement six of them. The single most-cited and most-effective trick — the one the talk is named after — is:

- A) Sprite-sheet animation.
- B) `lerp`-driven camera follow.
- C) Screen shake, decayed over time, triggered on impacts.
- D) Chromatic aberration.

---

## Answer key

<details>
<summary>Click to reveal answers</summary>

1. **B** — Real-time control, simulated physical space, polish. Swink's three pillars, *Game Feel* (2009). Week 1-5 covered the first two pillars; Week 6 is the third. (Lecture 2 §9.)
2. **C** — `subsurface(rect)` returns a no-copy view. Zero allocation per frame. The whole point of a sprite sheet vs. thirty separate PNGs. (Lecture 1 §2.)
3. **B** — `int(elapsed_t * fps) % len(frames)`. The animation rate is decoupled from the render rate. A 12-fps clip advances every 83 ms regardless of whether the screen is rendering at 30, 60, or 144 fps. (Lecture 1 §5.)
4. **B** — `t = 0.5`. `lerp(a, b, 0.5) = a + (b-a) * 0.5 = (a+b)/2`. Memorise the two lines. (Lecture 2 §1.)
5. **C** — `ease_out_back` is the overshoot curve. The 1.70158 constant is Robert Penner's; values 1.5-2.0 give a ~10% overshoot before settling. Used for "pop" juice on score-changes, button presses, coin pickups. (Lecture 2 §2.)
6. **C** — Squash-and-stretch is on the *art*, not the hitbox. `pygame.transform.scale_by(frame, (1.0, scale_y))` and blit. The collision rectangle does not deform. (Lecture 2 §4, "Three things to notice", item 3.)
7. **C** — 24 px / 400 ms is boss-explosion territory; player hits should be ~6 px / 150 ms; landings ~4 px / 100 ms. The dose matters more than the formula. (Lecture 2 §5, Nijman tuning table.)
8. **C** — Presentation is bound to state transitions. The "arrived from airborne" flag is the canonical cross-state field. Spawning from the input handler or collision code is the "scattered effects" antipattern the lecture explicitly argues against. (Lecture 2 §6, §7.)
9. **A** — `enter()` starts the loop, `exit()` stops it. The pattern that pairs setup with teardown was named in Week 5 Lecture 2 §2 as "asymmetric `enter`/`exit` is the State pattern's version of `malloc` without `free`." Week 6 §7 lights it up with SFX. (Lecture 2 §7.)
10. **C** — Screen shake. Nijman's 30-minute talk is named *The Art of Screenshake* for a reason. Cheap, universal, instantly recognisable. The full talk demos shake on twenty different events; the lecture's exercise implements four. (Lecture 2 §5 and §8; *resources.md* for the talk.)

</details>

---

If you scored under 7, re-read the lecture sections cited in the answers you missed. If you scored 9 or 10, you're ready for the [homework](./homework.md).
