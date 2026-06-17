# Week 1 — Quiz

Ten multiple-choice questions. Take it with your lecture notes closed. Aim for 9/10 before moving to Week 2. Answer key at the bottom — don't peek.

---

**Q1.** Which of the following is the canonical order of the three steps in a game loop?

- A) `render → input → update`
- B) `update → input → render`
- C) `input → update → render`
- D) `input → render → update`

---

**Q2.** What happens if your Pygame loop runs forever without ever calling `pygame.event.get()` (or `pygame.event.pump()`)?

- A) Nothing — the OS doesn't care.
- B) The window appears, then freezes, and the OS marks the app "not responding" because event-queue activity is the OS's liveness check.
- C) The CPU pegs at 100% but the window is fine.
- D) Pygame raises an exception after 1 second.

---

**Q3.** A player has a 144 Hz monitor. Your circle code is `x += 5` inside the loop. Compared to a 60 Hz monitor, what does the player observe?

- A) The circle moves at the same speed; Pygame normalises automatically.
- B) The circle moves about 2.4x faster on the 144 Hz monitor.
- C) The circle moves about 2.4x slower on the 144 Hz monitor.
- D) The circle does not move at all unless you explicitly opt into 144 Hz.

---

**Q4.** Which is the correct way to make a circle's movement frame-rate-independent?

- A) `pos += speed_per_frame` and trust `clock.tick(60)` to handle it.
- B) `pos += speed_per_second * dt`, where `dt` is seconds since the previous frame.
- C) `pos += speed_per_second / fps`, where `fps` is the current frame rate.
- D) `pos = pos + speed * pygame.time.get_ticks()`.

---

**Q5.** You write `dt = clock.tick(60) / 1000`. What units is `dt` in, and why?

- A) Milliseconds — `clock.tick` returns ms directly.
- B) Seconds — `clock.tick` returns ms, and we divide by 1000 to convert.
- C) Frames — `clock.tick` returns a frame count.
- D) Microseconds — Pygame's internal unit is µs.

---

**Q6.** Which Pygame function should you use to read held movement keys like WASD?

- A) `pygame.event.get()` with `event.type == pygame.KEYDOWN`.
- B) `pygame.key.get_pressed()` each frame.
- C) `pygame.input.read_keyboard_state()`.
- D) `sys.stdin.read()`.

---

**Q7.** A player presses W and D together. Your code does `if K_w: y -= speed*dt` and `if K_d: x += speed*dt`. What's wrong?

- A) Nothing — that's the canonical pattern.
- B) The player moves about 1.41x faster on the diagonal because the resulting vector has magnitude `sqrt(speed² + speed²)`.
- C) The player can't move at all — the keys cancel.
- D) Pygame raises a key-conflict error.

---

**Q8.** At a 60 fps target, your frame budget per loop iteration is approximately:

- A) 1.0 ms
- B) 16.6 ms
- C) 60 ms
- D) 100 ms

---

**Q9.** Why do we clamp `dt` (e.g. `dt = min(dt, 1/30)`) inside the game loop?

- A) Pygame's `Clock` returns negative values on overflow.
- B) A long frame (the player tabbed out, the debugger paused) returns a huge `dt`, which when multiplied by velocity can teleport objects and corrupt game state.
- C) The CPU heats up if `dt` exceeds 33 ms.
- D) It's required by the Pygame API.

---

**Q10.** Godot's `_process(delta)` and Pygame's hand-rolled game loop are best described as:

- A) Completely unrelated — Godot uses a different paradigm.
- B) The same idea, different syntax. Both pass elapsed time to your update code each frame.
- C) Identical — Godot's `_process` is implemented in Pygame under the hood.
- D) Godot is for 3D only; the comparison doesn't apply.

---

## Answer key

<details>
<summary>Click to reveal answers</summary>

1. **C** — `input → update → render`. Input must be first so update sees the current frame's input; render must be last so it shows the just-updated world. (Lecture 1 §2.)
2. **B** — The OS uses event-queue activity as a liveness check. Stop pumping it and the OS shows "not responding". (Lecture 1 §4.)
3. **B** — At 144 fps the loop runs 2.4x more often, so a per-frame increment moves the circle 2.4x further per second. This is the canonical "naive bug". (Lecture 2 §1.)
4. **B** — Pixels per second times seconds equals pixels. The math should be in physical units, not frame units. (Lecture 2 §2.)
5. **B** — `clock.tick` returns elapsed milliseconds; dividing by 1000 yields seconds. Keep your update code in seconds; convert at the boundary. (Lecture 2 §2.)
6. **B** — `pygame.key.get_pressed()` returns the current key state every frame, perfect for held movement. `KEYDOWN` fires once per press and is for one-shot actions. (Lecture 2 §8.)
7. **B** — Diagonal vectors have magnitude `~1.41x` an axis-aligned vector. You must normalise the direction vector before multiplying by speed. (Lecture 2 §9.)
8. **B** — `1 / 60 ≈ 0.0166 s = 16.6 ms`. Memorise this number. (Lecture 2 §3.)
9. **B** — A frame that took 10 seconds (alt-tab) returns `dt = 10.0`. Multiplied by a 300 px/s speed, the player jumps 3000 pixels — game state corruption. (Lecture 2 §4.)
10. **B** — Both engines compute delta time and pass it to user-supplied per-frame code. Pygame makes you write the `while` loop; Godot writes it for you and calls `_process(delta)`. Same idea. (Lecture 1 §6.)

</details>

---

If you scored under 7, re-read the lecture sections cited in the answers you missed. If you scored 9 or 10, you're ready for the [homework](./06-homework.md).
