# Mini-Project — Two Cursors on a Shared Canvas

> Build a polished LAN-only multiplayer demo: an authoritative Python server and a Pygame client that renders the local cursor at its OS position, the remote cursor through a 100 ms snapshot-interpolation jitter buffer, and a HUD showing peer count, jitter buffer size, and RTT. Two clients on the same LAN see each other's cursor move on a shared 1024 x 768 canvas. Add a tiny HELLO/WELCOME reliable handshake on top of the otherwise-unreliable channel. Record a 20-second demo. Write a 250-word reflection that contrasts the Python implementation with the Godot port from Exercise 4. Push to GitHub.

This is the artefact this week was building toward. By Sunday you have a tiny but complete LAN multiplayer demo whose network layer would not embarrass a small indie studio. The *game* itself is intentionally minuscule — two cursors on a shared canvas — because the *network system* is the substantive code this week.

The mini-project assembles every piece of the week: the UDP socket setup from Lecture 1 and Exercise 1, the snapshot loop and jitter buffer from Lecture 2 and Exercise 2, the Pygame rendering from Exercise 3, and the Godot bridge mental model from Lecture 3 and Exercise 4 (the Godot port is *contrast* material in the reflection — you do not have to re-implement it).

**Estimated time:** 9 hours (split across Wednesday → Sunday).

---

## What you will build

A new repo (or a `cursor-multiplayer/` subfolder of your portfolio repo), with:

1. **A server** — `server.py`, ~200-300 lines, that binds to UDP port 5005, accepts HELLO from any peer, sends WELCOME with a freshly-allocated peer_id, drains INPUT packets at any rate, and broadcasts SNAP packets at 20 Hz containing every connected peer's latest cursor position.
2. **A client** — `client.py`, ~300-400 lines, that opens a 1024 x 768 Pygame window, sends HELLO at 5 Hz until WELCOMEd, sends INPUT at 30 Hz with the OS-reported mouse position, drains the inbound socket every frame, inserts received snapshots into a jitter buffer, and renders the local cursor at the OS position plus every remote cursor at the interpolated position.
3. **A shared protocol module** — `protocol.py`, ~80-120 lines, that defines the four message types (HELLO, WELCOME, INPUT, SNAP), the struct-packed wire formats, and the `serialise_snapshot` / `parse_snapshot` helpers. Both `server.py` and `client.py` import this.
4. **A jitter buffer module** — `jitter_buffer.py`, ~60-80 lines, that defines `JitterBuffer` with `insert`, `find_bracket`, `size`, `latest_server_time`. Reusable across this project and Week 10's reliability layer.
5. **A HUD** — overlaid on the client canvas. Shows peer_id, RTT (measured via a HELLO/WELCOME timestamp), snapshot count, jitter buffer size, time since last snapshot. The HUD is the network observability that lets you debug the connection without a packet sniffer.
6. **A reliable HELLO/WELCOME handshake** — the one event in the system that *must* be delivered. The client retransmits HELLO every 200 ms until a WELCOME arrives. The server is idempotent: a duplicate HELLO from a known peer responds with the same WELCOME again.
7. **A `LANConfig` dataclass** — the configuration shape for the demo. Port, max peers, snapshot rate, interp delay, jitter buffer size, window dimensions. Loaded from `config.json` if present, else defaults. (Reuses last week's atomic-write pattern *only* if the player has a settings screen; for the demo, a read-only config is fine.)
8. **A "connection lost" overlay** — when the client receives no snapshot for 2 seconds, a translucent red banner overlays the canvas saying "RECONNECTING..." while the client keeps sending HELLO. When snapshots resume, the banner fades out.
9. **A `CREDITS.md`** — lists every dependency. For this project that is Pygame plus the Python stdlib; both get a credit line.
10. **A 20-second demo video** at `demo.mp4` showing: start the server, start client 1, see your own cursor; start client 2 in a second terminal/window, see the second cursor join; move both cursors and see them mirror; close client 2 and see the cursor disappear from client 1.
11. **A 250-word `REFLECTION.md`** using this week's vocabulary correctly.

You will NOT add:

- Client-side prediction. Cursors are light-weight; the 100 ms interp delay is barely noticeable. Prediction is Week 11+.
- Server reconciliation. Same reason.
- Lag compensation. Out of scope.
- Internet multiplayer. LAN only. The mini-project's reflection asks you to *name* the next steps for internet play but not implement them.
- Voice chat, text chat, accounts, persistence. None of those are in this week's scope.
- A second platform (Godot). The Godot port in Exercise 4 is contrast material. If you really want to ship a Godot version, do it as a Week 9 stretch goal after the Python version is done.

---

## Rules

- **You may** copy from this week's exercises freely — that is why they exist. Exercise 3 in particular is the closest starting point.
- **You may** reuse your Week-7 atomic-write pattern if you implement the config-reload feature.
- **You may** use the starter files (`starter_server.py`, `starter_client.py`) in this folder as a scaffold. They have `TODO` markers indicating what to fill in.
- **You may NOT** load any image, sound, or font *inside* the game loop. All assets load once at startup; the loop calls draw / play only.
- **You may NOT** use TCP for any gameplay traffic. UDP only.
- **You may NOT** send any packet larger than 1400 bytes. A typical snapshot at 8 peers is ~250 bytes; you should be nowhere near the limit.
- **You may NOT** rely on packets always arriving. Every state-replication code path must be designed so that missing one packet is fine.
- **You must** ship the HELLO/WELCOME handshake as a *reliable* layer over UDP (retransmit until acknowledged).
- **You must** commit the demo video (or link to it).
- **Python 3.11+, Pygame 2.5+.**
- **Use a virtual environment.**

---

## Acceptance criteria

- [ ] A repo (or subfolder) called `c11-week-09-cursor-multiplayer-<yourhandle>`.
- [ ] `python -m py_compile server.py client.py protocol.py jitter_buffer.py` succeeds with no output.
- [ ] `python server.py` runs and prints "[server] listening on udp 0.0.0.0:5005 (tick=20 Hz)".
- [ ] `python client.py 127.0.0.1` opens a 1024 x 768 window with the local cursor as a small crosshair.
- [ ] Running two clients against the same server shows both cursors in both windows.
- [ ] Closing one client makes that cursor disappear from the other window within 6 seconds (timeout-and-evict).
- [ ] Killing the server makes both clients show the "RECONNECTING..." overlay within 3 seconds.
- [ ] Restarting the server makes the overlay fade and snapshots resume.
- [ ] The HUD shows current peer_id, snapshot count, jitter buffer fill, and "ms since last snapshot."
- [ ] `protocol.py` defines all four message types as named constants and provides struct-packed serialise / parse functions.
- [ ] `jitter_buffer.py` defines `JitterBuffer` with `insert`, `find_bracket`, `size`, `latest_server_time` and is reusable.
- [ ] The HELLO/WELCOME handshake retransmits HELLO every 200 ms until WELCOME is received.
- [ ] **`demo.mp4`** — 15-30 seconds, showing the join / mirror / leave / disconnect flow.
- [ ] **`REFLECTION.md`** — 250 words at the repo root that:
  - Names the FOUR major network features your demo ships (UDP transport, snapshot interpolation, jitter buffer, HELLO/WELCOME handshake — pick four).
  - Identifies which line of the Lecture 1-2-3 material justified each feature.
  - Contrasts your Python implementation with the Godot equivalent from Exercise 4 in 2-3 sentences (which one is shorter, why; which one is more explicit, why).
  - Names ONE behaviour of the network system you would want a play-tester on a poor connection to listen for to find a bug.
  - Cites Glenn Fiedler's series and the Godot 4.x networking documentation by name.
- [ ] **`CREDITS.md`** — credits for Pygame and the Python stdlib, plus a note that the Godot bridge documentation was used as reference.
- [ ] **`README.md`** includes:
  - A controls section ("move the mouse — your cursor moves; ESC or close window — quit; the network is implicit").
  - A "What this demonstrates" section listing the network features (UDP transport, snapshot interpolation, jitter buffer, reliable HELLO/WELCOME, timeout/eviction, reconnection overlay).
  - The demo video inlined (or linked).
  - A "Run it" section with the exact commands for one-machine and two-machine setups.

---

## Suggested order of operations

Build incrementally rather than trying to write the whole thing at once. Each phase ends with a commit.

### Phase 1 — Scaffold the protocol (~45 min)

1. Create the new repo.
2. Copy `starter_server.py` and `starter_client.py` into the repo as `server.py` and `client.py`.
3. Extract the protocol constants and struct definitions into `protocol.py`. Both server and client should `from protocol import ...`.
4. Confirm both files compile: `python -m py_compile server.py client.py protocol.py`.
5. Commit: `Scaffold protocol module and starter server/client.`

### Phase 2 — One-way echo (~1 hour)

1. Wire `server.py` to accept HELLO, reply WELCOME. No snapshots yet.
2. Wire `client.py` to send HELLO every 200 ms until WELCOME arrives. Print the assigned peer_id.
3. Run server + one client. Confirm the WELCOME arrives.
4. Run server + two clients. Confirm each gets a distinct peer_id.
5. Commit: `Implement HELLO/WELCOME reliable handshake.`

### Phase 3 — Server tick + snapshot broadcast (~1 hour)

1. In `server.py`, implement the 20 Hz tick loop. Even when no inputs arrive, broadcast a snapshot with each peer's last-known position (initially the canvas centre).
2. In `client.py`, drain inbound snapshots into a list. Print "snap received" lines.
3. Run server + one client; confirm ~20 lines/sec of snap-received.
4. Commit: `Server broadcasts snapshots at 20 Hz; client logs receipt.`

### Phase 4 — Client INPUT and server-side state update (~1 hour)

1. In `client.py`, send INPUT packets at 30 Hz with the current `pygame.mouse.get_pos()`.
2. In `server.py`, update each peer's stored position on every INPUT.
3. Confirm the server's snapshots now reflect the cursor positions of each connected client.
4. Commit: `Client sends INPUT; server applies and reflects via snapshots.`

### Phase 5 — Jitter buffer and interpolation (~1.5 hours)

1. Extract `JitterBuffer` from `exercise-02-snapshot-loop.py` into `jitter_buffer.py`. Add type hints and docstrings.
2. In `client.py`, insert received snapshots into the buffer instead of just logging.
3. Implement the `t_render = t_now - INTERP_DELAY` calculation and `find_bracket` lookup.
4. Render remote cursors at the interpolated position; render the local cursor at `pygame.mouse.get_pos()`.
5. Run two clients; confirm both see two cursors moving smoothly.
6. Commit: `Wire jitter buffer and snapshot interpolation for remote cursors.`

### Phase 6 — HUD and reconnection overlay (~1.5 hours)

1. Add a fixed-position HUD top-left with peer_id, snapshot count, buffer size, "ms since last snap."
2. Add a "RECONNECTING..." overlay that appears after 2 seconds of no snapshots and fades when snapshots resume.
3. Test by killing and restarting the server while two clients are running.
4. Commit: `Add HUD and reconnection overlay.`

### Phase 7 — Timeout and eviction (~30 min)

1. In `server.py`, evict peers silent for >5 seconds. Print the eviction.
2. In `client.py`, the remote cursor should disappear within ~6 seconds of the other client closing.
3. Commit: `Evict stale peers on the server.`

### Phase 8 — Polish and the demo (~1.5 hours)

1. Per-peer cursor colours via the golden-ratio trick from Exercise 3.
2. Draw a small grid in the background so cursor motion is visible.
3. Record `demo.mp4` (use OS screen capture, or OBS Studio if you already have it).
4. Write `REFLECTION.md` (250 words).
5. Write `CREDITS.md`.
6. Fill in `README.md` with the run commands and the demo video.
7. Final commit: `Polish: grid, colours, demo video, reflection.`

---

## Recommended file layout

```
c11-week-09-cursor-multiplayer-<yourhandle>/
├── server.py
├── client.py
├── protocol.py
├── jitter_buffer.py
├── config.json              (optional; can be a .py default if you skip the JSON)
├── README.md
├── REFLECTION.md
├── CREDITS.md
├── demo.mp4
└── .gitignore
```

---

## Common bugs (read before debugging)

- **"Address already in use" on server start.** The kernel has not released the port from a previous run. Wait 30 seconds or set `SO_REUSEADDR` on the socket before `bind`.
- **Client connects but no snapshots arrive.** Firewall is blocking the *return* path. The server's `sendto` succeeds but the reply is dropped. On macOS, allow Python in Settings > Network > Firewall. On Windows, allow through Windows Firewall.
- **Local cursor lags too.** You wired the local cursor through the snapshot pipeline. The local cursor *must* be rendered straight from `pygame.mouse.get_pos()` every frame, never through the interpolator.
- **Cursor flickers.** Jitter buffer is too small, or `find_bracket` is sometimes returning `None` because `INTERP_DELAY` is too short relative to `1/SERVER_TICK_HZ`.
- **Cursors snap to (0, 0) periodically.** Server is timing out the client (no INPUT received in 5 seconds) and respawning at the default position. Ensure INPUT is being sent at ≥1 Hz, ideally 10-30 Hz.

---

## Stretch goals (after submission)

- **Add a second LAN machine.** The localhost demo lies; the real demo reveals jitter. Move one client to your phone hotspot or a wired router and compare the HUD numbers.
- **Add a "RTT" column to the HUD.** Measured by appending a client-local timestamp to each HELLO and reading it back in the WELCOME. (The server treats it as opaque bytes.)
- **Add a simple chat overlay.** Press T, type a message, press Enter — the message goes to every connected peer via a new `MSG_CHAT` reliable-over-UDP packet. This forces you to implement the reliability layer from Fiedler's article in miniature.
- **Port to Godot.** Take Exercise 4's GDScript and add the jitter buffer + interpolation. Compare LOC against the Python version. (Spoiler: Godot is ~70% the size.)
- **Wireshark the demo while it runs.** Filter `udp.port == 5005`. Identify SNAP vs INPUT vs HELLO/WELCOME packets by cadence and size. Take a screenshot for `WIRESHARK.md`.
- **Add bandwidth telemetry.** Print bytes-per-second sent and received on each side every 10 seconds. Compare to the homework Problem 6 estimate.

---

## What this mini-project does NOT teach (and how to learn it next)

This week is LAN-only and snapshot-only. Real internet multiplayer has more:

- **NAT traversal.** Two players behind home routers cannot trivially see each other. Solutions: hosted relays, Steam Datagram Relay, STUN/TURN. Week 10's reading covers the design; an implementation is later.
- **Reliability layer over UDP.** Critical events (player joined match, scored, killed) must arrive. The minimal protocol is Fiedler's sequence-and-ACK-bitfield. Week 10's lecture and exercises.
- **Client-side prediction and reconciliation.** Hides the snapshot-interpolation delay for the local player. Quake III, Source engine, Rocket League all do this. Week 11 or 12.
- **Delta-compressed snapshots.** When you have hundreds of entities, full-state snapshots become expensive. Send only what changed. Week 11 stretch.
- **Server-side anti-cheat validation.** Authoritative servers are the venue for cheat prevention. The mini-project does one piece (clamp input to canvas) but a real game does much more.
- **Lobby and matchmaking.** Finding a game, joining it, recovering from disconnects. Week 10 covers the design.

None of these are part of this week's mini-project. List them in your reflection as "what I would do next."

---

*Push your mini-project before Sunday night. The first ten clean repos go on the C11 showcase page.*
