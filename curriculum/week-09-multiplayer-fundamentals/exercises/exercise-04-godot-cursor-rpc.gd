# exercise-04-godot-cursor-rpc.gd
#
# Goal
# ----
# The Godot 4.x port of Exercise 3 (the Pygame two-cursor demo).
# Reproduces the same shared-canvas experience using Godot's high-level
# multiplayer API: `ENetMultiplayerPeer` for the LAN transport, `@rpc`
# annotations for the cursor-position broadcast, and the scene tree
# for state. The whole script is intentionally under 100 lines of
# GDScript - that is the *point* of this exercise.
#
# What you learn
# --------------
# - Setting up an authoritative server via `ENetMultiplayerPeer
#   .create_server(port, max_peers)`.
# - Connecting a client via `.create_client(host, port)`.
# - Listening to `multiplayer.peer_connected` / `peer_disconnected`
#   to track who is in the game.
# - Annotating a function with `@rpc("any_peer", "call_local",
#   "unreliable")` and calling it via `.rpc(...)`.
# - Reading `multiplayer.get_remote_sender_id()` to learn which peer
#   invoked an RPC.
# - Drawing the per-peer cursor with `queue_redraw()` and `_draw()`.
#
# Godot version
# -------------
# Tested against Godot 4.2-stable. Should work on any Godot 4.x.
#
# Setup (read this carefully)
# ---------------------------
# 1. Open Godot 4.x. Create a new project.
# 2. In the project root, create a scene `cursor_demo.tscn` with the
#    following node hierarchy:
#
#       Main (Node2D)         <-- attach THIS script (exercise-04-godot-cursor-rpc.gd)
#         |- InfoLabel (Label)
#         |- HostButton (Button)
#         |- JoinButton (Button)
#         |- JoinIPEdit (LineEdit)
#
# 3. In the Main node's inspector, set the script path to point at
#    this file (or copy this file into the project as
#    `res://cursor_demo.gd`).
#
# 4. In the InfoLabel inspector, set Position to (12, 12). Width ~400.
#    In the HostButton inspector, set Text to "Host", Position
#    (12, 540).
#    In the JoinButton inspector, set Text to "Join", Position
#    (140, 540).
#    In the JoinIPEdit inspector, set Placeholder Text to "127.0.0.1",
#    Position (220, 540), Custom Min Size (200, 30).
#
# 5. In the Project Settings, set Display -> Window -> Size -> Viewport
#    Width to 800 and Height to 600.
#
# 6. Connect the HostButton's `pressed` signal to `_on_host_pressed`.
#    Connect the JoinButton's `pressed` signal to `_on_join_pressed`.
#
# 7. Play the scene. To test on one machine:
#       - Press F5 to run. Click "Host".
#       - Open a *second* Godot editor (or run a second exported build)
#         and click "Join" with IP `127.0.0.1`.
#    To test across two LAN machines: replace `127.0.0.1` with the
#    host's LAN IP.
#
# References
# ----------
# - Godot 4.x docs, *High-level multiplayer*:
#   <https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html>
# - Godot 4.x docs, *ENetMultiplayerPeer*:
#   <https://docs.godotengine.org/en/stable/classes/class_enetmultiplayerpeer.html>
# - Godot 4.x docs, *@rpc annotation*:
#   <https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_exports.html>
# - Glenn Fiedler, *Networking for Game Programmers*:
#   <https://gafferongames.com/categories/game-networking/>

extends Node2D

const PORT: int = 5005
const MAX_PEERS: int = 8

# peer_id -> Vector2 (latest reported position).
var cursors: Dictionary = {}

# UI nodes (assigned by the scene tree).
@onready var info_label: Label = $InfoLabel
@onready var host_button: Button = $HostButton
@onready var join_button: Button = $JoinButton
@onready var join_ip_edit: LineEdit = $JoinIPEdit


func _ready() -> void:
    # Subscribe to peer-lifecycle signals from the MultiplayerAPI.
    multiplayer.peer_connected.connect(_on_peer_connected)
    multiplayer.peer_disconnected.connect(_on_peer_disconnected)
    multiplayer.connected_to_server.connect(_on_connected_to_server)
    multiplayer.connection_failed.connect(_on_connection_failed)
    info_label.text = "Click Host or Join to start."


func _on_host_pressed() -> void:
    var peer: ENetMultiplayerPeer = ENetMultiplayerPeer.new()
    var err: int = peer.create_server(PORT, MAX_PEERS)
    if err != OK:
        info_label.text = "create_server failed: " + str(err)
        return
    multiplayer.multiplayer_peer = peer
    # The host always has peer_id 1 in Godot's high-level API.
    cursors[1] = Vector2(400, 300)
    info_label.text = "Hosting on UDP port " + str(PORT) + ". Peer id = 1."
    host_button.disabled = true
    join_button.disabled = true


func _on_join_pressed() -> void:
    var ip: String = join_ip_edit.text.strip_edges()
    if ip.is_empty():
        ip = "127.0.0.1"
    var peer: ENetMultiplayerPeer = ENetMultiplayerPeer.new()
    var err: int = peer.create_client(ip, PORT)
    if err != OK:
        info_label.text = "create_client failed: " + str(err)
        return
    multiplayer.multiplayer_peer = peer
    info_label.text = "Connecting to " + ip + ":" + str(PORT) + "..."
    host_button.disabled = true
    join_button.disabled = true


func _process(_delta: float) -> void:
    if multiplayer.multiplayer_peer == null:
        return
    if multiplayer.multiplayer_peer.get_connection_status() \
            != MultiplayerPeer.CONNECTION_CONNECTED:
        return
    # Send our mouse position to every connected peer (and ourselves
    # via `call_local`). The unreliable transfer mode is correct here:
    # if a single position update is lost, the next one supersedes it.
    var mouse: Vector2 = get_global_mouse_position()
    report_cursor.rpc(mouse.x, mouse.y)


@rpc("any_peer", "call_local", "unreliable")
func report_cursor(x: float, y: float) -> void:
    # `get_remote_sender_id()` returns the peer_id of whoever invoked
    # this RPC. With `call_local`, that includes ourselves.
    var sender_id: int = multiplayer.get_remote_sender_id()
    if sender_id == 0:
        # 0 means "the local peer when no network is involved" - the
        # `call_local` path goes through this branch on the sender.
        sender_id = multiplayer.get_unique_id()
    cursors[sender_id] = Vector2(x, y)
    queue_redraw()


func _draw() -> void:
    var my_id: int = -1
    if multiplayer.multiplayer_peer != null:
        my_id = multiplayer.get_unique_id()
    for peer_id in cursors.keys():
        var pos: Vector2 = cursors[peer_id]
        var color: Color = _color_for(int(peer_id))
        var radius: float = 10.0
        # Filled disc.
        draw_circle(pos, radius, color)
        # Outline.
        draw_arc(pos, radius, 0.0, TAU, 24, Color(0, 0, 0), 1.0)
        # Label.
        var tag: String = "#" + str(peer_id)
        if int(peer_id) == my_id:
            tag = "YOU (" + tag + ")"
        draw_string(ThemeDB.fallback_font, pos + Vector2(14, -6),
                    tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 14,
                    Color(0.9, 0.9, 0.95))


func _color_for(peer_id: int) -> Color:
    # Deterministic colour via the golden ratio. Same approach as the
    # Pygame demo, so colours match across the two implementations.
    var hue: float = fmod(float(peer_id) * 0.61803398875, 1.0)
    return Color.from_hsv(hue, 0.7, 0.95)


func _on_peer_connected(peer_id: int) -> void:
    print("peer connected: ", peer_id)
    cursors[peer_id] = Vector2(400, 300)
    if multiplayer.is_server():
        info_label.text = "Peer " + str(peer_id) + " joined. Total peers: " \
                          + str(cursors.size())


func _on_peer_disconnected(peer_id: int) -> void:
    print("peer disconnected: ", peer_id)
    cursors.erase(peer_id)
    queue_redraw()


func _on_connected_to_server() -> void:
    info_label.text = "Connected as peer " + str(multiplayer.get_unique_id())
    cursors[multiplayer.get_unique_id()] = Vector2(400, 300)


func _on_connection_failed() -> void:
    info_label.text = "Connection failed. Is the server running?"
    multiplayer.multiplayer_peer = null
    host_button.disabled = false
    join_button.disabled = false


# What this exercise demonstrates vs Exercise 3
# ---------------------------------------------
# Pygame demo (Exercise 3)          Godot equivalent (this file)
# --------------------------------- ---------------------------------------
# socket(AF_INET, SOCK_DGRAM)       ENetMultiplayerPeer.new()
# sock.bind(("0.0.0.0", 5005))      peer.create_server(PORT, MAX_PEERS)
# sock.connect((host, port))        peer.create_client(host, PORT)
# Hand-packed struct payload        Auto-marshalled by the @rpc decorator
# sock.sendto(payload, addr)        report_cursor.rpc(x, y)
# while True: recvfrom()...         Built into MultiplayerAPI; no code
# HELLO/WELCOME handshake           Built into ENet's connection protocol
# Per-peer dict on server           multiplayer.peer_connected signal
# 20 Hz tick + jitter buffer +      @rpc fires every _process, no buffer
#  interpolation                    needed for a cursor demo; production
#                                   games would add MultiplayerSynchronizer
#                                   with hand-rolled lerp, see Lecture 3 §5
#
# The Pygame version is the *teaching* artefact. The Godot version is
# the *production* artefact. They do the same thing.
