# Week 4 — Challenges

The exercises drill the systems. **Challenges stretch you toward shippable artefacts.** This week's challenge is *building a real level-select pipeline* — three CSV levels loaded from disk, picked from a menu, replayable.

## Index

1. **[Challenge 1 — Three Loadable Levels](./challenge-01-3-loadable-levels.md)** — ship three CSV levels and a level-select screen. The same engine loads all three. Level 1 is hand-authored to be easy, Level 2 introduces vertical platforms, Level 3 is a maze. The constraint is that *only the data files change* — your loader code stays still. (~120 min including the level-design work.)

Challenges are optional. If you skip this one you can still pass the week — but this is the exact artefact the mini-project builds on, and doing the challenge first means the mini-project (a 2D platformer with three loadable levels) becomes "add jump physics and AABB-vs-grid collision to a thing that already loads three levels." The challenge is the cheap path to the mini-project.

## How to work the challenges

- Read the spec end-to-end before you open Tiled or your text editor.
- **Author the levels before you write the level-select code.** It is tempting to build the menu first because menus feel like programming. Resist. The level design is the *content*; the menu is plumbing for the content. Build the content first.
- Use the same launcher script for all three levels. If you find yourself writing per-level branches, stop — that's a sign the engine and the data are still tangled.
- Commit each level file in its own commit. Future-you reviewing the diff will appreciate it.

Challenges live under your portfolio repo at `c11-week-04-<yourhandle>/challenges/challenge-01/`. The mini-project repo is separate but will reuse the same loader.
