# Exercise 06 — The Godot SaveManager autoload.
#
# Goal
# ----
# Port the Python substrate from exercises 01-05 to GDScript inside Godot 4.x.
# The SaveManager is registered as an autoload singleton (Project Settings ->
# Autoload) so any scene can call SaveManager.save_to_slot(0) without
# instantiating anything.
#
# Features
# --------
# - Two-bucket model: a meta file (settings) and per-slot run files.
# - Atomic write via temp-file-plus-rename (DirAccess.rename).
# - SHA-256 integrity tag computed over the canonicalised payload.
# - Backup rotation: save_NN.json -> save_NN.json.prev on each successful write.
# - Schema versioning with a v1 -> v2 migration that mirrors exercise 04.
# - A _validate_save_dict helper that mirrors Pydantic's role on the Python side.
#
# Usage
# -----
# 1. Open Godot 4.2+.
# 2. Project Settings -> Autoload -> add this file as SaveManager.
# 3. From any script: SaveManager.save_to_slot(0, your_state_dict).
# 4. From any script: var s = SaveManager.load_from_slot(0).
#
# The mini-project ships a polished version of this file with a sample scene.

extends Node

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------

const CURRENT_VERSION: int = 2
const SLOT_COUNT: int = 3
const SAVE_DIR_NAME: String = "saves"  # under OS.get_user_data_dir()

# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------

func save_to_slot(slot: int, state: Dictionary) -> bool:
	"""Write the current run state to the given slot.

	Returns true on success. On failure, push_error is called with the reason
	and the slot's previous good save is left untouched.
	"""
	if slot < 0 or slot >= SLOT_COUNT:
		push_error("save: slot out of range: " + str(slot))
		return false

	# Always stamp the latest version on outgoing writes.
	var stamped: Dictionary = state.duplicate(true)
	stamped["version"] = CURRENT_VERSION

	if not _validate_save_dict(stamped):
		push_error("save: refusing to write invalid state")
		return false

	var paths: Dictionary = _paths_for_slot(slot)
	return _write_atomic_with_rotation(paths, stamped)


func load_from_slot(slot: int) -> Dictionary:
	"""Load the run state from the given slot, migrating to current version.

	Returns the loaded dictionary on success, or an empty dictionary if both
	the latest and previous backup are unreadable.
	"""
	if slot < 0 or slot >= SLOT_COUNT:
		push_error("load: slot out of range: " + str(slot))
		return {}

	var paths: Dictionary = _paths_for_slot(slot)
	var loaded: Dictionary = _load_with_fallback(paths)
	if loaded.is_empty():
		return {}

	loaded = _migrate_to_latest(loaded)
	if not _validate_save_dict(loaded):
		push_error("load: loaded save fails validation; refusing to return")
		return {}
	return loaded


func slot_exists(slot: int) -> bool:
	"""Return true if the given slot has any save (latest or previous)."""
	if slot < 0 or slot >= SLOT_COUNT:
		return false
	var paths: Dictionary = _paths_for_slot(slot)
	return FileAccess.file_exists(paths["latest"]) or FileAccess.file_exists(paths["previous"])


func delete_slot(slot: int) -> bool:
	"""Delete both files for a slot. Returns true if anything was deleted."""
	if slot < 0 or slot >= SLOT_COUNT:
		return false
	var paths: Dictionary = _paths_for_slot(slot)
	var deleted_any: bool = false
	for key in ["latest", "previous", "temp"]:
		var p: String = paths[key]
		if FileAccess.file_exists(p):
			var dir: DirAccess = DirAccess.open(p.get_base_dir())
			if dir != null:
				dir.remove(p.get_file())
				deleted_any = true
	return deleted_any


# ---------------------------------------------------------------------------
# Path helpers.
# ---------------------------------------------------------------------------

func _save_dir() -> String:
	"""Return the per-OS save directory, creating it if needed."""
	var base: String = OS.get_user_data_dir().path_join(SAVE_DIR_NAME)
	var dir: DirAccess = DirAccess.open(OS.get_user_data_dir())
	if dir != null and not dir.dir_exists(SAVE_DIR_NAME):
		dir.make_dir(SAVE_DIR_NAME)
	return base


func _paths_for_slot(slot: int) -> Dictionary:
	"""Return the {latest, previous, temp} path triple for the given slot."""
	var base: String = _save_dir().path_join("slot_%02d.save" % slot)
	return {
		"latest": base,
		"previous": base + ".prev",
		"temp": base + ".tmp",
	}


# ---------------------------------------------------------------------------
# Canonicalisation, integrity, envelope.
# ---------------------------------------------------------------------------

func _canonical_string(payload: Dictionary) -> String:
	"""Render payload as a deterministic string suitable for hashing.

	JSON.stringify with sort_keys=true and no indentation gives us the same
	determinism property as Python's json.dumps(sort_keys=True, separators=...).
	"""
	return JSON.stringify(payload, "", true)


func _integrity_tag(payload: Dictionary) -> String:
	"""Compute the sha256:<hex> tag of the canonicalised payload."""
	var canonical: String = _canonical_string(payload)
	var ctx: HashingContext = HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(canonical.to_utf8_buffer())
	var digest: PackedByteArray = ctx.finish()
	return "sha256:" + digest.hex_encode()


func _envelope(payload: Dictionary) -> Dictionary:
	"""Wrap payload in the on-disk envelope carrying its integrity tag."""
	return {"payload": payload, "integrity": _integrity_tag(payload)}


func _open_envelope(parsed: Dictionary) -> Dictionary:
	"""Verify the integrity tag and return the inner payload, or {} on failure."""
	if not parsed.has("payload") or not parsed.has("integrity"):
		push_error("envelope: missing 'payload' or 'integrity'")
		return {}
	var payload = parsed["payload"]
	if not (payload is Dictionary):
		push_error("envelope: 'payload' is not a Dictionary")
		return {}
	var stored: String = parsed["integrity"]
	var expected: String = _integrity_tag(payload)
	if stored != expected:
		push_error("envelope: integrity mismatch (" + stored + " != " + expected + ")")
		return {}
	return payload


# ---------------------------------------------------------------------------
# Atomic write and read with fallback.
# ---------------------------------------------------------------------------

func _write_atomic_with_rotation(paths: Dictionary, payload: Dictionary) -> bool:
	"""Atomic write: temp -> fsync (via close) -> rotate -> rename. Returns success."""
	var enveloped: Dictionary = _envelope(payload)
	var blob: String = JSON.stringify(enveloped, "\t", true)

	# 1. Write to the temp file.
	var temp_file: FileAccess = FileAccess.open(paths["temp"], FileAccess.WRITE)
	if temp_file == null:
		push_error("save: cannot open temp file: " + paths["temp"])
		return false
	temp_file.store_string(blob)
	temp_file.close()  # Godot flushes on close.

	# 2. Rotate latest -> previous (if latest exists).
	var save_dir: DirAccess = DirAccess.open(paths["latest"].get_base_dir())
	if save_dir == null:
		push_error("save: cannot open save dir")
		return false
	if FileAccess.file_exists(paths["latest"]):
		# DirAccess.rename overwrites silently on success.
		var rot_err: int = save_dir.rename(paths["latest"], paths["previous"])
		if rot_err != OK:
			push_error("save: rotation rename failed err=" + str(rot_err))
			return false

	# 3. Publish: temp -> latest.
	var pub_err: int = save_dir.rename(paths["temp"], paths["latest"])
	if pub_err != OK:
		push_error("save: publish rename failed err=" + str(pub_err))
		return false
	return true


func _load_with_fallback(paths: Dictionary) -> Dictionary:
	"""Try latest, fall back to previous. Returns the inner payload or {}."""
	for key in ["latest", "previous"]:
		var path: String = paths[key]
		if not FileAccess.file_exists(path):
			continue
		var file: FileAccess = FileAccess.open(path, FileAccess.READ)
		if file == null:
			push_error("load: cannot open " + path)
			continue
		var blob: String = file.get_as_text()
		file.close()
		var parsed = JSON.parse_string(blob)
		if parsed == null or not (parsed is Dictionary):
			push_error("load: " + key + " is not a valid JSON object; trying fallback")
			continue
		var payload: Dictionary = _open_envelope(parsed)
		if payload.is_empty():
			push_error("load: " + key + " failed envelope check; trying fallback")
			continue
		print("load: ", key, " accepted")
		return payload
	push_error("load: no readable save in slot")
	return {}


# ---------------------------------------------------------------------------
# Migration table.
# ---------------------------------------------------------------------------

func _migrate_to_latest(parsed: Dictionary) -> Dictionary:
	"""Run the single-step migration chain until parsed is at CURRENT_VERSION."""
	var current: Dictionary = parsed.duplicate(true)
	if not current.has("version"):
		current["version"] = 1  # legacy unversioned saves are treated as v1
	var safety: int = 0
	while int(current.get("version", 0)) < CURRENT_VERSION:
		var from_version: int = int(current["version"])
		var migrated: Dictionary = _migrate_step(current, from_version)
		if migrated.is_empty():
			push_error("migrate: no step registered from v" + str(from_version))
			return {}
		current = migrated
		safety += 1
		if safety > 100:
			push_error("migrate: chain exceeded 100 steps; aborting")
			return {}
	return current


func _migrate_step(d: Dictionary, from_version: int) -> Dictionary:
	"""Dispatch to the appropriate v_N -> v_N+1 step. Returns {} if no step exists."""
	if from_version == 1:
		return _migrate_v1_to_v2(d)
	return {}


func _migrate_v1_to_v2(v1: Dictionary) -> Dictionary:
	"""Promote a v1 save to v2 by adding current_level with the safe default."""
	var v2: Dictionary = v1.duplicate(true)
	v2["version"] = 2
	v2["current_level"] = "level_01"
	return v2


# ---------------------------------------------------------------------------
# Schema validation.
# ---------------------------------------------------------------------------

func _validate_save_dict(d: Dictionary) -> bool:
	"""Hand-rolled validator. Mirrors the Pydantic v2 SaveV2 schema."""
	if not d.has("version"):
		push_error("validate: missing 'version'")
		return false
	if not (d["version"] is int) or int(d["version"]) != CURRENT_VERSION:
		push_error("validate: 'version' not equal to current (" + str(CURRENT_VERSION) + ")")
		return false
	if not d.has("player_name") or not (d["player_name"] is String):
		push_error("validate: 'player_name' missing or wrong type")
		return false
	var name: String = d["player_name"]
	if name.length() < 1 or name.length() > 64:
		push_error("validate: 'player_name' out of length bounds")
		return false
	if not d.has("current_score") or not (d["current_score"] is int):
		push_error("validate: 'current_score' missing or wrong type")
		return false
	var score: int = int(d["current_score"])
	if score < 0 or score > 10_000_000:
		push_error("validate: 'current_score' out of range")
		return false
	if not d.has("current_level") or not (d["current_level"] is String):
		push_error("validate: 'current_level' missing or wrong type")
		return false
	var level: String = d["current_level"]
	if level.length() < 1 or level.length() > 128:
		push_error("validate: 'current_level' out of length bounds")
		return false
	return true
