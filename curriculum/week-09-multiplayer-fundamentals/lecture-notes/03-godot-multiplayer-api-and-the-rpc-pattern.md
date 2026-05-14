# Lecture 3 — The Godot 4.x Multiplayer API and the `@rpc` Pattern

> **Duration:** ~2 hours of reading plus hands-on (you should have Godot 4.x installed and a starter project open while reading).
> **Outcome:** You can read a small Godot multiplayer scene, identify what `MultiplayerAPI`, `ENetMultiplayerPeer`, `MultiplayerSpawner`, `MultiplayerSynchronizer`, and `@rpc` each do, and translate a Pygame UDP cursor demo into Godot in under fifty lines of GDScript.

If you only remember one thing from this lecture, remember this:

> **Godot's high-level multiplayer API is a *thin opinionated layer* over the same UDP authoritative-server model we built by hand in Pygame. The thinking — authoritative server, snapshot interpolation, latency budget, state vs events — is identical. The *code* shrinks by an order of magnitude because Godot serialises, sends, receives, and dispatches on your behalf. You annotate functions with `@rpc` and place `MultiplayerSynchronizer` nodes; Godot does the rest.**

This lecture is the bridge between the Python hand-build and the production engine. We do not abandon any of the Lecture 1-2 vocabulary; we re-meet each concept under its Godot name.

The required reading is the Godot 4.x *High-level multiplayer* tutorial. Read it before this lecture if you have not. Then read this lecture with the tutorial open in another tab.

---

## 1. The Godot networking stack

Godot's networking is a stack of four layered abstractions:

```
   +------------------------------------------------+
   |  Your GDScript                                 |
   |  @rpc functions, MultiplayerSpawner config,    |
   |  MultiplayerSynchronizer node setup            |
   +------------------------------------------------+
   |  MultiplayerAPI                                |
   |  - dispatches rpcs                             |
   |  - tracks connected peers                      |
   |  - issues spawner/synchronizer messages        |
   +------------------------------------------------+
   |  MultiplayerPeer (abstract transport)          |
   |  Concrete: ENetMultiplayerPeer,                |
   |            WebSocketMultiplayerPeer,           |
   |            MultiplayerPeerSteam (Steam)        |
   +------------------------------------------------+
   |  Underlying transport library                  |
   |  ENet (C lib, wraps UDP with channels)         |
   |  WebSocket (TCP with framing)                  |
   +------------------------------------------------+
   |  OS sockets (the same socket calls from L1)    |
   +------------------------------------------------+
```

Read this stack top-to-bottom: your GDScript is opinionated, the API in the middle is generic, the transport is pluggable, and the very bottom is the same UDP `sendto` / `recvfrom` we wrote ourselves.

The default transport for LAN multiplayer is **ENetMultiplayerPeer**, which wraps the ENet C library. ENet is UDP with optional per-channel reliability — a tiny reliability protocol roughly equivalent to what Fiedler describes in *Reliability and Flow Control*, plus channels (parallel reliable streams within one UDP socket). For HTML5 export, **WebSocketMultiplayerPeer** is the only option because browsers do not expose UDP. For Steam-distributed games, **MultiplayerPeerSteam** routes through Steam Datagram Relay and hides NAT.

For our purposes — LAN demo, Godot 4.x — we use `ENetMultiplayerPeer.create_server(port)` on the host and `ENetMultiplayerPeer.create_client(host, port)` on the joiners.

---

## 2. The minimal Godot server and client

The shortest working multiplayer Godot setup is this GDScript on an auto-loaded `Network` singleton:

```gdscript
extends Node

const PORT: int = 5005
const MAX_PEERS: int = 8

func host_game() -> void:
    var peer: ENetMultiplayerPeer = ENetMultiplayerPeer.new()
    var err: int = peer.create_server(PORT, MAX_PEERS)
    if err != OK:
        push_error("create_server failed: " + str(err))
        return
    multiplayer.multiplayer_peer = peer
    print("Hosting on port ", PORT)

func join_game(host_ip: String) -> void:
    var peer: ENetMultiplayerPeer = ENetMultiplayerPeer.new()
    var err: int = peer.create_client(host_ip, PORT)
    if err != OK:
        push_error("create_client failed: " + str(err))
        return
    multiplayer.multiplayer_peer = peer
    print("Connecting to ", host_ip, ":", PORT)
```

That is *the entire transport setup* for a LAN multiplayer game. The `multiplayer` keyword refers to the scene-tree-attached `MultiplayerAPI` instance; assigning a `MultiplayerPeer` to it is enough to make any `@rpc`-annotated function in the tree network-callable.

Compare to the Pygame version: ten lines vs the ~80 lines of socket setup, packet framing, and connection tracking in Exercise 3. Godot is doing real work — connection tracking, peer ID assignment, scene-tree integration — that the Pygame version intentionally omits.

---

## 3. The `@rpc` annotation

The `@rpc` annotation on a GDScript function marks it as *remotely callable*. Any peer connected via the `MultiplayerAPI` can invoke it on any other peer.

```gdscript
@rpc("any_peer", "call_local", "unreliable")
func report_cursor(x: float, y: float) -> void:
    cursors[multiplayer.get_remote_sender_id()] = Vector2(x, y)
```

The four annotation arguments:

1. **`who_can_call`** — `"any_peer"` (any connected peer can invoke this) or `"authority"` (only the network authority — usually the server — can invoke it). Default is `"authority"`.
2. **`call_local`** — `"call_local"` (invoke the function on the sender too) or `"call_remote"` (only on the receivers). Default `"call_remote"`. `call_local` is useful when the sender wants to render the same effect immediately without waiting for the network round trip.
3. **`transfer_mode`** — `"unreliable"`, `"unreliable_ordered"`, or `"reliable"`. Maps to ENet's channel transfer modes:
   - `"unreliable"`: send-and-forget. Use for state that can be missed (snapshot data). Default.
   - `"unreliable_ordered"`: drop late arrivals but never deliver out-of-order. Useful for chronologically-meaningful state.
   - `"reliable"`: ACK + retransmit. Use for events that must arrive (player joined, scored). Higher cost.
4. **`transfer_channel`** — a small integer that names a logical channel. Channels are independent reliability streams; a stall on one does not stall another. Default `0`.

The annotation is checked at runtime; calling an `@rpc("authority", ...)` function from a non-authority peer throws an error. Calling an `@rpc("any_peer", ...)` function from anywhere works.

To invoke an RPC, write:

```gdscript
report_cursor.rpc(120.5, 240.0)             # call on all peers
report_cursor.rpc_id(server_peer_id, 1.0, 2.0)  # call on one specific peer
```

The `.rpc()` suffix is required — `report_cursor(...)` alone is just a local function call.

### 3.1 The `@rpc` mapping to Lecture 1's vocabulary

| Concept (Lecture 1-2)                | Godot `@rpc` equivalent                                  |
|--------------------------------------|----------------------------------------------------------|
| UDP, no reliability                  | `"unreliable"` transfer mode                             |
| Acknowledged delivery (Week 10)      | `"reliable"` transfer mode                               |
| Snapshot stream                      | `@rpc("authority", "call_remote", "unreliable")` from server |
| Input stream (client to server)      | `@rpc("any_peer", "call_remote", "unreliable")` to server|
| Event ("player joined")              | `@rpc("authority", "call_remote", "reliable")`           |
| Local immediate echo                 | `"call_local"`                                           |

Internalise this table. Once you read an `@rpc` annotation as the four-axis description it is, every Godot multiplayer tutorial becomes legible.

---

## 4. `MultiplayerSpawner` — replicated node spawning

When a player joins, you need a player-character node to appear in every connected client's scene tree. Doing this manually means sending an RPC like `spawn_player(peer_id)` to every peer and having each peer instantiate the scene. `MultiplayerSpawner` does this automatically.

```gdscript
# In your Game.tscn, add a MultiplayerSpawner node.
# In the inspector:
#   spawn_path:  ../Players       (where to spawn under)
#   _spawnable_scenes: [res://player.tscn]
#
# In the server's code, when a peer connects:
func _on_peer_connected(peer_id: int) -> void:
    var p: Node = preload("res://player.tscn").instantiate()
    p.name = str(peer_id)
    p.set_multiplayer_authority(peer_id)
    $Players.add_child(p)
```

When the server calls `$Players.add_child(p)`, the `MultiplayerSpawner` notices the new node under its watched path and broadcasts a "spawn this scene at this path with these properties" message to every connected client. Each client instantiates the same `player.tscn` under their own `$Players` node. The scene trees on every machine now agree.

The `set_multiplayer_authority(peer_id)` call tells Godot which peer "owns" this node. The owning peer is the only one whose inputs drive the node's state (subject to `@rpc("authority", ...)` checks). For player characters, the owner is the peer that controls them.

### 4.1 Spawnable scenes

`MultiplayerSpawner` requires you to enumerate every scene that can be spawned under its path. This is a security feature: a malicious client cannot trick the server into spawning a scene of the client's choosing. Only scenes in the spawner's whitelist can appear.

---

## 5. `MultiplayerSynchronizer` — replicated node properties

`MultiplayerSynchronizer` declares which *properties* of its parent node are network-replicated, at what rate, and on which transfer channel. Configure it once in the editor; never write replication code by hand for the common case.

```
   Player (Node2D)
   |-- Sprite2D
   |-- CollisionShape2D
   |-- MultiplayerSynchronizer
         |-- ReplicationConfig:
         |     position  ->  replicated on Process, channel 0, unreliable
         |     hp        ->  replicated on Process, channel 1, reliable
         |     facing    ->  replicated on Process, channel 0, unreliable
         |-- public_visibility: true
         |-- replication_interval: 0.05  (20 Hz tick)
```

Every 50 ms (20 Hz tick), the synchroniser inspects each replicated property; if it has changed since the last sync, the new value is broadcast to every peer. Receivers apply the new value to their local copy of the node.

For our cursor demo, a `MultiplayerSynchronizer` on each cursor node, replicating `position` at 20 Hz, is *literally all the code you need* for state replication. No serialisation, no UDP, no jitter buffer.

### 5.1 The implicit interpolation

Godot does *not* interpolate between received synchroniser updates by default. The replicated property snaps to the new value on each receive. To get smooth interpolation — the technique from Lecture 2 — you have two options:

1. Replicate at high frequency (e.g. 60 Hz). The visible snaps become imperceptible. Costs bandwidth.
2. Replicate at low frequency (e.g. 20 Hz), expose a `target_position` property, and tween `position` toward `target_position` every frame. This is interpolation in user code. Adds 30-50 lines of GDScript.

For the LAN cursor demo, option 1 is fine. For a production action game, option 2 is required, and the implementation closely matches the Python snapshot interpolation from Exercise 2.

### 5.2 The `MultiplayerSynchronizer`-vs-Pygame mapping

| Pygame component (Week 9)              | Godot equivalent                            |
|----------------------------------------|----------------------------------------------|
| Server-side world dict `{id -> (x,y)}` | Authority-owned nodes in the scene tree     |
| `struct.pack("!IHff", ...)` per state  | Synchroniser's auto-serialisation           |
| `sock.sendto(bytes, addr)` for snapshot| Synchroniser broadcast on tick              |
| Client jitter buffer + interpolation   | High-frequency sync, or hand-rolled lerp    |
| `recvfrom` drain loop on client        | Synchroniser receive handler (built-in)     |

The whole left column is the Python hand-built version. The right column is two editor nodes and a configuration.

---

## 6. The cursor demo in Godot (~50 lines)

Here is the *full* Godot 4.x port of the Pygame two-cursor demo. The code is short enough to read in one go. (Exercise 4 contains the runnable version with a setup `README`.)

```gdscript
# cursor_main.gd - attached to the main scene's root Node2D.

extends Node2D

const PORT: int = 5005
var cursors: Dictionary = {}    # peer_id -> Vector2
var is_host: bool = false

@onready var label: Label = $InfoLabel

func _ready() -> void:
    multiplayer.peer_connected.connect(_on_peer_connected)
    multiplayer.peer_disconnected.connect(_on_peer_disconnected)

func host_game() -> void:
    var peer := ENetMultiplayerPeer.new()
    var err := peer.create_server(PORT, 8)
    if err != OK:
        push_error(str(err)); return
    multiplayer.multiplayer_peer = peer
    is_host = true
    cursors[1] = Vector2.ZERO    # host always has peer_id 1

func join_game(ip: String) -> void:
    var peer := ENetMultiplayerPeer.new()
    var err := peer.create_client(ip, PORT)
    if err != OK:
        push_error(str(err)); return
    multiplayer.multiplayer_peer = peer

func _process(_dt: float) -> void:
    if multiplayer.multiplayer_peer == null: return
    var mouse: Vector2 = get_global_mouse_position()
    report_cursor.rpc(mouse.x, mouse.y)

@rpc("any_peer", "call_local", "unreliable")
func report_cursor(x: float, y: float) -> void:
    var sender: int = multiplayer.get_remote_sender_id()
    cursors[sender] = Vector2(x, y)
    queue_redraw()

func _draw() -> void:
    for peer_id in cursors:
        var pos: Vector2 = cursors[peer_id]
        draw_circle(pos, 8.0, _color_for(peer_id))
        draw_string(ThemeDB.fallback_font, pos + Vector2(12, -8),
                    str(peer_id), HORIZONTAL_ALIGNMENT_LEFT, -1, 14)

func _color_for(peer_id: int) -> Color:
    var hue: float = fmod(peer_id * 0.61803, 1.0)
    return Color.from_hsv(hue, 0.7, 0.95)

func _on_peer_connected(peer_id: int) -> void:
    cursors[peer_id] = Vector2.ZERO
    print("peer ", peer_id, " connected")

func _on_peer_disconnected(peer_id: int) -> void:
    cursors.erase(peer_id)
    print("peer ", peer_id, " disconnected")
```

That is *50 lines of GDScript* and it replaces ~250 lines of Pygame UDP code. Read every line; you should be able to identify what each line replaces in Exercise 3.

The `@rpc("any_peer", "call_local", "unreliable")` annotation says: any peer can call `report_cursor`, the sender also runs it locally so their own cursor renders immediately, and the message is unreliable (drop if lost — fine, the next frame sends a new one).

---

## 7. Where things get harder

The cursor demo is *easy* in Godot. The harder problems do not go away; they just move:

### 7.1 Authoritative validation

The Pygame mini-project's server validates inputs (e.g. clamping cursor positions to canvas bounds). In Godot, you must explicitly route player inputs through a server-side validation step:

```gdscript
@rpc("any_peer", "call_remote", "reliable")
func client_requests_move(target: Vector2) -> void:
    # Runs on the server only (because the annotation lacks "call_local").
    if not _is_valid_move(target):
        return
    position = target  # MultiplayerSynchronizer broadcasts the new state.
```

Without `"call_local"`, the client's call invokes only on the receivers — and the server (peer ID 1) is the one whose authority owns the player node. This is the "client sends an input, server validates and applies" pattern Lecture 1 §1.1 described.

### 7.2 Bandwidth and tick rate

`MultiplayerSynchronizer.replication_interval` is your snapshot tick rate. 20 Hz is the default we recommend for action games at indie scale; 60 Hz is what competitive shooters target. Higher = smoother but more bandwidth.

For mobile or HTML5 export, drop to 10-15 Hz and add explicit lerp-interpolation on the client. The Godot demo project `Pong Multiplayer` shows this pattern.

### 7.3 NAT traversal

Everything in this lecture is LAN-only. ENet does not punch through NAT on its own. The production options:

- **Steam Datagram Relay (`MultiplayerPeerSteam`).** If you ship on Steam, this is free and handles NAT.
- **Nakama** or another self-hosted relay server.
- **Hosted dedicated servers.** All clients connect to a public IP; no NAT punch-through needed.
- **Manual port-forwarding by the host.** Not realistic for non-technical players.

We do not cover NAT this week. Week 10 will sketch the design; an actual implementation is a Week 13+ topic.

### 7.4 Replication for many entities

`MultiplayerSynchronizer` works well up to dozens of entities. At hundreds or thousands, the per-tick scan of "did this property change" becomes a CPU cost, and the bandwidth becomes a bandwidth cost. At that scale you move to delta-encoded snapshots, area-of-interest filtering, and prioritised replication. Out of scope for this week and most of this course.

---

## 8. When you should *not* use Godot's high-level API

The high-level API is opinionated. There are cases where you should drop down to the lower-level `MultiplayerPeer` and write your own packet protocol:

- **Heavy delta-compression of snapshots.** Beyond what synchroniser does.
- **Custom reliability protocol** (e.g. a Fiedler-style sequence-bitfield ACK).
- **Spectator-only or replay channels** with different visibility rules.
- **Cross-engine play** (Godot client talking to a non-Godot server). The server's protocol is whatever you write; the high-level API would not interoperate.

For the typical indie LAN co-op or small online competitive game, the high-level API is exactly right. The cases above are the bottom 5% — interesting, advanced, not Week 9 material.

---

## 9. The mental-model check

Before moving on:

1. *What is `MultiplayerAPI`?* — The orchestrator that dispatches RPCs and tracks connected peers.
2. *What is `ENetMultiplayerPeer`?* — The transport implementation that wraps the ENet C library (UDP with optional channels and reliability).
3. *What does `@rpc("any_peer", "call_local", "unreliable")` mean?* — Any connected peer can invoke this function; the sender also runs it locally; the message is unreliable (no ACK, no retransmit).
4. *What does `MultiplayerSpawner` replace?* — The manual "tell every peer to instantiate this scene at this path" message.
5. *What does `MultiplayerSynchronizer` replace?* — The manual per-tick serialisation, send, receive, and apply of state properties.
6. *Does Godot's high-level API interpolate state replication?* — Not by default. Either raise the tick rate or add hand-rolled lerp on the client.

---

## 10. Reading order for the rest of the week

- **Before Exercise 4 (Godot port):** Godot *High-level multiplayer* tutorial, plus the *MultiplayerSpawner* and *MultiplayerSynchronizer* class references.
- **Before the mini-project:** All of the Fiedler series articles you have not yet read. The mini-project does not require Godot; it is the Pygame two-cursor demo polished to publication quality.
- **Stretch:** Browse the official Godot demos repo, `networking/` folder. The *Pong Multiplayer* demo is the closest analogue to our work.

---

## Up next

We move to the exercises. Exercise 1 is the UDP echo; Exercise 2 is the headless snapshot loop; Exercise 3 is the Pygame two-cursor demo; Exercise 4 is the Godot port. The mini-project is the polished version of Exercise 3 with a HELLO/WELCOME reliable handshake on top.

---

*References cited in this lecture:*

- *Godot 4.x, High-level multiplayer tutorial* — the canonical Godot multiplayer reference.
- *Godot 4.x, MultiplayerAPI / MultiplayerPeer / ENetMultiplayerPeer / MultiplayerSpawner / MultiplayerSynchronizer class references* — the API surface.
- *Glenn Fiedler, Networking for Game Programmers* — the underlying mental model.
- *Godot demo projects, networking folder* — runnable reference code.
