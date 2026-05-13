"""exercise-01-blank-window.py

Goal
----
Open a Pygame window, fill it with a solid colour, and close it cleanly
when the user clicks the X. This is the smallest possible Pygame program.
Every game in this course starts from this shape.

Expected behaviour
------------------
- A 800x600 window appears with the title "C11 Week 1 - Blank Window".
- The interior is filled with Coin Pink (the C11 brand colour, #DB2777).
- Clicking the X (or pressing Cmd-Q / Alt-F4) closes the window cleanly.
- The terminal returns to a prompt with no errors and no rainbow spinner
  hanging on the closed window.

What you learn
--------------
- ``pygame.init()`` initialises every subsystem.
- ``pygame.display.set_mode((w, h))`` creates the window and returns the
  drawable Surface.
- ``pygame.event.get()`` MUST be called every frame, otherwise the OS
  thinks your process is hung and shows a "not responding" badge.
- ``screen.fill(colour)`` replaces every pixel in the back-buffer.
- ``pygame.display.flip()`` hands the back-buffer to the OS to present.
- ``pygame.time.Clock().tick(60)`` caps the loop at 60 fps.
- ``pygame.quit()`` releases subsystems on exit.

Estimated time
--------------
Around 25 minutes if it's your first time. Under 5 once you've done it.

To complete
-----------
Find the ``TODO`` comments and fill in the missing lines. Do not look at
the HINT block at the bottom of this file until you have tried for at
least 15 minutes.

Run with::

    python exercise-01-blank-window.py
"""

from __future__ import annotations

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "C11 Week 1 - Blank Window"
TARGET_FPS = 60

# Coin Pink, the C11 brand colour (#DB2777). Pygame colours are
# (red, green, blue) tuples, each component 0-255.
COIN_PINK = (219, 39, 119)


def main() -> None:
    """Open a Pygame window and run the minimum-viable game loop."""

    # TODO: call ``pygame.init()`` to initialise every Pygame subsystem.

    # TODO: create the window with ``pygame.display.set_mode((w, h))``.
    #       Store the returned Surface in a variable called ``screen``.

    # TODO: set the window title with ``pygame.display.set_caption(...)``.

    # TODO: create a ``pygame.time.Clock`` for frame-rate capping.

    running = True

    while running:
        # 1. Input -----------------------------------------------------------
        # TODO: iterate over ``pygame.event.get()`` and set ``running = False``
        #       when you see a ``pygame.QUIT`` event.

        # 2. Update ----------------------------------------------------------
        # Nothing to update yet. The window has no moving parts.

        # 3. Render ----------------------------------------------------------
        # TODO: fill the screen with ``COIN_PINK``.

        # TODO: call ``pygame.display.flip()`` to present the frame.

        # 4. Frame-rate cap --------------------------------------------------
        # TODO: call ``clock.tick(TARGET_FPS)`` to cap the loop at 60 fps.
        pass  # remove this once you've added the calls above.

    # TODO: call ``pygame.quit()`` to release subsystems before the
    #       Python process exits. Without this you may see lingering
    #       audio-device handles or window handles on some platforms.


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------------
# HINT (read only if you have been stuck for more than 15 minutes)
# ----------------------------------------------------------------------------
#
# import pygame
#
# def main() -> None:
#     pygame.init()
#     screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
#     pygame.display.set_caption(WINDOW_TITLE)
#     clock = pygame.time.Clock()
#
#     running = True
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#
#         screen.fill(COIN_PINK)
#         pygame.display.flip()
#         clock.tick(TARGET_FPS)
#
#     pygame.quit()
#
# ----------------------------------------------------------------------------
# COMMON MISTAKES
# ----------------------------------------------------------------------------
# - Forgetting ``pygame.event.get()`` => the window appears, then freezes.
#   The OS shows a rainbow spinner / "Not Responding". This is the most
#   common Pygame bug. The OS uses event-queue draining as a liveness
#   check; stop pumping it and you look hung.
# - Forgetting ``pygame.display.flip()`` => black window forever. You drew
#   to the back-buffer and never asked the OS to show it.
# - Forgetting ``pygame.quit()`` => works most of the time. Eventually
#   bites you when you start using audio.
# - Calling ``pygame.init()`` inside the loop => slow, wasteful, and on
#   some platforms genuinely buggy. Once, at the top.
# ----------------------------------------------------------------------------
