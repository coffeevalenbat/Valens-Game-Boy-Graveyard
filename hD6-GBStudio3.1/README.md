# hUGEDriver V6 in GB Studio 3.1
This guide will explain how to "inject" hUGEDriver V6 (Aka the format used by hUGETracker Beta 10) music into GB Studio 3.1, using some plugin shenanigans.

 - [Acknowledgements](#acknowledgements)
 - [Requirements](#requirements)
 - [Exporting your music to .c](#exporting-your-music-to-c)
 - [Setting up the plugin](#setting-up-the-plugin)
 - ["Why is my music going faster now?"](#why-is-my-music-going-faster-now)

## Acknowledgements
This injection method, as technically sound as it is, is still prone to breaking many things in the GB Studio engine, such as the built-in "Play music" event and any tracks loaded through GB Studio, if you use this plugin, you gotta side load all your music through it, using the built-in Play music event will compile and try to play music data tailor-made for hUGEDriver V5, which to the V6 driver will be garblo. I doubt this plugin is able to somehow corrupt your project, but make sure to make a backup before trying it first-time. As mentioned in the main readme, any code in this repo is shared with no warranty.

## Requirements
Of course you'll need [hUGETracker](https://github.com/SuperDisk/hUGETracker/releases/tag/1.0b10) to actually compose your music first. Any version that uses the Version 6 format revision (As of writing this, that'd be Beta 10) will do.

Next you'll need the hD-Import plugin, this is the bit in charge of side-loading the music into GB Studio, [download](https://github.com/datguywitha3ds/Valens-Game-Boy-Graveyard/raw/main/hD6-GBStudio3.1/hD-Import.zip) the .zip file and extract it alongside any other plugins your project may use (*Project-folder > plugins*).

I'd recommend putting your .uge files in the plugin's *music* folder to avoid GB Studio trying to compile the music.

## Exporting music to .c
After you've composed your tracks in hUGETracker, go to [**File > Export GBDK .c ...**], a window asking for a song descriptor will show up, this is the name given to your song's header that is used to identify it during compilation, give it the name of your song in a way that is clear and won't be mixed with any other variables (I'd recommend adding "\_SONG" at the end to make extra sure), also make sure to make it a valid C variable name (IE, no spaces or special characters). After this, save the .c file in the plugin's *engine > src > data > music* folder with the same name as the song descriptor.

Now, open the file in a text editor, some modifications have to be done to the .c export to match what GB Studio expects.

At the top of the file, replace the existing `#define` lines before the `order_cnt` line so that it looks like this:
```c
#pragma bank 255
#include "hUGEDriver.h"
#include <stddef.h>
#include "hUGEDriverRoutines.h"
```

Now scroll all the way down to the end of the file, you'll see that the last line is something among the lines of `const hUGESong_t .......`, add the following line right before it. Replace `XXXX` with your song's descriptor.
```c
const void __at(255) __bank_XXXX;
```

Finally, all you gotta do is look for the word `NULL` (Normally right before the word `waves`) in the before mentioned last line and replace it with `routines`. That's it! Your song is now (hopefully) a valid GB Studio track.

## Setting up the plugin
Now that you have your tracks exported and ready for GB Studio, we have to tell the plugin that they exist. Look for the file `event-hD-Import.js` inside the plugin's *events* folder and open it in a text editor.

This file is the one in charge of adding the new "Play music" replacement event, to make it aware that our tracks exist, we have to edit an array including all the tracks, you'll see it with a `//SONG FILE LIST` line above it.

The array/list has a pretty simple format, each song has it's own sub array (Marked in square brackets and separated by commas), inside each there is 3 values. The first is the index of the song, it should always go in ascending order starting from 0. Next is the song name, this is what's displayed in the editor, so it doesn't need to be a valid C variable like our song descriptor. Finally there's our song's descriptor. Add all your tracks in that format, it should look something like this by the end:
```js
// SONG FILE LIST
const song_list = [
    [0, "Title Theme", "title_theme_SONG"],
    [1, "Grassy Grasses", "grassy_grasses_SONG"],
    [2, "Billy Bob Boss Theme", "billy_bob_boss_SONG"],
    [3, "Game Over Theme", "game_over_SONG"]
];
```

Once that's done, save the file. Open up your project (or reload it if it was already open, I recommend not editing plugins while the editor is open) and look in the [**Music & Sound Effects**] section of the events window, you'll see a new event named [**Play Imported hUGEDriver Track**], adding it to your game will let you pick a track and play it just like the original event.

Now try compiling your game with one of these events, if everything went right, you should get your track playing in-game perfectly.

## Why is my music going faster now?
If you got this far and got your tune in-game, you'll notice its playing *slightly* faster now. This is because normally hUGETracker runs at 60hz using a V-Blank interrupt, GB Studio on the other hand runs the driver at 64hz using a timer interrupt, the easiest way to get around this is to compose with the timer in mind, using the [**Enable timer-based tempo**] setting in hUGETracker and setting the timer divider to 192, this will make the player run at the same speed as GB Studio.

The other method is a lot messier since it breaks even more stuff (as far as I know, this break .WAV playback or makes it sound a bit weird);
Go into your project in GB Studio and go to [**Game > Advanced > Eject engine**]. This will create a new folder in your project's *assets* folder called *engine*, inside here, look for `music_manager.h` inside of the *include* folder and open it up in a text editor, we have to edit the `music_setup_timer` function, changing `0x80u : 0xC0u;` to `0x78u : 0xBCu;`, this will bring the music speed down to ~60.2hz. It should look something like this:
```c
inline void music_setup_timer() {
    TMA_REG = ((_cpu == CGB_TYPE) && (*(uint8_t *)0x0143 & 0x80)) ? 0x78u : 0xBCu;
    TAC_REG = 0x07u;
}
```
