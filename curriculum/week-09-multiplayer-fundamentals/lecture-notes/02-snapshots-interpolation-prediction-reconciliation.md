# Lecture 2 — Snapshots, Interpolation, Prediction, and Reconciliation

> **Duration:** ~2 hours of reading plus hands-on.
> **Outcome:** You can describe the snapshot loop, implement snapshot interpolation, size a jitter buffer, explain client-side prediction and server reconciliation at the intuition level, and distinguish state replication from event replication.

If you only remember one thing from this lecture, remember this:

> **The client renders the past. The server is in the present. The client predicts the future for the local player. The visible smoothness of every modern multiplayer game is the sum of those three sentences. Snapshot interpolation is how you render the past well. Client-side prediction is how you make the local player feel native. Server reconciliation is how the past and the future stay consistent when the server disagrees.**

The lecture builds on Lecture 1's transport layer. We now sit on top of UDP and design the *client-side* smoothing that hides latency, jitter, and packet loss from the player. The technique is *snapshot interpolation*, due to Fiedler's article of the same name, and used in some form by every modern action game.

By the end of this lecture you can read Exercise 2 (the headless snapshot loop) and Exercise 3 (the Pygame two-cursor demo) and recognise every line.

---

## 1. The snapshot loop

The simplest authoritative-server architecture sends *snapshots* on a fixed cadence. A snapshot is a serialised description of the world's state at a moment in server time — the positions and orientations of every relevant entity, plus any HUD-level state (score, health, status flags) the client needs to render.

```
   Server tick rate: 20 Hz (every 50 ms)

   t=0     50    100   150   200   250   300   ms (server time)
   |      |     |     |     |     |     |
   S0    S1    S2    S3    S4    S5    S6      snapshots sent

   Each snapshot is a small UDP packet:

   +--------+--------+-----------+-----------+
   | proto  | seq#   | entity 1  | entity 2  | ... |
   | id 1B  | 2B     | id+x+y    | id+x+y    |
   +--------+--------+-----------+-----------+
```

The client receives these snapshots over UDP. They arrive when they arrive: in order if the network is well-behaved, out of order or with gaps if it is not. The client's job is to produce a smooth 60 fps render from a stream that arrives at 20 Hz.

### 1.1 Why not just render the latest snapshot?

The naive approach: every frame, render the most recent snapshot you have received. This produces visible *steps* — the client's render time advances continuously (one frame every 16.6 ms), but the input data jumps in 50 ms chunks. Movement looks staccato.

You can interpolate within the last snapshot, but you have nothing to interpolate *to*: you do not yet know where the entity is going.

### 1.2 The trick: render in the past

Snapshot interpolation accepts a fixed *interpolation delay* — typically 100-150 ms — and renders the world at `t_render = t_now - INTERP_DELAY`. At any rendered frame, the client has *two* snapshots whose server-timestamps bracket `t_render`, and it interpolates linearly (or with a small spline) between them.

```
  Client receive timeline:

  t=  50     100    150    200    250    280       ms (client real time)
       |     |      |      |      |      |
       S0    S1     S2     S3     S4     S5  (arrival)

  Client renders at t_render = t_now - 150 ms:

  t_now=280, INTERP_DELAY=150  ->  t_render = 130 ms
  130 ms is bracketed by S2 (server t=100) and S3 (server t=150).
  Lerp parameter alpha = (130 - 100) / (150 - 100) = 0.6.
  Render every entity at S2 * 0.4 + S3 * 0.6.
```

By rendering 150 ms behind real time, the client is always interpolating between two known snapshots. Entity motion is silky-smooth at 60 fps even though the server only updates 20 times a second. The cost is the visible 150 ms delay — for action games this is small; for competitive shooters at the top end this is unacceptable and motivates client-side prediction (§4).

### 1.3 Picking the interp delay

The interp delay must be at least one *snapshot period* (50 ms for 20 Hz) plus a margin for jitter. A typical setting:

- 50 ms snapshot period (20 Hz)
- 100 ms interp delay (~2 snapshot periods)

This gives the client one buffered snapshot to interpolate towards even if the next snapshot is up to 50 ms late.

For a higher-tick-rate game (60 Hz server) the interp delay can drop to ~50 ms total. For a high-jitter connection it goes up to ~200 ms. The exercises this week use 100 ms.

---

## 2. The jitter buffer

The jitter buffer is the queue of received snapshots from which the interpolator reads. Its job: smooth out the variance in arrival time so that, every frame, the interpolator has *two* snapshots bracketing `t_render`.

```
   Snapshot arrivals (with jitter):

   t=  50  100   165   180   240   295         (real arrival times)
        S0   S1    S2    S3    S4    S5

   Notice the gap between S1 and S2: 65 ms instead of 50 ms.
   And the gap between S2 and S3: 15 ms (a burst).

   Jitter buffer contents at t=270:
   [S2 (server 100), S3 (server 150), S4 (server 200), S5 (server 250)]

   Interpolator at t_render = 270 - 150 = 120:
   bracketed by S2 (100) and S3 (150). Lerp alpha = 0.4.
```

### 2.1 Sizing the buffer

The buffer should hold:
- One snapshot period as the *target* (the snapshot just before `t_render`).
- One more for the one *after* `t_render`.
- Two to three more for jitter margin and out-of-order arrival.

For a 20 Hz server, that is 4-5 snapshots, or ~200 ms of buffered state. The memory cost is trivial — a few hundred bytes.

### 2.2 Discarding stale snapshots

The buffer should evict snapshots that are *behind* the rendered window. Anything with `server_time < t_render - INTERP_DELAY` is no longer useful. A bounded deque (e.g. `collections.deque(maxlen=8)`) handles eviction automatically.

### 2.3 Out-of-order arrival

UDP can deliver snapshots in any order. The receiver inspects each snapshot's sequence number; if it is older than the highest seen, the packet is *not* automatically dropped — it can fill a hole in the buffer. The interpolator selects the bracketing pair by server-time, not arrival order.

The exception: if the snapshot is *older than the oldest entry in the buffer*, drop it. It is past the rendered window.

### 2.4 Packet loss

If a snapshot is lost entirely, the buffer has a gap. The interpolator notices that the bracket pair spans more than one snapshot period and adjusts the lerp `alpha` accordingly:

```
   Server sends: S0  S1  S2  (LOST)  S4  S5
   Client buffer: S0  S1  S2  S4  S5    (S3 missing)

   At t_render = server t=170:
   Bracket pair = S2 (100) and S4 (200). Snapshot period = 100 ms, double.
   alpha = (170 - 100) / (200 - 100) = 0.7.
   Render at S2 * 0.3 + S4 * 0.7.
```

The motion remains smooth; the visible cost of the lost packet is one slightly-longer interpolation. This is exactly the property that makes snapshot replication so robust to UDP's drop-on-failure.

If too many consecutive snapshots are lost — say, four in a row — the buffer runs dry and the renderer has to *extrapolate* (linearly project from the last known velocity). Extrapolation is a brittle backup; if you have a 1+% loss rate sustained, raise the interp delay rather than extrapolate.

---

## 3. The state and event distinction

Snapshot interpolation is great for *state* — the continuous "where is everyone right now." It is poor for *events* — discrete one-off things like "you scored a point" or "player A picked up the powerup."

| Category | Examples                          | Replication strategy             | Loss tolerance |
|----------|-----------------------------------|----------------------------------|----------------|
| State    | Position, velocity, health, score | Snapshot (best-effort, frequent) | High           |
| Event    | "Scored", "Joined", "Hit"         | Reliable (ACK + retransmit)      | Zero           |

A snapshot can be missed: the next one will repair the rendered state. An event cannot be missed: if the client misses "player joined," they never spawn the player.

The standard architecture: two parallel logical channels over the *same* UDP socket. State goes over the unreliable channel. Events go over a small reliability layer (sequence + ACK + retransmit). Fiedler's *Reliability and Flow Control* article shows the minimal implementation.

For this week we cheat: the mini-project sends only state. The "join" event is sent with a small retry loop (the client sends HELLO every 200 ms until it receives WELCOME). This is sufficient for a LAN demo with two peers; for a real game, Week 10 covers the proper reliability layer.

---

## 4. Client-side prediction (intuition only)

Imagine you press the W key to move your player forward. With pure snapshot interpolation, your local view of yourself does not move until the server's next snapshot reflects the move. That is 50 ms (snapshot period) plus 50 ms (interp delay) plus the network RTT — 150-300 ms of *input lag* on your own player. Unplayable.

The fix: the client runs the simulation *locally* for its own player, applying inputs the moment they happen. The server still has the authoritative truth and corrects the client if they disagree.

```
   t=0:  player presses W.
         client: immediately moves player by 60 fps * speed * dt (predicted).
         client: also sends INPUT(W) to server.

   t=50: server receives INPUT(W). Applies in server's simulation.
         server: sends snapshot containing player's authoritative new position.

   t=100: client receives snapshot. Authoritative position = where client
          predicted. No correction needed. Player saw zero lag.

   If the client predicted wrong (e.g. ran into a wall the client did not
   know about), the snapshot shows the player at a different position.
   The client visibly *snaps* to the server position - but for a well-tuned
   prediction, these snaps are rare.
```

Predicted entities are usually only the *local* player and projectiles fired by the local player. Other players are rendered through snapshot interpolation (no prediction). This is the standard split: *render the past for others, predict the present for yourself.*

We do not implement prediction this week. The cursor demo gets away without it because the cursor is so light-weight a 150 ms render-delay is barely noticeable on a desktop mouse. For a player character on a controller, prediction becomes essential.

### 4.1 Reading the Gambetta article

Gabriel Gambetta's *Fast-Paced Multiplayer* part 2 has an interactive visualisation of prediction. Open it in a browser and toggle the "client-side prediction" checkbox on and off. The visual difference is the entire argument.

---

## 5. Server reconciliation (intuition only)

Prediction creates a problem: the client and server can disagree about the local player. When the server's snapshot arrives showing the player at position P_server, and the client had predicted P_client, what does the client do?

**Naive answer:** snap the player to P_server.
**Problem:** if the client kept moving in the meantime, the snap *undoes* the recent inputs.

**Real answer:** the client *reconciles*. It rewinds the local player to P_server, then re-applies every input that has happened since the snapshot's timestamp.

```
   Snapshot from server: t_server=100, player at (100, 200).
   Client's local prediction at t_now=180: player at (130, 200).
   Client has logged its inputs:
      t=100 -> W pressed
      t=120 -> W still pressed
      t=140 -> W still pressed
      t=160 -> W released

   On reconcile:
   1. Set player to server position: (100, 200).
   2. Replay inputs from t=100 to t=now (180) at the local sim rate.
      After replay, player ends up at (130, 200) - same as the prediction.

   No visible correction. If the prediction had been wrong, the replay
   would produce a different end position, and the visible correction
   is the difference between (130, 200) and the replayed end.
```

In practice, reconciliation requires:
- A circular buffer of recent local inputs, tagged by the local time they were issued.
- The client tracks which input sequence numbers have been acknowledged by the server.
- On every received snapshot, the client rewinds to the snapshot's state and replays unacknowledged inputs.

This is more work than fits in a single week's exercise, which is why we leave it at the intuition level. Quake III, Source engine, and Rocket League all do this. Mirror (the Unity library) and Mirror's competitors implement it for you.

---

## 6. Lag compensation (mentioned)

A separate concept from reconciliation: *lag compensation* runs on the server.

When player A shoots at player B at client time t=100, A's bullet, on A's screen, is travelling through B's *visible* position at that moment. By the time A's "shoot" command arrives at the server (say t=130), B has moved. If the server checks against B's current position, A's shot misses.

Lag compensation: the server *rewinds* the world to where A saw it (t=100 in server time), checks the hit, then returns to the present. This is how shooter hits feel fair across a network.

The Valve paper *Latency Compensating Methods in Client/Server In-Game Protocol Design* covers this in depth. For this week, we do not implement it. It is reading.

---

## 7. The state-replication abstractions

Production multiplayer engines (Unreal's replication, Unity Mirror, Godot's `MultiplayerSynchronizer`) provide higher-level abstractions for state replication. The two common patterns:

### 7.1 Full-state snapshots

Every snapshot contains every replicated entity's full state. Simple to implement; simple to interpolate; simple to recover from packet loss. Bandwidth scales with `(entities x state-per-entity x snapshot-rate)`.

For 8 players at 32 bytes each at 20 Hz: 8 x 32 x 20 = 5120 bytes/sec. Tiny. This is the model we use this week.

For 80 players at 32 bytes each at 20 Hz: 80 x 32 x 20 = 51200 bytes/sec. Still tiny.

For 800 players at 32 bytes each at 20 Hz: 800 x 32 x 20 = 512000 bytes/sec = 4 Mbps. Noticeable on a residential uplink. This is where you start delta-encoding and area-of-interest filtering.

### 7.2 Delta-compressed snapshots

Each snapshot contains only the *changes* since the last one the client acknowledged. The server tracks which snapshots each client has acknowledged. If `entity_3.x` did not change since the last ACK, it is omitted from this snapshot.

Bandwidth drops dramatically for slow-moving worlds (most worlds). The cost is complexity: the server tracks per-client acknowledgement state, and the client needs the previous snapshot to apply the delta.

Quake III, Source, and most modern engines use delta-compressed snapshots. We do not implement this; Week 11 covers it.

### 7.3 Event streams

Some games replicate only *events* (entity spawned, entity moved by N, entity died) and let the client reconstruct state from the event log. Fiedler's *State Synchronisation* article covers this model. It is more complex to get right but excels for games with many independent entities.

---

## 8. Bandwidth, in concrete numbers

A useful sanity check for any multiplayer design:

```
   Single-player snapshot payload (player + 7 enemies + 4 props):

   12 entities x (4-byte id + 4-byte x + 4-byte y + 2-byte facing) = 168 bytes
   + 8-byte UDP header
   + 20-byte IP header
   --------
   ~196 bytes per snapshot

   At 20 Hz: 196 * 20 = 3920 bytes/sec per client.
   For 8 clients on a listen-server: 8 * 3920 = 31360 bytes/sec downstream.

   A home upload link of 5 Mbps = 625000 bytes/sec.
   We are using 5% of it. There is room.
```

The exercise: every time you add a field to your snapshot, multiply by 20 (the tick rate) and by the number of clients. If the result is uncomfortable, push the field into delta-encoding or event-replication.

For the mini-project's two-cursor demo at 20 Hz with 16-byte payloads: 2 x 16 x 20 = 640 bytes/sec aggregate. Three orders of magnitude under any uplink. The whole point of staying small is being able to ignore bandwidth as a constraint.

---

## 9. The full picture, end to end

Putting Lectures 1 and 2 together, here is the complete data flow for an authoritative-server game with prediction:

```
   Frame on client:
   1. Poll OS input. Build INPUT(seq=N, keys).
   2. Append INPUT to local input log.
   3. Apply INPUT to local player simulation. Predicted player advances.
   4. Send INPUT to server via UDP.
   5. Drain socket. For each received snapshot:
      a. Stamp arrival time.
      b. Drop if older than oldest buffered snapshot.
      c. Insert into jitter buffer (by server time).
      d. Pop too-old entries.
      e. If snapshot includes local player: rewind, reconcile, replay
         inputs newer than snapshot.seq_ack.
   6. Render every other entity at t_render = t_now - INTERP_DELAY,
      interpolating between bracketing snapshots.
   7. Render local player at predicted (current) position.

   Tick on server (every 50 ms):
   1. Receive all queued inputs.
   2. Apply each input to the canonical simulation.
   3. Advance simulation by 50 ms.
   4. Serialise world to snapshot.
   5. Send snapshot to every connected client.
```

For Week 9's exercises and mini-project we implement *steps 4-6* on the client (snapshot drain, jitter buffer, interpolation) and *steps 1-5* on the server (input drain, sim tick, broadcast). We omit prediction and reconciliation — both are real and important, but they multiply the code volume by ~3x and obscure the snapshot pattern that is this week's load-bearing concept.

Week 10 (Networking II) will add reliability and the input-replication channel. Prediction and reconciliation are Week 11 or 12.

---

## 10. The mental-model check

Before moving on:

1. *Why does the client render in the past?* — To always have two received snapshots bracketing the render time, so motion can be interpolated smoothly.
2. *What is a jitter buffer?* — The queue of received snapshots from which the interpolator reads. Sized to absorb the variance in arrival times.
3. *What is the difference between state and event replication?* — State is continuous and tolerates loss (next snapshot repairs it); events are discrete and require reliability.
4. *What is client-side prediction?* — The client runs the simulation locally for its own player, applying inputs immediately, while the server provides authoritative correction.
5. *What is server reconciliation?* — When the server's snapshot disagrees with the client's prediction, the client rewinds to the server state and replays unacknowledged inputs.
6. *What is lag compensation?* — A server-side technique that rewinds the world to where the firing client saw it when validating hit-detection.

---

## Up next

Lecture 3 is the Godot bridge. We have implemented the snapshot loop in Python by hand in Exercises 2 and 3. In Lecture 3 we read what the same idea looks like in Godot 4.x — `MultiplayerSpawner`, `MultiplayerSynchronizer`, `@rpc`, and `ENetMultiplayerPeer`. The hand-built Python version makes the production engine make sense.

Read the Godot *High-level multiplayer* tutorial before Lecture 3.

---

*References cited in this lecture:*

- *Glenn Fiedler, Snapshot Interpolation (gafferongames.com)* — the core technique.
- *Glenn Fiedler, State Synchronisation (gafferongames.com)* — the alternative.
- *Gabriel Gambetta, Fast-Paced Multiplayer parts 1-4* — visual companion.
- *Valve Developer Wiki, Latency Compensating Methods (Yahn Bernier, 2001)* — lag compensation.
- *Valve Developer Wiki, Source Multiplayer Networking* — industry reference.
