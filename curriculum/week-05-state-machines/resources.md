# Week 5 — Resources

Every resource on this page is **free** and **publicly accessible** unless explicitly noted as "excerpts free." No paywalled books, no proprietary PDFs. If a link breaks, please open an issue.

## Required reading (work it into your week)

- **Bob Nystrom — *Game Programming Patterns*, chapter "State."** The single most important free reading of this whole week. Forty minutes. Read before Lecture 2. The book is online in full, gratis:
  <https://gameprogrammingpatterns.com/state.html>
- **Bob Nystrom — *Game Programming Patterns*, chapter "Update Method."** Re-read this from Week 1's resources; it pairs cleanly with State because every state's `update(dt)` is one example of the Update Method pattern:
  <https://gameprogrammingpatterns.com/update-method.html>
- **Python `enum` documentation.** You'll spend the week writing `class State(Enum): IDLE = "idle"; RUN = "run"; ...`. Skim once:
  <https://docs.python.org/3/library/enum.html>

## Robert Nystrom — *Game Programming Patterns* (free online, full book)

Already linked above. The chapters relevant this week:

- **State** (the State pattern, with a worked Heroine example that is the *exact* shape of this week's mini-project):
  <https://gameprogrammingpatterns.com/state.html>
- **Update Method** (still relevant; each state's `update(dt)` is an Update Method):
  <https://gameprogrammingpatterns.com/update-method.html>
- **Component** (next-level architecture — the State and Component patterns interact when one entity has multiple state machines, e.g. movement-state + weapon-state):
  <https://gameprogrammingpatterns.com/component.html>
- **Bytecode** (if you want to go deep on data-driven AI; not required, but the natural next step after FSMs):
  <https://gameprogrammingpatterns.com/bytecode.html>

## Industry-standard FSM writing (free or excerpts free)

- **Robert Green — *AI Game Programming Wisdom* (book series, 2002-2008).** The book is paywalled but the FSM chapters of Volume 1 ("The Basics of Finite-State Machines") have been excerpted across the web. Search for the exact phrase. The series is what gave gamedev its shared FSM vocabulary.
- **Brian Schwab — *AI Game Engine Programming* (excerpts free).** The state-pattern chapter is a careful walk-through that complements Nystrom's:
  <https://www.charlesriver.com/Products/AIGameEngine/>
- **Game AI Pro (Steve Rabin, ed.) — free online articles.** A community-edited follow-on to *AI Game Programming Wisdom*. Several chapters are FSM or hierarchical-FSM:
  <http://www.gameaipro.com/>

## State machines outside game dev (worth the cross-pollination)

- **David Harel — *Statecharts: A Visual Formalism for Complex Systems* (1987).** The foundational paper on hierarchical state machines. PDF is freely circulated as a classic:
  <https://www.inf.ed.ac.uk/teaching/courses/seoc/2005_2006/resources/statecharts.pdf>
- **Miro Samek — *Practical UML Statecharts in C/C++* (book; first three chapters free).** Statecharts done industrially. The first three chapters explain HFSMs better than any 2025-era blog post:
  <https://www.state-machine.com/doc/PSiCC2.pdf>
- **XState docs (JavaScript state-machine library).** The docs are an excellent FSM tutorial even if you never write JavaScript. The visual statechart editor is free:
  <https://stately.ai/docs>

## Pygame-specific (free)

- **Pygame `pygame.event` and `pygame.key`.** You'll read both this week. Events drive transitions; key-state drives in-state behaviour:
  <https://www.pygame.org/docs/ref/event.html>
  <https://www.pygame.org/docs/ref/key.html>
- **Pygame `pygame.sprite.Sprite`.** Once you have a state machine, the natural shape for the player is a `Sprite` whose `update(dt)` delegates to the current state. The sprite-group docs help:
  <https://www.pygame.org/docs/ref/sprite.html>
- **Pygame Wiki — "Game with state."** Old but the pattern is still right. A useful counterpoint to the State pattern: this is what beginners usually write:
  <https://www.pygame.org/wiki/tutorials>

## Talks and videos (free)

- **GDC — *AI Workshop: The Magic of State Machines* (David "Rez" Graham).** Free on the GDC Vault and on YouTube. One hour, dense, indie-friendly:
  <https://www.youtube.com/@Gdconf>
- **GDC — *Building the AI of F.E.A.R.* (Jeff Orkin).** F.E.A.R. used GOAP (goal-oriented action planning), which sits above FSMs. The talk explains *why* you eventually outgrow plain FSMs and is essential context:
  <https://www.youtube.com/results?search_query=jeff+orkin+fear+ai+gdc>
- **GDC — *Animation Bootcamp* (multiple speakers, multiple years).** The animation-state-machine talks are where Week 5 meets Week 6. Watch the *Halo*, *Tomb Raider*, and *Insomniac Games* sessions specifically:
  <https://www.gdcvault.com/>
- **Sebastian Lague — *AI for Beginners: Finite-State Machines*.** A clean fifteen-minute primer with code, free on YouTube. Unity, not Pygame, but the *vocabulary* is exactly what we use:
  <https://www.youtube.com/@SebastianLague>
- **Mark Brown — *Game Maker's Toolkit — Why Does Celeste Feel So Good to Control?*** *Celeste* is a public, well-documented FSM-driven platformer. Brown's analysis is the design counterpart to Lecture 2:
  <https://www.youtube.com/c/GameMakersToolkit>

## Code to read (open-source games with public FSMs)

Reading other people's state machines is the single fastest way to internalise the pattern. All four below are MIT/BSD/zlib licensed and have FSMs you can read in an afternoon.

- **Celeste — the Madeline character is a public, well-commented C# FSM.** Maddy Thorson and Noel Berry open-sourced the original 2017 PICO-8 prototype:
  <https://github.com/NoelFB/Celeste>
- **Open Hexagon (by vittorio romeo) — small, readable C++ game with an FSM-driven game state:**
  <https://github.com/SuperV1234/SSVOpenHexagon>
- **Mari0 (a fan-made Mario clone) — LÖVE/Lua, character states are tagged in source:**
  <https://github.com/Stabyourself/mari0>
- **Pygame community — `pygame-fsm` and similar small libraries on GitHub.** Read the source, not the README. Most are 200 lines:
  <https://github.com/topics/pygame-fsm>

## Python state-machine libraries (you don't need them this week, but they exist)

You can complete this week with pure stdlib. The libraries below are excellent and you should know they exist for later projects, but resist using them this week — the State pattern is the lecture.

- **`python-statemachine`.** The most popular pure-Python FSM library. Declarative, has graph-export. Good for application code; overkill for character AI:
  <https://pypi.org/project/python-statemachine/>
- **`transitions`.** Compact, hierarchical-state-machine support. Used in some game projects:
  <https://github.com/pytransitions/transitions>
- **`automat`.** Twisted's state-machine library. Production-grade for protocols. Almost never the right tool for games, but worth knowing exists:
  <https://github.com/glyph/automat>

## Books and longer-form (free or excerpts free)

- **Bob Nystrom — *Game Programming Patterns* (free, full).** Already linked. Read **State** and **Update Method** this week.
  <https://gameprogrammingpatterns.com/>
- **Ian Millington — *Artificial Intelligence for Games* (3rd ed., chapter excerpts free).** The "Decision Making" chapter covers FSMs, decision trees, and behaviour trees in the same breath. After this week, behaviour trees are the natural next stop:
  <https://www.routledge.com/Artificial-Intelligence-for-Games/Millington/p/book/9781138483972>
- **Jesse Schell — *The Art of Game Design* (chapter excerpts free).** *Lens of Character* applies to AI-driven NPCs as well as players. Read it once:
  <http://www.artofgamedesign.com/>

## Glossary cheat sheet

Keep this open in a tab.

| Term | Plain English |
|------|---------------|
| **State** | One of the mutually-exclusive behaviour modes a character can be in (e.g. `idle`, `run`, `jump`). |
| **Event** | A trigger that may cause a transition (e.g. `jump_pressed`, `landed`, `hit_detected`). Not the same as a state. |
| **Transition** | The move from one state to another, fired by an event. Has a precondition; may have side effects (play a sound, reset a timer). |
| **FSM (finite state machine)** | A set of states + a set of events + a transition function from `(state, event)` to a new state. |
| **HFSM (hierarchical FSM)** | An FSM where one state can contain its own sub-FSM. The `airborne` superstate has `jump` and `fall` substates. |
| **State pattern** | Nystrom's name for "one class per state, polymorphic dispatch." The OOP shape of an FSM. |
| **Pushdown automaton** | An FSM with a *stack* of states instead of a single current state. Pause menus, dialog overlays. |
| **`enter()`** | The lifecycle hook that runs once when a state is entered. Where you start animations, reset timers, play sounds. |
| **`exit()`** | The lifecycle hook that runs once when a state is left. Where you stop animations, clear timers. |
| **Transition table** | A dict (or 2D array) of allowed transitions: `(from_state, event) -> to_state`. Data, not code. |
| **Illegal transition** | An event arriving in a state where it has no defined transition. Should log loudly, never silently no-op. |
| **State leak** | A bug where one state mutates a field that another state later misinterprets. The classic FSM bug. |
| **Animation state machine** | The visual-cousin FSM used by animators. States hold animation clips; transitions blend between them. Week 6 territory. |
| **Behaviour tree** | The pattern that supersedes FSMs once you have more than ~15 states. Outside this week, but on the horizon. |

---

*If a link 404s, please [open an issue](https://github.com/CODECRUNCHWORLDWIDE) so we can replace it.*
