# hUGEye
This script analyzes a ROM file and prints any possible hUGEDriver song headers, it should work perfectly with games made with GB Studio or any games that use the unmodified hUGETracker/UGE2SOURCE output, but others like Genesis II and Shock Lobster may be harder to recognize.

Usage:
`python3 hUGEye.py ROM.gb -t X`

In this case, tolerance can be a number between 0 and 15, it tells the code how many Wave/Duty instrument slots to check as valid, by default it checks all 15. Lowering the value may help with games like the before mentioned that use cutted down data.