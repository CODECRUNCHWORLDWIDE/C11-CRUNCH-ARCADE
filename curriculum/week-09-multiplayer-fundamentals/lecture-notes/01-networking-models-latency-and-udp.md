# Lecture 1 — Networking Models, Latency, and Why UDP

> **Duration:** ~2 hours of reading plus hands-on.
> **Outcome:** You can name the three networking models, justify the choice of UDP for game traffic in one sentence, cite the latency budget from memory, and read the byte-level format of a UDP datagram against RFC 768.

If you only remember one thing from this lecture, remember this:

> **A multiplayer game is a distributed system whose physics is bounded by the speed of light. Every other constraint — UDP vs TCP, snapshot rate, interpolation delay, prediction, reconciliation — is a consequence of that single fact. The whole job is to design *around* the latency you cannot avoid.**

The lecture begins with the three classic networking models for games, contrasts UDP and TCP at the protocol level, names the latency budget in concrete milliseconds, and ends with a byte-level read of the UDP header from RFC 768. By the end you can write the line `sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)` and know exactly what you are asking the kernel for.

We lean heavily on Glenn Fiedler's free *Networking for Game Programmers* series throughout. The four required articles for this lecture are *What every programmer needs to know about game networking*, *UDP vs. TCP*, *Sending and Receiving Packets*, and *Virtual Connection over UDP*. Read them in that order. They are short.

---

## 1. The three networking models

There are exactly three ways to architect a multiplayer game in 2026, and most games pick one and never deviate. Fiedler's *What every programmer needs to know about game networking* walks the full history; the summary follows.

### 1.1 Client-server authoritative

The server runs the real simulation. Clients are render terminals that send *inputs* and receive *state*. The server is the source of truth; if a client and the server disagree, the server wins.

```
                +----------------+
                |  AUTHORITATIVE |
                |     SERVER     |
                |  (the real     |
                |   simulation)  |
                +-------+--------+
                        |
       +----------------+----------------+
       |                |                |
  state v          state v          state v   inputs ^
       |                |                |
  +----+----+      +----+----+      +----+----+
  | Client  |      | Client  |      | Client  |
  | (render |      | (render |      | (render |
  |  +pred) |      |  +pred) |      |  +pred) |
  +---------+      +---------+      +---------+
```

This is the default for every shipped action game in the last 25 years that we would want to imitate: *Quake* (1996), *Half-Life* (1998), *Counter-Strike*, *Team Fortress 2*, *Overwatch*, *Apex Legends*, *Rocket League*, *Valorant*. The model wins on three axes:

- **Anti-cheat.** Cheating is bounded to "client lies to server about its inputs," which the server can validate. Without an authoritative server, every client is its own truth, and there is no honest place to detect lies.
- **Consistency.** Every client sees the same world state up to network latency. There is no "client A and client B disagree about who has the flag."
- **Bandwidth.** The server can decide what each client *needs to know*. A client far from a fight does not receive snapshots about that fight (*area of interest*). This is hard to do with peer-to-peer.

The cost is that you need a server. For an indie game, "a server" can be a dedicated process on one of the player's machines (a *listen-server* / *peer-hosted server*) or a hosted machine (a *dedicated server*). Both are authoritative server architectures; they differ in *where* the server runs, not in *what* it does.

This is what we build this week.

### 1.2 Peer-to-peer (trust-the-peer)

Each peer simulates its own piece of the world and broadcasts updates to everyone else.

```
   +---------+         +---------+
   | Peer A  | <-----> | Peer B  |
   +---+-----+         +-----+---+
       |                     |
       +---------+-----------+
                 |
            +----+----+
            | Peer C  |
            +---------+
```

Pros: no server to host; bandwidth scales linearly with peer count for small groups; latency from any peer A to any peer B is one direct hop (vs two hops through a server).

Cons: every peer can lie about its own state. "I have 200 hp now." "I just killed you." The model gives every player a cheating console. It also fails the consistency test: peers A and B can disagree about who picked up the powerup if their packets cross.

P2P-trust-the-peer is *out of fashion* for new games. The only modern category that still uses it is "two friends playing on console couch-style" — a low-stakes context where cheating does not matter.

We do not build this model. We mention it so that, when you read about old games (*Diablo II* in TCP-based multiplayer, *Age of Empires II* in lockstep, *Star Wars: Battlefront 2002*), you can identify what they were doing.

### 1.3 Lockstep deterministic

Every peer receives the same *input stream* in the same order and runs the same simulation locally. If the simulation is *deterministic* — the same inputs always produce the same outputs — every peer's state stays in sync without any state being sent over the wire.

```
                                  Inputs from
                                  every peer
                                       |
                          +------------+------------+
                          |            |            |
                       broadcast    broadcast    broadcast
                          |            |            |
                       +--v--+      +--v--+      +--v--+
                       | A   |      | B   |      | C   |
                       |sim()|      |sim()|      |sim()|
                       +--+--+      +--+--+      +--+--+
                       (same state each tick, because same inputs,
                        because deterministic simulation)
```

This is the model behind classic RTS games: *Age of Empires*, *StarCraft*, *Supreme Commander*. The trick: each tick of the simulation, every peer collects its own input, broadcasts it to every other peer, *waits* until it has received all peers' inputs for that tick, then advances the simulation by one tick.

Pros: bandwidth scales with the number of *inputs*, not the number of *entities*. 500 units on a battlefield cost the same to network as 5. Deterministic replays come free.

Cons: the simulation has to be *exactly* deterministic across all platforms. Floating-point math is allowed only with extreme care; integer math is preferred. One slow peer stalls everyone. *Desync* — when one peer's simulation diverges from another's — is catastrophic and hard to debug. Fighting games have made lockstep work via *rollback netcode* (a sophisticated variant); RTSes accept the stall.

We do not build this model. We mention it because fighting-game rollback netcode (e.g. GGPO, Skullgirls' netcode) is the most sophisticated networking in the indie scene and worth knowing exists. Challenge 2 asks you to sketch one on paper.

### 1.4 Which model and why

For C11's purposes — a 2D action arcade game with 2-8 players, on a college LAN — the answer is **client-server authoritative**. It is what every reference shipping game does. It is what Godot's high-level multiplayer API is shaped around. It is what Fiedler's series teaches. It is the only model we implement this week.

---

## 2. The latency budget

The number every multiplayer programmer carries in their head: **how much round-trip-time (RTT) is too much?**

The answers come from a generation of human-factors research and a generation of game post-mortems. They are not pinpoint exact, but the orders of magnitude are firm:

| RTT (round-trip) | Subjective experience                                       |
|-----------------:|-------------------------------------------------------------|
|  **0-50 ms**     | Feels native. LAN. Same-city fibre.                         |
|  **50-100 ms**   | Excellent. Cross-state fibre. Most North American players.  |
|  **100-150 ms**  | Good. Cross-country. Fully playable for every genre.        |
|  **150-200 ms**  | OK for non-twitch genres. Twitch shooters start to suffer.  |
|  **200-300 ms**  | Tolerable for turn-based. Bad for action.                   |
|  **300-500 ms**  | Wrong. Inputs feel delayed. Most players notice.            |
|  **500+ ms**     | Unplayable for real-time gameplay.                          |

For this week's mini-project, we target **anything under 150 ms RTT** as the playable ceiling. On a college LAN you should see <5 ms; on home Wi-Fi to a peer in the same building, <20 ms; across the open internet to a peer in the same continent, ~50-100 ms.

These numbers come from Fiedler's articles and from the Source Multiplayer Networking page on the Valve Developer Wiki. The Riot Games engineering blog *Peeking into Valorant's Netcode* tells you what 128 Hz competitive shooters target (well under 30 ms server tick + ~25 ms one-way network = ~80 ms total under-the-hood budget per player input).

### 2.1 Where does the latency *come from*?

Three sources, in roughly equal proportions on the open internet:

1. **Speed-of-light propagation.** Light in a fibre takes ~5 ms per 1000 km. New York to Los Angeles is ~4000 km, ~20 ms one-way. New York to Sydney is ~16000 km, ~80 ms one-way. You cannot beat this. It is physics.

2. **Routing and switching.** Each router a packet passes through adds 1-5 ms in queueing and forwarding decisions. A coast-to-coast US route can traverse 12-15 hops; an intercontinental route can traverse 25+.

3. **The last mile.** Your home Wi-Fi adds 1-10 ms; a saturated cable modem can add 50+ ms; a busy 4G cell can add 100+ ms. Players on mobile or DSL feel this most.

The sum is RTT. Fiedler's article *What every programmer needs to know about game networking* covers this with specific Quake-era numbers; the modern numbers are smaller but the proportions are similar.

### 2.2 Jitter is variance in RTT

Two connections can have the same average RTT and feel completely different. A connection with 100 ms RTT and 5 ms jitter — packets reliably arrive 95-105 ms after sending — feels stable; the renderer can interpolate ~110 ms behind and never run out of buffer. A connection with the same 100 ms average but 80 ms jitter — packets arrive anywhere from 60 to 180 ms after sending — *will* run the buffer dry occasionally, producing visible stutter.

We will spend Lecture 2 on the *jitter buffer*: a queue of received snapshots sized to ride out the worst few percent of jitter. The buffer is your insurance against the long tail of arrival times.

### 2.3 Packet loss is the third number

UDP delivers what arrives and silently drops what does not. The OS or the network may drop packets for many reasons (buffer overflow at a switch, signal corruption on Wi-Fi, deliberate policing). A 1% loss rate is the threshold of "acceptable"; 5% loss is the threshold of "this game is broken." Above 10% loss, no amount of clever interpolation will save the experience.

The lesson: we cannot assume packets arrive. Every state update must be designed such that *missing one* is recoverable. Snapshot-based replication has this property natively — the next snapshot supersedes the lost one. Event-based replication does not — a lost "you scored a point" event must be retransmitted.

---

## 3. UDP vs TCP — why UDP wins for games

This is the most-asked question in the introductory networking literature, and Fiedler's article *UDP vs. TCP* answers it definitively. Read it; the summary below covers the load-bearing argument.

### 3.1 TCP guarantees in-order, reliable delivery

TCP gives you a *stream*: bytes you write on one side appear in the same order on the other side, with no gaps. To deliver this guarantee, TCP:

- **Re-sends lost packets.** If a packet is not ACKed within an estimated round-trip, TCP re-sends it.
- **Buffers out-of-order packets.** If packet 5 arrives before packet 4, TCP holds 5 in a buffer until 4 arrives. *The application does not see 5 until 4 has been delivered.*
- **Slows down on loss.** Loss is interpreted as congestion; TCP reduces its send rate.

For a file transfer, a web page, an SSH session — these are exactly the right behaviours. You want the bytes; you want them in order; you can wait.

### 3.2 The fatal property: head-of-line blocking

For game traffic, the *order* and the *waiting* are both wrong.

Consider a 20 Hz game state snapshot stream:

```
   Server sends:  S1 .... S2 .... S3 .... S4 .... S5
                  |       |       |       |       |
                  t=0     t=50    t=100   t=150   t=200 ms

   Network drops S2.
   TCP behaviour at the client: holds S3, S4, S5 in a buffer
   while it asks the server to re-send S2. Re-send arrives at
   t=200ish. The client sees:

                  S1 .... <stall> .................. (S2,S3,S4,S5 burst)

   By the time S2-S5 are delivered, S5 was already the truth.
   The intermediate snapshots are obsolete the moment they arrive.
```

This is *head-of-line blocking*. One missing packet stalls every packet behind it. For a stream of *state updates*, this is exactly the wrong behaviour: each newer update is *more valuable* than the older one it would block on.

UDP does not do this. UDP delivers whatever arrives, whenever it arrives, in whatever order it arrives. If S2 is lost, the application receives S1, S3, S4, S5 and never sees S2. For state snapshots, this is *fine*: S5 already contains everything we needed S2 for, plus more.

### 3.3 The other UDP advantages

- **Smaller header.** UDP header is 8 bytes; TCP header is 20+ bytes. For 32-byte payloads at 20 Hz, the overhead difference is real.
- **No connection state.** UDP has no handshake (no SYN/SYN-ACK/ACK). The first packet you send is real game data. TCP costs you one full RTT before any data flows.
- **No congestion-control surprises.** TCP's slow-start and congestion-avoidance algorithms can cut your send rate without warning. UDP gives you a flat firehose; you decide the rate.

### 3.4 What UDP costs you

- **Reliability is your problem.** If a packet *must* arrive ("you scored," "the match started"), you have to layer your own retransmit-on-no-ack on top. Fiedler's *Reliability and Flow Control* article covers the minimal version; we will implement it in Week 10.
- **Ordering is your problem.** Packets can arrive out of order. Add a 16-bit sequence number; discard any packet with a sequence older than the highest you have already seen.
- **Connection state is your problem.** "Is this peer still talking to me?" is answered by your own application-level timeout. Fiedler's *Virtual Connection over UDP* article describes the minimal version.

For this week, we accept the cost. The exercises and mini-project use raw UDP with a sequence number; we do not retransmit anything; we assume the LAN is reliable enough that lost packets are rare and lost snapshots are covered by the next snapshot.

### 3.5 The short answer

> Use UDP for state. Use TCP for the lobby chat. Use UDP-with-an-ACK-layer for critical events. Never use TCP for game state.

This summarises the entire networking-protocol decision tree for a typical action game.

---

## 4. A UDP datagram at the byte level (RFC 768)

RFC 768 is four pages long. You should read it. The summary follows.

A UDP datagram has an 8-byte header followed by a payload of 0-65507 bytes (limited by IPv4 / IPv6 MTUs in practice to ~1400 bytes for a single datagram that does not fragment on the typical internet path).

```
   0                   1                   2                   3
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |          Source Port          |       Destination Port        |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |             Length            |            Checksum           |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                          Payload  ...                          |
  +---------------------------------------------------------------+
```

The four header fields, each 16 bits (2 bytes):

- **Source Port.** The port on the sender. In practice the OS assigns this when you `sendto` from a socket that has not explicitly bound a port.
- **Destination Port.** The port on the receiver. This is the port your server `bind`s to.
- **Length.** Total UDP length in bytes, *including* the 8-byte header.
- **Checksum.** A 16-bit one's-complement checksum of a pseudo-header plus the UDP datagram. Optional on IPv4 (set to 0 to indicate "no checksum"); mandatory on IPv6.

Below the UDP header, on IPv4, is the 20-byte IP header (RFC 791), which carries source / destination IP addresses. Below that is the Ethernet / Wi-Fi frame. For our purposes, the OS takes care of the IP and link layers; we work at the UDP-and-up level.

When you call `sock.sendto(b"hello", ("192.168.1.5", 5005))`, the kernel:

1. Wraps `b"hello"` in a UDP datagram (header + 5-byte payload, total 13 bytes).
2. Wraps that in an IP packet to `192.168.1.5`.
3. Hands it to the network driver.

When you call `sock.recvfrom(2048)` on the other side, the kernel:

1. Reads the next queued UDP datagram from the kernel buffer for your socket.
2. Strips the UDP header.
3. Returns the payload bytes and the sender's `(ip, port)` tuple.

Nothing about UDP is mysterious. RFC 768 is one of the shortest, oldest protocol specs you will ever read. The author, Jon Postel, wrote it in 1980. It has not changed since.

---

## 5. Sockets in Python — the minimal API

The whole exercise stack lives in three functions and a constructor.

### 5.1 The constructor

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
```

`AF_INET` is IPv4. (`AF_INET6` is IPv6; same UDP semantics.) `SOCK_DGRAM` is "give me a UDP socket"; the alternative `SOCK_STREAM` is TCP. We always want `SOCK_DGRAM` this week.

### 5.2 `bind` (the server)

```python
sock.bind(("0.0.0.0", 5005))
```

`bind` tells the kernel "I want to receive datagrams sent to this port." `"0.0.0.0"` means "any interface"; `"127.0.0.1"` would mean loopback only; the specific IP of your machine would mean "only datagrams arriving on that interface." For a server on a LAN, `"0.0.0.0"` is the right answer.

Port 5005 is arbitrary — pick anything in the 1024-65535 range that does not conflict with another service. Ports below 1024 are privileged on Unix.

### 5.3 `sendto` (the client, and the server's reply)

```python
sock.sendto(payload_bytes, (dest_ip, dest_port))
```

`payload_bytes` is a `bytes` object (not `str`). The size is limited by the network MTU; in practice keep it under ~1400 bytes per datagram to avoid IP fragmentation, and ideally under ~512 bytes for safe traversal across the open internet.

### 5.4 `recvfrom` (the receiver)

```python
data, addr = sock.recvfrom(2048)
```

`recvfrom` blocks by default until a datagram arrives. `2048` is the buffer size; any datagram larger than this is truncated. `data` is `bytes`; `addr` is `(sender_ip, sender_port)`. To poll without blocking, set `sock.setblocking(False)` and catch `BlockingIOError` when the queue is empty.

### 5.5 The minimal echo server in Python

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5005))
print("Echo server listening on UDP port 5005...")

while True:
    data, addr = sock.recvfrom(2048)
    print(f"received {len(data)} bytes from {addr}")
    sock.sendto(data, addr)
```

That is the whole server. Twelve lines including the prints. The client is symmetric: `socket(AF_INET, SOCK_DGRAM)`, `sendto`, `recvfrom`, done. Exercise 1 wraps both in a single file with a RTT meter.

### 5.6 Non-blocking sockets

For a game loop running at 60 fps, blocking on `recvfrom` is wrong — we need to drain whatever is queued and then move on. The pattern:

```python
sock.setblocking(False)

# Every frame:
while True:
    try:
        data, addr = sock.recvfrom(2048)
    except BlockingIOError:
        break
    handle(data, addr)
```

The `while True` drains the kernel buffer; the `BlockingIOError` is how the kernel signals "no more packets right now." This loop is the only correct way to consume UDP in a real-time game loop.

---

## 6. The TCP digression — when *would* you use TCP?

For completeness: TCP is the right choice for these categories of game traffic:

- **Lobby and matchmaking.** "Find a game," "join this match," "show the player list." None of this is real-time. TCP's reliability is helpful; head-of-line blocking does not matter because there is no continuous stream.
- **Chat.** Chat messages must arrive; they must arrive in order; they tolerate ~200 ms of latency on the wire. TCP is correct.
- **Asset downloads / patcher.** Self-evidently TCP.
- **Persistent state.** Saving a player's progress to a server-side database. TCP underneath HTTPS, almost always.

The dividing line is the answer to: *"if a packet is delayed by 100 ms, does the experience break?"* If yes, UDP. If no, TCP.

---

## 7. The data-flow picture

Putting it all together, the data flow for a typical authoritative-server game looks like:

```
  +--------+      inputs (every frame)         +--------+
  | Client |  -------------------------------> |        |
  |   A    |  <-------------------------------+ Server |
  +--------+      snapshots (every 50 ms)     |        |
                                              |        |
  +--------+      inputs (every frame)        |        |
  | Client |  -------------------------------> |        |
  |   B    |  <-------------------------------+        |
  +--------+      snapshots (every 50 ms)     +--------+
```

Two streams of data per client:

- **Client to server: inputs.** Small (a few bytes per frame). Sent at the client's frame rate (60 Hz). UDP. Sequence-numbered so the server can discard out-of-order or stale inputs.
- **Server to client: snapshots.** Larger (a few hundred bytes for an 8-player game). Sent at the server's snapshot tick rate (10-30 Hz). UDP. Sequence-numbered so the client can identify the latest and interpolate between the last two.

That is the architecture. Lecture 2 fills in the *client side* — how the client renders smoothly off a 20 Hz input. Lecture 3 shows what this looks like in Godot.

---

## 8. The mental-model check

Before moving on, you should be able to answer these without notes:

1. *Why is UDP the right transport for game state?* — Because head-of-line blocking in TCP turns a single dropped packet into a stall, and the next state update is more valuable than the missing one.
2. *What is the playable RTT ceiling?* — Roughly 150 ms for most games; below 100 ms for competitive twitch shooters; above 300 ms is wrong for everything real-time.
3. *Why is the server authoritative and not the client?* — Anti-cheat, consistency, and per-client bandwidth control. The simulation has one true home.
4. *What is the UDP header size?* — 8 bytes. Four 16-bit fields: source port, destination port, length, checksum.
5. *What three sources contribute to RTT?* — Speed-of-light propagation, router queueing/switching, and the last mile.

If any of those are shaky, re-read the relevant section and the matching Fiedler article. They will recur every lecture this semester.

---

## Up next

Lecture 2 covers the client-side smoothing layer: snapshot interpolation, the jitter buffer, the intuition behind client-side prediction and server reconciliation, and the state-vs-event distinction. Then we hand-build the smoothing layer in Python with Exercises 2 and 3.

Read Fiedler's *Snapshot Interpolation* before Lecture 2. It is the single most useful 20-minute read of the week.

---

*References cited in this lecture:*

- *Glenn Fiedler, Networking for Game Programmers (gafferongames.com)* — the canonical series.
- *RFC 768, User Datagram Protocol, Jon Postel, 1980* — the four-page UDP spec.
- *Valve Developer Wiki, Source Multiplayer Networking* — industry reference.
- *Python docs, socket module reference* — the Python API.
