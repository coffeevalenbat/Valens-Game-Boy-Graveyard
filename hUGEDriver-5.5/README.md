# hUGEDriver "5.5"
So... Funny story, A few months ago (June/July 2022) I started scoring Genesis II with the intent of it being my first hUGEDriver 6 score, using hUGETracker beta 10, after a while I noticed this wouldn't be possible, due to the general bloatedness of my computer right now, upgrading Ubuntu to be able to run beta 10 or move to windows is too much pain for what it's worth. So instead I just sorta, modded hUGEDriver, hUGETracker itself will be fine if you modify hUGEDriver.asm as long as you keep the general behavior of it intact, this helped with translating the score with ease, leaving me lots of wiggle room.

This mod includes:
- Wait note command replaced with a speed groove control (See code for 7xx).
- Super Game Boy support with two note LUT.
- Software volume control (Shifts volume by X amount, works OK enough).
- Speed 0 (F00) is equivalent to FamiTracker's stop command (Cxx).
- Volume Slide effect replaced with an inverted arpeggio (Axx).
- Panning effect rets out if any channels are muted.
- Run routine effect (6xx) commented out (Never used it lol).

I cannot confirm this is a perfect mod, but the main goal was to make a mod with extra features while still being able to be used and compiled using hUGETracker beta 9.

Also, in case you wanna use this with GBDK:
- Compile hUGEDriver.asm with rgbasm.
- Use RGB2SDAS to convert that to an SDCC object file.
- Use SDAR to compile that to a .lib file.