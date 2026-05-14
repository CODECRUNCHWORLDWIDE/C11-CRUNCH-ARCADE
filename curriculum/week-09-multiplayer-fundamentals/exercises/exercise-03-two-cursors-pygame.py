"""exercise-03-two-cursors-pygame.py

Goal
----
A LAN-only two-cursor shared-canvas demo. One process is the
authoritative server; one or more processes are Pygame clients. Each
client renders its own mouse cursor *and* every other connected
client's cursor on the same canvas, at ~60 fps, with snapshots
arriving from the server at 20 Hz and interpolation hiding the
mismatch.

This is the capstone exercise of Week 9. The mini-project polishes
this same demo into a publication-quality artefact; this exercise is
the working skeleton.

What you learn
--------------
- The Pygame event-loop variant of the snapshot/interp pattern from
  Exercise 2.
- Routing OS mouse input into per-frame INPUT(x, y) datagrams sent
  to the server at 30 Hz (every other client frame).
- Building a server-side world of `{peer_id -> (x, y)}` and
  broadcasting snapshots that include every connected peer.
- Drawing remote cursors at their interpolated positions and the
  local cursor at its raw OS-reported position (a tiny "you" marker
  that is not subject to network lag).
- A clean shutdown protocol (Ctrl-C on server, ESC or window close
  on client).

Expected behaviour
------------------
Server (in one terminal):
    python exercise-03-two-cursors-pygame.py --server
    Prints "[server] listening on udp 0.0.0.0:5005 (tick=20 Hz)".
    Reports each peer that joins.

Client 1 (in a second terminal):
    python exercise-03-two-cursors-pygame.py --client 127.0.0.1
    Opens an 800x600 window. The local cursor is rendered as a small
    bright crosshair at the current mouse position. The HUD in the
    top-left shows peer_id, ping, jitter buffer size, snapshot count.

Client 2 (in a third terminal):
    Same command. A second window opens. After a moment each window
    shows two cursors - your own and the other client's. Moving the
    mouse in either window updates the other window's view of "your"
    cursor with ~100 ms of interp delay and ~20 ms LAN RTT.

To run on one machine:
    Use 127.0.0.1 as the server address from each client.

To run across two LAN machines:
    On the host machine running the server, find the LAN IP
    (ifconfig / ipconfig). On each client, pass that IP. Make sure
    UDP port 5005 is not firewalled.

To complete
-----------
This exercise ships complete. Read top-to-bottom. Run it. Two clients
on the same machine work; two clients on different LAN machines work
identically.

If Pygame is not installed:
    pip install pygame

References
----------
- Glenn Fiedler, *Snapshot Interpolation*:
  <https://gafferongames.com/post/snapshot_interpolation/>
- Glenn Fiedler, *Sending and Receiving Packets*:
  <https://gafferongames.com/post/sending_and_receiving_packets/>
- Python docs, *socket*:
  <https://docs.python.org/3/library/socket.html>
- Pygame docs, *event* and *mouse*:
  <https://www.pygame.org/docs/ref/event.html>
  <https://www.pygame.org/docs/ref/mouse.html>
"""

from __future__ import annotations

import argparse
import collections
import socket
import struct
import sys
import time
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Tuple

try:
    import pygame
except ImportError:
    pygame = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------

MSG_HELLO: int = 0x10
MSG_WELCOME: int = 0x11
MSG_SNAP: int = 0x12
MSG_INPUT: int = 0x13

# HELLO:    !B                       msg
# WELCOME:  !BH                      msg + peer_id
# INPUT:    !BHff                    msg + sequence + x + y
# SNAP:     !BHd                     msg + sequence + server_time
# SNAP_E:   !H                       count
# PER_ENT:  !Iff                     peer_id + x + y

INPUT_STRUCT: struct.Struct = struct.Struct("!BHff")
SNAP_HEADER: struct.Struct = struct.Struct("!BHd")
SNAP_COUNT: struct.Struct = struct.Struct("!H")
SNAP_ENTITY: struct.Struct = struct.Struct("!Iff")

PORT: int = 5005
RECV_BUFSIZE: int = 2048

# Tick rates.
SERVER_TICK_HZ: int = 20
SERVER_TICK_DT_S: float = 1.0 / SERVER_TICK_HZ
CLIENT_FPS: int = 60
CLIENT_INPUT_HZ: int = 30
CLIENT_INPUT_DT_S: float = 1.0 / CLIENT_INPUT_HZ
INTERP_DELAY_MS: float = 100.0
JITTER_BUFFER_MAXLEN: int = 16
CLIENT_TIMEOUT_S: float = 5.0

# Window.
WIN_W: int = 800
WIN_H: int = 600


# ---------------------------------------------------------------------------
# Shared data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EntityState:
    """A peer's cursor position at a snapshot time."""
    peer_id: int
    x: float
    y: float


@dataclass(frozen=True)
class Snapshot:
    sequence: int
    server_time_s: float
    entities: Tuple[EntityState, ...]


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def serialise_snapshot(snap: Snapshot) -> bytes:
    buf: bytearray = bytearray()
    buf += SNAP_HEADER.pack(MSG_SNAP, snap.sequence & 0xFFFF,
                            snap.server_time_s)
    buf += SNAP_COUNT.pack(len(snap.entities))
    for ent in snap.entities:
        buf += SNAP_ENTITY.pack(ent.peer_id, ent.x, ent.y)
    return bytes(buf)


def parse_snapshot(data: bytes) -> Optional[Snapshot]:
    if len(data) < SNAP_HEADER.size + SNAP_COUNT.size:
        return None
    msg_type, sequence, server_time_s = SNAP_HEADER.unpack_from(data, 0)
    if msg_type != MSG_SNAP:
        return None
    count_offset: int = SNAP_HEADER.size
    (count,) = SNAP_COUNT.unpack_from(data, count_offset)
    entities_offset: int = count_offset + SNAP_COUNT.size
    expected_size: int = entities_offset + count * SNAP_ENTITY.size
    if len(data) < expected_size:
        return None
    entities: List[EntityState] = []
    for i in range(count):
        offset: int = entities_offset + i * SNAP_ENTITY.size
        pid, ex, ey = SNAP_ENTITY.unpack_from(data, offset)
        entities.append(EntityState(pid, ex, ey))
    return Snapshot(sequence, server_time_s, tuple(entities))


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

@dataclass
class ServerPeer:
    """Per-peer state on the authoritative server."""
    peer_id: int
    addr: Tuple[str, int]
    x: float
    y: float
    last_seen_s: float


def run_server(bind_host: str, bind_port: int) -> None:
    """Run the authoritative cursor server until interrupted.

    Behaviour:
      - HELLO from a new address gets a fresh peer_id and a WELCOME.
      - INPUT from a known address updates that peer's stored x, y.
      - Every 50 ms, broadcast a snapshot containing every peer's
        latest (x, y).
      - Peers silent for CLIENT_TIMEOUT_S are evicted.
    """
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((bind_host, bind_port))
    sock.setblocking(False)
    print(f"[server] listening on udp {bind_host}:{bind_port}  "
          f"(tick={SERVER_TICK_HZ} Hz)")

    peers: Dict[Tuple[str, int], ServerPeer] = {}
    next_peer_id: int = 100
    sequence: int = 0
    server_start_s: float = time.monotonic()
    next_tick_s: float = time.monotonic()

    try:
        while True:
            current_s: float = time.monotonic()

            # --- Drain inbound socket -----------------------------
            while True:
                try:
                    data, addr = sock.recvfrom(RECV_BUFSIZE)
                except BlockingIOError:
                    break
                if not data:
                    continue
                msg_type: int = data[0]
                if msg_type == MSG_HELLO:
                    if addr not in peers:
                        peers[addr] = ServerPeer(
                            peer_id=next_peer_id,
                            addr=addr,
                            x=WIN_W * 0.5,
                            y=WIN_H * 0.5,
                            last_seen_s=current_s,
                        )
                        print(f"[server] new peer {addr} -> "
                              f"peer_id={next_peer_id}")
                        next_peer_id += 1
                    peer: ServerPeer = peers[addr]
                    peer.last_seen_s = current_s
                    sock.sendto(struct.pack("!BH", MSG_WELCOME,
                                            peer.peer_id), addr)
                elif msg_type == MSG_INPUT \
                        and len(data) >= INPUT_STRUCT.size:
                    if addr not in peers:
                        # Ignore inputs from peers we have not welcomed.
                        continue
                    _, _seq, ix, iy = INPUT_STRUCT.unpack_from(data, 0)
                    # Clamp to window bounds. This is the server's one
                    # piece of input validation - the client cannot
                    # report a cursor outside the canvas.
                    ix = max(0.0, min(float(WIN_W), ix))
                    iy = max(0.0, min(float(WIN_H), iy))
                    p: ServerPeer = peers[addr]
                    p.x = ix
                    p.y = iy
                    p.last_seen_s = current_s

            # --- Evict stale peers --------------------------------
            stale: List[Tuple[str, int]] = [
                a for a, pr in peers.items()
                if current_s - pr.last_seen_s > CLIENT_TIMEOUT_S
            ]
            for a in stale:
                print(f"[server] peer {peers[a].peer_id} at {a} timed out")
                del peers[a]

            # --- Tick: build snapshot, broadcast -----------------
            if current_s >= next_tick_s:
                server_time_s: float = current_s - server_start_s
                entities: Tuple[EntityState, ...] = tuple(
                    EntityState(pr.peer_id, pr.x, pr.y)
                    for pr in peers.values()
                )
                snap: Snapshot = Snapshot(sequence, server_time_s, entities)
                payload: bytes = serialise_snapshot(snap)
                for addr in list(peers.keys()):
                    try:
                        sock.sendto(payload, addr)
                    except OSError:
                        del peers[addr]
                sequence = (sequence + 1) & 0xFFFF
                next_tick_s += SERVER_TICK_DT_S
                if current_s - next_tick_s > SERVER_TICK_DT_S:
                    next_tick_s = current_s + SERVER_TICK_DT_S

            time.sleep(0.001)

    except KeyboardInterrupt:
        print("\n[server] interrupted, shutting down")
    finally:
        sock.close()


# ---------------------------------------------------------------------------
# Client - jitter buffer + interpolation
# ---------------------------------------------------------------------------

class JitterBuffer:
    """A bounded queue of recent snapshots, ordered by server_time."""

    def __init__(self, max_len: int = JITTER_BUFFER_MAXLEN) -> None:
        self._buf: Deque[Snapshot] = collections.deque(maxlen=max_len)

    def insert(self, snap: Snapshot) -> None:
        if not self._buf:
            self._buf.append(snap)
            return
        if snap.server_time_s > self._buf[-1].server_time_s:
            self._buf.append(snap)
            return
        existing: List[Snapshot] = list(self._buf)
        existing.append(snap)
        existing.sort(key=lambda s: s.server_time_s)
        dedup: List[Snapshot] = []
        last_time: float = -1.0
        for s in existing:
            if s.server_time_s != last_time:
                dedup.append(s)
                last_time = s.server_time_s
        ml: Optional[int] = self._buf.maxlen
        self._buf.clear()
        for s in dedup[-ml if ml else 0:]:
            self._buf.append(s)

    def size(self) -> int:
        return len(self._buf)

    def latest_server_time(self) -> Optional[float]:
        if not self._buf:
            return None
        return self._buf[-1].server_time_s

    def find_bracket(self, t_render_s: float) -> Optional[
        Tuple[Snapshot, Snapshot, float]
    ]:
        if len(self._buf) < 2:
            return None
        snaps: List[Snapshot] = list(self._buf)
        for i in range(len(snaps) - 1, 0, -1):
            older: Snapshot = snaps[i - 1]
            newer: Snapshot = snaps[i]
            if older.server_time_s <= t_render_s <= newer.server_time_s:
                span: float = newer.server_time_s - older.server_time_s
                if span <= 0.0:
                    return (older, newer, 0.0)
                alpha: float = (t_render_s - older.server_time_s) / span
                return (older, newer, alpha)
        return None


def lerp_entity(a: EntityState, b: EntityState, alpha: float) -> EntityState:
    return EntityState(
        b.peer_id,
        a.x + (b.x - a.x) * alpha,
        a.y + (b.y - a.y) * alpha,
    )


def interpolate_snapshot(older: Snapshot, newer: Snapshot,
                         alpha: float) -> Dict[int, EntityState]:
    older_map: Dict[int, EntityState] = {e.peer_id: e for e in older.entities}
    result: Dict[int, EntityState] = {}
    for ent_newer in newer.entities:
        ent_older: Optional[EntityState] = older_map.get(ent_newer.peer_id)
        if ent_older is None:
            result[ent_newer.peer_id] = ent_newer
        else:
            result[ent_newer.peer_id] = lerp_entity(ent_older,
                                                    ent_newer, alpha)
    return result


def color_for_peer(peer_id: int) -> Tuple[int, int, int]:
    """Deterministic colour from peer_id via the golden ratio."""
    hue_step: float = 0.618033988749895
    h: float = (peer_id * hue_step) % 1.0
    # Simple HSV -> RGB at fixed S=0.7, V=0.95.
    s: float = 0.7
    v: float = 0.95
    i: int = int(h * 6.0)
    f: float = h * 6.0 - i
    p: float = v * (1.0 - s)
    q: float = v * (1.0 - s * f)
    t: float = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
    return (int(r * 255), int(g * 255), int(b * 255))


# ---------------------------------------------------------------------------
# Client - main loop
# ---------------------------------------------------------------------------

def run_client(server_host: str, server_port: int) -> None:
    """Run the Pygame two-cursor client until ESC or window close."""
    if pygame is None:
        print("ERROR: pygame not installed. Run: pip install pygame")
        sys.exit(1)

    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    server_addr: Tuple[str, int] = (server_host, server_port)

    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption(f"two-cursors  ->  {server_host}:{server_port}")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 18)

    buf: JitterBuffer = JitterBuffer()
    my_peer_id: Optional[int] = None
    last_hello_s: float = 0.0
    next_input_s: float = time.monotonic()
    input_sequence: int = 0
    snaps_received: int = 0
    server_time_offset_s: Optional[float] = None
    last_snap_s: float = 0.0

    running: bool = True
    try:
        while running:
            current_s: float = time.monotonic()

            # --- Pygame events --------------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN \
                        and event.key == pygame.K_ESCAPE:
                    running = False

            # --- HELLO retransmit until WELCOMEd ----------------
            if my_peer_id is None and current_s - last_hello_s >= 0.2:
                sock.sendto(struct.pack("!B", MSG_HELLO), server_addr)
                last_hello_s = current_s

            # --- Drain inbound socket -----------------------------
            while True:
                try:
                    data, _addr = sock.recvfrom(RECV_BUFSIZE)
                except BlockingIOError:
                    break
                if not data:
                    continue
                msg_type: int = data[0]
                if msg_type == MSG_WELCOME and len(data) >= 3:
                    (_, peer_id) = struct.unpack("!BH", data[:3])
                    if my_peer_id != peer_id:
                        my_peer_id = peer_id
                        print(f"[client] welcomed as peer_id={peer_id}")
                elif msg_type == MSG_SNAP:
                    snap: Optional[Snapshot] = parse_snapshot(data)
                    if snap is None:
                        continue
                    if server_time_offset_s is None:
                        server_time_offset_s = current_s - snap.server_time_s
                    buf.insert(snap)
                    snaps_received += 1
                    last_snap_s = current_s

            # --- Send INPUT at fixed cadence -------------------
            if my_peer_id is not None and current_s >= next_input_s:
                mx, my = pygame.mouse.get_pos()
                packet: bytes = INPUT_STRUCT.pack(
                    MSG_INPUT, input_sequence & 0xFFFF,
                    float(mx), float(my),
                )
                try:
                    sock.sendto(packet, server_addr)
                except OSError as exc:
                    print(f"[client] input send error: {exc}")
                input_sequence += 1
                next_input_s = current_s + CLIENT_INPUT_DT_S

            # --- Interpolate the world for rendering ------------
            rendered: Dict[int, EntityState] = {}
            if server_time_offset_s is not None:
                t_render_s: float = (current_s - server_time_offset_s) \
                    - (INTERP_DELAY_MS / 1000.0)
                bracket = buf.find_bracket(t_render_s)
                if bracket is not None:
                    older, newer, alpha = bracket
                    rendered = interpolate_snapshot(older, newer, alpha)

            # --- Render -------------------------------------
            screen.fill((20, 22, 28))
            # Light grid background to make motion visible.
            for gx in range(0, WIN_W, 40):
                pygame.draw.line(screen, (35, 38, 46),
                                 (gx, 0), (gx, WIN_H), 1)
            for gy in range(0, WIN_H, 40):
                pygame.draw.line(screen, (35, 38, 46),
                                 (0, gy), (WIN_W, gy), 1)

            # Remote cursors at their interpolated positions.
            for peer_id, ent in rendered.items():
                if peer_id == my_peer_id:
                    continue  # We render our own cursor separately.
                color: Tuple[int, int, int] = color_for_peer(peer_id)
                px: int = int(ent.x)
                py: int = int(ent.y)
                pygame.draw.circle(screen, color, (px, py), 10)
                pygame.draw.circle(screen, (0, 0, 0), (px, py), 10, 1)
                label = font.render(f"#{peer_id}", True, (230, 230, 240))
                screen.blit(label, (px + 14, py - 8))

            # Local cursor at the OS mouse position (no network lag).
            mx, my = pygame.mouse.get_pos()
            if my_peer_id is not None:
                local_color: Tuple[int, int, int] = color_for_peer(my_peer_id)
            else:
                local_color = (255, 255, 255)
            pygame.draw.line(screen, local_color,
                             (mx - 12, my), (mx + 12, my), 2)
            pygame.draw.line(screen, local_color,
                             (mx, my - 12), (mx, my + 12), 2)
            you_label = font.render(
                "YOU" if my_peer_id is None else f"YOU (#{my_peer_id})",
                True, (240, 240, 250),
            )
            screen.blit(you_label, (mx + 14, my + 6))

            # HUD.
            hud_lines: List[str] = [
                f"server : {server_host}:{server_port}",
                f"peer   : {my_peer_id if my_peer_id is not None else '...'}",
                f"snaps  : {snaps_received}",
                f"buffer : {buf.size()} / {JITTER_BUFFER_MAXLEN}",
                f"remote : {sum(1 for k in rendered if k != my_peer_id)}",
                f"last   : {(current_s - last_snap_s) * 1000:5.1f} ms ago"
                if last_snap_s > 0.0 else "last   : -",
            ]
            for i, line in enumerate(hud_lines):
                surf = font.render(line, True, (200, 210, 220))
                screen.blit(surf, (8, 8 + i * 18))

            pygame.display.flip()
            clock.tick(CLIENT_FPS)

    finally:
        sock.close()
        pygame.quit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="LAN-only two-cursor shared-canvas demo (Pygame client + "
                    "Python authoritative server).",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--server", action="store_true",
                      help="Run in server mode (no window).")
    mode.add_argument("--client", metavar="HOST", type=str,
                      help="Run a Pygame client against the given host.")
    parser.add_argument("--port", type=int, default=PORT,
                        help=f"UDP port (default {PORT}).")
    parser.add_argument("--bind", type=str, default="0.0.0.0",
                        help="Server bind host (default 0.0.0.0).")
    return parser.parse_args()


def main() -> int:
    args: argparse.Namespace = parse_args()
    if args.server:
        run_server(args.bind, args.port)
    else:
        run_client(args.client, args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())


# HINT
# ----
# Variations worth trying:
#
# 1. Run THREE clients against the same server. The HUD's "remote"
#    count should read 2, and you should see two coloured cursors
#    in addition to your own.
#
# 2. Drop INTERP_DELAY_MS to 30 and watch the remote cursors stutter
#    intermittently when the buffer runs dry. Raise it to 250 ms and
#    they smooth out but visibly lag behind.
#
# 3. Drop SERVER_TICK_HZ to 5 (snapshot every 200 ms). The remote
#    cursors will still be smooth thanks to interpolation, but the
#    interp delay needs to rise to ~300 ms to keep two snapshots
#    in the buffer at all times.
#
# 4. Add an "input_dropper" knob: every Nth INPUT packet from the
#    client, skip the sendto. This simulates packet loss on the
#    input channel. Then watch what happens to the server's view of
#    the dropping client and the other client's render of them.
#
# 5. Capture loopback traffic with Wireshark (filter udp.port == 5005)
#    while the demo runs. Identify the snapshot packets by their
#    20 Hz cadence and the 13-byte INPUT packets at the client's
#    30 Hz cadence.
