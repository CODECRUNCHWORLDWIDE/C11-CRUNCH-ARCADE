# Week 3 — Quiz

Ten multiple-choice questions. Take it with your lecture notes closed. Aim for 9/10 before moving to Week 4. Answer key at the bottom — don't peek.

---

**Q1.** Steve Swink's definition of *game feel* names three pillars. Which set is correct?

- A) Graphics, audio, controls.
- B) Input response, simulated space, polish.
- C) Mechanics, dynamics, aesthetics.
- D) Intention, perceivable consequence, story.

---

**Q2.** Lecture 1 argues that "juice is information, not decoration." What is the most direct consequence of that claim for your design?

- A) Every juice effect should answer a specific player question (what happened, how big, was it good).
- B) Every juice effect should be as flashy as possible to grab attention.
- C) Juice should be applied uniformly to every event in the game.
- D) Juice can be added at the very end of development, after all mechanics ship.

---

**Q3.** A common beginner mistake is applying screen shake to BOTH the world and the HUD. Why is that wrong?

- A) It costs too much CPU.
- B) Pygame doesn't support shaking surfaces.
- C) The HUD is the player's anchor; shaking it makes the screen read as a glitch rather than an impact, and obscures information.
- D) Screen shake is purely cosmetic; it doesn't matter where it's applied.

---

**Q4.** In the MDA framework (Hunicke, LeBlanc, Zubek, 2004), the designer perceives the game in which order, and the player perceives it in which order?

- A) Designer: A → D → M. Player: M → D → A.
- B) Designer: M → D → A. Player: A → D → M.
- C) Both perceive M → D → A.
- D) Both perceive A → D → M.

---

**Q5.** Doug Church's 1999 essay names four lenses. Which set is correct?

- A) Mechanics, Dynamics, Aesthetics, Polish.
- B) Sensation, Challenge, Fellowship, Discovery.
- C) Intention, Perceivable Consequence, Story, Goals.
- D) Input, Update, Render, Audio.

---

**Q6.** You add a screen-shake effect that lasts 2.5 seconds at constant 12-px magnitude. A playtester says "the game crashed." Why?

- A) Their machine couldn't render the shake.
- B) A long-duration constant-magnitude shake reads as a persistent broken state, not as an impact. Shakes need to decay quickly (typically ≤ 350 ms).
- C) Pygame can't render shakes longer than 1 second.
- D) The tester is wrong; the effect is correct.

---

**Q7.** Pygame's `mixer` has a default audio buffer of 4096 samples at 44.1 kHz. What's the perceptual problem with the default, and what's the canonical fix?

- A) No problem; the default is fine.
- B) Default produces ~90 ms of audio latency, which feels disconnected from the visuals. Call `pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)` *before* `pygame.init()` to drop latency to ~12 ms.
- C) Default uses too little CPU. Increase the buffer to 16384.
- D) Default plays at the wrong sample rate; switch to 22050 Hz.

---

**Q8.** Which of the following is the BEST candidate for the "Sensation" aesthetic (per MDA's eight aesthetics) in your brick-breaker?

- A) A title screen with a story crawl.
- B) A juicy brick-destruction effect — particles + shake + audio — that makes each hit feel substantial.
- C) A high-score leaderboard.
- D) An online multiplayer mode.

---

**Q9.** A particle list in Pygame, naively managed, leaks memory over time. What is the canonical fix?

- A) Use `pygame.sprite.Group` (which auto-cleans dead sprites).
- B) Filter the list each frame to keep only particles whose `age < lifetime`. Equivalently, pre-allocate a fixed-size pool and recycle slots.
- C) Call `gc.collect()` every frame.
- D) Particles don't leak; the question is wrong.

---

**Q10.** A tester says "I don't know what to do" while playing your brick-breaker. Per Lecture 2 §5's translation table, the most likely framework-level problem is:

- A) Weak **Mechanics** — add more rules.
- B) Weak **Goals** (Church) — add a visible objective, counter, or clear win-state.
- C) Weak **Aesthetics** — add more particles.
- D) Weak **Audio** — add background music.

---

## Answer key

<details>
<summary>Click to reveal answers</summary>

1. **B** — Swink (2009): real-time control + simulated space + polish. A is too vague; C is MDA, not Swink; D is Church's four lenses. (Lecture 1 §1.)
2. **A** — Juice as information means every effect carries a signal. Effects that don't answer player questions are noise; over time the brain filters them out. (Lecture 1 §4.)
3. **C** — The HUD is screen-space; the world is world-space. Shaking screen-space UI destroys the anchor the player uses to read information. (Exercise 1 hint block.)
4. **B** — The designer ships M and reasons forward to A; the player feels A and (sometimes) reasons backward to M. Knowing this is the single most useful thing MDA gives you. (Lecture 2 §3.2.)
5. **C** — Intention, Perceivable Consequence, Story, Goals. The other lists are MDA (A), MDA aesthetics (B), and the game-loop phases (D). (Lecture 2 §2.)
6. **B** — Decay is the difference between "impact" and "broken." 80–350 ms with a clear decay curve is the standard. (Lecture 1 §5, table.)
7. **B** — The 90 ms default latency is one of the most-skipped Pygame fixes. 512-sample buffer at 44.1 kHz yields ~12 ms — perceptually instant. (Lecture 1 §8.)
8. **B** — Brick-breaker primarily targets Sensation and Challenge (MDA §3.3, §3.4). A juicy destruction effect is the canonical reinforcement of Sensation. (Lecture 2 §3.3, §3.4.)
9. **B** — Either filter-each-frame or an object pool (Nystrom's *Game Programming Patterns*). The naive `append-forever` pattern leaks. (Lecture 1 §7; resources.md — Object Pool.)
10. **B** — "I don't know what to do" is a Goals-level signal in Church's vocabulary. Add a visible objective, a counter, or a clear win-state. (Lecture 2 §5.)

</details>

---

If you scored under 7, re-read the lecture sections cited in the answers you missed. If you scored 9 or 10, you're ready for the [homework](./homework.md).
