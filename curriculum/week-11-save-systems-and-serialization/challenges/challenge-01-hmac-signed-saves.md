# Challenge 01 — HMAC-Signed Saves

**Difficulty:** Stretch. Adds about 80 lines of Python on top of Exercise 05.
**Estimated time:** Two hours including the writeup.

---

## What you are building

Take the atomic-write + SHA-256 envelope from Exercise 05 and upgrade the integrity tag from a plain SHA-256 to an **HMAC-SHA-256** signed with a per-install secret key.

The unsigned SHA-256 catches accidental corruption. An attacker who knows the format can edit the payload, recompute the SHA-256, write it back, and the loader will accept the modified save. The HMAC closes that gap *for any attacker who does not know the secret key*. A casual editor in Notepad cannot regenerate a valid HMAC; a copy-a-friend's-save attack fails (the friend's HMAC was signed with the friend's key, not yours).

The HMAC is not cryptographic *protection*. The key lives on the machine; a sufficiently determined cheater finds it and can sign whatever they want. The HMAC raises the cost of cheating from "minutes" to "a few hours of reverse engineering." For most single-player games, that is enough.

---

## The deliverable

A file `challenge-01-hmac-signed-saves.py` in your homework directory that:

1. Defines a `KEY_FILE_NAME = ".save_key"` constant. The file lives in the same directory as the save files, holds 32 bytes of cryptographically random data, and is created on first launch via `secrets.token_bytes(32)`.

2. Provides `read_or_create_key(directory: Path) -> bytes` that returns the 32-byte key, creating the file with `secrets.token_bytes(32)` if it does not yet exist. The function is idempotent: subsequent calls return the same key.

3. Replaces the `integrity_tag(payload)` function from Exercise 05 with `hmac_tag(payload, key)` that returns `"hmac-sha256:" + hmac.new(key, canonical_bytes(payload), hashlib.sha256).hexdigest()`.

4. Replaces `open_envelope(parsed)` with `open_envelope_signed(parsed, key)` that verifies the HMAC instead of a plain SHA-256.

5. Includes a `_demo()` function that:
   - Writes a save with the HMAC envelope.
   - Loads it successfully.
   - Tampers with the payload (changes `current_score` from 100 to 999_999) *without recomputing the HMAC*.
   - Demonstrates that the loader rejects the tampered save.
   - Tampers with the payload *and* recomputes the SHA-256 (the way an attacker would for a plain-SHA-256 envelope).
   - Demonstrates that even the SHA-256-aware tamper is rejected because the HMAC does not match.

The script must run with no third-party dependencies; everything is in the Python standard library (`hashlib`, `hmac`, `secrets`).

---

## Constraints

- **`hmac.compare_digest`, not `==`.** When comparing the computed HMAC to the stored HMAC, use the timing-safe `hmac.compare_digest`. A naive `==` comparison is technically vulnerable to a timing attack; in practice for local saves the attack is unrealistic, but the *habit* of using `compare_digest` carries over to networking code where timing attacks are real.

- **The key file is not committed to git.** Treat it like a password. Add a line to your project's `.gitignore`: `*.save_key`.

- **The key is per-install, not per-user-account.** A player who reinstalls the game generates a new key and their old saves become unloadable. This is the intended trade-off; the alternative (a key tied to a cloud account) is the topic of Challenge 02 of a future week.

- **The HMAC tag's prefix is `"hmac-sha256:"`, not `"sha256:"`.** The prefix tells the loader which algorithm was used. A loader that sees an `"sha256:"` prefix on a v2-format save (which should always be HMAC) treats it as a downgrade attack and rejects.

---

## Why this matters

The shipped save systems of most competitive PC games (Hearthstone collection caches, *Genshin Impact* progression files, *Diablo III*'s offline-mode caches) use some flavour of HMAC or AES-encrypted-with-MAC. The single most-cited reason in postmortems and engineering blogs is *not* "prevent cheating in single-player" — most studios accept that single-player cheating is a player choice — but **prevent casual save-file editing from leaking into competitive multiplayer where the same characters are used**.

For an indie game that ships with online leaderboards or shared progression, HMAC-signing the local save is a sensible default. It is not a complete defence (a server-authoritative leaderboard is the only complete defence), but it is the cheapest meaningful step.

For an indie game with no multiplayer, the HMAC is optional. Plain SHA-256 from Exercise 05 is enough.

---

## What to write up

Submit two files:

1. **`challenge-01-hmac-signed-saves.py`** — the runnable script. Must produce an `OK` line on success.

2. **`challenge-01-writeup.md`** — a ~500-word essay covering:
   - What threat HMAC-signing closes that plain SHA-256 does not.
   - What threat HMAC-signing does *not* close. (At least three: the on-machine key can be extracted; an attacker who can read your process memory while you are saving can extract the key; a sophisticated attacker can binary-patch the game to skip the HMAC check entirely.)
   - The cost of HMAC vs plain SHA-256, in milliseconds per save on your machine. (Roughly identical for small saves; the cost is in `hmac.new` initialisation, which is negligible.)
   - Whether you would ship this in your hypothetical-future indie game and why.

The essay matters. The substance is in the threat-model analysis, not in the code.

---

## Marking criteria

| Criterion                                            | Points |
|------------------------------------------------------|-------:|
| `read_or_create_key` is idempotent and uses `secrets`|   2    |
| `hmac_tag` produces `"hmac-sha256:..."`              |   2    |
| `open_envelope_signed` verifies with `compare_digest`|   2    |
| Demo: clean round-trip                               |   1    |
| Demo: plain-tamper rejected                          |   2    |
| Demo: SHA-aware-tamper rejected                      |   3    |
| Writeup covers the three threats not closed          |   3    |
| Writeup covers the cost analysis                     |   1    |
| Writeup ships-or-not decision with rationale         |   1    |
| **Total**                                            | **17** |

---

## Hints

- **`hmac.new(key, msg, digestmod)`** returns an HMAC object; `.hexdigest()` returns the hex string.
- **`hmac.compare_digest(a, b)`** returns `True` iff the two strings (or bytes) are equal, in *constant time* relative to the input length. Slower than `==` by a small constant factor; safer to use everywhere.
- **`secrets.token_bytes(32)`** returns 32 bytes from the OS's cryptographic RNG.
- **The key file's path** is `directory / KEY_FILE_NAME`, same directory as the saves; the file is binary (mode `"wb"` on write, `"rb"` on read).
- **The integrity check on load is the only path that calls `compare_digest`.** Do not use `compare_digest` for the envelope's structural checks (`if "payload" not in parsed: ...`); use it only for the HMAC comparison itself.

---

## Stretch on the stretch

If the HMAC-signing was easy and you want to keep going, two follow-ups in increasing difficulty:

**S1 — Key rotation.** Add a `key_version: int` field to the save. The game knows two keys: a current one and the previous one. A save signed with the previous key still validates (the loader tries both keys, accepts the first that matches), but is re-saved under the current key on the next write. Rotation lets you change the key when you suspect a key compromise.

**S2 — Authenticated encryption.** Instead of HMAC-over-plaintext, use `AES-GCM` (via `cryptography.hazmat.primitives.ciphers.aead.AESGCM`) to encrypt-and-MAC in a single primitive. The save bytes on disk are no longer human-readable; the player cannot even see what fields exist. The cost is the dependency on the `cryptography` library and the loss of all hand-edit-for-modding workflows.

Both are stretches because they introduce trade-offs the unsigned-or-HMAC versions do not. Each is the topic of a half-day's reading on its own. Skip both if you are working to a deadline; the core HMAC challenge is the load-bearing skill.
