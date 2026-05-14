# Week 9 — Quiz

Ten multiple-choice questions. Take it with your lecture notes closed. Aim for 9/10 before moving to Week 10. Answer key at the bottom — do not peek.

---

**Q1.** Lecture 1 §1 names three networking models for games. Which one runs the canonical simulation on a single dedicated machine, treats clients as render terminals, and is the default for nearly every modern action game?

- A) Peer-to-peer trust-the-peer.
- B) Client-server authoritative.
- C) Lockstep deterministic.
- D) Hybrid mesh.

---

**Q2.** Lecture 1 §3 names the *single load-bearing reason* TCP is the wrong transport for real-time game state. That reason is:

- A) TCP packets are larger than UDP packets, so they cost more bandwidth.
- B) TCP's head-of-line blocking turns one dropped packet into a stall of every newer packet behind it, and the newer state is more valuable than the lost one.
- C) TCP is unreliable.
- D) UDP supports broadcast and TCP does not.

---

**Q3.** Lecture 1 §2 gives the latency budget for action games. The threshold above which "the game feels wrong" for most genres is approximately:

- A) 30 ms RTT.
- B) 80 ms RTT.
- C) 300 ms RTT.
- D) 1000 ms RTT.

---

**Q4.** Lecture 1 §4 reads RFC 768. The UDP header has *exactly* how many bytes?

- A) 4 bytes.
- B) 8 bytes.
- C) 20 bytes.
- D) 64 bytes.

---

**Q5.** Lecture 2 §1.2 describes the trick of "rendering in the past." The client renders at `t_render = t_now - INTERP_DELAY`. The reason is:

- A) Rendering in the past saves CPU cycles.
- B) So the client always has two received snapshots whose server-timestamps bracket `t_render`, allowing linear interpolation between them.
- C) Rendering in the past prevents lag.
- D) Snapshot interpolation requires that the future be simulated, which is impossible.

---

**Q6.** Lecture 2 §2 describes the jitter buffer. Its size should hold *at least*:

- A) One snapshot. Anything more wastes memory.
- B) Several snapshot periods plus margin for arrival-time variance, typically 4-5 entries at 20 Hz.
- C) The entire history of the game so far.
- D) Exactly two entries — the latest and the previous.

---

**Q7.** Lecture 2 §3 distinguishes *state* replication from *event* replication. Which statement is accurate?

- A) State and event replication are the same thing.
- B) State (positions, velocities) tolerates packet loss because the next snapshot supersedes the lost one; events (scores, joins) must be delivered reliably because each is unique.
- C) State must be delivered reliably; events can be dropped freely.
- D) Both should always be sent over TCP.

---

**Q8.** Lecture 2 §4-5 describes client-side prediction and server reconciliation. The role of *reconciliation* is to:

- A) Reset the player's score when the server disagrees.
- B) Rewind the client's local prediction to the authoritative snapshot's state and re-apply every input that happened after the snapshot's timestamp, so that the visible correction reflects only the *new* information the server contributed.
- C) Average the client's prediction with the server's authoritative position.
- D) Disable client-side prediction whenever the server is responding.

---

**Q9.** Lecture 3 §3 explains the `@rpc` annotation. The annotation `@rpc("any_peer", "call_local", "unreliable")` declares a function that:

- A) Can be called only by the server, runs only on remote peers, and is sent reliably.
- B) Can be called by any connected peer, also runs locally on the sender, and is sent without ACKs or retransmission.
- C) Cannot be called across the network; it is a documentation-only marker.
- D) Is automatically rate-limited to 1 Hz.

---

**Q10.** Lecture 3 §4-5 contrasts `MultiplayerSpawner` and `MultiplayerSynchronizer`. The split is:

- A) Spawner replicates *node creation*; Synchronizer replicates *node properties*.
- B) Spawner is for 2D games; Synchronizer is for 3D games.
- C) They are aliases for the same node.
- D) Spawner is server-only; Synchronizer is client-only.

---

## Answer key

Do not read this until you have answered all ten questions on your own.

1. **B.** Client-server authoritative. (Lecture 1 §1.1)
2. **B.** Head-of-line blocking. (Lecture 1 §3.2)
3. **C.** ~300 ms RTT. (Lecture 1 §2 table — 150-200 is "tolerable for non-twitch," 200-300 is "tolerable for turn-based," above 300 is "wrong.")
4. **B.** 8 bytes. (Lecture 1 §4 — four 16-bit fields.)
5. **B.** To always have two received snapshots bracketing the render time. (Lecture 2 §1.2)
6. **B.** Several snapshot periods plus margin. (Lecture 2 §2.1)
7. **B.** State tolerates loss; events do not. (Lecture 2 §3)
8. **B.** Rewind and re-apply inputs. (Lecture 2 §5)
9. **B.** Any peer can call; runs locally on sender too; sent unreliably. (Lecture 3 §3)
10. **A.** Spawner replicates node creation; Synchronizer replicates node properties. (Lecture 3 §4-5)

---

**Scoring guide:**
- 10/10 — excellent. Move on with confidence.
- 8-9/10 — good. Review the misses against the cited lecture sections.
- 6-7/10 — re-read Lectures 1-2 and retake the quiz.
- ≤5/10 — re-read Lectures 1-2-3 in full and ask in the course channel for clarification on the topics you missed.
