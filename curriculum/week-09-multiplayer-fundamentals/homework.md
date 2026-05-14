# Week 9 Homework

Six practice problems that revisit the week's topics. The full set should take about **5-6 hours** in total. Work in your Week 9 Git repository so each problem produces at least one commit you can point to later.

The work this week splits between *transport* (problems 1-3) and *the synchronisation layer* (problems 4-6). The mini-project assembles the whole stack; these homework problems are the parts.

Each problem includes:

- A short **problem statement**.
- **Acceptance criteria** so you know when you are done.
- A **hint** if you get stuck.
- An **estimated time**.

---

## Problem 1 — Add a 32-bit sequence number to Exercise 1

**Problem statement.** Take `exercise-01-udp-echo.py` and change the header from `!BH` (1-byte type + 16-bit sequence) to `!BI` (1-byte type + 32-bit sequence). Run it for an hour. Compare the RTT meter's behaviour to the 16-bit version. Save the modified file as `homework/p1_udp_echo_32bit_seq.py`. Document in a 50-word comment block at the top of the file what changed and why a 32-bit sequence is a meaningful improvement for long-running clients.

**Acceptance criteria.**

- A file `homework/p1_udp_echo_32bit_seq.py` exists.
- The header struct format is `!BI`.
- The file's docstring includes a note explaining the change and citing Lecture 1 §4 (where the 16-bit sequence in the original is justified).
- `python -m py_compile homework/p1_udp_echo_32bit_seq.py` succeeds.
- All function signatures have type hints.

**Hint.** The sequence wraps from 65535 -> 0 in the 16-bit version after ~110 minutes at 10 Hz. With 32 bits the wrap is at ~13.6 years at 10 Hz, which for game purposes is "never." The trade is a 2-byte cost per packet; for our payload size it is ~7% overhead, irrelevant.

**Estimated time.** 30 minutes.

---

## Problem 2 — Measure your loopback floor

**Problem statement.** Write `homework/p2_loopback_rtt_floor.py` that runs both the echo server and a single-shot ping client *in the same process* using two threads, and measures the absolute floor of localhost UDP RTT. Run it 1000 times and report the median, P95, and P99 RTT. The result is a number you can use as your "this is not the network" baseline for every other measurement this semester.

**Acceptance criteria.**

- A file `homework/p2_loopback_rtt_floor.py` exists.
- The script runs to completion in under 60 seconds.
- It prints the median, P95, and P99 RTT in microseconds.
- The PRNG, if any, is seeded for reproducibility.
- `python -m py_compile homework/p2_loopback_rtt_floor.py` succeeds.
- All function signatures have type hints.

**Hint.** Two threads, two sockets. One thread runs a tiny echo loop bound to `127.0.0.1:5006`. The main thread sends 1000 PINGs serially, records each RTT, sleeps 1 ms between sends. Use `time.perf_counter_ns()` for ns-resolution timing. Sort the RTT list and pick the median / P95 / P99 entries.

**Estimated time.** 50 minutes.

---

## Problem 3 — Add a packet-loss simulator

**Problem statement.** Write `homework/p3_loss_simulator.py` that wraps a UDP socket with a configurable artificial-loss layer. The wrapper class `LossySocket` accepts a `loss_prob: float` (0.0 to 1.0); every `sendto` flips a biased coin and either sends or silently drops. Run Exercise 2's snapshot loop through a `LossySocket` with `loss_prob=0.05` (5% loss). Verify that the client's interpolation still produces smooth motion (because snapshot replication is loss-tolerant). Save the output of the 60-second run as `homework/p3_run.log`.

**Acceptance criteria.**

- A file `homework/p3_loss_simulator.py` defines `LossySocket` with type-hinted methods `sendto`, `recvfrom`, `setblocking`, `bind`, `setsockopt`, `close`.
- The wrapper passes through every method to the underlying socket *except* `sendto`, which probabilistically drops.
- A `homework/p3_run.log` contains the captured client output showing smooth motion despite 5% loss.
- `python -m py_compile homework/p3_loss_simulator.py` succeeds.
- All function signatures have type hints.

**Hint.** The wrapper is ~30 lines. `random.random() < loss_prob` is the drop condition. To use it without rewriting Exercise 2, import the exercise module, monkey-patch `socket.socket` to return your wrapper for `SOCK_DGRAM` calls. Or just copy the exercise's `run_server` body into `p3_loss_simulator.py` and replace the socket construction line.

**Estimated time.** 60 minutes.

---

## Problem 4 — Hand-roll the interpolation lookup

**Problem statement.** Write `homework/p4_interp_unit_tests.py` that contains 8 unit tests (one per scenario below) for an `interpolate(snapshots, t_render)` function you implement yourself, *without* looking at Exercise 2. The signature: takes a list of `(server_time, x, y)` tuples and a target time; returns `(x, y)` or `None`. The eight scenarios:

1. Empty list → `None`.
2. Single entry, exact match → that entry's (x, y).
3. Single entry, t_render ≠ entry → `None` (cannot interpolate from one point).
4. Two entries, t_render between them at α=0.5 → midpoint.
5. Two entries, t_render exactly equal to older → older's (x, y).
6. Two entries, t_render exactly equal to newer → newer's (x, y).
7. Three entries, t_render between middle and last → interpolate middle-to-last.
8. Three entries, t_render older than oldest → `None`.

**Acceptance criteria.**

- A file `homework/p4_interp_unit_tests.py` exists.
- All 8 tests are written as `assert` statements with descriptive messages.
- The file prints "PASS" if all 8 pass and the first failure's message otherwise.
- `python homework/p4_interp_unit_tests.py` exits 0 with output `PASS`.
- The `interpolate` function and the test cases are all type-hinted.

**Hint.** You can implement `interpolate` in ~10 lines using `bisect.bisect_right` on a sorted list of timestamps. Or you can do a linear scan — fine for short lists. Linear interpolation is `a + (b - a) * alpha` per axis.

**Estimated time.** 60 minutes.

---

## Problem 5 — A jitter-buffer stress test

**Problem statement.** Write `homework/p5_jitter_stress.py` that exercises the `JitterBuffer` from Exercise 2 (copy the class into your file) with a synthetic input stream representing pathological jitter. Generate 100 snapshots with server-times `[0.00, 0.05, 0.10, ..., 4.95]` (50 ms cadence), then *shuffle* them randomly before inserting, simulating maximally-bad out-of-order arrival. After all inserts, the buffer should contain the *latest* `JITTER_BUFFER_MAXLEN` entries in sorted order. Print the buffer's contents and verify the sort.

**Acceptance criteria.**

- A file `homework/p5_jitter_stress.py` exists.
- It generates the 100-snapshot stream, shuffles, inserts.
- It asserts the final buffer is sorted by `server_time`.
- It asserts the final buffer contains the `JITTER_BUFFER_MAXLEN` *most recent* snapshots (server-times 4.20s through 4.95s for a 16-entry buffer).
- The PRNG is seeded for reproducibility.
- `python -m py_compile homework/p5_jitter_stress.py` succeeds.
- All function signatures have type hints.

**Hint.** Use `random.seed(42); random.shuffle(snapshots)` for a reproducible shuffle. After inserts, iterate the deque and confirm `for i in range(len-1): assert deque[i].server_time < deque[i+1].server_time`. The "latest 16" check uses `assert min(s.server_time for s in deque) >= expected_threshold`.

**Estimated time.** 45 minutes.

---

## Problem 6 — A bandwidth budget worksheet

**Problem statement.** Write `homework/p6_bandwidth_budget.md` analysing the bandwidth profile of a hypothetical 2D arena game called *Crunch Arena*. The game has:

- 8 players per match.
- 60 Hz client frame rate.
- 20 Hz server snapshot tick.
- Per-player state: id (4 B), x (4 B), y (4 B), vx (4 B), vy (4 B), facing (2 B), hp (2 B), state_flags (2 B). Total: 26 bytes per player.
- Per-frame inputs from each client: id (4 B), seq (2 B), keys (2 B), mouse_x (4 B), mouse_y (4 B). Total: 16 bytes per input.

Compute and write up:

1. **Server -> client snapshot bandwidth per peer.** (8 players x 26 B + 8 B UDP header + 20 B IP header = ?? bytes per snapshot. At 20 Hz: ?? bytes/sec downstream to each client.)
2. **Client -> server input bandwidth.** (16 B payload + 8 B UDP + 20 B IP per packet. At 60 Hz: ?? bytes/sec upstream from each client.)
3. **Total per-client.** Sum of (1) and (2). Convert to kbps.
4. **Server aggregate downstream.** 8 clients x (1). Convert to kbps.
5. **Comparison to typical home uplink.** A 5 Mbps uplink can support how many of these matches concurrently?
6. **What changes at 64 Hz server tick?** Recompute (1) and (4) at 64 Hz instead of 20.
7. **What changes at 32 players?** Recompute (1) at 32 players, 20 Hz.

**Acceptance criteria.**

- A file `homework/p6_bandwidth_budget.md` exists.
- All seven items are answered with a number and a one-sentence interpretation.
- The math is shown (not just the result).
- The conclusion states which design choice (player count or tick rate) most dominates the bandwidth profile.
- The write-up cites Lecture 2 §8 (where the bandwidth math is sketched).

**Hint.** UDP header is 8 B (Lecture 1 §4); IPv4 header is 20 B. The total per-datagram overhead is 28 B regardless of payload. For an 8-player snapshot at 26 B/player: 8 * 26 + 28 = 236 B per packet. At 20 Hz: 4720 B/s = ~37.8 kbps per client downstream. Most home links are 100x this.

**Estimated time.** 60 minutes.

---

## Submission

Push every file to your Week 9 repo. Tag the commit `week-09-homework-complete`. Bring questions to the Friday review session.

If you finish all six in under five hours, take the extra time on either Challenge 2 (rollback netcode design) or the mini-project polish.
