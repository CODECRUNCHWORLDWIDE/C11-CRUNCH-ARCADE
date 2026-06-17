"""exercise-01-udp-echo.py

Goal
----
Build a UDP echo client and server in raw Python sockets. The server
binds to a port, receives a datagram, and sends it back. The client
times each round trip and reports a moving-average RTT.

This is the entry-point exercise for the week. It demonstrates the
minimal UDP API - socket(SOCK_DGRAM), bind, sendto, recvfrom - and
gives you a working tool to measure your own LAN's latency.

What you learn
--------------
- socket.socket(AF_INET, SOCK_DGRAM) creates a UDP socket.
- sock.bind((host, port)) on the server.
- sock.sendto(payload, addr) from either end.
- sock.recvfrom(bufsize) returns (bytes, sender_addr).
- A 16-bit sequence number prepended to each payload (the Fiedler-style
  packet header). Sequence numbers detect dropped and out-of-order
  packets.
- time.perf_counter for sub-millisecond RTT measurement.
- A bounded deque of recent RTTs for a moving-average display.

Expected behaviour
------------------
Server mode (--server):
    Listens on 0.0.0.0:5005. For each received datagram, prints a one-
    line summary and echoes the payload back to the sender.

Client mode (--client):
    Sends one PING datagram every 100 ms to the server. On each reply,
    computes the RTT and prints a rolling average over the last 32
    pings.

To run on one machine (two terminals):
    Terminal 1:  python exercise-01-udp-echo.py --server
    Terminal 2:  python exercise-01-udp-echo.py --client 127.0.0.1

To run across two LAN machines:
    On the host (LAN IP e.g. 192.168.1.10):
        python exercise-01-udp-echo.py --server
    On the joiner:
        python exercise-01-udp-echo.py --client 192.168.1.10

To complete
-----------
This exercise ships complete. Run it. Watch the RTT meter. Try the
LAN variant if you have a second machine; the difference between
localhost RTT (~0.1 ms) and a LAN peer (~2-10 ms) is instructive.

References
----------
- Glenn Fiedler, *Sending and Receiving Packets*:
  <https://gafferongames.com/post/sending_and_receiving_packets/>
- RFC 768, *User Datagram Protocol*:
  <https://www.rfc-editor.org/rfc/rfc768>
- Python docs, *socket* module:
  <https://docs.python.org/3/library/socket.html>
"""

from __future__ import annotations

import argparse
import collections
import socket
import struct
import sys
import time
from typing import Deque, Optional, Tuple


# ---------------------------------------------------------------------------
# Protocol constants
# ---------------------------------------------------------------------------

# A tiny header on every datagram. Two fields packed in network byte order:
#   - msg_type:  1 byte. 0x01 = PING, 0x02 = PONG.
#   - sequence:  2 bytes. Wraps at 65536.
# Total header: 3 bytes. Payload is whatever follows.
HEADER_STRUCT: struct.Struct = struct.Struct("!BH")
HEADER_SIZE: int = HEADER_STRUCT.size  # = 3 bytes

MSG_PING: int = 0x01
MSG_PONG: int = 0x02

PORT: int = 5005
RECV_BUFSIZE: int = 2048
PING_INTERVAL_S: float = 0.10
RTT_WINDOW: int = 32


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pack_header(msg_type: int, sequence: int) -> bytes:
    """Pack a 3-byte header. `sequence` is taken modulo 65536."""
    return HEADER_STRUCT.pack(msg_type, sequence & 0xFFFF)


def unpack_header(data: bytes) -> Tuple[int, int]:
    """Unpack a 3-byte header. Returns (msg_type, sequence)."""
    return HEADER_STRUCT.unpack_from(data, 0)


def now_ms() -> float:
    """Monotonic time in milliseconds, sub-ms resolution."""
    return time.perf_counter() * 1000.0


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

def run_server(bind_host: str, bind_port: int) -> None:
    """Run the UDP echo server until interrupted.

    The server binds to ``(bind_host, bind_port)``, blocks on
    ``recvfrom`` for each datagram, flips the message type from PING
    to PONG, and sends the datagram back to the sender. The sequence
    number and payload are passed through unchanged so the client can
    correlate replies to its outgoing pings.
    """
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((bind_host, bind_port))
    print(f"[server] listening on udp {bind_host}:{bind_port}")
    print(f"[server] (header size = {HEADER_SIZE} bytes, "
          f"protocol: 0x01=PING -> 0x02=PONG)")

    packets_seen: int = 0
    try:
        while True:
            data, addr = sock.recvfrom(RECV_BUFSIZE)
            packets_seen += 1
            if len(data) < HEADER_SIZE:
                print(f"[server] {addr}: short datagram ({len(data)} B), "
                      f"ignored")
                continue
            msg_type, seq = unpack_header(data)
            payload: bytes = data[HEADER_SIZE:]
            if msg_type != MSG_PING:
                print(f"[server] {addr}: unexpected msg_type 0x{msg_type:02x}")
                continue
            # Echo it back as a PONG with the same sequence and payload.
            reply: bytes = pack_header(MSG_PONG, seq) + payload
            sock.sendto(reply, addr)
            if packets_seen % 20 == 1:
                print(f"[server] {addr}: ping seq={seq} "
                      f"payload={len(payload)} B (echoed)")
    except KeyboardInterrupt:
        print("\n[server] interrupted, shutting down")
    finally:
        sock.close()


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

def run_client(server_host: str, server_port: int) -> None:
    """Run the UDP echo client until interrupted.

    The client sends one PING every PING_INTERVAL_S seconds. It records
    the local send time per sequence number in a dict, and computes
    the RTT when the matching PONG arrives. A moving-average RTT over
    the last RTT_WINDOW samples is printed every second.

    The socket is non-blocking; the main loop alternates between
    "drain all queued PONGs" and "if it is time, send the next PING."
    This is the same pattern the Pygame game loop uses in Exercise 3.
    """
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    server_addr: Tuple[str, int] = (server_host, server_port)
    print(f"[client] pinging {server_host}:{server_port} every "
          f"{PING_INTERVAL_S * 1000:.0f} ms (Ctrl-C to stop)")

    send_times_ms: dict[int, float] = {}
    rtts_ms: Deque[float] = collections.deque(maxlen=RTT_WINDOW)
    sent_count: int = 0
    recv_count: int = 0
    next_seq: int = 0
    next_send_ms: float = now_ms()
    last_report_ms: float = now_ms()

    try:
        while True:
            current_ms: float = now_ms()

            # --- Send phase ----------------------------------------
            if current_ms >= next_send_ms:
                seq: int = next_seq
                payload: bytes = b"hello-from-client"
                packet: bytes = pack_header(MSG_PING, seq) + payload
                try:
                    sock.sendto(packet, server_addr)
                    send_times_ms[seq] = current_ms
                    sent_count += 1
                    next_seq = (next_seq + 1) & 0xFFFF
                except OSError as exc:
                    print(f"[client] send error: {exc}")
                next_send_ms = current_ms + PING_INTERVAL_S * 1000.0

            # --- Receive phase (drain) -----------------------------
            while True:
                try:
                    data, _addr = sock.recvfrom(RECV_BUFSIZE)
                except BlockingIOError:
                    break
                except OSError as exc:
                    print(f"[client] recv error: {exc}")
                    break
                if len(data) < HEADER_SIZE:
                    continue
                msg_type, seq = unpack_header(data)
                if msg_type != MSG_PONG:
                    continue
                send_ms: Optional[float] = send_times_ms.pop(seq, None)
                if send_ms is None:
                    # Reply with no record - the original entry was
                    # already evicted as too-old. Ignore.
                    continue
                rtt_ms: float = now_ms() - send_ms
                rtts_ms.append(rtt_ms)
                recv_count += 1

            # --- Stale-send cleanup --------------------------------
            # Drop any send record older than 1 second; the matching
            # PONG is not coming back. (This is what "packet loss"
            # looks like at the application level.)
            stale_cutoff_ms: float = current_ms - 1000.0
            stale_seqs: list[int] = [s for s, t in send_times_ms.items()
                                     if t < stale_cutoff_ms]
            for s in stale_seqs:
                del send_times_ms[s]

            # --- Report ------------------------------------------
            if current_ms - last_report_ms >= 1000.0:
                last_report_ms = current_ms
                if rtts_ms:
                    avg_rtt: float = sum(rtts_ms) / len(rtts_ms)
                    min_rtt: float = min(rtts_ms)
                    max_rtt: float = max(rtts_ms)
                    loss_pct: float = 0.0
                    if sent_count > 0:
                        loss_pct = 100.0 * (1.0 - recv_count / sent_count)
                    print(f"[client] rtt avg={avg_rtt:6.2f} ms  "
                          f"min={min_rtt:5.2f}  max={max_rtt:5.2f}  "
                          f"sent={sent_count}  recv={recv_count}  "
                          f"loss={loss_pct:4.1f}%")
                else:
                    print(f"[client] no replies yet "
                          f"(sent={sent_count}, recv=0)")

            # --- Small sleep to avoid pegging a CPU core ---------
            time.sleep(0.005)

    except KeyboardInterrupt:
        print("\n[client] interrupted, shutting down")
    finally:
        sock.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Build the CLI: one of --server / --client HOST is required."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="UDP echo client/server with a moving-average RTT meter.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--server", action="store_true",
                      help="Run in server mode (bind on 0.0.0.0:PORT).")
    mode.add_argument("--client", metavar="HOST", type=str,
                      help="Run in client mode, ping the given host.")
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
# 1. Change PING_INTERVAL_S to 0.01 (100 Hz). On a busy Wi-Fi network
#    you should start to see non-trivial jitter (max_rtt much higher
#    than avg_rtt). On a wired LAN it should remain ~uniform.
#
# 2. Run two clients against the same server. The server's
#    one-line-per-20-pings log will interleave the two senders'
#    addresses, demonstrating that the same UDP socket can serve
#    multiple peers concurrently (no per-connection state).
#
# 3. Comment out the "stale send cleanup" block and watch
#    send_times_ms grow unboundedly. This is how memory leaks
#    happen in long-running network code; always evict stale state.
#
# 4. Make the payload larger - say, b"x" * 1400. You should see no
#    change in behaviour. Try b"x" * 2000 - on most networks this
#    will fragment at the IP layer, slightly raising RTT and slightly
#    raising loss rate. The "safe" UDP payload size is ~1400 bytes.
#
# 5. Kill the server while the client is running. The client prints
#    high loss but never crashes; UDP has no connection state, so
#    "the server is gone" looks identical to "every packet was lost."
#    This is why your application has to time out by hand.
