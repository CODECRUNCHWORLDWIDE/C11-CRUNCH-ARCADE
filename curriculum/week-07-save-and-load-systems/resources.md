# Week 7 — Resources

Every resource on this page is **free** and **publicly accessible**. No paywalled books, no proprietary PDFs. If a link breaks, please open an issue.

## Required reading and watching (work it into your week)

- **Glenn Fiedler — *Reading and Writing Packets* (Gaffer On Games, free).** The canonical free essay on how to lay out a serialized packet that includes version, integrity check, and forward-compatible fields. The save-file format we build this week is the *same shape* as Fiedler's network packet. Read once at the start of the week and again at the end:
  <https://gafferongames.com/post/reading_and_writing_packets/>
- **Glenn Fiedler — *Serialization Strategies* (Gaffer On Games, free).** Fiedler's three-strategy taxonomy — read-function/write-function pairs, a unified read-or-write function, and a generic visit-the-fields pattern. The middle one is what we use in `to_dict()` / `from_dict()`:
  <https://gafferongames.com/post/serialization_strategies/>
- **RFC 8259 — *The JavaScript Object Notation (JSON) Data Interchange Format* (Bray, ed., IETF, December 2017, free).** Twelve pages. The single canonical JSON specification. Read at least sections 1, 2, 3, 4, 7, and 8:
  <https://www.rfc-editor.org/rfc/rfc8259>
- **MessagePack specification (msgpack-spec on GitHub, free).** Six pages. The binary wire format. Read the type-prefix table once; you will recognise the bytes in Exercise 3's hex dump:
  <https://github.com/msgpack/msgpack/blob/master/spec.md>
- **Pygame documentation — main reference (free).** The canonical Pygame docs we cite every week. Week 7 specifically uses `pygame.image`, `pygame.font`, and the standard event loop. Nothing in `pygame.Surface` or `pygame.mixer` belongs in a save file:
  <https://www.pygame.org/docs/>

## Glenn Fiedler — Gaffer On Games (free, ~6 essays)

Fiedler's serialization essays are the closest the industry has to a textbook on this topic. All free. All in the public domain in spirit if not in licence.

- **Reading and Writing Packets.** The packet layout, the version stamp, the integrity check.
  <https://gafferongames.com/post/reading_and_writing_packets/>
- **Serialization Strategies.** The three strategies; pick one and stick with it.
  <https://gafferongames.com/post/serialization_strategies/>
- **Reliable Ordered Messages.** Networking-flavoured but the *ordering* discipline is the same as save migrations.
  <https://gafferongames.com/post/reliable_ordered_messages/>
- **State Synchronization.** Network-game state sync. The "delta state" idea (only send what changed) is how a future Week-12 save system would shrink autosave costs to zero:
  <https://gafferongames.com/post/state_synchronization/>
- **Snapshot Compression.** Bit-packed integer ranges. Out of scope this week; included for the curious:
  <https://gafferongames.com/post/snapshot_compression/>

## JSON, MessagePack, and binary formats (specs)

- **RFC 8259 — JSON (12 pages, IETF).** The spec. Read sections 1-4 carefully, section 7 (Strings) at least once, and section 8 (String and Number Encoding) for the gotchas:
  <https://www.rfc-editor.org/rfc/rfc8259>
- **JSON spec interactive reference — json.org.** The one-page railroad-diagram view of the grammar Douglas Crockford originally hosted. Same content as RFC 8259, half the prose:
  <https://www.json.org/json-en.html>
- **MessagePack specification — msgpack-spec on GitHub.** Six pages. The type-prefix table is on page 2; print it:
  <https://github.com/msgpack/msgpack/blob/master/spec.md>
- **MessagePack project home — msgpack.org.** Library list per language; benchmarks; rationale:
  <https://msgpack.org/>
- **Python `struct` module — official docs.** The canonical reference for byte-level packing in stdlib. Used in Lecture 2 §3 to demonstrate "custom binary," which we explicitly recommend against for saves:
  <https://docs.python.org/3/library/struct.html>
- **Python `json` module — official docs.** The stdlib `json` library reference. Note `indent=2` and `sort_keys=True` for readable saves and `ensure_ascii=False` if you want UTF-8 characters in the file:
  <https://docs.python.org/3/library/json.html>
- **Python `gzip` module — official docs.** Stdlib compression. `gzip.open(path, "wt")` is a drop-in for `open(path, "w")`:
  <https://docs.python.org/3/library/gzip.html>
- **Python `hashlib` module — official docs.** SHA-256 for save integrity. `hashlib.sha256(data).hexdigest()` is the line of code:
  <https://docs.python.org/3/library/hashlib.html>

## Pygame-specific (free)

- **Pygame main docs — landing page.**
  <https://www.pygame.org/docs/>
- **`pygame.image.save`.** Used in the stretch goal for embedding a screenshot in a save slot. Not used in the core week.
  <https://www.pygame.org/docs/ref/image.html#pygame.image.save>
- **`pygame.event` reference.** Event polling for the save-slot UI in Challenge 2:
  <https://www.pygame.org/docs/ref/event.html>
- **`pygame.font.Font`.** Used by the slot UI for rendering timestamps and slot labels:
  <https://www.pygame.org/docs/ref/font.html>
- **`pygame.time.get_ticks`.** Used by autosave cadence (compare against a last-save timestamp):
  <https://www.pygame.org/docs/ref/time.html#pygame.time.get_ticks>

## Godot save-game documentation (for the Week-9 bridge)

We mention Godot to set up Week 9 (when C11 transitions to Godot). The algorithms in this week's lectures port verbatim. Skim these now; come back in Week 9.

- **Godot — *Saving games* (official docs, free).** Godot's canonical save-system tutorial. Uses `FileAccess.open` and `JSON.parse_string`. Note the `save_data` dict shape — it is the same shape as our `to_dict()`:
  <https://docs.godotengine.org/en/stable/tutorials/io/saving_games.html>
- **Godot — *ConfigFile* class reference.** The engine's stdlib for simple key/value settings — the equivalent of "INI for games." Useful for player preferences, not for game state:
  <https://docs.godotengine.org/en/stable/classes/class_configfile.html>
- **Godot — *FileAccess* class reference.** The engine's file I/O primitive. `FileAccess.open` is Pygame's `open`. The `flush()` call is your `fsync`:
  <https://docs.godotengine.org/en/stable/classes/class_fileaccess.html>
- **Godot — *ResourceSaver* class reference.** Saves Godot `Resource` objects to `.tres` or `.tscn`. Used for level data, not game state. Out of scope this week; included for completeness:
  <https://docs.godotengine.org/en/stable/classes/class_resourcesaver.html>

## Atomic writes and crash safety

- **Python `os.replace` — official docs.** The atomic-rename call. Available on every platform since Python 3.3. The line of code that makes a save crash-safe:
  <https://docs.python.org/3/library/os.html#os.replace>
- **Python `os.fsync` — official docs.** Force the OS to flush a file's buffers to disk before the rename. The pair of `fsync` + `replace` is the gold standard for crash-safe writes:
  <https://docs.python.org/3/library/os.html#os.fsync>
- **LWN.net — *Ensuring data reaches disk* (free article).** A short, technical write-up on `fsync`, `O_DIRECT`, and what "the file is on disk" actually means on Linux. Skim:
  <https://lwn.net/Articles/457667/>
- **PostgreSQL documentation — *Reliability* (free).** PostgreSQL's own write-ahead-log discipline. We borrow the pattern (write to `.tmp`, fsync, rename) directly from databases:
  <https://www.postgresql.org/docs/current/wal-reliability.html>

## Talks and long-form (free)

- **Jonathan Blow — *Why I Wrote My Own Save System* (2018, ~45 min, free on YouTube).** Blow explains *The Witness*'s memory-snapshot save system. Overkill for an indie game; the design reasoning is excellent. Watch in your stretch hours:
  <https://www.youtube.com/results?search_query=jonathan+blow+save+system>
- **Casey Muratori — *Handmade Hero* (free, ongoing series).** Specifically the episodes on the asset format. Muratori's "everything has a header with a version" discipline is the same one we use:
  <https://handmadehero.org/>
- **GDC Vault — *Save Systems in Modern Games* (free GDC vault sessions).** Search the GDC Vault for "save system" — the free sessions on tutorial-design and save-flow are short and useful. Look specifically for sessions tagged "Free":
  <https://www.gdcvault.com/>
- **Mark Brown — *Game Maker's Toolkit* on save points (free, ~10 min episodes).** Design-level commentary on save *placement* (the player-facing decision), distinct from save *implementation* (the engineering decision):
  <https://www.youtube.com/@GMTK>

## Examples of save formats in real games (free reading)

These are studies. You will not implement any of them this week; you may recognise their patterns in your own saves later.

- **Minecraft NBT format — public spec.** The "Named Binary Tag" format Mojang uses for world saves. A worked example of a custom binary tree format with type tags. Free spec:
  <https://wiki.vg/NBT>
- **Stardew Valley save file format — community wiki.** Plain XML (one of the more unusual choices). The community-written guide on the wiki is detailed and free:
  <https://stardewvalleywiki.com/Saves>
- **Celeste save data — public format.** Celeste saves are XML. Discussed openly by the developers in interviews. The community has documented the layout:
  <https://github.com/EverestAPI/Everest/wiki/Save-Data-Format>

## Free Python packages we use this week

Install in your virtual environment:

```bash
pip install pygame msgpack
```

- **pygame (>= 2.5).** The game engine. Free, open-source, LGPL.
  <https://www.pygame.org/>
- **msgpack (>= 1.0).** MessagePack reference implementation for Python. Pure-Python fallback plus a Cython-accelerated path. Free, Apache 2.0 licence.
  <https://github.com/msgpack/msgpack-python>

Stdlib only (no install needed):

- `json`, `gzip`, `hashlib`, `os`, `struct`, `pathlib`, `dataclasses`, `time`, `datetime`.

## Asset packs (for the mini-project)

- **Kenney — *Tiny Dungeon* (CC0).** A 16×16 tile and sprite pack with three character variants, a small dungeon tileset, and props. The mini-project recommends this pack. ~3 MB:
  <https://kenney.nl/assets/tiny-dungeon>
- **Kenney — *Generic Items* (CC0).** Inventory icons for coins, potions, keys, scrolls. ~1 MB:
  <https://kenney.nl/assets/generic-items>
- **Kenney — *Interface Sounds* (CC0).** Already in your repo from Week 6. Reuse the "confirm" and "cancel" beeps for save/load:
  <https://kenney.nl/assets/interface-sounds>

All Kenney packs are CC0 (public domain). Credit is *not required*. Credit anyway; it is the right thing to do.

## What you will *not* need this week

- A database engine (SQLite, Postgres). A save file is a *single record*, not a table. SQLite is the right tool for Week 14 (player analytics, achievement progress across many runs), not for a game save.
- A cloud SDK (AWS, Firebase, Steam Cloud). The cloud-save *protocol* is in Challenge 1 (paper design only). The plumbing is a Week-17 stretch topic.
- An ORM (SQLAlchemy, Peewee). Save files are flat dicts; an ORM is the wrong shape.
- Encryption (`cryptography`, `nacl`). Local saves do not need encryption. If you want to discourage casual editing, an `XOR-with-a-constant` "obfuscation" pass is two lines, but it is not security and we will not pretend otherwise.

---

*Bookmark this page. Resources accumulate; by Week 12 this file is the most-revisited document in your repo.*
