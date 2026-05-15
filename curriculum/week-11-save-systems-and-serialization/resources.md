# Week 11 — Resources

Every link below is **free** to read. No paywalls, no trial-period gates, no "sign up for the newsletter to continue" interstitials. The four primary references are also the four references cited throughout the lectures.

---

## Primary references

### Godot 4.x — Saving games (official tutorial)

[docs.godotengine.org/en/stable/tutorials/io/saving_games.html](https://docs.godotengine.org/en/stable/tutorials/io/saving_games.html)

The engine's own production reference. Walks through three approaches: `ConfigFile` for small settings, JSON for general-purpose, and custom `Resource` classes with `ResourceSaver` for the all-Godot path. Read it in full before Monday — it is short, dense, and frames the vocabulary the lectures use.

Adjacent pages that are also free and worth reading the same evening:

- *FileAccess* — the I/O primitive every save path eventually calls: [docs.godotengine.org/en/stable/classes/class_fileaccess.html](https://docs.godotengine.org/en/stable/classes/class_fileaccess.html)
- *DirAccess* — directory and rename operations: [docs.godotengine.org/en/stable/classes/class_diraccess.html](https://docs.godotengine.org/en/stable/classes/class_diraccess.html)
- *JSON* — the parser and stringifier Godot ships: [docs.godotengine.org/en/stable/classes/class_json.html](https://docs.godotengine.org/en/stable/classes/class_json.html)
- *ResourceSaver* and *ResourceLoader* — the native binary/text save path: [docs.godotengine.org/en/stable/classes/class_resourcesaver.html](https://docs.godotengine.org/en/stable/classes/class_resourcesaver.html) and [docs.godotengine.org/en/stable/classes/class_resourceloader.html](https://docs.godotengine.org/en/stable/classes/class_resourceloader.html)
- *OS.get_user_data_dir* — the per-OS save directory: [docs.godotengine.org/en/stable/classes/class_os.html#class-os-method-get-user-data-dir](https://docs.godotengine.org/en/stable/classes/class_os.html#class-os-method-get-user-data-dir)

### MessagePack — the official specification

[github.com/msgpack/msgpack/blob/master/spec.md](https://github.com/msgpack/msgpack/blob/master/spec.md)

The complete on-the-wire format definition. Around 600 lines of plain markdown, all of which is reference-quality. Pay attention to the *type system* section (the data model is *deliberately* a strict superset-ish of JSON's) and the *formats* table (the one-byte-per-type tags are what make MessagePack 2x to 3x denser than JSON on real-world game saves).

For the Python library specifically:

- `msgpack-python` on PyPI: [pypi.org/project/msgpack/](https://pypi.org/project/msgpack/)
- The library's documentation: [msgpack-python.readthedocs.io/en/latest/](https://msgpack-python.readthedocs.io/en/latest/)

Both are MIT-licensed and free.

### Pydantic v2 — the official documentation

[docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/)

The canonical reference for schema-validated Python data classes. The *Models* page covers the `BaseModel` class you will use in every exercise; the *Validators* page covers the per-field and per-model custom validation you need for non-trivial fields; the *JSON Schema* page covers exporting a schema to disk for QA tooling. Read in this order: *Models* → *Fields* → *Validators* → *Migration from v1*.

Two specific pages are required reading for this week:

- *Models* — the `BaseModel` API: [docs.pydantic.dev/latest/concepts/models/](https://docs.pydantic.dev/latest/concepts/models/)
- *Validators* — `field_validator` and `model_validator`: [docs.pydantic.dev/latest/concepts/validators/](https://docs.pydantic.dev/latest/concepts/validators/)

Pydantic v2 is a near-complete rewrite of v1 with breaking API changes. Make sure you are reading v2 docs (the URL contains `latest/`); v1 docs live at `v1.docs.pydantic.dev`.

### Steamworks — Steam Cloud documentation

[partner.steamgames.com/doc/features/cloud](https://partner.steamgames.com/doc/features/cloud)

The vendor's own documentation for the cloud-save service. Reading is free — implementing requires a Steamworks account, which is gated behind a $100 fee per title. We do not implement against the API this week; we read about it. The page covers the *Auto-Cloud* path (declarative: list the file globs to sync, Steam handles the rest) and the *ISteamRemoteStorage* path (programmatic: your game calls write/read functions and Steam handles transport).

Adjacent free reads in the same docs tree:

- *Steam Auto-Cloud configuration*: [partner.steamgames.com/doc/features/cloud/autocloud](https://partner.steamgames.com/doc/features/cloud/autocloud)
- *Steam Cloud conflict resolution*: [partner.steamgames.com/doc/features/cloud#3](https://partner.steamgames.com/doc/features/cloud#3) (the same page, anchor link)

Google Play Saves and Apple iCloud documentation are also free to read; we link them in the survey section below rather than as primaries because we cover them as a survey rather than implement against them.

---

## Background reading on serialisation hazards

The two "do not use" formats deserve their own citations. We do not implement either; we cite the reasons.

### Why never `pickle.load` untrusted data

The Python core team's own warning, at the top of the `pickle` module documentation:

[docs.python.org/3/library/pickle.html#module-pickle](https://docs.python.org/3/library/pickle.html#module-pickle)

Quoted in full from the standard library: *"The pickle module is not secure. Only unpickle data you trust. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling."*

The mechanism: a pickle stream is a small stack-based VM whose `REDUCE` opcode invokes any callable the pickler chose. An attacker who controls the bytes controls the call. The standard exploit is one line of pickle that calls `os.system("...")` on load.

Free background reading from a security perspective:

- Dan Crosta's *"Don't Pickle Your Data"*: [late.am/post/2012/03/26/exploring-the-hidden-potential-of-pickle](https://late.am/post/2012/03/26/exploring-the-hidden-potential-of-pickle) (free, dated 2012, still accurate)
- David Hamann's *"Exploiting Python pickles"*: [davidhamann.de/2020/04/05/exploiting-python-pickle/](https://davidhamann.de/2020/04/05/exploiting-python-pickle/) (free, dated 2020)

### Why never `BinaryFormatter.Deserialize` in .NET

Microsoft's own deprecation notice, at the top of the `BinaryFormatter` documentation:

[learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide)

Quoted: *"The BinaryFormatter type is dangerous and is not recommended for data processing. Applications should stop using BinaryFormatter as soon as possible, even if they believe the data they're processing to be trustworthy."*

The mechanism is the same as `pickle`'s. The format encodes type names; the deserialiser constructs instances of those types; many .NET types execute code as a side effect of construction or property-setter invocation. The CVE history is extensive.

`BinaryFormatter` is removed from .NET 9 entirely. Use `System.Text.Json` or `MessagePack-CSharp` instead.

---

## Survey — cloud save services

Read for vocabulary and conceptual familiarity; do not implement this week.

### Steam Cloud (Windows / macOS / Linux via Steam)

- Main docs: [partner.steamgames.com/doc/features/cloud](https://partner.steamgames.com/doc/features/cloud)
- Conflict resolution callback: [partner.steamgames.com/doc/api/ISteamRemoteStorage](https://partner.steamgames.com/doc/api/ISteamRemoteStorage)

### Google Play Saves (Android)

- Main docs: [developers.google.com/games/services/common/concepts/savedgames](https://developers.google.com/games/services/common/concepts/savedgames)
- Snapshot API: [developers.google.com/games/services/android/savedgames](https://developers.google.com/games/services/android/savedgames)

### Apple iCloud Key-Value Storage (iOS / macOS)

- Conceptual overview: [developer.apple.com/documentation/foundation/icloud/storing_key-value_data_in_icloud](https://developer.apple.com/documentation/foundation/icloud/storing_key-value_data_in_icloud)
- The `NSUbiquitousKeyValueStore` class: [developer.apple.com/documentation/foundation/nsubiquitouskeyvaluestore](https://developer.apple.com/documentation/foundation/nsubiquitouskeyvaluestore)

The three services solve overlapping problems with different trade-offs. Steam Cloud is the most player-visible (a per-title sync indicator in the Steam UI); Google Play Saves is the most explicit (your code calls upload/download); iCloud Key-Value Storage is the most invisible (key writes propagate within ~30 seconds with no API call needed).

---

## Free books and long-form

### *Game Programming Patterns* by Robert Nystrom (free online)

[gameprogrammingpatterns.com/contents.html](https://gameprogrammingpatterns.com/contents.html)

The *Bytecode* and *Component* chapters are tangentially relevant to save design (the component pattern is the architecture that makes "save only the components you need" trivial). The whole book is free online and worth a slow read across the course; this week, the two named chapters take ~30 minutes each.

### *Designing Data-Intensive Applications* — chapter 4 ("Encoding and Evolution")

The book itself is not free, but chapter 4 — the chapter most directly relevant to save versioning — is excerpted by the author at:

[martin.kleppmann.com/2017/03/27/dynamic-typing-in-data-storage.html](https://martin.kleppmann.com/2017/03/27/dynamic-typing-in-data-storage.html)

The blog excerpt covers the same ground as the chapter on forwards and backwards compatibility in serialisation formats. Reading time ~20 minutes. The framing of *"a save format is a contract with your future self"* is from this work.

---

## Tooling, free to download

### `msgpack` (Python library)

- PyPI: [pypi.org/project/msgpack/](https://pypi.org/project/msgpack/)
- Apache 2.0 licensed.

### `pydantic` (Python library)

- PyPI: [pypi.org/project/pydantic/](https://pypi.org/project/pydantic/)
- MIT licensed.

### `pytest` (Python test framework)

- PyPI: [pypi.org/project/pytest/](https://pypi.org/project/pytest/)
- MIT licensed.

### Godot 4.x (game engine)

- Downloads: [godotengine.org/download/](https://godotengine.org/download/)
- MIT licensed.

---

## What to read in what order

For the student who has the week to spend, the recommended reading order is:

1. *Monday morning* — the Godot saving-games tutorial (linked above) in full. Twenty minutes.
2. *Monday evening* — Lecture 1 in this folder.
3. *Tuesday morning* — Lecture 2 in this folder, then skim the Pydantic v2 *Models* page.
4. *Tuesday evening* — read the MessagePack spec front-to-back. It is six hundred lines and the data-types section is the only thing you will reference later.
5. *Wednesday* — the Pydantic v2 *Validators* page in full while writing exercises 02 and 04.
6. *Thursday morning* — Lecture 3, then the Steamworks Steam Cloud overview page.
7. *Friday* — the cloud-save survey links above, skimming. Treat it as orientation, not study.
8. *Weekend* — the mini-project, with the Godot `FileAccess` and `DirAccess` class references open as references.

For the student short on time, the irreducible minimum is the Godot saving-games tutorial and the three lecture notes in this folder. The rest is enrichment.
