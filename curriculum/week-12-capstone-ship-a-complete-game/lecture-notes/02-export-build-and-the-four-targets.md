# Lecture 2 — Export, build, and the four targets

Yesterday's lecture was about scope — what to build and what not to build. Today's lecture is about getting the thing you have built off your development machine and into a folder a stranger can download. This is the moment in the week when a project stops being "a game I am making" and becomes "a game I have made." The transition is mechanical (the steps are the same every time) and emotional (it is the first time the project leaves your control). Both deserve respect.

The pipeline is *Godot Editor → export-templates → export-presets.cfg → four shipped binaries*. The four binaries target HTML5 (the web), Windows (the desktop majority), macOS (the indie creator majority — your peers, your professors, your friends), and Linux (the open-source storefront browsers). Three of the four are double-clickable; the macOS one needs an unquarantine command that you document on the itch.io page. None of the four are signed — code-signing is a separate, paid pipeline for the commercial release. We will name it, we will know what we are skipping, and we will skip it cleanly.

The canonical reference for this lecture is the **Godot 4 export documentation** at [docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html](https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html) and the **HTML5-specific deep dive** at [docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html). Both are linked in `resources.md`. Read them once before today's lecture and once before Thursday's export pass; the exports are the only step of the week that the engine documentation is the *only* authoritative source for.

## Installing the export templates

Export templates are platform-specific runtime binaries that the engine packs with your project to produce the shipped executable. The Godot editor does not ship with them — they are a separate download because they are large (~1.5 GB total) and platform-specific. The flow is:

1. Open the Godot editor.
2. *Editor* → *Manage Export Templates* → *Download and Install*.
3. The dialog downloads the templates for your editor's version (e.g. `Godot_v4.2.2-stable_export_templates.tpz`) and unpacks them to the platform-specific cache directory:
   - On macOS: `~/Library/Application Support/Godot/export_templates/4.2.2.stable/`
   - On Linux: `~/.local/share/godot/export_templates/4.2.2.stable/`
   - On Windows: `%APPDATA%\Godot\export_templates\4.2.2.stable\`
4. Wait for the green check. Close the dialog.

The dialog has two paths — *Download* (default; pulls from `downloads.tuxfamily.org` or the configured mirror) and *Install from file* (pick a `.tpz` you downloaded separately). The file path is useful on a metered connection or in a country where the default mirror is slow. Both produce identical results.

The single most common Monday mistake is to skip this step on the assumption that the editor will prompt for it later. The editor *does* prompt — but it prompts on *Thursday at 3 pm when you are trying to export*. The download is 1.5 GB; the metering and the prompt-handling and the version check eat 30 minutes. Do it Monday. Do it on the cohort wifi. Do it once.

The templates are versioned to the editor. If you upgrade the editor mid-week (a 4.2.2 → 4.3.0 jump), reinstall the templates for the new version. The old templates remain on disk and the editor uses the matching version automatically; there is no penalty to keeping both.

## The four export presets

The export targets we care about for the capstone are HTML5, Windows Desktop, macOS, and Linux/X11. Godot 4 ships export presets for each. Open *Project* → *Export* to see the dialog.

### HTML5 (web)

The web target is the **primary** capstone target. It produces a folder containing `index.html`, a `.wasm` (the engine runtime, ~25 MB unstripped), a `.js` shim (~150 KB), a `.pck` (your assets and scripts), and a few support files (`favicon.png`, `audio_worklet.js` if your project uses audio). The user runs the game in a browser by navigating to the URL; no install, no antivirus warning, no gatekeeper bypass.

Add the preset:

1. *Project* → *Export* → *Add...* → *HTML5*.
2. Name it *Web* (or leave the default).
3. **Custom HTML shell:** Leave blank for the default. You can write a custom `index.html` later for a branded loading screen; for the capstone week, the default shell is fine.
4. **Export path:** `dist/web/index.html`. Create the `dist/web/` folder first.
5. **Variant: Threads enabled:** *Off* for itch.io. itch.io's HTML5 hosting does not by default serve the cross-origin isolation headers (`Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp`) that `SharedArrayBuffer` needs. Threads-on builds will fail to launch. Threads-off builds run on a single thread, which is fine for a one-week capstone. The itch.io HTML5 docs at [itch.io/docs/creators/html5](https://itch.io/docs/creators/html5) cover the threads-on flag the platform recently added; for the capstone, default off is safest.
6. **VRAM Texture Compression / For mobile:** Off, unless you specifically target mobile browsers. Leaving it on doubles the export size for no desktop benefit.
7. **HTML / Canvas Resize Policy:** *Adaptive*. The canvas resizes to fit the itch.io iframe (typically 960x540 or 1280x720).
8. **HTML / Focus Canvas on Start:** *On*. The game accepts keyboard input on launch.
9. **Progressive Web App:** *Off*. PWA is for app-like installs; the capstone is not.
10. **Encryption:** Leave blank. Encryption is a commercial-release feature; for a free itch.io release, the PCK does not need encrypting.

Run the export with the **Export Project** button (not *Export PCK/Zip*, which is for advanced flows). The output is the `dist/web/` folder. Zip it (`zip -r dist/web.zip dist/web`); the zip is what you upload to itch.io.

The HTML5 export has three pitfalls that catch first-time exporters:

- **Audio does not play until the user clicks.** Browsers gate `AudioContext.resume()` on a user gesture. The default Godot shell has a *Start Game* button that satisfies the gesture; if you swap to a custom shell, make sure the shell still requires a click before the engine starts.
- **The wasm payload is huge on the wire.** A typical Godot HTML5 build is 25-30 MB. Gzipped, it is 8-12 MB; brotli-compressed, 6-9 MB. itch.io serves gzip automatically, so the user only sees the compressed size. Do not pre-gzip the files yourself; itch.io's CDN does it.
- **Fonts load asynchronously.** If your game uses a custom font, the first frame may render in a fallback font while the custom font loads. Either preload the font (in `index.html`) or accept a brief flash. The default shell handles this for most fonts.

### Windows Desktop

The Windows target produces a `.exe` plus a `.pck`. Default behaviour bundles them in the same folder; the `.exe` looks for the `.pck` by name on launch.

Add the preset:

1. *Project* → *Export* → *Add...* → *Windows Desktop*.
2. Name it *Windows*.
3. **Export path:** `dist/windows/MyGame.exe`. The `.pck` is co-located automatically.
4. **Embed PCK:** *On* if you want a single-file `.exe` (the PCK is appended to the EXE and read at runtime). *Off* if you want two files. For itch.io, single-file is convenient; the user downloads one `.exe` and runs it.
5. **Application / Icon:** Point at a `.ico` file with multi-resolution embedded sizes (16x16, 32x32, 48x48, 256x256). A free `.ico` builder is [icoconvert.com](https://icoconvert.com); the input is a 1024x1024 PNG.
6. **Application / Console Wrapper:** *Off*. The console wrapper opens a black console window alongside the game on launch; that is for development, not shipped builds.
7. **Code Signing:** Off (no certificate available). Add a note to the itch.io page about SmartScreen.
8. **Embed PCK / Custom Template:** Leave default.

Export. The output is `dist/windows/MyGame.exe` (single-file if embedded) or `MyGame.exe` plus `MyGame.pck` (two files). Zip both into `windows.zip` for itch.io.

The Windows target has one major pitfall: **SmartScreen warns the user on first launch** because the `.exe` is unsigned. The warning is "Windows protected your PC" with a *Don't run* button as the prominent action. Users have to click *More info* → *Run anyway* to launch. Code-signing eliminates the warning, but a code-signing certificate from a recognised CA (Sectigo, DigiCert, Comodo) costs $250-400/year and requires identity verification. For a one-week free capstone, the warning is acceptable; add a sentence to the itch.io page so users know what to do. The first 20-50 launches across all users earn the binary enough reputation that Microsoft Defender stops warning; this is called *SmartScreen reputation* and it is the de facto way unsigned indie binaries operate.

### macOS

The macOS target produces a `.app` bundle — a directory that the Finder displays as a single icon. Inside the bundle is the executable, the PCK, the `Info.plist`, and an icon. On the Internet, the bundle is shipped inside a `.zip` (which preserves the bundle structure across cross-platform downloads).

Add the preset:

1. *Project* → *Export* → *Add...* → *macOS*.
2. Name it *macOS*.
3. **Export path:** `dist/macos/MyGame.app`. The `.app` is created as a folder.
4. **Application / Icon:** A `.icns` file (multi-resolution, macOS-native). Build with [cloudconvert.com/png-to-icns](https://cloudconvert.com/png-to-icns) from a 1024x1024 PNG.
5. **Application / Bundle Identifier:** A reverse-DNS name. *com.yourname.mygame*. Apple-style. The identifier must be unique to your build; pick something now and never change it.
6. **Architecture:** *Universal* (Apple Silicon + Intel x86_64). The universal binary is twice the size but runs everywhere. For a free itch.io release, the convenience is worth the size cost.
7. **Code Signing:** *None*. Signing requires an Apple Developer account ($99/year) and provisioning certificates. Out of scope for week 12.
8. **Notarization:** *None*. Same reason. Notarization requires signing as a prerequisite.

Export. The output is `dist/macos/MyGame.app/` (a folder Finder shows as a single file). Zip the folder (`zip -r dist/macos.zip dist/macos/MyGame.app`); upload the zip to itch.io.

The macOS target has the **biggest** pitfall of the four. Unsigned `.app` bundles downloaded from the Internet trigger Gatekeeper's quarantine, and **Gatekeeper refuses to open them** on macOS 10.15 (Catalina) and later. The error message is "MyGame.app cannot be opened because the developer cannot be verified." The user is then prompted to *Move to Trash*. There is no obvious "open anyway" button.

The bypasses are:

1. **Finder right-click → Open.** The user navigates to the `.app`, right-clicks, picks *Open*, then clicks *Open* again in the dialog. This bypasses Gatekeeper for the specific binary on the specific machine.
2. **Terminal:** `xattr -dr com.apple.quarantine /path/to/MyGame.app`. This removes the quarantine attribute, after which the binary launches normally.

Document *both* methods on the itch.io page. Most users will pick method 1; the technical minority who feel uncomfortable with right-click → Open will appreciate method 2. The Godot macOS export documentation at [docs.godotengine.org/en/stable/tutorials/export/exporting_for_macos.html](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_macos.html) covers the full notarization workflow if you decide to graduate to a paid commercial macOS release.

### Linux / X11

The Linux target produces an `.x86_64` ELF binary. Most Linux distributions launch it on double-click; some require the executable bit set (`chmod +x MyGame.x86_64`) before double-clicking.

Add the preset:

1. *Project* → *Export* → *Add...* → *Linux/X11*.
2. Name it *Linux*.
3. **Export path:** `dist/linux/MyGame.x86_64`.
4. **Embed PCK:** *On* for single-file delivery; *Off* if you want a side-car `.pck`.
5. **Architecture:** `x86_64`. ARM64 Linux is rare on desktop; do not target it for the capstone.
6. The remaining fields are mostly defaults.

Export. The output is `dist/linux/MyGame.x86_64`. Mark it executable (`chmod +x dist/linux/MyGame.x86_64`); the export does *not* preserve the bit on macOS hosts. Zip the file (`zip dist/linux.zip dist/linux/MyGame.x86_64`); upload to itch.io.

Linux has the fewest gotchas of the four. The one pitfall: **the executable bit is sometimes lost in transit** through certain Windows-hosted file systems and certain unzip tools. Add a note to the itch.io page: "If double-click does not launch the game, run `chmod +x MyGame.x86_64` from a terminal then `./MyGame.x86_64`." Power users will do it without thinking; first-time Linux users will appreciate the explicit instruction.

## The `export_presets.cfg` file

Adding presets in the editor writes them to a file in the project root called `export_presets.cfg`. The file is plain INI-style text. **Commit it to git.** Without it, the next time you open the project on another machine (or after a re-clone), you redo every preset by hand. The file is tens of kilobytes; it diffs cleanly; it belongs in version control.

A truncated example of the file's structure:

```ini
[preset.0]
name="Web"
platform="Web"
runnable=true
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="dist/web/index.html"

[preset.0.options]
custom_template/debug=""
custom_template/release=""
variant/extensions_support=false
variant/thread_support=false
vram_texture_compression/for_desktop=true
vram_texture_compression/for_mobile=false
html/export_icon=true
html/custom_html_shell=""
html/head_include=""
html/canvas_resize_policy=2
html/focus_canvas_on_start=true
html/experimental_virtual_keyboard=false
progressive_web_app/enabled=false
encryption/encrypted=false

[preset.1]
name="Windows"
... and so on for all four presets
```

The file is not secret. The encryption keys, if any, *are* sensitive — but for a free itch.io capstone, no encryption is used and the file is safe to commit publicly. The exercise `exercise-04-export-config-check.py` in this week's folder parses an `export_presets.cfg` and verifies that all four target presets are present; running it before Thursday's export ensures you have not silently dropped a target.

## Debug vs release builds

Each preset has a *Runnable* checkbox in the editor and a separate *Export with Debug* option in the export dialog. The difference:

- **Debug build.** Includes the engine's debug runtime, prints `_print_debug` lines, opens a console window on launch (on Windows), allows the editor to attach a debugger. Useful for the *playable prototype* gate on Tuesday. Larger binary. Slower.
- **Release build.** No debug runtime, no console, no debugger hooks. Smaller binary. Faster. The shipped artefact.

The week-12 shipped builds are *release* builds. The Tuesday playable prototype is fine as debug. Thursday's export pass should produce four release binaries; if you ship a debug build by accident, the user sees console output and the binary is larger than necessary. Set the export-dialog *Export with Debug* checkbox to *off* before clicking *Export Project*.

## Per-platform binary sizes — what to expect

A "small" Godot 4 capstone exports to roughly the following sizes. Your mileage varies with assets and embedded fonts, but the order of magnitude holds.

| Target  | Engine runtime | Your assets | Total binary | Compressed (zip) |
|---------|---------------:|------------:|-------------:|-----------------:|
| HTML5   |        ~25 MB  |       5 MB  |       30 MB  |          ~12 MB  |
| Windows |        ~50 MB  |       5 MB  |       55 MB  |          ~25 MB  |
| macOS   |        ~70 MB  |       5 MB  |       75 MB  |          ~30 MB  |
| Linux   |        ~55 MB  |       5 MB  |       60 MB  |          ~25 MB  |

If your binary is much larger than this, you have probably included asset source files (PSDs, RAW audio, source `.aseprite` files) in the export. Check the *Export Filter* in the preset; the default is *all_resources*, which is correct, but the *Include/Exclude* filters can over-include. Common surplus directories: `assets/source/`, `art/raw/`, `audio/wav/`. Move those out of the project, or add them to the exclude filter.

itch.io's free tier has a **1 GB per-file limit**. None of the four capstone targets approaches that; if yours does, the build is over-asseted.

## The future paid targets — survey

This week we ship to free targets. The future paid targets exist and are worth naming briefly so you know what the migration path looks like.

### Steam Direct

Valve's storefront onboarding fee is **$100 USD one-time per app**, refundable after the app accrues $1,000 in lifetime adjusted gross revenue. The fee is non-trivial for a hobbyist; it is a near-rounding-error for a commercial release. The Steam onboarding documentation at [partner.steamgames.com/steamdirect](https://partner.steamgames.com/steamdirect) covers the legal forms (W-9 for US developers, W-8BEN for international), the tax forms, and the bank-account-on-file requirement.

The Steam **revenue share** is 30% of gross sales, reducing to 25% above $10M lifetime gross and 20% above $50M lifetime gross. For an indie game, 30% is what you pay; for a successful indie game, 30% is still what you pay. Compared to itch.io's 0-10% (creator-adjustable) on paid sales, Steam's share is heavy. Steam pays for the share with audience — Steam's user base is approximately 130 million monthly active accounts; itch.io's is approximately 5-10 million. A Steam launch is roughly an order of magnitude wider audience at three times the revenue share.

The Steamworks integration — Steam Cloud, achievements, the Build Pipeline, Steam Input, the Big Picture overlay, the storefront's tagging system — is a multi-week effort on top of a finished game. Plan for it as a *Week 13-16* sized commitment if you decide to commercialise the capstone.

We do not ship to Steam this week. We know it exists. The migration plan from a shipped itch.io build to a Steam Direct release is the subject of *challenge-02* in this week's folder.

### Apple App Store Connect

The Apple Developer Program is **$99 USD per year**. The iOS build pipeline requires Xcode on a Mac, an Apple Developer account, code-signing certificates, provisioning profiles, and TestFlight for beta builds. The revenue share is **15% for the first $1M/year** (under Apple's small-business programme) or **30% standard**. The macOS App Store uses the same toolchain and revenue share.

The Godot iOS export documentation at [docs.godotengine.org/en/stable/tutorials/export/exporting_for_ios.html](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_ios.html) covers the export from Godot's side. The Apple side — provisioning, certificates, TestFlight, App Store Connect review queues — is its own learning curve, comparable in time to the entire week-12 capstone.

Out of scope for week 12. On the roadmap for projects whose mechanics are touch-friendly.

### Google Play Console

Google's developer fee is **$25 USD one-time lifetime**. The Android build pipeline runs through the Godot Android export plus a JDK plus the Android SDK plus a signing keystore. The revenue share is **30% standard, 15% for small developers** (defined as those earning under $1M/year).

The Godot Android export documentation at [docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html) is the canonical reference. The Android Studio dependency and the keystore management are the highest-friction parts of the pipeline.

Out of scope for week 12. On the roadmap.

### Other storefronts worth knowing

Three additional free or near-free storefronts exist and are worth naming:

- **GameJolt** ([gamejolt.com](https://gamejolt.com)). Free upload. Smaller audience than itch.io; younger demographic. Worth a cross-post.
- **Newgrounds** ([newgrounds.com](https://newgrounds.com)). Free upload. HTML5 only. Long-running indie scene with a dedicated audience.
- **OpenProcessing** ([openprocessing.org](https://openprocessing.org)). p5.js / Processing only, so not a Godot fit; mentioned for completeness because some capstone students come from a creative-coding background and want to know.

Itch.io remains the recommended primary target for week 12 because (a) it natively supports HTML5 embedding with no per-platform binaries, (b) the pricing model is the most creator-friendly of the major storefronts, and (c) the page customisation is the deepest, which matters for the marketing-page side of the capstone.

## A worked example — exporting *Frog Cross*

To make the export concrete, here is a stepwise walk through Thursday's export of the *Frog Cross* example from yesterday's lecture.

```text
Thursday 10:00  - Open Godot.
                - Editor -> Manage Export Templates -> confirm 4.2.2 stable installed.
                  (Installed Monday; nothing to do.)

Thursday 10:05  - Project -> Export.
                - Add preset Web, configure as documented above, export to dist/web/.
                - Verify dist/web/ contains index.html, index.wasm, index.pck, index.js.
                - Wall-clock: 6 seconds. Output size: 32 MB.

Thursday 10:08  - Add preset Windows, configure, export to dist/windows/FrogCross.exe.
                - Verify dist/windows/FrogCross.exe is a single ~54 MB file.
                - Wall-clock: 8 seconds.

Thursday 10:11  - Add preset macOS, configure, export to dist/macos/FrogCross.app.
                - Verify dist/macos/FrogCross.app is a folder, opens in Finder as a single icon.
                - Wall-clock: 11 seconds. Output size: ~73 MB unzipped.

Thursday 10:14  - Add preset Linux, configure, export to dist/linux/FrogCross.x86_64.
                - chmod +x dist/linux/FrogCross.x86_64
                - Wall-clock: 7 seconds. Output size: ~58 MB.

Thursday 10:18  - cd dist
                - zip -r web.zip web
                - zip windows.zip windows/FrogCross.exe
                - zip -r macos.zip macos/FrogCross.app
                - zip linux.zip linux/FrogCross.x86_64
                - Four .zip files. 12 + 25 + 30 + 25 = 92 MB total. Well under itch.io's 1 GB limit.

Thursday 10:22  - Quick local test:
                - cd dist/web && python3 -m http.server 8000
                - Open localhost:8000 in Chrome. Game loads. Plays for 30 seconds. OK.
                - Open dist/windows/FrogCross.exe on a Windows VM (or a friend's laptop). OK.
                - Open dist/macos/FrogCross.app from Finder with right-click -> Open. OK.
                - Run dist/linux/FrogCross.x86_64 in WSL or a Linux VM. OK.

Thursday 10:35  - All four targets verified. Ready for tomorrow's itch.io upload.
```

That is a 35-minute Thursday export pass. The students who installed the export templates on Monday do this in 35 minutes. The students who install them on Thursday at 10:00 sharp do it in two hours after the download finishes.

## Summary, end of lecture

Tomorrow's lecture covers the itch.io page, the 30-second trailer, the credits, and the post-ship checklist. By Friday evening the four shipped binaries from today's export pass are uploaded, the page is public, and the trailer is embedded. By Saturday night the shipped build is on the public internet. By Sunday the retrospective is written.

The pipeline is mechanical. The four targets follow the same template. The friction is real but small. The discipline is to *do the export on Thursday, not on Saturday at midnight* — the gap is the slack you will need if a target unexpectedly fails. Saturday-night exports are the single biggest predictor of a missed capstone deadline. Thursday exports are the cheapest insurance you buy this week.
