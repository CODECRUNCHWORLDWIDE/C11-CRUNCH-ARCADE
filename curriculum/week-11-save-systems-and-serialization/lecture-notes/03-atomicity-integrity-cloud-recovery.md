# Lecture 3 — Atomicity, Integrity, Cloud Saves, Recovery

> **Duration:** ~2 hours of reading plus hands-on.
> **Outcome:** You can implement the temp-file-plus-rename pattern, verify a save with a SHA-256 integrity check, rotate `save.latest` → `save.previous` for crash recovery, and describe at the conceptual level what Steam Cloud, Google Play Saves, and iCloud Key-Value Storage each guarantee and each silently break.

If you only remember one thing from this lecture, remember this:

> **The production save path is read-only at write time. Write to a sibling temp file. `fsync` the temp file. Rename it onto the production path. The rename is the only step that publishes the new save. A crash before the rename leaves the previous good save intact.**

The lecture begins with the temp-file-plus-rename pattern (the single most impactful change to a save subsystem), continues with integrity checks (SHA-256 plus a backup-rotation scheme that recovers from corruption), and ends with the cloud-save survey — Steam Cloud, Google Play Saves, iCloud — at the conceptual level only.

We lean on the Steamworks Steam Cloud documentation for the survey portion and the Godot 4.x `FileAccess` and `DirAccess` references for the atomic-write implementations.

---

## 1. The temp-file-plus-rename pattern

The pattern in three lines of pseudocode:

```
write payload to "save.tmp"
fsync "save.tmp"
rename "save.tmp" -> "save.latest"
```

That is the entire pattern. The rest of this section is why each step matters.

### 1.1 Why never write directly to the production path

A naive save looks like:

```python
with open("save.latest", "w") as f:
    json.dump(state, f)
```

The naive save has two failure modes that are unrecoverable:

**Failure mode A — crash before any write.** The `open(path, "w")` call truncates `save.latest` to zero bytes. The `json.dump` call is supposed to fill it back up. If the program crashes between the two — power loss, OS kill, user pulls the USB drive — the file on disk is zero bytes, and the previous good save is gone.

**Failure mode B — crash mid-write.** The `json.dump` call writes the payload in chunks. The OS may buffer those chunks. A crash during the writes leaves the file half-populated; the JSON is unparseable. The previous good save is gone *and* the new save is broken.

Both failure modes are common in practice. Crashes are common. Power losses happen on laptops. Users force-quit games. The naive save loses data on each.

### 1.2 The pattern, in Python

```python
import json
import os
from pathlib import Path

def write_save_atomic(path: Path, payload: dict) -> None:
    tmp_path: Path = path.with_suffix(path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, sort_keys=True, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)  # atomic on POSIX and on Windows
```

Three things to notice:

1. **The temp file lives next to the production file.** Same directory. Not in `/tmp/`, not in a hidden subfolder, not in the user's documents folder. The reason: `rename` is only atomic *within a filesystem*. Putting the temp file in the same directory guarantees it is on the same filesystem.

2. **`flush` then `fsync` before `rename`.** `flush` pushes the Python buffer to the OS; `fsync` pushes the OS buffer to the disk. Without `fsync`, the rename can succeed and the file's bytes can still be in the OS write-back queue; a power loss right after the rename leaves the production file pointing at not-yet-flushed bytes, which round to zero bytes on power restoration.

3. **`os.replace`, not `os.rename`.** `os.rename` is allowed to fail on Windows if the target exists (older Python versions, older Windows behaviour). `os.replace` is the cross-platform "rename and replace" that works on Linux, macOS, and Windows.

### 1.3 The pattern, in GDScript

```gdscript
func write_save_atomic(path: String, payload: Dictionary) -> bool:
    var tmp_path: String = path + ".tmp"
    var file: FileAccess = FileAccess.open(tmp_path, FileAccess.WRITE)
    if file == null:
        push_error("save: cannot open " + tmp_path)
        return false
    var as_json: String = JSON.stringify(payload, "\t", true)
    file.store_string(as_json)
    file.close()  # FileAccess flushes on close in Godot 4.x
    var dir: DirAccess = DirAccess.open(path.get_base_dir())
    if dir == null:
        push_error("save: cannot open dir")
        return false
    var rename_err: int = dir.rename(tmp_path, path)
    if rename_err != OK:
        push_error("save: rename failed err=" + str(rename_err))
        return false
    return true
```

Godot's `FileAccess.close()` flushes the file. There is no explicit `fsync` exposed; the engine relies on the OS to flush on close. For save sizes under a megabyte on modern SSD-equipped hardware this is acceptable. For multi-megabyte saves or hard-drive-equipped hardware, the lack of explicit `fsync` is a known limitation; the workaround is to invoke a small helper via `OS.execute` that calls `sync` (POSIX) or to accept the engine's behaviour.

The `JSON.stringify(payload, "\t", true)` call passes `true` for the third `sort_keys` argument; we will need sorted keys when we add the integrity check in section 2.

### 1.4 The atomicity guarantee, precisely

The POSIX rename guarantee is: *at every moment, the production path resolves to either the old contents or the new contents, never a partial state or an absent file.* The kernel implements this with a single inode-table swap; there is no observable in-between.

On Windows, `MoveFileEx` with `MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH` is the equivalent. Python's `os.replace` is a thin wrapper around the appropriate underlying call.

The guarantee does *not* extend across filesystems. If the temp file is on `/tmp` and the production path is on the user's home directory and the two are different filesystems, `rename` performs a copy-and-delete which is *not* atomic. The mitigation is the rule from section 1.2: the temp file always lives in the same directory as the production file.

The guarantee does *not* extend to network filesystems with unusual semantics (NFS in some configurations, SMB). For game saves on the local user data directory of a typical desktop machine, none of those apply.

### 1.5 Cost in practice

For a 5 KB save:

- Write to temp file: ~0.1 ms.
- `fsync`: ~1 to 5 ms on SSD, ~10 to 30 ms on a hard drive.
- Rename: ~0.1 ms.

Total: a few milliseconds. Below one frame at 60 fps. Acceptable on the main thread.

For a 5 MB save the `fsync` cost grows roughly linearly; an SSD reaches ~3 ms per MB, a slow USB drive can reach 30 ms per MB. Above 1 MB of save data on slow storage, move the save off the main thread.

---

## 2. Integrity checks

The temp-file-plus-rename pattern protects against *crash-induced* corruption. It does not protect against:

- Disk-level corruption (a bad sector silently flips a bit).
- Manual editing (the player tampered).
- Cloud-sync corruption (the cloud service uploaded truncated bytes).

The protection is an integrity check.

### 2.1 SHA-256 of the payload

The simplest scheme: hash the payload before writing, store the hash alongside, recompute on load, compare. A mismatch means the file is bad; the loader rejects it.

In JSON, the hash can be a field in the save itself:

```json
{
  "version": 2,
  "payload": { ... actual save data ... },
  "integrity": "sha256:7c4a8d09ca3762af61e59520943dc26494f8941b"
}
```

The hash is computed over the canonicalised `payload` block (`json.dumps(payload, sort_keys=True, separators=(",", ":"))`). Canonicalisation matters: the same logical payload must produce the same bytes regardless of dict-iteration order. `sort_keys=True` does the work.

The load path:

```python
def load_save_with_integrity(path: Path) -> dict:
    parsed: dict = json.loads(path.read_text(encoding="utf-8"))
    payload: dict = parsed["payload"]
    stored: str = parsed["integrity"]
    canonical: str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    expected: str = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if stored != expected:
        raise ValueError(f"integrity check failed: {stored} != {expected}")
    return payload
```

A bit flip in the payload changes the hash; the loader rejects the file. The player loses *this* save; they fall back to the backup (section 3).

### 2.2 What SHA-256 does and does not protect against

The SHA-256 check protects against:

- Random bit flips from disk or memory errors.
- Truncation (the hash is computed over the full payload; a truncated payload hashes to a different value).
- Accidental editing (a player who hand-edits the file in a text editor and saves; the saved bytes do not match the stored hash).

The SHA-256 check does *not* protect against:

- Deliberate editing where the editor knows the format (the editor re-computes the hash after their changes; the stored hash matches the modified payload).

The mitigation against deliberate editing is a *keyed* hash — an HMAC-SHA-256 with a per-install secret key. The key lives in the player's user-data directory under a different filename; an editor who does not know the key cannot regenerate a matching MAC. This is not cryptographic *protection* — the key is on the machine, an attacker with file-system access can copy it — but it stops casual editing and the most common copy-a-friend's-save attack. The HMAC variant is in `challenges/challenge-01-hmac-signed-saves.md`.

### 2.3 Why SHA-256 and not CRC32

CRC32 is faster. CRC32 is fine for *crash-only* protection — detecting accidental corruption.

SHA-256 is slower (~5 ms per MB on modern hardware). The cost is invisible for save sizes under a megabyte.

We use SHA-256 because:

- The standard library has both, and `hashlib.sha256` is one line.
- The hash is the same primitive as the HMAC in the stretch challenge.
- The cost is invisible.

For a multi-megabyte save where the SHA-256 cost is visible, switch to CRC32 (or `xxhash` if the dependency is acceptable). The choice is project-specific; the *presence* of an integrity check is not negotiable.

---

## 3. Backup rotation

The integrity check tells the loader that `save.latest` is broken. The backup rotation is what the loader does next.

### 3.1 The three-file scheme

At any moment, the save directory contains up to three files for a given slot:

- `slot_0.save` — the production file. Always-current, atomically updated.
- `slot_0.save.prev` — the previous good save. Updated on each successful write of the production file.
- `slot_0.save.tmp` — the in-flight write. Only briefly visible during a save operation.

The write sequence:

```python
def write_save_with_rotation(path: Path, payload: dict) -> None:
    tmp_path: Path = path.with_suffix(path.suffix + ".tmp")
    prev_path: Path = path.with_suffix(path.suffix + ".prev")

    # 1. Write payload to temp file (atomically replacing any old temp file).
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, sort_keys=True, indent=2)
        f.flush()
        os.fsync(f.fileno())

    # 2. Rotate: production -> previous (if production exists).
    if path.exists():
        os.replace(path, prev_path)

    # 3. Publish: temp -> production.
    os.replace(tmp_path, path)
```

The load sequence:

```python
def load_save_with_rotation(path: Path) -> dict:
    prev_path: Path = path.with_suffix(path.suffix + ".prev")

    # 1. Try production.
    if path.exists():
        try:
            return load_save_with_integrity(path)
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"production save failed: {exc}; falling back to previous")

    # 2. Try previous.
    if prev_path.exists():
        try:
            return load_save_with_integrity(prev_path)
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"previous save failed: {exc}; both saves are bad")
            raise

    # 3. No good save anywhere.
    raise FileNotFoundError("no readable save found")
```

The cost: two extra renames per write, one extra `exists` plus possibly one extra parse attempt per load. Both are cheap.

The win: the player who experiences a corruption event loses at most the work done *since the previous save*, not their entire progression. For most games that is a few minutes — survivable.

### 3.2 The four-state corruption table

A two-save scheme has four possible loader states at startup:

| Production | Previous   | Loader behaviour                                       |
|------------|------------|--------------------------------------------------------|
| Good       | Good       | Load production. Normal case.                          |
| Good       | Missing    | Load production. (First-ever save or backup was deleted.) |
| Broken     | Good       | Log warning, load previous, offer recovery.            |
| Missing    | Good       | Load previous, offer recovery.                         |
| Broken     | Broken     | Surface a clear error to the player. No load possible. |
| Missing    | Missing    | Start new game; no save exists.                        |

The last row — broken and broken — happens essentially only in disk-failure scenarios. The player has bigger problems than your save system at that point.

### 3.3 Optional: multiple backup generations

For high-stakes saves (a single-shot 80-hour playthrough, a competitive run), the three-file scheme can extend to N backups: `slot_0.save`, `slot_0.save.1`, `slot_0.save.2`, ..., `slot_0.save.N`. Each write rotates the chain.

The cost grows with N. The benefit grows too. For an indie game, N=2 (the three-file scheme above) is the right balance. For a roguelike with permadeath where the entire run is the save, N=5 or N=10 is justified.

The mini-project ships N=2. Extending to N>2 is a stretch in the homework.

---

## 4. The cloud-save survey

The three services below sync game saves between a player's local machine and a vendor-operated cloud. We cover each at the conceptual level. We do not implement any of them this week — each requires a vendor SDK, signing keys, and a registered application — but you should be able to read the documentation and orient yourself in it.

### 4.1 Steam Cloud (Windows, macOS, Linux via Steam)

The Steam Cloud documentation is at [partner.steamgames.com/doc/features/cloud](https://partner.steamgames.com/doc/features/cloud).

Steam Cloud offers two integration paths:

**Auto-Cloud (declarative).** In the Steamworks partner portal, you declare a list of glob patterns (e.g. `%USER%/AppData/Local/MyGame/save_*.json`). Steam silently syncs files matching the globs between the local machine and the cloud. Your game writes to disk as normal; the syncing is invisible.

**ISteamRemoteStorage (programmatic).** Your game calls Steam API functions to write and read files: `FileWrite`, `FileRead`, `FileExists`, `FileDelete`. Steam transports them. The advantage is *explicit* sync: you know when a file is up to date.

For a typical indie game, Auto-Cloud is the right answer. The Steamworks portal lets you list the globs and ship. The cost is the loss of explicit control; saves sync when Steam decides to sync them.

The conflict-resolution default is *last-writer-wins by file mtime*. A player who plays the game on two machines and clocks drift (one machine has the wrong date) can lose data: the older-mtime write is silently overwritten. The mitigation is to *opt in to conflict callbacks* via `ISteamRemoteStorage::OnConflict`, then surface a "two save versions found, which would you like to keep?" dialog when a conflict is detected.

Most shipped games do not opt in. Most shipped games occasionally eat saves. The vendor's documentation acknowledges the trade-off; the mitigation is your responsibility.

### 4.2 Google Play Saves (Android)

The Google Play Saves documentation is at [developers.google.com/games/services/common/concepts/savedgames](https://developers.google.com/games/services/common/concepts/savedgames).

The model is *explicit snapshots*. Your game packages the save as a "snapshot" — a binary blob plus a metadata header (last-modified time, total playtime, level number, description, optional cover image). The game calls `SnapshotsClient.open(snapshotName, createIfMissing, conflictPolicy)` to read; calls `SnapshotsClient.commitAndClose(snapshot, metadata)` to write.

The conflict-resolution policy is a parameter. The options are:

- `RESOLUTION_POLICY_LAST_KNOWN_GOOD` — keep the version on the device.
- `RESOLUTION_POLICY_MOST_RECENTLY_MODIFIED` — keep the most-recent.
- `RESOLUTION_POLICY_HIGHEST_PROGRESS` — keep the one with the larger "progress value" metadata.
- `RESOLUTION_POLICY_LONGEST_PLAYTIME` — keep the one with the larger playtime metadata.
- `RESOLUTION_POLICY_MANUAL` — surface the conflict to the app; the app picks.

For most games `RESOLUTION_POLICY_HIGHEST_PROGRESS` is the right answer: store a single monotonic progress integer (e.g. total experience, total level reached) and let the cloud pick the bigger one. The pattern protects against clock skew (no mtime dependency).

The cost: every save must compute the progress metadata. The implementation is a single function: a save's `progress` value is, say, `xp + 1000 * deepest_level`.

### 4.3 Apple iCloud Key-Value Storage (iOS, macOS)

The iCloud Key-Value Storage documentation is at [developer.apple.com/documentation/foundation/icloud/storing_key-value_data_in_icloud](https://developer.apple.com/documentation/foundation/icloud/storing_key-value_data_in_icloud).

The model is *implicit key-value sync*. Your app gets an `NSUbiquitousKeyValueStore` instance, sets values on it, and reads values from it. Apple's framework syncs the values across the user's Apple devices automatically.

The quota is small: **1 MB total across all keys, 1 MB per key.** This is the lowest of any of the three services. Large saves do not fit.

For settings and small progression flags (a `current_level` integer, a `total_playtime` integer, a `unlocked_achievements` bitset), iCloud Key-Value Storage is the right tool. For a full save file, use **iCloud Documents** instead, which uses iCloud Drive and has multi-gigabyte capacity.

The conflict-resolution model is broadcast notifications: when a value changes in the cloud, every device gets an `NSUbiquitousKeyValueStoreDidChangeExternallyNotification` and can choose to accept the new value, reject it, or merge. The merging logic is the app's responsibility.

### 4.4 What the three services have in common

- All three sync local files to a vendor cloud. The transport is the vendor's concern.
- All three have a quota. Steam Cloud's is per-title (typically 100 MB to 1 GB, configurable in the Steamworks portal). Google Play Saves' is 3 MB per snapshot, with up to 4 named snapshots per player. iCloud Key-Value Storage is 1 MB total.
- All three have a conflict model. None defaults to "preserve both versions"; you must opt in.
- All three are *eventually consistent*. A write on one device takes seconds to a minute to appear on another. A game that immediately reads what it just wrote on the same device sees the new value; a game that wrote on Device A and reads on Device B may see the old value for some period.

### 4.5 What you should do this week

Read each vendor's overview page once. You should be able to answer: which service is which, what each one's quota is, what each one's conflict-resolution default is. You should *not* attempt to integrate against any of them. The vendor SDKs each take a day or two to set up correctly, and the platform-specific signing requirements are out of scope.

The mini-project's save system is designed to be *cloud-portable*: writes are atomic, the production path is a stable file, and the format is self-describing. When a future you adds Steam Cloud Auto-Cloud, the only configuration change is declaring the save glob in the Steamworks portal; the game code does not change at all.

---

## 5. Recap

We covered:

- The temp-file-plus-rename pattern, in Python and in GDScript, with `fsync` and `os.replace` and the GDScript `DirAccess.rename` equivalent.
- The SHA-256 integrity check, the canonicalisation requirement, and the difference between CRC32 (faster, accident-only) and SHA-256 (slower, accident-and-HMAC-substrate).
- Backup rotation: `save.latest` → `save.previous` on every write, fall back to `previous` if `latest` fails to load.
- The cloud-save survey: Steam Cloud's silent last-write-wins, Google Play Saves' explicit snapshot model, iCloud Key-Value Storage's 1 MB quota and broadcast notifications.

Next week we ship input remapping and accessibility, with bindings persisted through the save system you build this week.
