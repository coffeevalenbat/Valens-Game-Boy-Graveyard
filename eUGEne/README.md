# eUGEne
This script lets you "decompile" games that use hUGEDriver and rip out any music tracks, there's more info on it's limitations in the script itself. You can use hUGEye.py to analyze a ROM and look for any hUGEDriver headers, but it might not work with optimized songs (IE, what you might find on Shock Lobster or Genesis II). This will only work with V5 games and no fancy forks that change the data format.

Usage:
`python3 eUGEne.py ROM.gb ADDRESS BANK`

The address and bank must be in hex notation (`0x`).

Do **NOT** use this tool for piracy and/or theft, I cannot express enough how much I want to avoid this. This tool was written as a way to document the .UGE v5 format in an easier to read way and to allow for research and or recovery. I'd hate to ruin anyone's day because someone used **MY** tool to steal their songs. But as any tool in our world, it can also be a weapon. If you use this tool or any other piece of code of mine for evil, harm of theft, Fuck you from the bottom of my heart! <3