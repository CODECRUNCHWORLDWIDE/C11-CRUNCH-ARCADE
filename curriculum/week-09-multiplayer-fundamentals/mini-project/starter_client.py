"""starter_client.py - Mini-project scaffold for the Pygame client.

Copy this file into your mini-project repo as `client.py` and fill in
the TODO blocks. The structure is here; the wiring is yours to do.

Architecture
------------
A 60 fps Pygame client that:

  - Opens a 1024 x 768 window.
  - Sends HELLO at 5 Hz until WELCOME arrives.
  - Sends INPUT at 30 Hz with the current mouse position.
  - Drains inbound snapshots every frame; inserts into a JitterBuffer.
  - Renders the local cursor at `pygame.mouse.get_pos()`.
  - Renders every remote cursor at its interpolated position
    (t_render = t_now - INTERP_DELAY_MS / 1000).
  - Shows a HUD with peer_id, snapshot count, buffer size,
    ms-since-last-snap.
  - Shows a "RECONNECTING..." overlay when no snapshot has arrived
    for 2 seconds.

Run
---
    python client.py <server-ip>
    (default: 127.0.0.1)

References
----------
- Glenn Fiedler, *Snapshot Interpolation*:
  <https://gafferongames.com/post/snapshot_interpolation/>
- Pygame docs:
  <https://www.pygame.org/docs/>
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
# Configuration
# ---------------------------------------------------------------------------
# TODO Phase 1: Move into `protocol.py` and import.

PORT: int = 5005
RECV_BUFSIZE: int = 2048
CLIENT_FPS: int = 60
CLIENT_INPUT_HZ: int = 30
CLIENT_INPUT_DT_S: float = 1.0 / CLIENT_INPUT_HZ
HELLO_RETRY_S: float = 0.20
INTERP_DELAY_MS: float = 100.0
JITTER_BUFFER_MAXLEN: int = 16
RECONNECT_OVERLAY_AFTER_S: float = 2.0
WIN_W: int = 1024
WIN_H: int = 768

MSG_HELLO: int = 0x10
MSG_WELCOME: int = 0x11
MSG_SNAP: int = 0x12
MSG_INPUT: int = 0x13

INPUT_STRUCT: struct.Struct = struct.Struct("!BHff")
SNAP_HEADER: struct.Struct = struct.Struct("!BHd")
SNAP_COUNT: struct.Struct = struct.Struct("!H")
SNAP_ENTITY: struct.Struct = struct.Struct("!Iff")
WELCOME_STRUCT: struct.Struct = struct.Struct("!BH")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EntityState:
    peer_id: int
    x: float
    y: float


@dataclass(frozen=True)
class Snapshot:
    sequence: int
    server_time_s: float
    entities: Tuple[EntityState, ...]


# ---------------------------------------------------------------------------
# Snapshot parsing
# ---------------------------------------------------------------------------

def parse_snapshot(data: bytes) -> Optional[Snapshot]:
    """Unpack a SNAP datagram. Returns None on malformed input."""
    if len(data) < SNAP_HEADER.size + SNAP_COUNT.size:
        return None
    msg_type, sequence, server_time_s = SNAP_HEADER.unpack_from(data, 0)
    if msg_type != MSG_SNAP:
        return None
    (count,) = SNAP_COUNT.unpack_from(data, SNAP_HEADER.size)
    entities_offset: int = SNAP_HEADER.size + SNAP_COUNT.size
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
# Jitter buffer
# ---------------------------------------------------------------------------
# TODO Phase 5: Move JitterBuffer into its own module `jitter_buffer.py`
# and import it here. The inline version below is the starting point.

class JitterBuffer:
    """A bounded queue of recent snapshots, sorted by server_time."""

    def __init__(self, max_len: int = JITTER_BUFFER_MAXLEN) -> None:
        self._buf: Deque[Snapshot] = collections.deque(maxlen=max_len)

    def insert(self, snap: Snapshot) -> None:
        if not self._buf:
            self._buf.append(snap)
            return
        if snap.server_time_s > self._buf[-1].server_time_s:
            self._buf.append(snap)
            return
        # Out-of-order arrival: rebuild sorted.
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
    return EntityState(b.peer_id,
                       a.x + (b.x - a.x) * alpha,
                       a.y + (b.y - a.y) * alpha)


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
    """Deterministic colour via the golden ratio."""
    h: float = (peer_id * 0.61803398875) % 1.0
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
# Client main loop
# ---------------------------------------------------------------------------

def run_client(server_host: str, server_port: int) -> None:
    """Run the Pygame client until ESC or window close."""
    if pygame is None:
        print("ERROR: pygame not installed. Run: pip install pygame")
        sys.exit(1)

    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    server_addr: Tuple[str, int] = (server_host, server_port)

    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption(f"cursor-multiplayer  ->  "
                               f"{server_host}:{server_port}")
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

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN \
                        and event.key == pygame.K_ESCAPE:
                    running = False

            # -----------------------------------------------------------
            # TODO Phase 2: HELLO retransmit until WELCOMEd.
            # If my_peer_id is None and current_s - last_hello_s >=
            # HELLO_RETRY_S: send HELLO; update last_hello_s.
            # -----------------------------------------------------------

            # -----------------------------------------------------------
            # TODO Phase 3-5: Drain inbound socket.
            # For each datagram:
            #   - MSG_WELCOME: unpack peer_id; set my_peer_id.
            #   - MSG_SNAP: parse_snapshot; if server_time_offset_s is
            #     None, calibrate it; insert into the jitter buffer;
            #     update last_snap_s.
            # -----------------------------------------------------------

            # -----------------------------------------------------------
            # TODO Phase 4: Send INPUT at fixed cadence.
            # If my_peer_id is not None and current_s >= next_input_s:
            #   - Get pygame.mouse.get_pos().
            #   - Pack INPUT_STRUCT.pack(MSG_INPUT, seq, x, y).
            #   - sendto(server_addr).
            #   - next_input_s = current_s + CLIENT_INPUT_DT_S.
            # -----------------------------------------------------------

            # -----------------------------------------------------------
            # TODO Phase 5: Interpolate for rendering.
            # If server_time_offset_s is not None:
            #   t_render_s = (current_s - server_time_offset_s)
            #                 - (INTERP_DELAY_MS / 1000.0).
            #   bracket = buf.find_bracket(t_render_s).
            #   If bracket: rendered = interpolate_snapshot(older,
            #               newer, alpha).
            # -----------------------------------------------------------
            rendered: Dict[int, EntityState] = {}

            # -----------------------------------------------------------
            # Render
            # -----------------------------------------------------------
            screen.fill((20, 22, 28))

            # TODO Phase 8: Draw a 40-px grid background.

            # TODO Phase 5: For each remote peer in `rendered`, draw a
            # circle at its position. Skip my_peer_id (we render
            # ourselves separately, below). Use color_for_peer for the
            # fill colour.

            # TODO Phase 5: Draw the local cursor as a 24x24 crosshair
            # at pygame.mouse.get_pos(). Use color_for_peer(my_peer_id)
            # or white if not yet welcomed.

            # TODO Phase 6: Draw the HUD top-left with:
            #   server : <host>:<port>
            #   peer   : my_peer_id
            #   snaps  : snaps_received
            #   buffer : buf.size() / JITTER_BUFFER_MAXLEN
            #   remote : count of rendered keys != my_peer_id
            #   last   : (current_s - last_snap_s) * 1000 ms ago

            # TODO Phase 6: Draw the "RECONNECTING..." overlay if
            # current_s - last_snap_s > RECONNECT_OVERLAY_AFTER_S
            # (only if last_snap_s > 0; before first snapshot just
            # show "Connecting...").

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
        description="LAN cursor-multiplayer client.",
    )
    parser.add_argument("host", nargs="?", default="127.0.0.1",
                        help="Server IP (default 127.0.0.1).")
    parser.add_argument("--port", type=int, default=PORT,
                        help=f"UDP port (default {PORT}).")
    return parser.parse_args()


def main() -> int:
    args: argparse.Namespace = parse_args()
    run_client(args.host, args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
