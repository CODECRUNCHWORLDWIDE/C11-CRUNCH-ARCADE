# Lecture 1 — The Game Loop and Why It Exists

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can write the bare-bones game loop in Pygame from memory, explain why it must look the way it does, and articulate why a game is not a script.

If you only remember one thing from this lecture, remember this:

> **A game is a loop, not a function.** A script runs top to bottom and ends. A game starts a loop and runs that loop, sixty times a second, until the player quits. Every game ever shipped — Pong, Tetris, Elden Ring — is at heart that loop.

---

## 1. Why a script is not enough

You have been writing scripts your whole programming life. A script is a program that does some work and exits. Most data-processing, automation, and CLI tooling is this shape.

A game is not that shape. A game has to keep responding to the player, forever, sixty times a second. If you wrote a game as a script, it would look like this:

```python
print_title_screen()
wait_for_player_to_press_start()
draw_player()
# now what?
```

Now what? You'd want to *also* read input, *and* update the world, *and* redraw — and you want to do that over and over until the player closes the window. So you wrap it all in a loop:

```python
while running:
    handle_input()
    update_world()
    render()
```

That is **the game loop**. Every game has one. Engines hide it from you — Unity has `Update()`, Godot has `_process()`, Unreal has `Tick()` — but underneath each of those engines is a `while` loop that does exactly the three steps above, in that order.

Pygame does not hide the loop. You write it yourself. That is great for learning and slightly annoying for production. We are here to learn, so it is great.

---

## 2. The triple — input, update, render

The three steps of a game loop are called the **input → update → render** triple. Some books call it "process input, update game state, draw the world." Same thing.

```
┌────────────────────────────────────────────────────┐
│                                                    │
│   ┌─────────┐    ┌─────────┐    ┌──────────┐       │
│   │  INPUT  │ →  │  UPDATE │ →  │  RENDER  │ ──┐   │
│   └─────────┘    └─────────┘    └──────────┘   │   │
│        ▲                                        │   │
│        └────────────────────────────────────────┘   │
│                                                    │
└────────────────────────────────────────────────────┘
```

### The order is not optional

Why must input come first? Because update needs to know what the player just did. If you update first and read input second, the update is based on **stale input from the previous frame**. The lag is exactly one frame — about 16 ms at 60 fps — which is small but accumulates. Speed-runners and rhythm-game players can feel a single frame of lag. So can your tester, even if they can't name it.

Why must render come last? Because render presents the world *as it is right now*. If you render first and update after, you are presenting last frame's world. That is also a one-frame lag, and it shows up as "the bullet visually leaves the gun a frame after I pulled the trigger."

The order is **input → update → render**. Memorise it. Tattoo it.

### A concrete example: WASD movement

A player presses `D` to move right. What has to happen in one frame:

1. **Input.** You ask "is `D` pressed?" The answer is yes.
2. **Update.** Because `D` is held, you increase the player's `x` by some amount. The player's logical position is now further right.
3. **Render.** You draw the player at the new `x`. The screen shows the player one step further right.

Reverse render and update and you draw the player at the *old* position, then update the position, and the player never visually moves until the next frame. Reverse input and update and the move you process this frame is based on whether `D` *was* pressed last frame, not whether it is pressed now.

It sounds pedantic. It is not. Every game-feel complaint about "input feels laggy" traces back to either this ordering, or the related v-sync / present-time issue we'll touch on at the end.

---

## 3. The minimum-viable Pygame loop

The shortest correct Pygame program is roughly this. Type it out. Do not copy-paste.

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
running = True

while running:
    # 1. Input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Update
    # (nothing to update yet)

    # 3. Render
    screen.fill((20, 20, 30))
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
```

That is **17 lines** and a complete game. Let's read it.

### `pygame.init()`

Initialises every Pygame subsystem — display, mixer, font, events. You call this once at the top. If you don't, the first time you call `pygame.display.set_mode()` you'll get a polite-ish error.

### `pygame.display.set_mode((800, 600))`

Creates the window and returns its **Surface** — the rectangle of pixels you draw into. 800×600 is fine for learning; we'll go larger later. The `Surface` Pygame returns is the back-buffer; we draw to it, then flip it onto the screen.

### `pygame.time.Clock()`

A small object that tracks frame timing. We'll call `.tick(60)` at the bottom of every loop iteration to cap the frame rate at 60 fps. The `Clock` does two things: it pauses (sleeps) for whatever fraction of a frame is left in the budget, and it records the elapsed time so you can ask it for the delta later.

### The `while running:` loop

This is the game loop. Everything important happens inside it.

### `pygame.event.get()`

This is the most important call in the program after `set_mode`. It drains the OS-level event queue. **You must call this every frame, or your application appears frozen to the OS.** Concretely, on macOS the rainbow spinner shows up; on Windows the title bar gets "(Not Responding)". The OS uses event-queue activity as a heartbeat for "this process is alive and listening." Stop pumping it, and the OS escalates.

If your loop has `while True: time.sleep(0.016)` with no `pygame.event.get()`, you will get a frozen window with no error message. Beginners hit this and conclude Pygame is broken. It is not — they removed Pygame's only way to talk to the OS.

We loop over the events the queue returned this frame. The only one we care about right now is `pygame.QUIT`, which the OS sends when the user clicks the X on the window or presses Cmd-Q / Alt-F4. We set `running = False`; the loop ends after this iteration.

### `screen.fill((20, 20, 30))`

Fill the back-buffer with a dark blue-grey colour. This *replaces* every pixel. If you don't fill, the previous frame's content is still in the buffer — which leads to ghost trails behind moving objects. You may want trails as a stylistic effect (sometimes you do!); for now, fill every frame.

### `pygame.display.flip()`

Hand the back-buffer to the OS to present on screen. We will look at what "flip" actually does on the GPU in section 5. For now: this is the line that makes the user see what you drew.

### `clock.tick(60)`

Pause for whatever fraction of a frame is left. If your loop body took 4 ms and you target 60 fps (16.6 ms per frame), `tick(60)` sleeps for ~12.6 ms. If the loop body took 20 ms — you blew the budget — `tick` returns immediately and your effective fps drops.

This is also where we will fetch delta time in Lecture 2.

### `pygame.quit()`

Tears down every subsystem. Without this, your terminal may keep the audio device open or — on some platforms — leak window handles. Call it once after the loop ends. Some courses skip this; don't. It is good hygiene and it matters when you start adding audio in Week 10.

---

## 4. Why `while True:` without `pygame.event.get()` doesn't work

We need to dwell on this because it traps every Pygame beginner exactly once.

Imagine you write this:

```python
import pygame
import time

pygame.init()
screen = pygame.display.set_mode((800, 600))

while True:
    screen.fill((20, 20, 30))
    pygame.display.flip()
    time.sleep(1 / 60)
```

It draws a window. Then the window freezes. You cannot move it, resize it, or close it. macOS shows the rainbow spinner; Windows shows "(Not Responding)" in the title bar. You quit Python from the terminal with Ctrl-C and curse at the world.

What happened? On every platform, GUI applications get input — keyboard, mouse, window-management events (move, resize, close) — through an OS-level **event queue**. The OS puts events into your application's queue. **You** are responsible for taking them out. The OS uses how often you take them out as a liveness check: "is this app processing its events? Then it's alive. Has it not touched its queue in 5 seconds? Then it's hung."

`pygame.event.get()` is the function that drains the queue. Call it every frame and your app is alive. Skip it and the OS quite literally puts a "not responding" badge on you.

You may add other handling around `pygame.event.get()` — filter for specific event types, ignore some — but you may not skip the call. Even if you don't care about any of the events, you must call it. (Some folks use `pygame.event.pump()` instead, which drains the queue without returning the events; same effect for the liveness check. We use `get()` because we care about `QUIT`.)

This is one of those things that is invisible until it bites you. Now you know.

---

## 5. What `display.flip()` actually does (high level)

You do not need to understand graphics-card pipelines this week. But it is worth a paragraph of intuition.

Modern monitors refresh at a fixed cadence — 60 Hz means 60 refreshes per second, evenly spaced 16.6 ms apart. If you draw mid-refresh, you get **screen tearing**: the top half of the screen shows last frame, the bottom half shows this frame, with a visible horizontal seam.

To avoid this, GPUs use **double-buffering**: two frame buffers in memory, the **front** buffer that the monitor is reading from and the **back** buffer that you are drawing into. When you finish a frame, you tell the GPU to **swap** the two buffers. Now the monitor reads from the new buffer, and you start drawing into the (now-stale) old one.

`pygame.display.flip()` is the swap. It hands the back-buffer to the OS, the OS hands it to the GPU, and on the next monitor refresh the player sees what you drew.

There is also `pygame.display.update()` which can flip just dirty rectangles instead of the whole buffer — a relic of pre-GPU-acceleration days when bandwidth mattered more than it does now. **Use `flip()`** unless you are deliberately optimising. With hardware acceleration there is essentially no cost to flipping the whole frame.

Two more notes for context:

- **VSync** is the option to wait for the next monitor refresh before flipping. It eliminates tearing and caps your fps at the monitor's refresh rate. Modern Pygame defaults to enabled VSync; you usually want it on.
- **Triple buffering** is a more elaborate scheme with three buffers; engines handle it for you. Not your problem in 2026.

The takeaway: `flip()` is the line that turns your drawing into pixels on a screen. It is also the line where you wait for the monitor. Everything before it happened in your CPU; everything after it happens in the GPU and the display hardware.

---

## 6. The render-loop equivalent in other engines

Pygame makes you write the loop. Most engines hide it and call your code from inside their own loop. The shape is identical.

### Godot 4

```gdscript
func _process(delta: float) -> void:
    # update
    position.x += speed * delta

func _input(event: InputEvent) -> void:
    # input
    if event.is_action_pressed("ui_right"):
        speed = 100
```

Godot's main loop calls `_process(delta)` once per frame on every Node that defines it. The `delta` parameter is delta time in seconds — exactly the same number we'll compute by hand in Lecture 2. Rendering is automatic; you just set positions and Godot draws.

### Unity (for context — C11 does not teach Unity)

```csharp
void Update() {
    transform.position += Vector3.right * speed * Time.deltaTime;
}
```

`Update()` on a `MonoBehaviour` is the equivalent. `Time.deltaTime` is the delta. Rendering, again, automatic.

### Pygame (what we just wrote)

```python
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_d]:
        x += speed * dt
    screen.fill((20, 20, 30))
    pygame.draw.circle(screen, (255, 0, 200), (x, y), 10)
    pygame.display.flip()
    dt = clock.tick(60) / 1000
```

Same loop. We just write it out. When you switch to Godot in Week 8, this is the only mental adjustment: "the engine calls my `_process(delta)` once per frame instead of me writing the `while`."

This portability is the point. The game-loop pattern transfers between Pygame, Godot, Unity, Unreal, raylib, Phaser, LÖVE, and every browser game made with `requestAnimationFrame`. Different syntax. Same idea.

---

## 7. Common mistakes (the greatest hits)

In four weeks of teaching this we have seen these on repeat:

- **Forgetting `pygame.event.get()`.** Frozen window. See §4.
- **Forgetting `screen.fill()`.** Trails behind every moving object. Sometimes a feature, mostly a bug.
- **Forgetting `pygame.display.flip()`.** Black window forever. You drew everything to the back-buffer and never asked the OS to show it.
- **Calling `pygame.init()` inside the loop.** Don't. Once, at the top.
- **Putting input handling after update.** One frame of lag. See §2.
- **Using `time.sleep()` instead of `clock.tick()`.** Works approximately. You don't get delta time, and you can't change the cap without rewriting the math. Use `Clock`.
- **Forgetting `pygame.quit()`.** Works most of the time. Eventually you'll write a test that imports your game module and the test runner won't release the audio device.

You will hit at least three of these this week. Everyone does. The error messages are not always helpful — "frozen window" has no traceback. The trick is to keep this list near your editor.

---

## 8. What a "prototype" gets you, and what it doesn't

We will end every lecture this term with a reminder. A game has many layers:

1. **The mechanic.** "A circle moves with WASD."
2. **Level design.** Where do you place obstacles? How does difficulty scale?
3. **Audio.** SFX and music that responds to action.
4. **UX.** Title screen, pause, game-over, settings.
5. **Polish.** Particles, screen shake, tweens, easing curves — the *juice*.
6. **Packaging.** A `.exe` or `.dmg` your friend can run without installing Python.

This week we are at layer 1. By the end of the course, you will have shipped a small game that has all six. **But layer 1 is not the game.** A moving circle is a prototype. A game is a prototype plus the other five layers, and roughly **80% of the work is in those other layers.** Senior indie devs have been saying this for thirty years; we're not making it up.

We mention this now because next week you'll have a bouncing ball, and you might say "I made a game." You made a mechanic. The game is the thing that ships.

---

## 9. What to do before Lecture 2

- Type out the minimum-viable loop from §3. Run it. Confirm you see a dark window. Click X; confirm it closes cleanly.
- Add a single `print("frame")` inside the loop. Run for two seconds, then close. You should see roughly 120 `frame` lines (60 fps × 2 s). If you see far fewer, your `clock.tick(60)` is wrong or VSync is throttling. If you see far more, `tick(60)` is missing.
- Read [the *Game Programming Patterns* — Game Loop chapter](https://gameprogrammingpatterns.com/game-loop.html). It's free, ~30 minutes.

In Lecture 2 we will make something move, and we will discover the most common Pygame bug along the way.

---

*Next: [Lecture 2 — Delta Time and the Fixed Timestep](./02-delta-time-and-the-fixed-timestep.md).*
