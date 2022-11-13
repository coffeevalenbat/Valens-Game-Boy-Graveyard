![Banner](banner.png)

This repository is mostly been set up to archive and share some of the tools I've developed through my time composing and programming for the Nintendo Game Boy and SuperDisk's hUGEDriver.

I like to write my own tools when it comes to music composition or reverse engineering, it can be a fun exercise on programming. Most of these tools were written because I like to compose on FamiTracker first, then translate that manually to hUGEDriver, plus the fact that as of this writing, I'm stuck using an earlier version of hUGETracker (Beta 9).

In this repository you'll find:

 - dmw2ugw: Converts Deflemask .dmw wave files to hUGETracker .ugw files.
 - ftn2ht: Converts FamiTracker "Plain Text" clipboard data to hUGETracker clipboard note data.
 - eUGEne: ROM decompiler to extract hUGEDriver songs back to .uge.
 - hUGEye: ROM analyzer to find hUGEDriver song headers.
 - uge2source: a Python .uge C compiler based on the GB Studio 3.1 data parser and hUGETracker's own uge2source. Includes some extra optimization flags.
 - FT-TXT2HT-UGW: Rips Namco N163 wavetables from a FamiTracker .txt export to hUGETracker .ugw files.
 - hUGEDriver 5.5: My hUGEDriver "mod" based on version 5, adds speed grooves, software volume control, inverted arpeggios, etc. Made to be usable and compile-able with hUGETracker Beta 9 (Used on Genesis II).
 - txt2ht-message: Converts strings to hUGETracker note clipboard data, usable to hide little ascii easter eggs in your music.
 - FurFX: A swiss tool for SFX data, compiles Furnace clipboard data to many sound effect drivers (CBT-FX, VGM2GBSFX, VGM).
 
These tools are shared with no warranty or help, I'm more than happy to accept push requests if you do find any bugs or fixes, but don't expect me to be very up and aware of repo issues.
 
![Works on MY machine™](womm.png)
