# Challenge 1 — Measure Your Link

> **Format:** Hands-on measurement exercise. ~2 hours including tool installs.
> **Deliverable:** A `link-report.md` containing your numbers, three captured screenshots, and a 200-word interpretation.
> **Estimated time:** 2 hours.

This challenge is the empirical counterpart to Lecture 1 §2 (the latency budget). You will measure your *actual* link characteristics — RTT, jitter, packet loss, route length — between two machines (or two terminals, if you only have one machine to work with), and write up what you find. By the end you have a concrete picture of what the network is *really* doing under your week's mini-project.

## The setup

You will need:

- The Week 9 Exercise 1 file (`exercise-01-udp-echo.py`), already in your repo from earlier in the week.
- The OS-built-in `ping` command. (Works on macOS, Linux, and Windows out of the box.)
- The OS-built-in `traceroute` (`tracert` on Windows) command.
- **Wireshark** (free, open-source, cross-platform). Download from <https://www.wireshark.org/>. The install takes ~5 minutes; on first run grant it permission to capture on your interfaces.
- Optionally **iperf3** (free, cross-platform) for a separate bandwidth-and-jitter sanity check: <https://iperf.fr/>. On macOS: `brew install iperf3`. On Linux: your package manager.

If you have *two* machines on the same LAN, run server on one and client on the other. If not, run both in two terminals on one machine and use `127.0.0.1` — the loopback numbers are not representative of "the network" but the procedure is the same.

## Step-by-step

### Step 1 — Baseline `ping`

In Terminal A, run:

```bash
ping -c 100 <target-ip>
```

`<target-ip>` is `127.0.0.1` (loopback), your LAN peer's IP (LAN), or a public host like `1.1.1.1` (open internet). Run it three times for three different targets and save the summary output (the `--- ping statistics ---` block) in your `link-report.md` under headings:

```markdown
## Ping baseline

### Loopback (127.0.0.1)
<paste>

### LAN peer (192.168.1.X)
<paste>

### Open internet (1.1.1.1)
<paste>
```

You should see something like:

```
100 packets transmitted, 100 received, 0.0% packet loss, time 99106ms
rtt min/avg/max/mdev = 0.039/0.077/0.158/0.020 ms
```

The four numbers — min / avg / max / mdev (mean deviation, a jitter proxy) — are what you write down.

### Step 2 — Run Exercise 1's UDP echo

In Terminal A: `python exercise-01-udp-echo.py --server`.
In Terminal B: `python exercise-01-udp-echo.py --client <target-ip>`.

Let it run for 60 seconds. Take a screenshot of the client's terminal output (the "rtt avg= ... min= ... max= ... loss= ..." line). Save the screenshot as `link-report-udp-echo.png` in your repo.

In `link-report.md`:

```markdown
## UDP echo (Exercise 1)

| Target           | Avg RTT | Min | Max | Loss % |
|------------------|--------:|----:|----:|-------:|
| Loopback         |         |     |     |        |
| LAN peer         |         |     |     |        |
| Open internet*   |         |     |     |        |

*Exercise 1 in client mode against a public IP requires that you also run
the server on a machine with a public IP. Skip this row if you do not
have one; the loopback and LAN rows are enough for this challenge.
```

### Step 3 — `traceroute`

In Terminal A:

```bash
traceroute -q 1 <target-ip>      # macOS / Linux
tracert <target-ip>              # Windows
```

`traceroute` shows the chain of routers between you and the target. For loopback it is one hop. For a LAN peer it is one or two hops (your router). For a public host it can be 10-20 hops.

Save the full output in `link-report.md`. For each non-loopback target, count the hops and record:

- Total hops.
- The hop with the *highest* latency contribution (compare consecutive RTTs in the output).
- The first hop *outside* your LAN (typically the first non-`192.168.x.x` or non-`10.x.x.x` address — your ISP's edge router).

### Step 4 — Wireshark capture

1. Open Wireshark. Pick your active network interface (loopback for the localhost test, Wi-Fi or Ethernet for the LAN test).
2. In the filter box at the top, enter `udp.port == 5005`.
3. Start the capture (the shark-fin button).
4. Run Exercise 1 server in Terminal A and client in Terminal B for ~10 seconds.
5. Stop the capture.

You should see two sets of packets: PING (client → server) and PONG (server → client). For each direction, click any packet and expand the `User Datagram Protocol` section. Verify the four fields:

- Source Port.
- Destination Port (5005 in one direction; the OS-chosen ephemeral port in the other).
- Length (8-byte UDP header + your payload, so e.g. 24 bytes for our 16-byte payload + 8-byte header).
- Checksum.

Take a screenshot of the Wireshark window with one PING packet expanded to show the UDP header. Save as `link-report-wireshark.png`.

In `link-report.md`:

```markdown
## Wireshark capture

Captured 10 seconds of Exercise 1 traffic on the <interface> interface.
Total UDP packets in capture: <count>.
PING packets sent by client: <count>.
PONG packets sent by server: <count>.
Any packets out of order? <yes/no, brief>.
Any duplicates? <yes/no, brief>.
UDP header for one PING packet (sample):
- Source Port: <port>
- Destination Port: 5005
- Length: <bytes>
- Checksum: <hex>
```

### Step 5 — Optional `iperf3`

If you have iperf3 installed, run on the server: `iperf3 -s -p 5006`. On the client: `iperf3 -u -c <server-ip> -p 5006 -t 10 -b 1M`. The `-u` flag is UDP; `-b 1M` is the target rate. The output reports jitter in milliseconds and packet loss as a percentage — a second opinion against the Exercise 1 numbers.

Add a row to `link-report.md` if you run this:

```markdown
## iperf3 jitter and loss

iperf3 UDP test, 1 Mbps target, 10 seconds.
Jitter: <ms>
Packet loss: <%>
Throughput achieved: <Mbps>
```

### Step 6 — Interpretation

Write a 200-word interpretation under the heading `## What I learned`. Answer:

- Which of the three latency sources from Lecture 1 §2.1 — propagation, routing, last-mile — is dominant on each link?
- Does your LAN's average RTT (Exercise 1) match the `ping` average within ~1 ms? If not, what could explain the difference?
- Would you be comfortable shipping a multiplayer game on the link you measured? Use the latency-budget table in Lecture 1 §2 to justify your answer.
- If you saw any packet loss above 0%, what was the link characteristic that caused it?

Save and commit.

## Acceptance criteria

- [ ] A file `link-report.md` exists in your Week 9 repo (or `homework/challenge-01/`).
- [ ] `link-report.md` contains the four sections above: ping baseline, UDP echo, traceroute, Wireshark.
- [ ] At least one `link-report-*.png` screenshot is committed.
- [ ] The `## What I learned` interpretation is ~200 words and references Lecture 1 §2 by name.
- [ ] If you ran iperf3, the optional section is filled in.
- [ ] The report distinguishes loopback, LAN, and (where possible) open-internet measurements.

## Hints

- Loopback `ping` should show RTTs under 0.5 ms. If yours are higher, your OS is throttling localhost — uncommon but happens on busy systems.
- LAN `ping` on Wi-Fi typically shows 1-10 ms RTT with jitter; on Ethernet, sub-1 ms with very low jitter. The difference is mostly the Wi-Fi MAC layer's retransmissions.
- A `traceroute` line that reads `* * *` is a hop that refused to ICMP-respond — your packet still got through, the router just declined to reveal itself. Don't read this as a failure.
- Wireshark on loopback requires extra permissions on macOS (the first capture will prompt for `chmod`). On Linux you may need `sudo wireshark` or to add yourself to the `wireshark` group.
- iperf3 in UDP mode reports zero loss until you exceed the link's actual capacity. Try `-b 100M` (100 Mbps) to find your real ceiling.

## What this challenge prepares you for

Three things every multiplayer programmer needs to do regularly:

1. **Diagnose connection problems empirically**, not by guessing. When a player complains that "the game is laggy," you need to ask them to run something like this challenge's measurement step and report the numbers.
2. **Read packet captures**. Wireshark is the eye doctor of the network. Whenever a protocol problem persists in code, the answer is usually visible in the bytes on the wire.
3. **Tell the difference between application latency and network latency**. Exercise 1 measures *application-to-application* RTT. `ping` measures *ICMP* RTT. The two should be close; if they are not, your application is the bottleneck.

Bring the `link-report.md` to the Friday review session.
