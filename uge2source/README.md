# uge2source.py
This is my attempt at making a version of uge2source in python, for portability mostly since as of now, I had to either compile my songs through HT or with uge2source through wine. It works just like the original, but lacks the .asm output since that's something I never tend to use and don't really need, it's not actually based on uge2source's code, but instead on the GB Studio 3.1 data parser/compiler.

This will only work with V5 uge files.

Usage:
`python3 uge2source.py song.uge song_descriptor out_song.c -b X -op -oi`

For doing banked songs, use the `-b` argument followed by the bank number.

There's also the `-oi` and `-op` arguments, these optimize a song's instruments and patterns respectufully by looking at the highest used instrument and removing any higher ones. For patterns, it looks for any jump commands (Dxx or Bxx) and skips saving any data after that. This can save a lot of data in the end.