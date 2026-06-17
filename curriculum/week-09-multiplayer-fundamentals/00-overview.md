# Week 9 — Multiplayer Game Fundamentals

Last week you wired a three-bus audio system, ducked dialogue under music, and persisted volume settings to disk. The speakers are now a real subsystem. This week we open the *network socket* — the subsystem indie developers fear most, and the subsystem that turns a single-player toy into a shared experience. By Sunday you ship a tiny LAN-only two-cursor demo: two Pygame clients on the same Wi-Fi see each other's mouse cursor move on a shared canvas, and a Python authoritative server keeps them in sync at 20 Hz over UDP.

Multiplayer is the discipline where bad assumptions become exponentially expensive. A bug in your save system corrupts one player's file; a bug in your network code corrupts every player's experience at once and is unreproducible because it lives between machines. The mid-tier indies who attempt online multiplayer without a *budget* — a latency budget, a bandwidth budget, a packet-loss budget — almost always ship something that works on the developer's LAN and falls apart the moment a player on cable internet joins. None of this is a code-quality problem in the usual sense. It is a *physics* problem: light takes ~5 ms per 1000 km in fibre, and your packet is racing it. The whole job is to design around that constraint.

Glenn Fiedler's free *Networking for Game Programmers* series at [gafferongames.com](https://gafferongames.com/categories/game-networking/) is the single best free resource on the topic; we cite it on every page this week. Godot 4.x's high-level multiplayer API — `MultiplayerAPI`, `MultiplayerSpawner`, `MultiplayerSynchronizer`, `@rpc` annotations — is the production destination of the patterns we hand-build in Python. RFC 768 is the four-page specification of UDP itself; we read it once, because the format of an actual game packet on the wire is a UDP datagram and you should know what one looks like at the byte level.

We start from *Fiedler's series* (in particular *UDP vs. TCP*, *Sending and Receiving Packets*, *Reliability and Flow Control*, and *Snapshot Interpolation*), the *Godot 4.x networking docs*, and *RFC 768*. Four free sources, all linked in `resources.md`. By Sunday you ship **a two-process LAN echo system in raw `socket.SOCK_DGRAM`, a two-cursor shared-canvas demo on top of it in Pygame, and a port of the same demo to Godot 4.x using `MultiplayerSpawner` plus an `@rpc` call**. The Godot port is small — it should be, since Godot does the hard parts — but you write it yourself so the *bridge* from the Python intuition to the production API is concrete in your hands.

This week stays LAN-only. Internet multiplayer requires NAT traversal, relay servers, and a host of operational concerns that are out of scope for a course week. The mental model — authoritative server, UDP transport, snapshot interpolation, latency-aware design — is identical. What we do not build this week is the *plumbing* to expose a LAN server on the open internet. We list the right next steps (Steam Datagram Relay, ENet, raw NAT punch-through, hosted relays) in the resources, but we do not implement them.

## Learning objectives

By the end of this week, you will be able to:

- **Distinguish** the three classic networking models for games — client-server *authoritative*, peer-to-peer *trust-the-peer*, and lockstep *deterministic-simulation* — by name, by one-sentence definition, and by the genre each fits (most action games are authoritative; many RTS games are lockstep; very few modern games are P2P-trust-the-peer for security reasons).
- **Explain** why UDP is the default transport for action games and why TCP, despite its better reliability story, is the wrong choice for most real-time gameplay. The single load-bearing reason: TCP's head-of-line blocking turns one dropped packet into a stall, and the gameplay state from the *next* packet is more valuable than the lost one.
- **Cite** the **latency budget**: ~50 ms one-way (~100 ms round-trip) feels native; up to ~150 ms RTT is playable for most genres; 200-300 ms RTT is the upper edge of "tolerable" for non-twitch games; above 300 ms RTT the game feels wrong. These numbers come from Fiedler and from a generation of public post-mortems.
- **Implement** a UDP echo client and server in raw Python `socket` calls. The server binds to a port, receives a datagram, prepends a sequence number, and sends it back. The client times the round trip and reports a moving-average RTT.
- **Implement** a 20 Hz snapshot loop on top of the echo skeleton: the server sends a snapshot every 50 ms; the client *interpolates* between the two most recent snapshots it has received, ~100 ms behind real time. This is the *snapshot interpolation* technique from Fiedler's series and the load-bearing trick that hides jitter.
- **Implement** a *jitter buffer*: a small queue of recent snapshots, sized to ~2-3 frames of latency, that lets the renderer always have two snapshots to interpolate between even when packets arrive out of order or in bursts.
- **Explain** (not implement, yet) *client-side prediction* and *server reconciliation* at the intuition level. The client runs the simulation locally for its own player without waiting for the server; when the authoritative server's snapshot arrives, the client *reconciles* by replaying any inputs that happened after the snapshot's timestamp. This is how Quake, Counter-Strike, and Rocket League hide latency.
- **Read** RFC 768 and identify the four 16-bit header fields of a UDP datagram (source port, destination port, length, checksum). The whole header is 8 bytes; anything after that is your payload.
- **Translate** the Pygame two-cursor demo into Godot 4.x. The server-bind and client-connect lines become `ENetMultiplayerPeer.create_server` / `.create_client`. The "send my cursor position" loop becomes an `@rpc("any_peer", "call_local", "unreliable")` annotated GDScript function. The state synchronisation becomes a `MultiplayerSynchronizer` node configured in the editor. Same mental model; one-tenth the code.
- **Bandwidth-budget** a multiplayer game. At 20 Hz with 32-byte snapshots and 8 players, the server sends 8 x 32 x 20 = 5120 bytes/sec to each client and 8x that aggregate; well under any modern uplink. Above 64 Hz or with hundreds of players the math demands delta-encoding, area-of-interest filtering, and other techniques out of scope for this week.

## Prerequisites

This week assumes you have completed **Weeks 1-8**. Specifically:

- You have a Week-8 audio system. The mini-project is a different game entirely but reuses the per-frame discipline (event loop at 60 fps, fixed-timestep simulation, careful resource lifetime) from prior weeks.
- You are comfortable with Pygame's event loop and basic input handling from Weeks 4-6.
- You know what an IP address and a port number are. If "127.0.0.1" and "localhost" feel mysterious, skim the *IPv4* and *Transport layer* Wikipedia pages linked in `resources.md` before Monday.
- You can install one third-party package with `pip install pygame` inside a virtual environment.
- You have two machines on the same Wi-Fi *or* you are comfortable running two terminals on the same laptop and connecting one to `127.0.0.1`. Both modes are supported in the exercises.

If any of those are shaky, do the previous week's mini-project before continuing.

## Topics covered

Lecture 1 — Networking models, latency, and why UDP:

- The three networking models. *Client-server authoritative* — the server runs the real simulation; clients are render terminals with a prediction layer. The default for every modern action game. *Peer-to-peer trust-the-peer* — each peer simulates its own state and broadcasts updates; cheap to host but trivially exploitable. *Lockstep deterministic* — every peer receives the same input stream in the same order and runs the same simulation locally; how RTS games sync hundreds of units, vulnerable to one slow peer stalling everyone.
- Why authoritative server wins for action games: cheating becomes a *server-side* problem; the server is the source of truth; the network only carries inputs and snapshots, not the simulation itself.
- The latency budget. ~50 ms one-way feels native. ~150 ms round-trip is the playable ceiling for most genres. ~300 ms feels wrong even on a turn-based game. The numbers come from human perception research and Fiedler's notes.
- *Round-trip time (RTT)*: the time from send to receive of a reply. Measured with a timestamped ping-pong. The number every multiplayer programmer watches.
- *Jitter*: the *variance* in RTT. A connection with 100 ms RTT and 5 ms jitter is excellent; the same 100 ms with 80 ms jitter is unplayable because the snapshot interpolation cannot smooth such a wide window.
- *Packet loss*: the fraction of packets that never arrive. Anything over 1% is bad; 5% is the threshold where most games become miserable. UDP exposes loss; TCP hides it at the cost of head-of-line blocking.
- UDP vs TCP. TCP guarantees in-order delivery; the cost is that *one* lost packet stalls everything behind it until the loss is recovered (head-of-line blocking). For a game where each packet contains the *latest* state, the lost packet is already obsolete by the time you would retransmit it; you want the new one. UDP delivers what arrives, drops what does not, and lets the application decide.

Lecture 2 — Snapshot interpolation, jitter buffers, prediction, and reconciliation:

- The *snapshot* model: at fixed cadence (typically 10-30 Hz) the server serialises the world state and broadcasts it to every client. Clients render *behind* real time — typically ~100 ms behind — so that for any rendered frame they have two received snapshots to interpolate between.
- *Snapshot interpolation*: a smoothing technique. For render time `t_render = t_now - INTERP_DELAY_MS`, find the two snapshots whose server-timestamps bracket `t_render`, and linearly interpolate every entity's state between them. The result is silky-smooth motion even on a 20 Hz server tick.
- The *jitter buffer*: the queue of recent snapshots from which interpolation reads. Sized to hold at least the interp delay's worth of snapshots plus margin. ~3 snapshots at 20 Hz = 150 ms of buffer is typical.
- *Client-side prediction* (intuition only): the player's own input is laggy if you wait for the server to acknowledge it. So the client runs the simulation *locally* for its own player using the same code the server runs, and accepts that the server may correct it.
- *Server reconciliation* (intuition only): when the server's snapshot arrives, the client rewinds its local prediction to the snapshot's authoritative state, then re-applies every input that happened after the snapshot's timestamp. If prediction was correct, the player sees nothing; if it was wrong (e.g. the player ran into a wall the client did not know about), the visible "snap" is the correction.
- *Lag compensation* (mentioned, not implemented): the server, when processing a player's "shoot" command, rewinds *its own* world state to where the player saw it at the moment they clicked. This is how hit detection feels fair in shooters. Out of scope for this week.
- The state-vs-event split. *State* is "the position of every entity right now"; sent via snapshots; can be missed without permanent damage (the next snapshot covers it). *Events* are "player A scored a point"; must be delivered reliably even over UDP; layered on top with a tiny reliability protocol or a parallel TCP channel.

Lecture 3 — The Godot 4.x bridge: high-level multiplayer API:

- Godot's networking stack at a glance: `MultiplayerAPI` is the orchestrator, `MultiplayerPeer` is the transport (most commonly `ENetMultiplayerPeer`, which wraps UDP with optional per-channel reliability), `MultiplayerSpawner` replicates node creation, `MultiplayerSynchronizer` replicates node state.
- The `@rpc` annotation. `@rpc("any_peer", "call_local", "unreliable")` declares that a function can be invoked across the network; the four arguments encode who can call it, whether it also runs locally, ordering, and transport reliability. Every multiplayer interaction in Godot funnels through `@rpc`.
- `MultiplayerSpawner` — when the server adds a node under a specific parent, Godot automatically spawns the same node on every client. The "join the game" flow is one node-add on the server.
- `MultiplayerSynchronizer` — declares which properties of a node are network-replicated, at what rate, and over which channel. Configured in the editor; no GDScript needed for the common case.
- The single biggest mental shift: in Pygame, *you* serialise, send, receive, and deserialise every byte. In Godot, you annotate a function with `@rpc` and *Godot* serialises, sends, receives, and dispatches. Almost all your hand-written code from the Python exercises disappears. The *thinking* — authoritative server, latency budget, snapshot interpolation as the consumer-side smoothing — does not.
- Hosting realities. ENet only handles LAN out of the box. For internet multiplayer, you need Steam Datagram Relay (`MultiplayerPeerSteam`), a custom relay server, or a service like Nakama. Linked in resources; not in scope this week.

## Weekly schedule

The schedule below adds up to approximately **33 hours**. Treat it as a target. Networking is deceptively quick to make work *on localhost* and deceptively slow to make work *across two real machines*.

| Day       | Focus                                          | Lectures | Exercises | Challenges | Quiz/Read | Homework | Mini-Project | Self-Study | Daily Total |
|-----------|------------------------------------------------|---------:|----------:|-----------:|----------:|---------:|-------------:|-----------:|------------:|
| Monday    | Lecture 1 + first UDP echo                     |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0h       |    0.5h    |     5.5h    |
| Tuesday   | Lecture 2 + snapshot loop + jitter buffer      |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0.5h     |    0h      |     5.5h    |
| Wednesday | Two-cursor Pygame demo end-to-end              |    0h    |    1.5h   |     0.5h   |    0.5h   |   1h     |     1.5h     |    0.5h    |     5.5h    |
| Thursday  | Lecture 3 + read Godot networking docs         |    2h    |    0.5h   |     1h     |    0.5h   |   1h     |     1h       |    0h      |     6h      |
| Friday    | Godot port of the cursor demo                  |    0h    |    0h     |     0.5h   |    0.5h   |   1h     |     2h       |    0.5h    |     4.5h    |
| Saturday  | Mini-project polish + README + demo capture    |    0h    |    0h     |     0h     |    0.5h   |   0.5h   |     2.5h     |    0h      |     3.5h    |
| Sunday    | Reflection, push, prepare for Week 10          |    0h    |    0h     |     0h     |    0.5h   |   0h     |     1.5h     |    0.5h    |     2.5h    |
| **Total** |                                                | **6h**   | **5h**    | **2h**     | **3.5h**  | **5.5h** | **9h**       | **2h**     | **33h**     |

## How to navigate this week

| File | What is inside |
|------|----------------|
| [README.md](./00-overview.md) | This overview (you are here) |
| [resources.md](./01-resources.md) | Fiedler's series, Godot networking docs, RFC 768, Wikipedia primers, free packet inspection tools |
| [lecture-notes/01-networking-models-latency-and-udp.md](./02-lecture-notes/01-networking-models-latency-and-udp.md) | The three models; the latency budget; UDP vs TCP; sockets at the byte level; RFC 768 |
| [lecture-notes/02-snapshots-interpolation-prediction-reconciliation.md](./02-lecture-notes/02-snapshots-interpolation-prediction-reconciliation.md) | The snapshot loop; jitter buffer; client-side prediction; server reconciliation; state vs events |
| [lecture-notes/03-godot-multiplayer-api-and-the-rpc-pattern.md](./02-lecture-notes/03-godot-multiplayer-api-and-the-rpc-pattern.md) | MultiplayerAPI, ENet, @rpc, MultiplayerSpawner, MultiplayerSynchronizer, hosting realities |
| [exercises/exercise-01-udp-echo.py](./03-exercises/exercise-01-udp-echo.py) | A raw `socket.SOCK_DGRAM` echo client + server in one file, with a moving-average RTT meter |
| [exercises/exercise-02-snapshot-loop.py](./03-exercises/exercise-02-snapshot-loop.py) | A 20 Hz server snapshot loop and a client jitter-buffered interpolator, headless |
| [exercises/exercise-03-two-cursors-pygame.py](./03-exercises/exercise-03-two-cursors-pygame.py) | The capstone exercise: two Pygame clients see each other's mouse cursor on a shared canvas |
| [exercises/exercise-04-godot-cursor-rpc.gd](./03-exercises/exercise-04-godot-cursor-rpc.gd) | The Godot 4.x port: an `@rpc` cursor-position broadcaster (read-only reference, with a setup README) |
| [exercises/SOLUTIONS.md](./03-exercises/SOLUTIONS.md) | Solution discussion and the "common bugs" list for each exercise |
| [challenges/challenge-01-measure-your-link.md](./04-challenges/challenge-01-measure-your-link.md) | A measurement exercise: `ping`, `traceroute`, packet capture, and a written RTT-distribution report |
| [challenges/challenge-02-design-a-rollback-netcode-sketch.md](./04-challenges/challenge-02-design-a-rollback-netcode-sketch.md) | A paper-design exercise: sketch a rollback netcode design for a two-player fighting game |
| [quiz.md](./05-quiz.md) | Ten multiple-choice questions |
| [homework.md](./06-homework.md) | Six practice problems for the week |
| [mini-project/README.md](./07-mini-project/00-overview.md) | The two-cursor shared canvas with an authoritative server, jitter buffer, and a 20-second demo |
| [mini-project/starter_server.py](./07-mini-project/starter_server.py) | The authoritative server scaffold: bind socket, accept HELLO, broadcast snapshots at 20 Hz |
| [mini-project/starter_client.py](./07-mini-project/starter_client.py) | The Pygame client scaffold: connect, send mouse, interpolate the cursor list, render |

## Frame budget for this week

A reminder of what 60 fps means in milliseconds. The network subsystem runs every frame, but it is *not* CPU-bound on a sensible design — `select` / non-blocking sockets cost microseconds per poll.

```
+---------------------------------------------------------+
|  FRAME BUDGET - 60 fps target, with a 20 Hz network tick|
|                                                         |
|  Input poll:       ~0.2 ms                              |
|  Network drain:    ~0.3 ms  (recvfrom in a non-block    |
|                              loop until EAGAIN)         |
|  Snapshot interp:  ~0.2 ms  (find bracket + lerp)       |
|  Update (sim):     ~1.4 ms                              |
|  Animation tick:   ~0.3 ms                              |
|  Render (entity):  ~1.5 ms                              |
|  HUD draw:         ~0.4 ms  (RTT, jitter, ping count)   |
|  Audio dispatch:   ~0.4 ms                              |
|  GPU + present:    ~4.0 ms                              |
|  Headroom:         ~7.9 ms                              |
|  ---------------------                                  |
|  Total:           ~16.6 ms / frame                      |
+---------------------------------------------------------+
```

The 0.3 ms "Network drain" budget covers our per-frame work: a `while True: try: sock.recvfrom(...) except BlockingIOError: break` loop that drains every queued packet from the kernel's socket buffer. The actual sending is even cheaper; a 32-byte snapshot copy into the buffer takes a few microseconds. If you ever see network drain exceed 1 ms on a profiler, you are probably calling `recvfrom` in *blocking* mode and stalling the game loop. Always set the socket non-blocking and drain in a loop.

## Stretch goals

If you finish early and want to push further:

- **Read every chapter of Glenn Fiedler's *Networking for Game Programmers* series**. It is shorter than you expect (~3 hours total). Pay particular attention to *Reliability and Flow Control* and *State Synchronisation* — they describe the next layer up from what we build this week.
- **Implement client-side prediction for the cursor.** Have the local cursor render at the client's *current* mouse position (no interpolation) while remote cursors render through the jitter buffer. The visible difference is striking.
- **Add a tiny reliability layer.** Define a 16-bit packet ID and an ACK; resend any packet that has not been ACKed within 200 ms. This is the seed of Fiedler's reliability article.
- **Run the demo across two real machines on your home Wi-Fi.** The localhost demo lies; the real demo reveals jitter, packet loss, and "why is my router so slow." Measure with Wireshark.
- **Implement the Godot port of the snapshot loop**, not just the cursor demo. Use `MultiplayerSynchronizer` to replicate 8 entity positions and `@rpc("authority", "call_remote", "unreliable")` to push them at 20 Hz. Compare line counts against the Pygame version.
- **Capture packets with Wireshark** on the loopback interface. Filter `udp.port == 5005`. Look at the actual datagram bytes; identify the 8-byte UDP header from RFC 768; identify your payload. This makes the abstract `sendto` call concrete.
- **Read RFC 768 in full.** It is four pages. There is no excuse not to.

## Voice rules for the week

- We define **authoritative server** as "the server runs the real simulation; clients are render terminals." It is not "the server is in charge of authentication" (that is a different sense of authority). The simulation is the authoritative artefact.
- We credit **Glenn Fiedler's *Networking for Game Programmers* series at gafferongames.com** as the canonical free reference for everything in this week's lectures. We link the exact URLs once and refer to "Fiedler" thereafter.
- We credit **Godot 4.x networking documentation** as the bridge to production. We write a small amount of GDScript this week; we read its documentation pages so the APIs look familiar.
- We credit **RFC 768** as the four-page specification of UDP itself. We do not embellish it; the spec is the spec.
- We **prefer UDP for game traffic** and **avoid TCP** for real-time gameplay state. We do not relitigate this; the reasoning is in Lecture 1 §3.
- We **never** ship "send and pray" reliability for events that matter (player joins, scores, match results). State is best-effort; events are layered with a reliability protocol or a parallel reliable channel. The Pygame exercises this week implement state-only; the mini-project optionally adds a HELLO/WELCOME reliable handshake.
- We **respect the LAN-only scope of this week**. Internet multiplayer involves NAT traversal, hosted relays, and operational concerns we do not have time for. We name them; we do not ship them.
- We **measure** before we optimise. The exercises ship a moving-average RTT and packet-loss meter; we read those numbers before we change anything.

## Up next

Continue to [Week 10 — Networking II: Reliability, NAT, and Session Lifecycle](../week-10/) once you have pushed your two-cursor demo. Week 10 takes the LAN-only scope of this week and adds the reliability protocol, NAT traversal sketch, and the session-lifecycle (lobby, join, disconnect, rejoin) state machine that real multiplayer games carry.

---

*If you find errors in this material, please open an issue or send a PR. Future learners will thank you.*
