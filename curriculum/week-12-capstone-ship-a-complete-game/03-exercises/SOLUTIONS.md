# Exercise solutions — Week 12

The exercises this week are deliberately *meta* — they validate the *artefacts* of the shipping process rather than the gameplay code itself. The capstone is the playable artefact; the exercises are the gates that prevent the most common Sunday-morning embarrassments. The five exercises pair to the three lectures as follows:

- Exercises 1 (scope sheet) pairs to Lecture 1.
- Exercises 2 (credits audit), 3 (page validator), and 5 (credits roll) pair to Lecture 3.
- Exercise 4 (export config check) pairs to Lecture 2.

Run all five before any milestone gate. The recommended cadence is:

- Monday end-of-day — run exercise 1 against `mini-project/scope_sheet_template.md` with your fields filled in.
- Wednesday end-of-day — run exercise 2 against the in-progress `CREDITS.md` and re-run as you add assets.
- Thursday end-of-day — run exercise 4 against the `export_presets.cfg` in your capstone project.
- Friday end-of-day — run exercise 3 against your drafted `page.md` before pasting into the itch.io editor.
- Saturday — re-run all four Python exercises plus the GDScript exercise 5 in the live project.

## Exercise 1 — Validate a Monday scope sheet against a schema

The point of the exercise is to give you a *mechanical* check against the ten fields prescribed in Lecture 1. The capstone graders will accept scope sheets in any format, but the empirical data is that students whose Monday scope sheet passes this validator are 70%+ likely to ship by Sunday, and students whose sheet fails it are 40% likely to be in a Wednesday-afternoon emergency rescope.

Key decisions in the solution code:

- The `ScopeSheet` dataclass has the ten fields named in Lecture 1; the parser tolerates the same keyed-section format that `mini-project/scope_sheet_template.md` uses.
- The validator rejects pitches shorter than 20 characters (the "PITCH: A game." failing fixture is the smoke test for this). 20 characters is roughly the minimum length for a pitch that names a *who*, a *verb*, and a *constraint*; anything shorter is missing at least one.
- The validator rejects verbs longer than four words (the "do many several various interesting things" failing fixture). A verb is one action; if it takes more than four words to name, it is a *theme* and not a verb. Lecture 1 covers this.
- The validator rejects subsystem-used lists shorter than three. The capstone is the integration test for Weeks 1-11; using fewer than three subsystems means the capstone is not actually leaning on the toolbox.
- The validator rejects asset lists shorter than four or longer than fifteen. Four is the floor (player, obstacle, music, font); fifteen is the ceiling (any more and the scope is too big for a week).

Common student errors on this exercise:

- Forgetting to indent bullet items under a list field. The parser only collects bullets that begin with `-`; indented bullets work, top-level bullets work, but a bullet without the leading dash does not. The mini-project template shows the canonical indent.
- Putting the cuts log on Monday with one entry. The cuts log is *expected* to grow through the week; one entry is fine on Monday. The validator does not impose a minimum on the cuts log because Monday's cuts-log can legitimately be empty (you have not yet cut anything).

## Exercise 2 — Audit a CREDITS.md against the asset-licensing rules

The exercise enforces Lecture 3's three rules: every asset has a licence, every CC-BY asset has an author, and CC-BY-NC is rejected if the build is marked for commercial release.

Key decisions in the solution code:

- The `Asset` dataclass has four fields: `name`, `licence`, `author`, `url`. The parser uses a regex on the bullet line plus a lookahead for an indented URL.
- The known-licence set covers the five CC family licences (CC0, CC-BY, CC-BY-SA, CC-BY-NC, CC-BY-NC-SA, CC-BY-ND), the Open Font License (OFL — used by Press Start 2P and most Google Fonts), MIT (most open-source code), Apache, GPL, Public Domain, and "Self-drawn"/"Self-made" for assets you made yourself.
- The `commercial_intent=False` flag is the default. A free itch.io ship is not commercial, so CC-BY-NC assets warn rather than error. When you re-run the validator before a Steam Direct migration (challenge 02), pass `commercial_intent=True` and the validator will error on every CC-BY-NC entry.
- The CC-BY-SA warning is informational by default. The licence is *legally* fine for a free itch.io release but *contaminating* if the build's code is ever released under a different licence (because CC-BY-SA derivatives must be CC-BY-SA). Lecture 3 covered this; the warning is a reminder.

Common student errors:

- Listing an asset with the licence inline but without the author. The validator catches this with the "CC-BY requires an author attribution" error. The fix is to add `by "AuthorName"` to the bullet line. Quotation marks around the author name are tolerated either way.
- Listing a self-drawn asset without a licence. The "Self-drawn" or "Self-made" tags are recognised as licences; without them, the validator reports "licence missing or unrecognised". Add `Self-drawn` (or `CC0` if you wish to release it publicly under CC0) to the line.

## Exercise 3 — Validate a page.md against the itch.io page checklist

The exercise is the Friday-evening gate before pasting the drafted page into the itch.io editor. The validator covers the twelve parts named in Lecture 3 and flags the common omissions (no banner, fewer than three screenshots, body too short, missing controls or credits section).

Key decisions:

- The parser tolerates both keyed-frontmatter style (`BANNER:`, `THUMBNAIL:`, etc.) and standard Markdown headings (`# Title`, `## Controls`).
- The tagline is the *first* paragraph after the title. The body paragraphs are everything after that until a `## Section` heading.
- The screenshot count is bounded between three and five. Three is the floor — fewer screenshots and the page reads as "I rushed this." Five is the ceiling — more screenshots and the page reads as padded.
- The body paragraph count is bounded between two and five. Two is the floor; five is the ceiling. The validator flags both ends.
- The trailer URL must point to YouTube or Vimeo. A bare MP4 link will fail; the trailer has to be on a hosting platform itch.io's embed system recognises.

Common student errors:

- Forgetting the `PRICE: Free` line. Without it, itch.io defaults to a fixed-price draft with `$0`, which displays as "Buy Now $0" instead of "Download for Free". The validator catches this.
- Forgetting the `## Credits` section. The capstone rubric requires credits; an itch.io page without them is a failed audit.
- Listing too many screenshots. The cap is five; ten screenshots is a yellow flag for the rubric and the validator flags it.

## Exercise 4 — Parse export_presets.cfg and verify four targets

The exercise is the Thursday-evening gate after the export pass. It verifies all four targets are present, none of them have empty export paths, none of them have encryption enabled (which would lock you out of the build), and the HTML5 preset has threads disabled.

Key decisions:

- The parser is a small hand-written INI-style reader because `configparser` from the stdlib trips on Godot's nested-option section headers (`[preset.0.options]`). The hand-written parser handles both `[preset.N]` and `[preset.N.options]` correctly.
- The "missing target" check uses the Godot platform names exactly as the editor writes them (`Web`, `Windows Desktop`, `macOS`, `Linux/X11`). Students sometimes hand-edit the file and use shorter names; the validator catches the mismatch.
- The threads-disabled check on the Web preset is the most-overlooked Lecture 2 gotcha. itch.io's free HTML5 hosting does not serve the cross-origin isolation headers that threads-on builds need. Threads-on Web builds fail to launch on itch.io. The validator catches this on Thursday so you do not discover it on Sunday morning during the post-upload smoke test.
- The encryption check is a guard against accidental commercial-build settings. The default in Godot is encryption=off; if you turned it on while exploring, the validator reminds you to turn it off before exporting.

Common student errors:

- Editing the file by hand and breaking the section-header format. The parser is strict on the `[preset.N]` and `[preset.N.options]` pattern. Edit through the Godot editor whenever possible.
- Naming the Web preset something other than `Web` (e.g. `HTML5`). The Godot editor names it `Web` in 4.2+; older tutorials and older Godot versions called it `HTML5`. The validator looks for the platform name, not the preset name, so renaming is safe.

## Exercise 5 — The credits-roll generator (GDScript)

The exercise wires the single source of truth (`CREDITS.md`) to the in-game credits roll. The roll renders during the capstone's title-screen idle or after game-over.

Key decisions:

- The parser reads the file with `FileAccess.open(path, FileAccess.READ)` and `get_as_text()`. The path defaults to `res://CREDITS.md`. The exercise's `_placeholder_credits()` provides a fallback if the file is missing — useful during early-week development before the credits file is written.
- The cleaner strips bold markers (`**...**`) from bullet lines because `Label` nodes do not render Markdown. If you use a `RichTextLabel` instead, you can keep the markup; the exercise uses a plain `Label` to minimise dependencies.
- The scroll is driven by `Tween.tween_property` on the label's `position:y`. The duration scales with the number of lines so a long credits list does not blur past too fast.
- The exercise exposes a `render_text_only(path)` function for headless testing. The mini-project's QA suite calls this function to verify the credits parser produces sensible output without instantiating a full scene.

Common student errors:

- Putting `CREDITS.md` at the wrong path. The exercise looks for `res://CREDITS.md` (the project root). If you placed it under `res://docs/CREDITS.md`, pass that path to `render_text_only`.
- Forgetting that GDScript's `String.split("\n")` returns a `PackedStringArray`, not a `String[]`. The two are mostly interchangeable but a typed annotation of `Array[String]` will fail; use `PackedStringArray` as the exercise does.
- Using a `RichTextLabel` and getting confused when the bold markers stop rendering. Either keep `Label` (and let the cleaner strip the markers) or switch to `RichTextLabel` and use `[b]...[/b]` BBCode instead of `**...**`.

## Running everything in one pass

A Saturday-morning "run all gates" pass looks like:

```bash
# From the week-12 folder:
cd exercises
python3 exercise-01-pitch-and-scope-sheet.py
python3 exercise-02-asset-license-audit.py
python3 exercise-03-itch-page-validator.py
python3 exercise-04-export-config-check.py
# (Then from your capstone Godot project's root:)
godot --headless --script /path/to/exercise-05-credit-line-generator.gd
```

If all five print `OK` (or render a sensible credits roll), the capstone is past the artefact gates and the next step is the post-ship checklist from Lecture 3.

A failing exercise is not a failing week — it is an early warning. The exercise tells you which artefact needs a 10-minute fix before upload. The students who skip the exercises and ship anyway are the same students whose itch.io page has the SmartScreen issue undocumented, the macOS Gatekeeper bypass missing, and the credits half-attributed. The exercises take twenty minutes total to run; they save hours of post-ship triage.
