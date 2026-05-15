# Mini-project — the full Godot save manager.
#
# Register this script as an autoload named ``SaveManager`` in Project Settings.
# Every scene can then call SaveManager.save_to_slot(0, dict) and
# SaveManager.load_from_slot(0) without instantiating anything.
#
# Features (mirror of save_schema.py on the Python side):
# - Two-bucket model: a meta file (settings) and per-slot run files.
# - Atomic write via DirAccess.rename (temp-file-plus-rename).
# - SHA-256 integrity tag computed via HashingContext.
# - Backup rotation: slot_NN.save -> slot_NN.save.prev on each successful write.
# - Schema versioning with the v1 -> v2 migration.
# - Hand-rolled validation mirroring Pydantic's role on the Python side.
# - Manual save (player-triggered) and autosave (engine-triggered).
#
# The on-disk format is identical to the Python side; a save written here
# round-trips through save_schema.py's loader and vice versa. The mini-project
# acceptance criterion G6 asserts this property.

extends Node

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------

const CURRENT_VERSION: int = 2
const SLOT_COUNT: int = 3
const AUTOSAVE_SLOT: int = SLOT_COUNT  # one extra slot beyond the manual range
const SAVE_DIR_NAME: String = "saves"  # under OS.get_user_data_dir()
const META_FILE_NAME: String = "meta.json"

# ---------------------------------------------------------------------------
# Signals.
# ---------------------------------------------------------------------------

signal save_completed(slot: int, success: bool)
signal load_completed(slot: int, success: bool)

# ---------------------------------------------------------------------------
# Public API: run-state slots.
# ---------------------------------------------------------------------------

func save_to_slot(slot: int, state: Dictionary) -> bool:
	"""Persist ``state`` to the given slot atomically.

	Returns true on success. On failure, push_error is called and the
	``save_completed`` signal is emitted with success=false.
	"""
	if slot < 0 or slot > AUTOSAVE_SLOT:
		push_error("save: slot out of range: " + str(slot))
		save_completed.emit(slot, false)
		return false

	var stamped: Dictionary = state.duplicate(true)
	stamped["version"] = CURRENT_VERSION

	if not _validate_save_dict(stamped):
		push_error("save: refusing to write invalid state")
		save_completed.emit(slot, false)
		return false

	var paths: Dictionary = _paths_for_slot(slot)
	var ok: bool = _write_atomic_with_rotation(paths, stamped)
	save_completed.emit(slot, ok)
	return ok


func autosave(state: Dictionary) -> bool:
	"""Convenience wrapper for the autosave slot."""
	return save_to_slot(AUTOSAVE_SLOT, state)


func load_from_slot(slot: int) -> Dictionary:
	"""Load and migrate the run state from the given slot.

	Returns the loaded dictionary on success, or {} if both the latest and
	previous backup are unreadable.
	"""
	if slot < 0 or slot > AUTOSAVE_SLOT:
		push_error("load: slot out of range: " + str(slot))
		load_completed.emit(slot, false)
		return {}

	var paths: Dictionary = _paths_for_slot(slot)
	var loaded: Dictionary = _load_with_fallback(paths)
	if loaded.is_empty():
		load_completed.emit(slot, false)
		return {}

	loaded = _migrate_to_latest(loaded)
	if not _validate_save_dict(loaded):
		push_error("load: loaded save fails validation; refusing to return")
		load_completed.emit(slot, false)
		return {}
	load_completed.emit(slot, true)
	return loaded


func slot_exists(slot: int) -> bool:
	if slot < 0 or slot > AUTOSAVE_SLOT:
		return false
	var paths: Dictionary = _paths_for_slot(slot)
	return FileAccess.file_exists(paths["latest"]) or FileAccess.file_exists(paths["previous"])


func delete_slot(slot: int) -> bool:
	if slot < 0 or slot > AUTOSAVE_SLOT:
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
# Public API: meta bucket.
# ---------------------------------------------------------------------------

func save_meta(settings: Dictionary, last_used_player_name: String) -> bool:
	"""Persist the meta bucket (settings + last-used name).

	The meta bucket has its own version field (currently 1) and lives in a
	separate file from the run slots. Corrupting one does not affect the
	other.
	"""
	var meta: Dictionary = {
		"version": 1,
		"settings": settings.duplicate(true),
		"last_used_player_name": last_used_player_name,
	}
	var path: String = _save_dir().path_join(META_FILE_NAME)
	var tmp: String = path + ".tmp"
	var enveloped: Dictionary = _envelope(meta)
	var blob: String = JSON.stringify(enveloped, "\t", true)

	var f: FileAccess = FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		push_error("save_meta: cannot open temp file")
		return false
	f.store_string(blob)
	f.close()

	var dir: DirAccess = DirAccess.open(path.get_base_dir())
	if dir == null:
		push_error("save_meta: cannot open save dir")
		return false
	var rename_err: int = dir.rename(tmp, path)
	if rename_err != OK:
		push_error("save_meta: rename failed err=" + str(rename_err))
		return false
	return true


func load_meta() -> Dictionary:
	"""Load the meta bucket. Returns {} if not present or invalid."""
	var path: String = _save_dir().path_join(META_FILE_NAME)
	if not FileAccess.file_exists(path):
		return {}
	var f: FileAccess = FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var blob: String = f.get_as_text()
	f.close()
	var parsed = JSON.parse_string(blob)
	if parsed == null or not (parsed is Dictionary):
		push_error("load_meta: invalid JSON")
		return {}
	var inner: Dictionary = _open_envelope(parsed)
	return inner


# ---------------------------------------------------------------------------
# Path helpers.
# ---------------------------------------------------------------------------

func _save_dir() -> String:
	var base: String = OS.get_user_data_dir().path_join(SAVE_DIR_NAME)
	var dir: DirAccess = DirAccess.open(OS.get_user_data_dir())
	if dir != null and not dir.dir_exists(SAVE_DIR_NAME):
		dir.make_dir(SAVE_DIR_NAME)
	return base


func _paths_for_slot(slot: int) -> Dictionary:
	var base: String
	if slot == AUTOSAVE_SLOT:
		base = _save_dir().path_join("slot_autosave.save")
	else:
		base = _save_dir().path_join("slot_%02d.save" % slot)
	return {
		"latest": base,
		"previous": base + ".prev",
		"temp": base + ".tmp",
	}


# ---------------------------------------------------------------------------
# Envelope (integrity).
# ---------------------------------------------------------------------------

func _canonical_string(payload: Dictionary) -> String:
	# JSON.stringify with sort_keys=true gives us deterministic bytes.
	return JSON.stringify(payload, "", true)


func _integrity_tag(payload: Dictionary) -> String:
	var canonical: String = _canonical_string(payload)
	var ctx: HashingContext = HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(canonical.to_utf8_buffer())
	var digest: PackedByteArray = ctx.finish()
	return "sha256:" + digest.hex_encode()


func _envelope(payload: Dictionary) -> Dictionary:
	return {"payload": payload, "integrity": _integrity_tag(payload)}


func _open_envelope(parsed: Dictionary) -> Dictionary:
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
		push_error("envelope: integrity mismatch")
		return {}
	return payload


# ---------------------------------------------------------------------------
# Atomic write and load.
# ---------------------------------------------------------------------------

func _write_atomic_with_rotation(paths: Dictionary, payload: Dictionary) -> bool:
	var enveloped: Dictionary = _envelope(payload)
	var blob: String = JSON.stringify(enveloped, "\t", true)

	# 1. Write to temp.
	var temp_file: FileAccess = FileAccess.open(paths["temp"], FileAccess.WRITE)
	if temp_file == null:
		push_error("save: cannot open temp file: " + paths["temp"])
		return false
	temp_file.store_string(blob)
	temp_file.close()

	# 2. Rotate latest -> previous.
	var save_dir: DirAccess = DirAccess.open(paths["latest"].get_base_dir())
	if save_dir == null:
		push_error("save: cannot open save dir")
		return false
	if FileAccess.file_exists(paths["latest"]):
		var rot_err: int = save_dir.rename(paths["latest"], paths["previous"])
		if rot_err != OK:
			push_error("save: rotation rename failed err=" + str(rot_err))
			return false

	# 3. Publish temp -> latest.
	var pub_err: int = save_dir.rename(paths["temp"], paths["latest"])
	if pub_err != OK:
		push_error("save: publish rename failed err=" + str(pub_err))
		return false
	return true


func _load_with_fallback(paths: Dictionary) -> Dictionary:
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
		print("SaveManager: loaded ", key, " from ", path)
		return payload
	push_error("load: no readable save in slot")
	return {}


# ---------------------------------------------------------------------------
# Migration table.
# ---------------------------------------------------------------------------

func _migrate_to_latest(parsed: Dictionary) -> Dictionary:
	var current: Dictionary = parsed.duplicate(true)
	if not current.has("version"):
		current["version"] = 1
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
	if from_version == 1:
		return _migrate_v1_to_v2(d)
	return {}


func _migrate_v1_to_v2(v1: Dictionary) -> Dictionary:
	# Adds current_level with the safe default. Mirrors save_schema.py exactly.
	var v2: Dictionary = v1.duplicate(true)
	v2["version"] = 2
	v2["current_level"] = "level_01"
	return v2


# ---------------------------------------------------------------------------
# Schema validation.
# ---------------------------------------------------------------------------

func _validate_save_dict(d: Dictionary) -> bool:
	"""Verify the dict matches the v2 schema. Mirrors save_schema.py's SaveV2."""
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
	if not d.has("session_start_timestamp") or not (d["session_start_timestamp"] is int):
		push_error("validate: 'session_start_timestamp' missing or wrong type")
		return false
	if int(d["session_start_timestamp"]) < 0:
		push_error("validate: 'session_start_timestamp' is negative")
		return false
	if not d.has("highest_score_this_session") or not (d["highest_score_this_session"] is int):
		push_error("validate: 'highest_score_this_session' missing or wrong type")
		return false
	var high: int = int(d["highest_score_this_session"])
	if high < 0 or high > 10_000_000:
		push_error("validate: 'highest_score_this_session' out of range")
		return false
	if not d.has("current_level") or not (d["current_level"] is String):
		push_error("validate: 'current_level' missing or wrong type")
		return false
	var level: String = d["current_level"]
	if level.length() < 1 or level.length() > 128:
		push_error("validate: 'current_level' out of length bounds")
		return false
	return true
