# Exercises — Solutions and Common Bugs

The four exercise files in this folder ship with their bodies *filled in*. They are not blanks; they are reference implementations you read, run, and modify. This document is the *teardown* — what each exercise is teaching, what people commonly get wrong when they try to write it themselves, and which lines deserve a second look.

Open each file alongside the matching section here. Do not skip ahead to the "Common bugs" sub-section until you have run the file at least once and watched it work.

---

## Exercise 1 — UDP echo (`exercise-01-udp-echo.py`)

### What this exercise teaches

- The minimal four-call UDP API: `socket(AF_INET, SOCK_DGRAM)`, `bind`, `sendto`, `recvfrom`. Everything in the rest of the week sits on top of these.
- A Fiedler-style packet header: one byte of message type plus a 16-bit sequence number. Three bytes total. Worth the cost on every datagram.
- The non-blocking `recvfrom` drain pattern: `setblocking(False)`, `while True: try ... except BlockingIOError: break`. Used in every exercise.
- `time.perf_counter` for sub-millisecond RTT measurement. Always `perf_counter`, never `time.time` — the latter has resolution issues on Windows.
- A moving-average RTT meter built on `collections.deque(maxlen=32)`. Tiny, allocation-free, and the canonical way to display "what is my ping right now" without flicker.
- The stale-send eviction pattern: if a send record has no matching reply within 1 second, the packet is lost; drop the record so the dict does not grow forever.

### What "done" looks like

You see one of three behaviours depending on the link:

- **Loopback (127.0.0.1).** Avg RTT < 1 ms, near zero variance, 0% loss. The number tells you nothing about the network and everything about your CPU's response time.
- **Wired LAN.** Avg RTT 1-5 ms, jitter <2 ms, 0% loss in a quiet room. This is the "good link" benchmark for the week.
- **Wi-Fi or busy LAN.** Avg RTT 5-30 ms with visible jitter (max RTT 2-5x the average), occasional loss. Real-world conditions; the mini-project should still work on this kind of link.

The "loss" column should be near zero on a quiet LAN. If it climbs above 1% on a loopback connection, something else (CPU starvation, firewall) is the cause — not the network.

### Common bugs

**Bug A — "Address already in use" on the server.**
Symptom: `OSError: [Errno 48] Address already in use` when the server binds.
Cause: a previous run of the server is still holding the port, or you `Ctrl-C`'d the server but the kernel has not released the socket yet (typical 30-60 second TIME_WAIT period).
Fix: the exercise sets `SO_REUSEADDR` before `bind`, which solves this in 95% of cases. For the remaining cases, either wait a minute or change the port (`--port 5006`).

**Bug B — Client RTT is 100+ ms on loopback.**
Symptom: RTT meter shows ~100 ms even though the server is on the same machine.
Cause: you accidentally set `PING_INTERVAL_S` to a non-zero value smaller than `time.sleep(0.005)` plus the print latency. The frame loop sleeps too long.
Fix: lower the `time.sleep(0.005)` or raise `PING_INTERVAL_S`. The default 100 ms ping cadence is comfortable on every platform.

**Bug C — Loss = 100% even though the server is running.**
Symptom: client sends pings, server logs receiving them, but client never sees a reply.
Cause: a firewall is blocking the *return* path. The client sends to the server fine, but the server's reply does not arrive because the client's port is firewalled.
Fix: on macOS, check Settings > Network > Firewall and either disable or allow `python`. On Windows, similar. On Linux, `ufw` or `iptables` rules. Localhost is exempt from most firewalls; cross-machine LAN is not.

**Bug D — Sequence numbers wrap and replies stop matching.**
Symptom: after ~65000 pings (about 110 minutes at 10 Hz) the RTT meter goes flat-zero.
Cause: the sequence number wraps at 65536. If the wrap happens to land on a sequence the client has already recorded, the dict lookup may match an old entry's send time.
Fix: in this exercise the impact is negligible (the dict is small, stale entries get cleaned), but for any production code you would use a 32-bit sequence number. Change `!BH` to `!BI`.

### Things to notice in the code

- The `HEADER_STRUCT` declared at module scope. Declaring `struct.Struct` once and reusing it is ~5x faster than calling `struct.pack` with a format string every time. Premature optimisation here is rewarded.
- `socket.SO_REUSEADDR` on line ~92. Without it, the bug-A scenario above happens reliably.
- The `time.sleep(0.005)` at the bottom of the client loop. Without it, the CPU pegs at 100% on one core. With it, the loop runs ~200 Hz and uses <1% CPU.
- The `send_times_ms.pop(seq, None)` on the reply path. `pop` (not `[]`) returns `None` for unknown keys so a duplicate or unsolicited PONG does not crash.

### Variations worth trying

1. Change `PING_INTERVAL_S` to 0.001 (1000 Hz). On a loopback connection you can saturate a CPU core; the RTT remains near zero. On Wi-Fi you will likely see loss above 1% and visible jitter.
2. Replace `b"hello-from-client"` with `b"x" * 1400`. The payload is now near the safe UDP limit. RTT should not change measurably. Try `b"x" * 2000` and watch for IP fragmentation costs.
3. Add a second instance of the server on a different port. The client can only ping one server at a time without code changes, but you can verify the OS allocates `socket` resources cleanly.
4. Capture loopback traffic in Wireshark (filter `udp.port == 5005`). Verify the actual bytes on the wire match your `pack_header` output.

---

## Exercise 2 — Snapshot loop (`exercise-02-snapshot-loop.py`)

### What this exercise teaches

- A fixed-rate authoritative tick at 20 Hz. The `next_tick_s += SERVER_TICK_DT_S` pattern keeps the cadence even if the loop occasionally runs late. The `if current_s - next_tick_s > SERVER_TICK_DT_S: catch-up` clause prevents runaway backlog.
- A struct-packed snapshot payload with a count field and per-entity records. Read `serialise_snapshot` and `parse_snapshot` together; they are mirror images.
- The `JitterBuffer` class: a bounded deque of received snapshots, sorted by server-time, supporting `find_bracket(t_render)` for the interpolation lookup.
- The `t_render_s = (t_now - offset) - INTERP_DELAY_MS/1000` calculation. This is the trick of "render in the past" stated in arithmetic.
- Per-entity linear interpolation between two snapshots. The lerp is one line; the bookkeeping around it is six.
- Comparing the rendered position against the *ground-truth* simulation (since the world here is a pure function of time) to measure how much error the interpolation introduces. The error is small and bounded.

### What "done" looks like

The server prints a few "[server] new client" lines as you start clients. The client prints lines like:

```
[client] render xy=( 462.5, 297.4)  err= 1.42 px  snaps=42  buf=4  latest=2.10s
```

The `err` column is the magnitude of `(rendered) - (ground truth)`. For a 5-second circle, 20 Hz snapshots, and 100 ms interp delay, expect 0.5-2 pixels. The `buf` column should stay around 3-5 entries in steady state.

### Common bugs

**Bug A — `find_bracket` returns None forever.**
Symptom: client never prints a render line; HUD says "no render yet" continuously.
Cause: `t_render_s` is outside the buffered range. Either (a) `server_time_offset_s` is uninitialised because no snapshots have arrived (server is down, firewall blocking), or (b) `INTERP_DELAY_MS` is so small that `t_render` is between the newest snapshot's time and "now," with nothing past it.
Fix: check `snaps_received > 0`. If yes, raise `INTERP_DELAY_MS` to 150 or 200.

**Bug B — Render position jumps backward in time.**
Symptom: the printed xy zigzags rather than tracing a smooth circle.
Cause: snapshots are arriving out of order and your jitter buffer is not sorting them. Or you implemented `find_bracket` with `>=` and `<=` swapped.
Fix: the reference `JitterBuffer.insert` sorts on out-of-order arrival; the `find_bracket` uses the deque in sorted order. If you wrote your own, the sort is the load-bearing piece.

**Bug C — Server tick rate drifts.**
Symptom: across 10 minutes of running, the server's actual tick rate falls to 15 Hz (or rises to 25 Hz) instead of staying at 20.
Cause: you computed `next_tick_s = current_s + SERVER_TICK_DT_S` (relative) instead of `next_tick_s += SERVER_TICK_DT_S` (absolute). The former accumulates drift; the latter does not.
Fix: use the absolute-add pattern, with a single catch-up clause for when the loop falls behind by more than one tick.

**Bug D — Memory grows unboundedly.**
Symptom: after 10 minutes of running, the client's RAM usage climbs steadily.
Cause: the jitter buffer's `maxlen` is set, but you implemented your own and forgot the cap.
Fix: `collections.deque(maxlen=16)` automatically evicts the oldest entry when full. Use it.

### Things to notice in the code

- `SNAP_HEADER`, `SNAP_COUNT`, `SNAP_ENTITY` declared as module-level `struct.Struct` objects. The `serialise_snapshot` function uses `.pack`; `parse_snapshot` uses `.unpack_from(buf, offset)` to avoid creating substring copies.
- `JitterBuffer.find_bracket` walks the deque in reverse. The common case (`t_render` near the newest entry) terminates on the first iteration.
- The `server_time_offset_s = current_s - snap.server_time_s` line on the client. This is *one-shot calibration*: the first snapshot's server-time gets mapped to "now," and every subsequent render uses the same offset. The mapping is approximate but stable enough for cursor-class accuracy.
- The simulation's `simulate_entity` is a pure function of time, so the client can compute "what the answer should be" and report its interpolation error. Real games cannot do this; the technique is for *debugging* the network layer only.

### Variations worth trying

1. Add a second entity in `simulate_entity` (return a tuple of `EntityState` and update the server's `entities` accordingly). Confirm the client interpolates both independently. The wire format already supports any count.
2. Change `INTERP_DELAY_MS` to 30 ms. Watch the `buf` column drop to 1-2 and the render error rise. The client now sometimes has no bracket pair.
3. Change `INTERP_DELAY_MS` to 300 ms. The render is visibly behind; `buf` rises to ~6 entries. The cost of higher delay is acceptable for high-jitter links.
4. Drop `SERVER_TICK_HZ` to 5 Hz. With `INTERP_DELAY_MS` at 100, you do not have enough buffered. Raise the delay to 300 ms to compensate.
5. Run two clients against the same server. Their reported positions and errors should match within a few pixels — they are both decoding the same snapshot stream.

---

## Exercise 3 — Two cursors in Pygame (`exercise-03-two-cursors-pygame.py`)

### What this exercise teaches

- The Pygame `pygame.event.get` loop combined with the non-blocking `recvfrom` drain pattern. The two coexist because both are *non-blocking* and *idempotent*; we poll each every frame.
- Routing OS mouse coords (`pygame.mouse.get_pos`) into network payloads at a separate cadence (30 Hz input vs 60 Hz frame vs 20 Hz snapshot). Three rates, three loops. None are coupled.
- Server-side validation of inputs (the `clamp to window` lines). Even on a LAN, the server is the source of truth; it does not trust the client's reported position.
- Per-peer colouring via the golden ratio. The technique is `hue = (peer_id * 0.618033) % 1.0`. Adjacent peer_ids get visually distinct colours.
- Rendering the local cursor at the OS-reported position (no network lag) and remote cursors at the interpolated position. The split is the entire local-vs-remote-feel of multiplayer games.
- A peer-timeout eviction on the server. After 5 seconds of silence, the server forgets a peer. The mini-project's reflection asks you to identify what could go wrong here.

### What "done" looks like

Two windows on the same machine, each showing a crosshair (your cursor) and a circle (the other client's cursor). The circle visibly lags the crosshair by ~100 ms when you move your mouse; the crosshair on the *other* window moves with no perceptible lag because that window is rendering its own local cursor straight from OS input.

The HUD should show steady values:

```
server : 127.0.0.1:5005
peer   : 100
snaps  : 247
buffer : 4 / 16
remote : 1
last   : 12.4 ms ago
```

### Common bugs

**Bug A — Window opens but no remote cursor appears.**
Symptom: HUD shows `peer: 100` and `snaps` climbing, but `remote: 0`.
Cause: the second client never started, or it started but never sent HELLO. Or the first client connected but its INPUT packets are not reaching the server.
Fix: check the server's terminal for "[server] new peer ... -> peer_id=101" lines. If only one peer_id appears, the second client is not registering. Common cause: a firewall on the second client's machine.

**Bug B — Remote cursor jumps to (0, 0) periodically.**
Symptom: the circle teleports to the top-left every few seconds.
Cause: the snapshot timeout/eviction is removing the peer and re-creating them at the spawn position. Their input packets are not arriving frequently enough.
Fix: the reference code times out after 5 seconds of silence. If you reduce `CLIENT_TIMEOUT_S`, this happens more often. The fix is to send INPUT more frequently than the timeout, which the default 30 Hz cadence does.

**Bug C — Local cursor is laggy too.**
Symptom: even your own crosshair feels sluggish.
Cause: you wired the local cursor through the snapshot/interpolation path instead of straight from `pygame.mouse.get_pos`.
Fix: the local cursor is rendered separately at `pygame.mouse.get_pos()` *after* the remote cursor loop. The branch `if peer_id == my_peer_id: continue` in the remote-render loop is the discipline.

**Bug D — Cursors flicker between two positions.**
Symptom: the remote cursor visibly oscillates between two near positions every frame.
Cause: the jitter buffer is too small and `find_bracket` is sometimes returning the same older/newer pair with `alpha=1.0` and sometimes returning `alpha=0.0`.
Fix: ensure `JITTER_BUFFER_MAXLEN >= 8`. Ensure `INTERP_DELAY_MS >= 80`.

### Things to notice in the code

- The render loop's clear order: background grid first, *then* remote cursors, *then* local cursor (drawn last so it is always on top). HUD last so it overlays everything.
- The `mx, my = pygame.mouse.get_pos()` call appears twice — once for the input send, once for the local-cursor render. Two reads, two purposes. Reading the same coords twice in a frame is cheap.
- The `clock.tick(CLIENT_FPS)` at the bottom of the loop. This is Pygame's idiomatic way to cap the frame rate; it sleeps internally to maintain the target.
- `color_for_peer` is a pure function of `peer_id`. It runs once per cursor per frame. If profiling shows it costing real time, hoist into a dict cache.

### Variations worth trying

1. Run three clients on the same machine. Verify all three see two remote cursors. The HUD's `remote` should read 2 on every client.
2. Add a fourth client window. Performance should remain at 60 fps on every machine; bandwidth scales linearly. At 8 clients the server is sending 8 snapshots x 8 entities x 20 Hz = ~10 kB/s, still trivial.
3. Drop `SERVER_TICK_HZ` to 10. The remote cursors visibly stutter unless you also raise `INTERP_DELAY_MS` to 200 ms.
4. Add a "ghost cursor" that shows where the *server* thinks your cursor is (i.e. render your *own* peer_id at its interpolated position too, in a faded colour). The visible gap between the local crosshair and the ghost is the network's contribution to lag.
5. Capture loopback traffic with Wireshark. Filter `udp.port == 5005`. You should see SNAP packets at 20 Hz from the server and INPUT packets at 30 Hz from each client.

---

## Exercise 4 — Godot port (`exercise-04-godot-cursor-rpc.gd`)

### What this exercise teaches

- Setting up an `ENetMultiplayerPeer` for both server and client.
- Wiring `multiplayer.peer_connected` / `peer_disconnected` signals.
- Reading the four arguments of `@rpc("any_peer", "call_local", "unreliable")` and recognising what each one buys you.
- Using `.rpc(args)` to invoke a function across the network.
- `multiplayer.get_remote_sender_id()` to identify the calling peer inside an RPC body.
- The Godot 4.x scene-tree drawing pattern: mark dirty with `queue_redraw()`, render in `_draw()`.

### What "done" looks like

Same as Exercise 3, but with less code. Two Godot instances, one hosts, one joins. Each window shows its own cursor and the other's cursor moving in real time. Total GDScript code: ~120 lines including signal handlers and UI plumbing.

### Common bugs

**Bug A — "Connection failed" immediately on join.**
Symptom: the join client shows the failure message right away.
Cause: the host has not started, or `create_server` returned an error (port in use).
Fix: check the host's output. Make sure `create_server` returned `OK`. If not, change `PORT` to something else (and update the same constant in the join client).

**Bug B — Cursor appears at (0, 0) on join.**
Symptom: the joining client sees a remote cursor stuck at the corner.
Cause: the joining client received a `peer_connected` signal for the host before any RPCs arrived. The default position from `_on_peer_connected` is `Vector2(400, 300)`, but if you initialise differently, you may see `(0, 0)`.
Fix: the reference code sets cursors to the canvas centre on first sight. If you change it to `Vector2.ZERO`, you will see the corner-stuck behaviour for the first frame.

**Bug C — `get_remote_sender_id()` returns 0 when called from `call_local`.**
Symptom: when the host's own cursor RPC fires `call_local`, the sender ID is 0 instead of 1.
Cause: in Godot 4.x, the local invocation path through `call_local` reports a sender ID of 0 because there is no actual network sender. This is documented but easy to miss.
Fix: the reference code handles this with `if sender_id == 0: sender_id = multiplayer.get_unique_id()`. Always check.

**Bug D — Two Godot editors cannot coexist on the same machine.**
Symptom: both editors run but only one can host; the other gets "port in use."
Cause: ENet binds the requested port and is exclusive. Two `create_server(5005)` calls on the same machine conflict.
Fix: only one editor hosts. The other clicks Join. To run *three* instances on one machine, you can export a build and run an exported binary alongside the editor.

### Things to notice in the code

- The `@rpc` annotation has *four* arguments, two of which are commonly omitted in tutorials. The full form is good discipline.
- The `multiplayer.peer_connected.connect(_on_peer_connected)` in `_ready` is the listener registration. `peer_id` 1 is always the server; client peer IDs start at random values around 100000000.
- The `multiplayer.is_server()` check inside `_on_peer_connected` — the same signal fires on every connected machine, but the server is the only one that should *log* the join (or run join validation, etc.). Always branch on `is_server()` for server-only logic.
- The `_color_for(peer_id)` function uses the same golden-ratio trick as the Pygame demo, so a peer with ID 1234 has the same colour in both implementations. Useful when running a Pygame client and Godot client side by side for comparison.

### Variations worth trying

1. Add a `MultiplayerSynchronizer` node to replicate cursor position automatically rather than via the explicit `@rpc`. The replication is configured in the editor; no GDScript changes.
2. Change the `@rpc` transfer mode from `"unreliable"` to `"reliable"` and observe the (small) latency increase under packet loss. On a clean LAN you will not see a measurable difference.
3. Print the network statistics: `multiplayer.multiplayer_peer.get_packet_count_in_buffer()` and similar telemetry are available on `ENetMultiplayerPeer`. Useful for the latency-budget feel.
4. Export the Godot project for HTML5 and run two browser tabs against a `WebSocketMultiplayerPeer`. The browser cannot host UDP, so the demo runs over WebSocket (TCP) — visibly higher latency on loss but functionally similar.
5. Open the Godot demos repository on GitHub and walk through the official `networking/pong_multiplayer` demo. Compare its architecture to this exercise.

---

## Wrapping up

You should now be able to:

- Read and modify Exercise 1 to test any LAN's RTT and loss characteristics.
- Read and modify Exercise 2 to add new entities to the snapshot stream.
- Read and modify Exercise 3 to add additional gameplay state (e.g. each peer has a `(r, g, b)` colour they can change, replicated like position).
- Read Exercise 4 and translate any of the Pygame patterns into Godot's high-level API.

The mini-project polishes Exercise 3 into a publication-quality artefact. The reflection asks you to *contrast* the Python implementation with the Godot one in your own words, citing each lecture's relevant section.

If anything in these exercises does not run on your machine, post in the course channel with the platform, Python version, and the full error trace. Most issues are firewall- or version-related and are quick to diagnose.
