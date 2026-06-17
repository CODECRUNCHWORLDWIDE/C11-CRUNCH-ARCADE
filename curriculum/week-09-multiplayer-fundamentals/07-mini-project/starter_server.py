"""starter_server.py - Mini-project scaffold for the authoritative server.

Copy this file into your mini-project repo as `server.py` and fill in
the TODO blocks. The structure is here; the wiring is yours to do.

Architecture
------------
A single-process, single-socket UDP authoritative server.

  - Binds on 0.0.0.0:PORT.
  - On HELLO from a new (ip, port) tuple, allocates a peer_id and
    replies with WELCOME.
  - On INPUT from a known peer, updates that peer's stored cursor
    position (clamped to canvas bounds for validation).
  - Every 50 ms (20 Hz), broadcasts a SNAP containing every peer's
    latest position.
  - Evicts peers silent for more than CLIENT_TIMEOUT_S seconds.

Wire format
-----------
See `protocol.py` (to be created in your mini-project repo).

Run
---
    python server.py

References
----------
- Glenn Fiedler, *Sending and Receiving Packets*:
  <https://gafferongames.com/post/sending_and_receiving_packets/>
- Glenn Fiedler, *Snapshot Interpolation*:
  <https://gafferongames.com/post/snapshot_interpolation/>
- Python docs, *socket*:
  <https://docs.python.org/3/library/socket.html>
"""

from __future__ import annotations

import socket
import struct
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------
# TODO Phase 1: Move these into your `protocol.py` once it exists, and
# import them here. The starter keeps them inline so the file compiles
# in isolation.

PORT: int = 5005
BIND_HOST: str = "0.0.0.0"
RECV_BUFSIZE: int = 2048
SERVER_TICK_HZ: int = 20
SERVER_TICK_DT_S: float = 1.0 / SERVER_TICK_HZ
CLIENT_TIMEOUT_S: float = 5.0
WIN_W: int = 1024
WIN_H: int = 768

MSG_HELLO: int = 0x10
MSG_WELCOME: int = 0x11
MSG_SNAP: int = 0x12
MSG_INPUT: int = 0x13

INPUT_STRUCT: struct.Struct = struct.Struct("!BHff")    # msg + seq + x + y
SNAP_HEADER: struct.Struct = struct.Struct("!BHd")      # msg + seq + t
SNAP_COUNT: struct.Struct = struct.Struct("!H")
SNAP_ENTITY: struct.Struct = struct.Struct("!Iff")      # peer + x + y
WELCOME_STRUCT: struct.Struct = struct.Struct("!BH")    # msg + peer_id


# ---------------------------------------------------------------------------
# Per-peer state
# ---------------------------------------------------------------------------

@dataclass
class ServerPeer:
    """Per-peer state. One entry per connected client."""
    peer_id: int
    addr: Tuple[str, int]
    x: float
    y: float
    last_seen_s: float


# ---------------------------------------------------------------------------
# Snapshot serialisation
# ---------------------------------------------------------------------------

def serialise_snapshot(sequence: int, server_time_s: float,
                       peers: Dict[Tuple[str, int], ServerPeer]) -> bytes:
    """Pack the current world state into a UDP payload."""
    buf: bytearray = bytearray()
    buf += SNAP_HEADER.pack(MSG_SNAP, sequence & 0xFFFF, server_time_s)
    buf += SNAP_COUNT.pack(len(peers))
    for pr in peers.values():
        buf += SNAP_ENTITY.pack(pr.peer_id, pr.x, pr.y)
    return bytes(buf)


# ---------------------------------------------------------------------------
# Server main loop
# ---------------------------------------------------------------------------

def run_server() -> None:
    """The server's only entry point. Runs until Ctrl-C."""
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((BIND_HOST, PORT))
    sock.setblocking(False)
    print(f"[server] listening on udp {BIND_HOST}:{PORT}  "
          f"(tick={SERVER_TICK_HZ} Hz)")

    peers: Dict[Tuple[str, int], ServerPeer] = {}
    next_peer_id: int = 100
    sequence: int = 0
    server_start_s: float = time.monotonic()
    next_tick_s: float = time.monotonic()

    try:
        while True:
            current_s: float = time.monotonic()

            # -----------------------------------------------------------
            # TODO Phase 2: Drain inbound socket. For each datagram,
            # inspect data[0]:
            #   - MSG_HELLO: if (addr) is new, allocate peer_id, append
            #     to `peers`. Always reply with WELCOME.
            #   - MSG_INPUT: if (addr) is known, unpack x/y, clamp to
            #     WIN_W/WIN_H, update peer.x / peer.y / peer.last_seen_s.
            # -----------------------------------------------------------
            while True:
                try:
                    data, addr = sock.recvfrom(RECV_BUFSIZE)
                except BlockingIOError:
                    break
                if not data:
                    continue
                msg_type: int = data[0]
                if msg_type == MSG_HELLO:
                    # TODO: Insert HELLO handling here.
                    pass
                elif msg_type == MSG_INPUT \
                        and len(data) >= INPUT_STRUCT.size:
                    # TODO: Insert INPUT handling here.
                    pass

            # -----------------------------------------------------------
            # TODO Phase 7: Evict stale peers.
            # For any peer where current_s - peer.last_seen_s >
            # CLIENT_TIMEOUT_S, remove from `peers` and print a line.
            # -----------------------------------------------------------
            stale: List[Tuple[str, int]] = []
            # ...

            # -----------------------------------------------------------
            # TODO Phase 3: Server tick.
            # If current_s >= next_tick_s:
            #   - Build the snapshot via serialise_snapshot(...).
            #   - sendto each peer's addr.
            #   - sequence = (sequence + 1) & 0xFFFF.
            #   - next_tick_s += SERVER_TICK_DT_S, with catch-up logic.
            # -----------------------------------------------------------
            if current_s >= next_tick_s:
                # TODO: Build and broadcast snapshot.
                next_tick_s += SERVER_TICK_DT_S
                if current_s - next_tick_s > SERVER_TICK_DT_S:
                    next_tick_s = current_s + SERVER_TICK_DT_S

            # Small sleep to avoid pegging a CPU core.
            time.sleep(0.001)

    except KeyboardInterrupt:
        print("\n[server] interrupted, shutting down")
    finally:
        sock.close()


def main() -> int:
    run_server()
    return 0


if __name__ == "__main__":
    sys.exit(main())
