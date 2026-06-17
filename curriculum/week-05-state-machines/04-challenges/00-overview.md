# Week 5 — Challenges

The exercises drill the systems. **Challenges stretch you toward shippable artefacts.** This week's challenge takes the State pattern from the player and applies it to an *enemy* — a patrolling guard with `patrol` / `chase` / `attack` / `return` states. Same pattern, different intent: the player's transitions are driven by *inputs*; the enemy's are driven by *observation* (line-of-sight, distance, attack range).

## Index

1. **[Challenge 1 — Enemy AI FSM](./challenge-01-enemy-ai-fsm.md)** — a patrolling enemy with four states: `patrol`, `chase`, `attack`, `return`. The enemy uses line-of-sight against a single static obstacle to decide whether to chase. The player is a Coin-Pink square you can drive with the arrow keys; the enemy is a Power-Up-Cyan square that hunts you. (~120 min including the AI tuning.)

Challenges are optional. If you skip this one you can still pass the week — but enemy AI is the *next* thing you'll want after your player has a state machine, and doing the challenge first means the rest of the course's NPC writing becomes "I have written this shape before." The Week 11 capstone usually involves at least one enemy; this week's challenge is where most students get their first one.

## How to work the challenges

- Read the spec end-to-end before you open your editor.
- **Draw the enemy's state diagram on paper before you write the code.** Five boxes, six or seven arrows. If you can't draw it, you can't code it.
- Use the same `State` base class from Exercise 2. The enemy is a *different character*, but it's the same shape of FSM. Reusing the pattern is the whole point of having one.
- Commit each state file (or each state class, if you keep them in one file) in its own commit. Future-you reviewing the diff will appreciate it.

Challenges live under your portfolio repo at `c11-week-05-<yourhandle>/challenges/challenge-01/`. The mini-project repo is separate but will reuse the same FSM scaffolding.
