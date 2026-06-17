# Week 9 — Resources

Every resource on this page is **free** and **publicly accessible**. No paywalled books, no proprietary PDFs. If a link breaks, please open an issue.

## Required reading and watching (work it into your week)

- **Glenn Fiedler — *Networking for Game Programmers* (free, gafferongames.com).** The single best free resource on real-time networking for games. Written by a senior engine networking engineer. Read the first four articles before Tuesday; the rest by Friday. Cited on every page this week:
  <https://gafferongames.com/categories/game-networking/>
- **Glenn Fiedler — *UDP vs. TCP* (free).** Read first. The article that justifies every other decision in the week:
  <https://gafferongames.com/post/udp_vs_tcp/>
- **Glenn Fiedler — *Sending and Receiving Packets* (free).** The minimal Python-equivalent of `socket.SOCK_DGRAM` in C. Translates directly to Exercise 1:
  <https://gafferongames.com/post/sending_and_receiving_packets/>
- **Glenn Fiedler — *Snapshot Interpolation* (free).** The technique behind Exercise 2 and the mini-project. Read this twice — once before writing the exercise, once after:
  <https://gafferongames.com/post/snapshot_interpolation/>
- **Godot 4.x — *High-level multiplayer* tutorial (free).** The editor- and `@rpc`-driven introduction. The bridge for Lecture 3:
  <https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html>
- **RFC 768 — *User Datagram Protocol* (free, IETF).** Four pages. The format of the UDP header at the byte level. Read in one sitting:
  <https://www.rfc-editor.org/rfc/rfc768>

## Glenn Fiedler's articles (read in order)

The series builds on itself. Read in order, do not skip:

- **Fiedler — *What every programmer needs to know about game networking* (free).** The history-of-game-networking primer. Quake, Tribes, Counter-Strike: how each game shaped the standard model:
  <https://gafferongames.com/post/what_every_programmer_needs_to_know_about_game_networking/>
- **Fiedler — *UDP vs. TCP* (free).** Why UDP wins for real-time gameplay:
  <https://gafferongames.com/post/udp_vs_tcp/>
- **Fiedler — *Sending and Receiving Packets* (free).** Raw `sendto` / `recvfrom` semantics:
  <https://gafferongames.com/post/sending_and_receiving_packets/>
- **Fiedler — *Virtual Connection over UDP* (free).** Tracking "is this peer still talking to me" without TCP. Layered on top of the raw socket:
  <https://gafferongames.com/post/virtual_connection_over_udp/>
- **Fiedler — *Reliability and Flow Control* (free).** The minimal reliability protocol — sequence numbers, ACK bitfields, retransmit on timeout — that lets you carry critical events over UDP. Out of scope this week; we will implement this in Week 10:
  <https://gafferongames.com/post/reliability_and_flow_control/>
- **Fiedler — *Snapshot Interpolation* (free).** The interpolation technique behind Exercise 2:
  <https://gafferongames.com/post/snapshot_interpolation/>
- **Fiedler — *Snapshot Compression* (free).** Cutting snapshot bandwidth via quantisation and delta-encoding. Out of scope this week but a strong stretch read:
  <https://gafferongames.com/post/snapshot_compression/>
- **Fiedler — *State Synchronisation* (free).** The alternative to snapshots: event-based replication of *changes*. Used in many MMO-class games. Read for vocabulary:
  <https://gafferongames.com/post/state_synchronization/>
- **Fiedler — *Networked Physics in Virtual Reality* (free).** A modern application of the same ideas in a VR context. Worth a skim for the closing intuition:
  <https://gafferongames.com/post/networked_physics_in_virtual_reality/>

## Godot 4.x networking documentation (free)

- **Godot — *High-level multiplayer* tutorial.** The starting page. Covers `MultiplayerAPI`, peer setup, `@rpc`:
  <https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html>
- **Godot — *MultiplayerAPI* class reference.** The orchestrator. `rpc_call`, `multiplayer_peer`, `is_server`, `get_unique_id`:
  <https://docs.godotengine.org/en/stable/classes/class_multiplayerapi.html>
- **Godot — *MultiplayerPeer* class reference.** The transport abstraction. Concrete implementations include `ENetMultiplayerPeer` and `WebSocketMultiplayerPeer`:
  <https://docs.godotengine.org/en/stable/classes/class_multiplayerpeer.html>
- **Godot — *ENetMultiplayerPeer* class reference.** The default LAN transport. `create_server(port)`, `create_client(host, port)`. Wraps the ENet C library, which wraps UDP:
  <https://docs.godotengine.org/en/stable/classes/class_enetmultiplayerpeer.html>
- **Godot — *MultiplayerSpawner* class reference.** Replicates node creation across peers. The "join the game" plumbing:
  <https://docs.godotengine.org/en/stable/classes/class_multiplayerspawner.html>
- **Godot — *MultiplayerSynchronizer* class reference.** Replicates node properties at a configurable rate. The everyday state-replication tool:
  <https://docs.godotengine.org/en/stable/classes/class_multiplayersynchronizer.html>
- **Godot — *@rpc annotation* (GDScript reference).** The four-argument decorator that marks a function as network-callable. Critical reading:
  <https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_exports.html>
- **Godot — *WebSocketMultiplayerPeer* class reference.** The HTML5-export transport. Web games use WebSocket; native games use ENet:
  <https://docs.godotengine.org/en/stable/classes/class_websocketmultiplayerpeer.html>

## RFCs and protocol specs (free, IETF)

- **RFC 768 — *User Datagram Protocol*.** The four-page UDP spec. Read in one sitting:
  <https://www.rfc-editor.org/rfc/rfc768>
- **RFC 793 — *Transmission Control Protocol*.** TCP for context. ~80 pages; skim the first 10 to understand why TCP is heavier than UDP:
  <https://www.rfc-editor.org/rfc/rfc793>
- **RFC 791 — *Internet Protocol* (IPv4).** The IP layer below UDP and TCP. Skim:
  <https://www.rfc-editor.org/rfc/rfc791>
- **RFC 8200 — *Internet Protocol Version 6*.** IPv6 reference. Same role as RFC 791 for the modern internet:
  <https://www.rfc-editor.org/rfc/rfc8200>

## Networking fundamentals (free)

- **Wikipedia — *Transport layer*.** Where UDP and TCP live. One-page primer on the layering:
  <https://en.wikipedia.org/wiki/Transport_layer>
- **Wikipedia — *User Datagram Protocol*.** The Wikipedia-level summary of RFC 768. Reads quickly:
  <https://en.wikipedia.org/wiki/User_Datagram_Protocol>
- **Wikipedia — *Transmission Control Protocol*.** The Wikipedia-level summary of RFC 793. Reads in 20 minutes:
  <https://en.wikipedia.org/wiki/Transmission_Control_Protocol>
- **Wikipedia — *Network socket*.** The OS-level abstraction. Berkeley sockets, `socket()`, `bind()`, `sendto()`:
  <https://en.wikipedia.org/wiki/Network_socket>
- **Wikipedia — *Round-trip delay*.** RTT defined, with one paragraph on measurement:
  <https://en.wikipedia.org/wiki/Round-trip_delay>
- **Wikipedia — *Jitter*.** Network jitter defined. The same word means three different things in three different fields; we use the networking one:
  <https://en.wikipedia.org/wiki/Jitter>
- **Wikipedia — *Packet loss*.** Causes and typical mitigation. Useful for the latency-budget conversation:
  <https://en.wikipedia.org/wiki/Packet_loss>
- **Wikipedia — *Head-of-line blocking*.** The one-line reason TCP is wrong for action games:
  <https://en.wikipedia.org/wiki/Head-of-line_blocking>
- **Wikipedia — *Network address translation*.** NAT defined. Why two peers behind home routers cannot trivially see each other. Out of scope this week; on the table for Week 10:
  <https://en.wikipedia.org/wiki/Network_address_translation>

## Game-specific networking writing (free)

- **Valve Developer Wiki — *Source Multiplayer Networking* (free).** Valve's own description of the model used in Counter-Strike, Team Fortress 2, and every Source-engine title. The single best industry reference for client-side prediction and lag compensation:
  <https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking>
- **Valve Developer Wiki — *Latency Compensating Methods in Client/Server In-Game Protocol Design* (free, Yahn Bernier).** The 2001 Valve paper that established the language. Still the best technical write-up:
  <https://developer.valvesoftware.com/wiki/Latency_Compensating_Methods_in_Client/Server_In-game_Protocol_Design_and_Optimization>
- **Gabriel Gambetta — *Fast-Paced Multiplayer* series (free).** A four-part visual walkthrough of authoritative server, prediction, interpolation, and reconciliation. Excellent companion to Fiedler — Gambetta is visual where Fiedler is prose:
  <https://www.gabrielgambetta.com/client-server-game-architecture.html>
- **Riot Games — *Peeking into Valorant's Netcode* (free engineering blog).** A production engineering team's description of a competitive shooter's netcode. Worth reading for the realities of a 128-tick server:
  <https://technology.riotgames.com/news/peeking-valorants-netcode>
- **Overwatch — *Networking Scripted Weapons & Abilities in Overwatch* (free, GDC talk video on YouTube).** Tim Ford's GDC talk. The "Hammond's pile-driver" segment is a textbook example of how interpolation and prediction interact:
  <https://www.youtube.com/results?search_query=overwatch+networking+gdc>
- **Rocket League — *It IS Rocket Science* (free, GDC talk video on YouTube).** Jared Cone's GDC talk on Rocket League's physics-replication model. Out of scope for this week; entertaining:
  <https://www.youtube.com/results?search_query=rocket+league+netcode+gdc>

## Python networking (stdlib, free)

The exercises use only the standard library. No third-party install needed for the network layer.

- **Python docs — *socket — Low-level networking interface* (free).** The whole exercise stack lives on this page. Read once top-to-bottom:
  <https://docs.python.org/3/library/socket.html>
- **Python docs — *Socket Programming HOWTO* (free).** Gentle intro. Read before Exercise 1:
  <https://docs.python.org/3/howto/sockets.html>
- **Python docs — *selectors — High-level I/O multiplexing* (free).** The non-blocking poll layer above raw sockets. We use `socket.setblocking(False)` and a manual loop in the exercises; `selectors` is the next step up:
  <https://docs.python.org/3/library/selectors.html>
- **Python docs — *struct — Interpret bytes as packed binary data* (free).** Used to serialise snapshot payloads into a tight byte format. The mini-project's snapshot is `!IHff` (one 32-bit player id, one 16-bit sequence number, two 32-bit floats x/y):
  <https://docs.python.org/3/library/struct.html>
- **Python docs — *time — Time access and conversions* (free).** `time.perf_counter` for measuring RTT with sub-millisecond resolution. `time.monotonic` for the server clock:
  <https://docs.python.org/3/library/time.html>

## Packet inspection (free tools)

- **Wireshark (free, cross-platform).** The standard open-source packet sniffer. Capture on the loopback interface to see your own UDP traffic at the byte level:
  <https://www.wireshark.org/>
- **tcpdump (free, built-in on macOS and Linux).** Command-line packet capture. A one-liner is enough to verify the cursor demo is actually sending packets:
  <https://www.tcpdump.org/>
- **netstat / lsof (free, built-in on every Unix).** "What is listening on port 5005?" — the answer to half the bugs in Exercise 1:
  <https://man7.org/linux/man-pages/man8/netstat.8.html>
- **iperf3 (free, cross-platform).** Bandwidth and jitter measurement between two hosts on a LAN. Useful for the "measure your link" challenge:
  <https://iperf.fr/>

## Free Python packages we use this week

The exercises and Pygame mini-project need only `pygame`. Install in your virtual environment:

```bash
pip install pygame
```

- **pygame (>= 2.5).** The game engine. Free, open-source, LGPL:
  <https://www.pygame.org/>

Stdlib only (no install needed):

- `socket`, `struct`, `time`, `selectors`, `dataclasses`, `enum`, `argparse`, `json`, `threading`, `queue`, `collections`.

## Godot (free)

- **Godot Engine — official site.** Free, open-source, MIT-licensed. Download the 4.x stable build:
  <https://godotengine.org/>
- **Godot — 4.x documentation root.** The whole 4.x docs site. Bookmark:
  <https://docs.godotengine.org/en/stable/>
- **Godot demos repository — *networking* folder (free, MIT).** The official multiplayer demos. The "Pong Multiplayer" demo is the closest analogue to our cursor demo and worth a 10-minute browse:
  <https://github.com/godotengine/godot-demo-projects/tree/master/networking>

## NAT and the open internet (free; on the table for Week 10)

These are not required reading this week. They are listed because students invariably ask "but how do I play with my friend across the country" — the answer is below, and the answer is "more work than fits in this week":

- **Wikipedia — *NAT traversal*.** The umbrella topic. STUN, TURN, ICE:
  <https://en.wikipedia.org/wiki/NAT_traversal>
- **RFC 8489 — *STUN*.** The Session Traversal Utilities for NAT. The discovery protocol:
  <https://www.rfc-editor.org/rfc/rfc8489>
- **RFC 8656 — *TURN*.** Traversal Using Relays around NAT. The fallback when STUN cannot punch through:
  <https://www.rfc-editor.org/rfc/rfc8656>
- **Steam Datagram Relay — *Valve's hosted relay overview* (free).** The production answer most indies pick. Hosts the relay; abstracts NAT entirely:
  <https://partner.steamgames.com/doc/features/multiplayer/steamdatagramrelay>
- **Nakama — open-source game-server framework (free, Apache 2.0).** A self-hostable session server with matchmaking and relays. A reasonable production target post-course:
  <https://heroiclabs.com/nakama/>

## Reference projects (free reading)

- **Quake III Arena source code (GPL, free).** The grandfather of client-server FPS netcode. The `client` and `server` directories are extensively commented:
  <https://github.com/id-Software/Quake-III-Arena>
- **OpenArena (Quake III fork, free, GPL).** Same architecture, easier-to-read modernised code:
  <https://github.com/OpenArena/engine>
- **Mirror (Unity networking, free, MIT).** Open-source Unity multiplayer library. Worth a 20-minute skim of the README even if you do not use Unity, because the API names mirror what professional networking code looks like:
  <https://github.com/MirrorNetworking/Mirror>
- **ENet (free, MIT).** The C library Godot wraps. The README is short and the protocol overview is excellent for understanding what `ENetMultiplayerPeer` is doing under the hood:
  <http://enet.bespin.org/>

## What you will *not* need this week

- A dedicated server. Localhost or a peer on your LAN is enough.
- A cloud account (AWS, GCP, DigitalOcean). LAN-only this week.
- Steam, Epic Online Services, or any platform SDK. Out of scope.
- A VPN or NAT-punch-through service. We stay LAN-only deliberately.
- TCP. We use UDP exclusively for gameplay traffic. The optional reliable channel in the mini-project is a hand-rolled ACK over UDP, not TCP.

---

*Bookmark this page. The Fiedler series alone is worth re-reading once a year for the rest of your career.*
