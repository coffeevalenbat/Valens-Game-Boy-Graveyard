# DMW2UGW
This script converts DefleMask .DMW wavetable files to hUGETracker .UGW files. This was written back in January of 2022 so I wouldn't be surprised if Paidmask uses a new format revision. Lol.

Usage:
`python3 dmw2ugw.py INPUT.dmw OUTPUT.ugw`

For reference, the .UGW format is just a file consisting of 32 uint32 values, each representing one wave nibble.

I've also included the waveforms I ripped from Alberto Jose Gonzalez's Game Boy music (Originally published [here](https://twitter.com/alberto_mcalby/status/1040709833115230209?s=20&t=nV5J9jJNZjbqRZKknpjRig)).