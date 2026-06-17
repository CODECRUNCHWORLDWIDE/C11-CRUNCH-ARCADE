"""exercise-02-snapshot-loop.py

Goal
----
Build a 20 Hz authoritative snapshot server and a 60 Hz client with a
jitter buffer and linear interpolation. The simulation is intentionally
trivial - a single point moving in a slow circle at the server's
authority - so all of the runtime can be devoted to the network and
interpolation discipline.

This exercise is HEADLESS (no Pygame, no window). The client prints
its interpolated position every 100 ms. The point is to see snapshot
interpolation work *as numbers* before adding the rendering layer in
Exercise 3.

What you learn
--------------
- A fixed-rate server loop that ticks the simulation every 50 ms
  (20 Hz) and broadcasts a snapshot per tick.
- A struct-packed snapshot payload: server_timestamp + entity_count
  + (id, x, y) tuples.
- A non-blocking client socket drained every "frame" (16.6 ms).
- A bounded deque jitter buffer of received snapshots.
- The snapshot-interpolation lookup: given t_render, find the two
  snapshots whose server-times bracket it, compute alpha, lerp.
- The INTERP_DELAY_MS constant: the client always renders 100 ms
  behind real time so that it has bracketing snapshots.

Expected behaviour
------------------
Server mode (--server):
    Binds on 0.0.0.0:5005. Every 50 ms, advances a single entity in
    a circular path, serialises the world to a snapshot, and broadcasts
    to every client that has said HELLO.

Client mode (--client HOST):
    Sends HELLO every 200 ms until the server replies with WELCOME.
    Then drains snapshots into the jitter buffer; every 100 ms,
    prints the interpolated entity position with metadata (snapshots
    received, jitter buffer size, RTT estimate).

To run on one machine (two terminals):
    Terminal 1:  python exercise-02-snapshot-loop.py --server
    Terminal 2:  python exercise-02-snapshot-loop.py --client 127.0.0.1

To complete
-----------
This exercise ships complete. Read top-to-bottom. Run it. Watch the
interpolated x-y values trace a smooth circle even though only 20
snapshots per second arrive. Stop the server briefly mid-run and
watch the client gracefully degrade (jitter buffer drains, then
extrapolation kicks in or the last known position freezes).

References
----------
- Glenn Fiedler, *Snapshot Interpolation*:
  <https://gafferongames.com/post/snapshot_interpolation/>
- Glenn Fiedler, *State Synchronisation*:
  <https://gafferongames.com/post/state_synchronization/>
- Gabriel Gambetta, *Fast-Paced Multiplayer parts 1-4*:
  <https://www.gabrielgambetta.com/client-server-game-architecture.html>
- Python docs, *struct*:
  <https://docs.python.org/3/library/struct.html>
"""

from __future__ import annotations

import argparse
import collections
import math
import socket
import struct
import sys
import time
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------

# Three message types:
#   - HELLO   client -> server, "I want to receive snapshots"
#   - WELCOME server -> client, "acknowledged, you are peer N"
#   - SNAP    server -> client, world state at this tick

MSG_HELLO: int = 0x10
MSG_WELCOME: int = 0x11
MSG_SNAP: int = 0x12

# Snapshot wire format:
#   header     = !BHd      msg_type (1B) + sequence (2B) + server_time_s (8B)
#   entity_n   = !H        count (2B)
#   per entity = !Iff      id (4B) + x (4B) + y (4B)
SNAP_HEADER: struct.Struct = struct.Struct("!BHd")
SNAP_COUNT: struct.Struct = struct.Struct("!H")
SNAP_ENTITY: struct.Struct = struct.Struct("!Iff")

# Tick / interp parameters.
SERVER_TICK_HZ: int = 20
SERVER_TICK_DT_S: float = 1.0 / SERVER_TICK_HZ
CLIENT_TICK_HZ: int = 60
CLIENT_TICK_DT_S: float = 1.0 / CLIENT_TICK_HZ
INTERP_DELAY_MS: float = 100.0
JITTER_BUFFER_MAXLEN: int = 16

PORT: int = 5005
RECV_BUFSIZE: int = 2048

# Simulation parameters - a single entity moves in a circle.
ENTITY_ID: int = 1
CIRCLE_CENTER_X: float = 320.0
CIRCLE_CENTER_Y: float = 240.0
CIRCLE_RADIUS: float = 150.0
CIRCLE_PERIOD_S: float = 5.0


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EntityState:
    """One entity's state at a moment in server time."""
    entity_id: int
    x: float
    y: float


@dataclass(frozen=True)
class Snapshot:
    """A complete world state as broadcast by the server."""
    sequence: int
    server_time_s: float
    entities: Tuple[EntityState, ...]


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def serialise_snapshot(snap: Snapshot) -> bytes:
    """Pack a Snapshot into a UDP payload."""
    buf: bytearray = bytearray()
    buf += SNAP_HEADER.pack(MSG_SNAP, snap.sequence & 0xFFFF,
                            snap.server_time_s)
    buf += SNAP_COUNT.pack(len(snap.entities))
    for ent in snap.entities:
        buf += SNAP_ENTITY.pack(ent.entity_id, ent.x, ent.y)
    return bytes(buf)


def parse_snapshot(data: bytes) -> Optional[Snapshot]:
    """Unpack a UDP payload into a Snapshot, or return None on malformed."""
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
        eid, ex, ey = SNAP_ENTITY.unpack_from(data, offset)
        entities.append(EntityState(eid, ex, ey))
    return Snapshot(sequence, server_time_s, tuple(entities))


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

def simulate_entity(server_time_s: float) -> EntityState:
    """Compute the canonical entity position at the given server time.

    The entity moves in a slow circle at constant angular velocity.
    The result is purely a function of time, so any client can
    independently compute the "ground truth" for cross-checking.
    """
    phase: float = (server_time_s / CIRCLE_PERIOD_S) * 2.0 * math.pi
    x: float = CIRCLE_CENTER_X + CIRCLE_RADIUS * math.cos(phase)
    y: float = CIRCLE_CENTER_Y + CIRCLE_RADIUS * math.sin(phase)
    return EntityState(ENTITY_ID, x, y)


def run_server(bind_host: str, bind_port: int) -> None:
    """Run the authoritative snapshot server until interrupted."""
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((bind_host, bind_port))
    sock.setblocking(False)
    print(f"[server] listening on udp {bind_host}:{bind_port}  "
          f"(tick={SERVER_TICK_HZ} Hz)")

    clients: Dict[Tuple[str, int], int] = {}    # addr -> peer_id
    next_peer_id: int = 100
    sequence: int = 0
    server_start_s: float = time.monotonic()
    next_tick_s: float = time.monotonic()

    try:
        while True:
            current_s: float = time.monotonic()

            # --- Drain incoming HELLOs ---------------------------
            while True:
                try:
                    data, addr = sock.recvfrom(RECV_BUFSIZE)
                except BlockingIOError:
                    break
                if not data:
                    continue
                msg_type: int = data[0]
                if msg_type == MSG_HELLO:
                    if addr not in clients:
                        clients[addr] = next_peer_id
                        print(f"[server] new client {addr} -> "
                              f"peer_id={next_peer_id}")
                        next_peer_id += 1
                    welcome: bytes = struct.pack("!BH", MSG_WELCOME,
                                                 clients[addr])
                    sock.sendto(welcome, addr)

            # --- Server tick (every 50 ms) -----------------------
            if current_s >= next_tick_s:
                server_time_s: float = current_s - server_start_s
                entity: EntityState = simulate_entity(server_time_s)
                snap: Snapshot = Snapshot(sequence, server_time_s,
                                          (entity,))
                payload: bytes = serialise_snapshot(snap)
                for addr in list(clients.keys()):
                    try:
                        sock.sendto(payload, addr)
                    except OSError:
                        # Client gone. Drop and continue.
                        del clients[addr]
                sequence = (sequence + 1) & 0xFFFF
                next_tick_s += SERVER_TICK_DT_S
                # Catch up if we fell behind by more than one tick.
                if current_s - next_tick_s > SERVER_TICK_DT_S:
                    next_tick_s = current_s + SERVER_TICK_DT_S

            # Small sleep to avoid pegging the CPU.
            time.sleep(0.001)

    except KeyboardInterrupt:
        print("\n[server] interrupted, shutting down")
    finally:
        sock.close()


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class JitterBuffer:
    """A bounded queue of recent snapshots, ordered by server_time.

    The buffer absorbs jitter and packet loss: new arrivals are
    inserted in server-time order, stale entries are evicted when the
    queue is full, and the interpolator reads bracketing pairs.
    """

    def __init__(self, max_len: int = JITTER_BUFFER_MAXLEN) -> None:
        self._buf: Deque[Snapshot] = collections.deque(maxlen=max_len)

    def insert(self, snap: Snapshot) -> None:
        """Insert a snapshot, keeping the deque sorted by server_time.

        Out-of-order arrivals (rare on LAN, possible on the open
        internet) are placed at the correct position. Duplicates
        (same server_time as an existing entry) are ignored.
        """
        if not self._buf:
            self._buf.append(snap)
            return
        # Fast path: arrived after the latest. Most common.
        if snap.server_time_s > self._buf[-1].server_time_s:
            self._buf.append(snap)
            return
        # Slow path: arrived earlier than something already in the
        # buffer. Rebuild the deque in sorted order.
        existing: List[Snapshot] = list(self._buf)
        existing.append(snap)
        existing.sort(key=lambda s: s.server_time_s)
        # Drop duplicates.
        dedup: List[Snapshot] = []
        last_time: float = -1.0
        for s in existing:
            if s.server_time_s != last_time:
                dedup.append(s)
                last_time = s.server_time_s
        self._buf.clear()
        for s in dedup[-self._buf.maxlen if self._buf.maxlen else 0:]:
            self._buf.append(s)

    def size(self) -> int:
        return len(self._buf)

    def latest_server_time(self) -> Optional[float]:
        if not self._buf:
            return None
        return self._buf[-1].server_time_s

    def find_bracket(self, t_render_s: float) -> Optional[Tuple[Snapshot,
                                                                Snapshot,
                                                                float]]:
        """Return (older, newer, alpha) for the pair bracketing t_render.

        ``alpha`` is in [0.0, 1.0] - it is how far ``t_render`` sits
        between the two snapshots. Returns ``None`` if no bracketing
        pair exists (the buffer has too few entries, or t_render is
        outside the buffered range).
        """
        if len(self._buf) < 2:
            return None
        # Walk in reverse so the common case (recent times) is fast.
        # The deque is sorted; pick the largest pair whose older
        # entry is <= t_render.
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
    """Linear-interpolate two EntityStates."""
    return EntityState(
        a.entity_id,
        a.x + (b.x - a.x) * alpha,
        a.y + (b.y - a.y) * alpha,
    )


def interpolate_snapshot(older: Snapshot, newer: Snapshot,
                         alpha: float) -> Dict[int, EntityState]:
    """Build the interpolated entity dict for a render frame.

    Entities present in ``newer`` but not ``older`` snap in at full
    weight (the first frame they appear). Entities present in ``older``
    but not ``newer`` are dropped (they have despawned).
    """
    older_map: Dict[int, EntityState] = {e.entity_id: e for e in older.entities}
    result: Dict[int, EntityState] = {}
    for ent_newer in newer.entities:
        ent_older: Optional[EntityState] = older_map.get(ent_newer.entity_id)
        if ent_older is None:
            result[ent_newer.entity_id] = ent_newer
        else:
            result[ent_newer.entity_id] = lerp_entity(ent_older,
                                                     ent_newer, alpha)
    return result


def run_client(server_host: str, server_port: int) -> None:
    """Run the headless interpolation client until interrupted."""
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    server_addr: Tuple[str, int] = (server_host, server_port)
    print(f"[client] connecting to {server_host}:{server_port}  "
          f"(interp delay = {INTERP_DELAY_MS:.0f} ms)")

    buf: JitterBuffer = JitterBuffer()
    my_peer_id: Optional[int] = None
    last_hello_s: float = 0.0
    snaps_received: int = 0
    # Local-to-server time mapping. The first snapshot we receive
    # establishes the mapping; subsequent renders compute t_render
    # in server-time using the same offset.
    server_time_offset_s: Optional[float] = None
    last_print_s: float = time.monotonic()
    last_loop_s: float = time.monotonic()

    try:
        while True:
            current_s: float = time.monotonic()

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
                    my_peer_id = peer_id
                    print(f"[client] welcomed as peer_id={peer_id}")
                elif msg_type == MSG_SNAP:
                    snap: Optional[Snapshot] = parse_snapshot(data)
                    if snap is None:
                        continue
                    if server_time_offset_s is None:
                        # First snapshot. Calibrate: t_local = t_server + offset.
                        server_time_offset_s = current_s - snap.server_time_s
                    buf.insert(snap)
                    snaps_received += 1

            # --- Render-frame work ------------------------------
            if server_time_offset_s is not None:
                # t_render in server-time, INTERP_DELAY_MS behind real time.
                t_render_s: float = (current_s - server_time_offset_s) \
                    - (INTERP_DELAY_MS / 1000.0)
                bracket = buf.find_bracket(t_render_s)
                if bracket is not None:
                    older, newer, alpha = bracket
                    rendered: Dict[int, EntityState] = interpolate_snapshot(
                        older, newer, alpha,
                    )
                else:
                    rendered = {}
            else:
                rendered = {}

            # --- Periodic print --------------------------------
            if current_s - last_print_s >= 0.1:
                last_print_s = current_s
                latest: Optional[float] = buf.latest_server_time()
                ground_truth: Optional[EntityState] = None
                if server_time_offset_s is not None:
                    t_render_s = (current_s - server_time_offset_s) \
                        - (INTERP_DELAY_MS / 1000.0)
                    ground_truth = simulate_entity(t_render_s)
                ent_render: Optional[EntityState] = rendered.get(ENTITY_ID)
                if ent_render is not None and ground_truth is not None:
                    err_x: float = ent_render.x - ground_truth.x
                    err_y: float = ent_render.y - ground_truth.y
                    err: float = math.sqrt(err_x * err_x + err_y * err_y)
                    print(f"[client] render xy=({ent_render.x:6.1f},"
                          f"{ent_render.y:6.1f})  "
                          f"err={err:5.2f} px  "
                          f"snaps={snaps_received}  "
                          f"buf={buf.size()}  "
                          f"latest={latest:.2f}s")
                else:
                    print(f"[client] (no render yet)  "
                          f"snaps={snaps_received}  buf={buf.size()}")

            # --- Frame sleep ---------------------------------
            frame_elapsed_s: float = time.monotonic() - last_loop_s
            sleep_s: float = CLIENT_TICK_DT_S - frame_elapsed_s
            if sleep_s > 0.0:
                time.sleep(sleep_s)
            last_loop_s = time.monotonic()

    except KeyboardInterrupt:
        print("\n[client] interrupted, shutting down")
    finally:
        sock.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="20 Hz snapshot server + 60 Hz interpolation client.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--server", action="store_true",
                      help="Run in server mode.")
    mode.add_argument("--client", metavar="HOST", type=str,
                      help="Run in client mode against the given host.")
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
# Things to notice:
#
# 1. The "err" column on the client should be small but not zero. Even
#    a perfect interpolator has linear error on a curved path - the
#    chord through two snapshots is not the arc. For a 20 Hz server
#    and 100 ms interp delay on a 5-second circle, expect ~0.5-2 px.
#
# 2. Drop INTERP_DELAY_MS to 30 ms. The buffer often has <2 snapshots
#    bracketing t_render; you will see "(no render yet)" appear
#    intermittently. The 100 ms default is a reasonable LAN choice.
#
# 3. Raise INTERP_DELAY_MS to 300 ms. The render is visibly behind
#    the ground truth. Useful for high-jitter links; bad for action.
#
# 4. Kill the server mid-run. The client keeps printing its last
#    rendered position until the t_render advances past the newest
#    buffered snapshot, then prints "(no render yet)".
#
# 5. Add a second entity to simulate_entity(): another point moving
#    in a different orbit. Notice that the wire format already
#    supports any number of entities via the count field.
