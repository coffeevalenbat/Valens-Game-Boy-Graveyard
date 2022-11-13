"""
FUR-FX - A furnace to Game Boy SFX converter by Coffee 'Valen' Bat
==================================================================

...With some borrowed code from smarter people :p (Srry, toxa, ISSOTM, random stackoverflow people, etc)

DISCLAIMER(S)
=============
This is NOT a plug and play converter, it's very finicky and was originally written
with FX-Hammer in mind, thus some things like using channels that werent enabled on
the first step, any of the effects not listed below, fancy tempos, speeds, etc, 
>WONT< work, this is mostly a way to compose SFX for a wider variety of drivers and
in a faster way then FX-Hammer.

THIS WILL ONLY WORK WITH CLIPBOARD DATA STRAIGHT
FROM THE TEMPLATE FILE INCLUDED, that means only CH2 and CH4, 
only the MAIN instrument and 3 effect columns. changing any of 
this >WILL< throw the converter off.

The supported note range is C-2 through B-7 for channel 2 and C-3 through G#5 for channel 4.

If your music/game uses channel 2 more than channel 1, you can use the --swapduty parameter.

SUPPORTED EFFECTS
=================
FFxx - stop/end sound effect
08xx - change channel panning (F0 = left, 0F = right)
12xx - change CH2 duty
11xx - change CH4 noise mode (0 = 15 bit, 1 = 7 bit)
09xx - change speed 1
0Fxx - change speed 2
E5xx - change CH2 pitch (80 = Center, 00 = One note lower, FF = One note higher) [VGM/VGM2GBSFX/CBT-FX only]

EVERY SOUND EFFECT MUST END WITH AT LEAST ONE INSTANCE OF "FFxx".

.TXT FORMAT SPECS:
==================
Every SFX must start with === Followed by the sfx name,
after that, you can define priority or sgb values with:
- "PRI X" (0-15)
- "SGB TABLE ID PITCH VOL" (CBT-FX/VAL-FX only)
- "REALSPEED" (VGM2GBSFX/.VGM only)
- "SWAPDUTY" (VGM2GBSFX/.VGM only)

If using --flist, any parameters except the output driver parameters will be ignored.
you can also fill the name command with anything you like, it'll be ignored when using --flist.

After that, an empty line followed by the furnace clipboard UNEDITED.

EXTRA NOTES:
============

For testing REALSPEED mode, you can set the virtual tempo in furnace to 
640bpm, 150bpm is 60hz and 640 is 256hz.

Unlike Furnace, the default starting speed is 1:1, when creating new tracks, 
Furnace makes the default 6:6, check that if you think your tracks are off speed.

If you use --export, make sure to have VGMPlay somewhere for the .wav converting.

Very few default writes are done on the first step, so if your duty or 
volume are wrong, add an effect to set it.

VGMPlay's 15 bit noise mode is kinda fucked, so don't worry if export mode sounds a bit off

"""
VGMPlay = "wine VGMPlay.exe"
VGMPlayDir = "/home/dev/Documents/comms/TOOLS/FurFX/VGMPlay"

FUR_note_table = [
"C-2","C#2","D-2","D#2","E-2","F-2","F#2","G-2","G#2","A-2","A#2","B-2",
"C-3","C#3","D-3","D#3","E-3","F-3","F#3","G-3","G#3","A-3","A#3","B-3",
"C-4","C#4","D-4","D#4","E-4","F-4","F#4","G-4","G#4","A-4","A#4","B-4",
"C-5","C#5","D-5","D#5","E-5","F-5","F#5","G-5","G#5","A-5","A#5","B-5",
"C-6","C#6","D-6","D#6","E-6","F-6","F#6","G-6","G#6","A-6","A#6","B-6",
"C-7","C#7","D-7","D#7","E-7","F-7","F#7","G-7","G#7","A-7","A#7","B-7",
]

CH2_freqs = [44,156,262,363,457,547,631,710,786,854,923,986,1046,1102,1155,1205,1253,1297,1339,1379,1417,1452,1486,1517,1546,1575,1602,1627,1650,1673,1694,1714,1732,1750,1767,1783,1798,1812,1825,1837,1849,1860,1871,1881,1890,1899,1907,1915,1923,1930,1936,1943,1949,1954,1959,1964,1969,1974,1978,1982,1985,1988,1992,1995,1998,2001,2004,2006,2009,2011,2013,2015]

NOI_lut_long = [0x74,0x67,0x66,0x65,0x64,0x57,0x56,0x55,0x54,0x47,0x46,0x45,0x44,0x37,0x36,0x35,0x34,0x27,0x26,0x25,0x24,0x17,0x16,0x15,0x14,0x07,0x06,0x05,0x04,0x03,0x02,0x01,0x00]
NOI_lut_short = [0x7c,0x6f,0x6e,0x6d,0x6c,0x5f,0x5e,0x5d,0x5c,0x4f,0x4e,0x4d,0x4c,0x3f,0x3e,0x3d,0x3c,0x2f,0x2e,0x2d,0x2c,0x1f,0x1e,0x1d,0x1c,0x0f,0x0e,0x0d,0x0c,0x0b,0x0a,0x09,0x08] 

import sys
import os
from struct import pack
import argparse
import pyperclip
import textwrap
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("out", help="Folder where the output files will be saved.")
parser.add_argument("name", help="Name of the files.")
parser.add_argument("--cbt", help="Save to CBT-FX C array", action="store_true")
parser.add_argument("--toxa", help="Save to VGM2GBSFX C array", action="store_true")
parser.add_argument("--vgm", help="Save to .VGM", action="store_true")
parser.add_argument("--valen", help="Save to VAL-FX format.", action="store_true")
parser.add_argument("--libbet", help="Save to libbet format.", action="store_true")
parser.add_argument("--fxh", help="Save to FX-Hammer .SAV slice", action="store_true")
parser.add_argument("--swapduty", help="Use CH1 instead of CH2 (VGM/VGM2GBSFX Only)", action="store_true")
parser.add_argument("--export", help="Make .VGM export player compatible (default is made with GB Studio 3.1 in mind), Includes .WAV output", action="store_true")
parser.add_argument("--realspeed", help="Override speed fix for VGM2GBSFX (SFX plays 4x faster)", action='store_const', const=1, default=4)
parser.add_argument("--sgb", help="Add Super Game Boy support (CBT-FX/VAL-FX only)", nargs=4, metavar=("FX_TAB", "FX_ID", "FX_PITCH", "FX_VOL"))
parser.add_argument("--flist", help="Read data from txt file.", nargs=1, metavar=("FILE_LIST"))
args = parser.parse_args()


def get_val(line,poi,len):
	return fur[line][poi:poi+len]

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def get_freq(note, offset):
	freq = CH2_freqs[note]
	prev = clamp(note - 1, 0, len(CH2_freqs))
	nxt = clamp(note + 1, 0, len(CH2_freqs))
	if offset < 0:
		freq = CH2_freqs[note] + (((CH2_freqs[note] - CH2_freqs[prev])/128) * offset)
	if offset > 0:
		freq = CH2_freqs[note] + (((CH2_freqs[nxt] - CH2_freqs[note])/127) * offset)
	return round(freq)

def array_to_hex(a):
	b = []
	for i in range(0, len(a)):
		b.append("0x%0.2X" % a[i])

	b = str(b).replace("'","").replace(" ","")[1:-1]
	return '\n'.join(textwrap.wrap(b, 45))

def create_vgm(filename):
    outfile = open(filename, "w+b")
    outfile.write(pack('IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII', 0x206D6756, 0, 0x161, 0,0,0,0,0,0,0,0,0,0,0xc0-0x34,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x400000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))
    if args.export:
    	# NRX2-NRX4
    	for n in [2,7,12,17]:
    		outfile.write(bytes([0xB3, n, 0x00]))
    		outfile.write(bytes([0xB3, n+2, 0x80]))

    	# NR52-54
    	outfile.write(bytes([0xB3, 0x0, 0x0]))
    	outfile.write(bytes([0xB3, 0x16, 0x8f]))
    	outfile.write(bytes([0xB3, 0x15, 0xff]))
    	outfile.write(bytes([0xB3, 0x14, 0x77]))

    return outfile

def finalize_vgm(outfile, chu, wait):
	duty_inc = 5
	if args.swapduty:
		duty_inc = 0
	if chu[0]:
		outfile.write(bytes([0xB3, 0x02 + duty_inc, 0x00]))
		outfile.write(bytes([0xB3, 0x04 + duty_inc, 0x80]))
	if chu[1]:
		outfile.write(bytes([0xB3, 0x11, 0x00]))
		outfile.write(bytes([0xB3, 0x13, 0x80]))
	outfile.write(bytes([0xB3, 0x15, 0xff]))
	outfile.write(bytes([0x62]))
	
	if args.export:
		outfile.read()
		# To allow for the sfx to have some time to be quiet
		outfile.write(bytes([0x61,0x02,0x00]))

		temp = outfile.tell() - 3 # -3 since we still need to write the termination byte
		outfile.seek(0x04)
		outfile.write(bytes(temp.to_bytes(4, "little") ))

		outfile.seek(0x18)
		outfile.write(bytes(wait.to_bytes(4, "little")))

		outfile.read()
	
	outfile.write(b'\x66')
	
	outfile.close()


def _header(_chu,pr,len):
	if _chu[0]:
		chu = "Channel 2 (Duty)"
	if _chu[1]:
		chu = "Channel 4 (Noise)"
	if _chu == [True, True]:
		chu = "Channel 2 and channel 4 (Duty & Noise)"
	if args.sgb:
		sgbs = "Yes"
	else:
		sgbs = "No"
	b = """/*

""" + args.name + """

Sound Effect File.

Info:
	Length			:	""" + str(len) + """
	Priority		:	""" + str(pr) + """
	Channels used	:	""" + chu + """
	SGB Support		:	""" + sgbs + """"""
	if args.sgb:
		b += """
	SGB SFX Table	:	""" + args.sgb[0] + """
	SGB SFX ID		:	""" + str(args.sgb[1]) + """
	SGB SFX	Pitch	:	""" + str(args.sgb[2]) + """
	SGB SFX Volume	:	""" + str(args.sgb[3]) + """"""
	b += """

This file was generated by FurFX

*/
"""
	return b

fur = pyperclip.paste().split("\n")[2:]
priority = 0
if args.out == ".":
	args.out = ""

def main():
	noise = False # Check if noise is long or short
	CHUsed = [False, False]
	over = False
	CHon = [False, False] # Not usefule for CBT, but useful for VGM and FHX to avoid pointless writes to a dead channel
	CHOver = [False, False]
	speed = [1, 1] # Speed is in pairs in fur/dmf
	pitch_offset = 0 # value from E5xx
	wait_counter = 0 # Used on VGM export mode

	# SPEED, PAN, VOL, DUTY, NOTE, PAN, VOL, FREQ
	step_buffer = [1, 0xFF, 0xf, 0, 0, 0xFF, 0xf, 0x00]

	if args.cbt:
		# CBT-FX export
		cbtfx_buf = []
		# Placeholder header
		cbtfx_buf.append(0)
		cbtfx_buf.append(0)
		if args.sgb:
			cbtfx_buf.append(65) # Command byte ((SGB_SOUND << 3) | 1)
			if args.sgb[0] == "A":
				cbtfx_buf.append(int(args.sgb[1])) # Sound Effect A
				cbtfx_buf.append(0) # Sound Effect B
			elif args.sgb[0] == "B":
				cbtfx_buf.append(0) # Sound Effect A
				cbtfx_buf.append(int(args.sgb[1])) # Sound Effect B
			if args.sgb[0] == "A":
				cbtfx_buf.append(int(args.sgb[2]) | (int(args.sgb[3]) << 2)) # Sound effect attributes (A)
			elif args.sgb[0] == "B":
				cbtfx_buf.append((int(args.sgb[2]) << 4) | (int(args.sgb[3]) << 6)) # Sound effect attributes (B)
			cbtfx_buf.append(0) # Music Score Code (Unused)

	# VGM export
	if args.vgm:
		vgm_buf = create_vgm(args.out + args.name + ".vgm")

	if args.fxh:
		with open("blankFXH.bin","rb") as b:
			fxh_buf = bytearray(b.read())

	# VGM2GBSFX
	if args.toxa:
		toxa_buf = []

	# Libbet driver
	if args.libbet:
		libbet_buf = []

	if args.valen:
		valfx_buf = []
		valfx_buf.append(priority)

	for n in range(len(fur)):
		CHOver[0] = False
		CHOver[1] = False
		# Flags set if any new values are set, probably not 
		# useful for CBT-FX but maybe useful for VGM2GBSFX

		"""
		0 - Speed
		1 - CH2 Pan
		2 - CH2 Vol 
		3 - CH2 Duty
		4 - CH2 Note 
		5 - CH4 Pan 
		6 - CH4 Vol 
		7 - CH4 Freq
		"""
		flag_buffer = [False, False, False, False, False, False, False, False]

		# Parse effects first
		for x in [7, 11, 15, 27, 31, 35]:
			fx = get_val(n, x, 2)
			fxpar = get_val(n, x + 2, 2)

			# FFxx - Stop song
			if fx == "FF":
				over = True

			# 08xx - change panning
			if fx == "08":
				c = 1
				if x > 15:
					c = 5
				flag_buffer[c] = True
				step_buffer[c] = int(fxpar,16)

			# 12xx - change CH2 duty
			if fx == "12":
				flag_buffer[3] = True
				step_buffer[3] = int(fxpar,16)

			# 11xx - change CH4 noise
			if fx == "11":
				noise = False
				if fxpar != "00":
					noise = True

			# 09xx - change speed 1
			if fx == "09":
				speed[0] = int(fxpar,16)

			# 0Fxx - change speed 1
			if fx == "0F":
				speed[1] = int(fxpar,16)

			# E5xx - change CH2 pitch offset
			if fx == "E5":
				flag_buffer[4] = True
				pitch_offset = int(fxpar,16) - 128

		# Note CH2
		if get_val(n,0,3) != "...":
			if get_val(n,0,3) == "OFF": # Set volume to 0 to ensure a blank retrigger
				flag_buffer[4] = False
				flag_buffer[2] = True
				step_buffer[2] = 0
				CHon[0] = False
				CHOver[0] = True
			else:
				if n == 0:
					CHUsed[0] = True
					CHon[0] = True
				if step_buffer[0] != FUR_note_table.index(get_val(n,0,3)) or n == 0:
					flag_buffer[4] = True
					step_buffer[4] = FUR_note_table.index(get_val(n,0,3))

		# Vol CH2
		if get_val(n,6,1) != ".":
			if step_buffer[2] != int(get_val(n,6,1), 16) or n == 0:
				flag_buffer[2] = True
				step_buffer[2] = int(get_val(n,6,1), 16)

		# Note CH4
		if get_val(n,20,3) != "...":
			if get_val(n,20,3) == "OFF": # Set volume to 0 to ensure a blank retrigger
				flag_buffer[7] = False
				flag_buffer[6] = True
				step_buffer[6] = 0
				CHon[1] = False
				CHOver[1] = True
			else:
				if n == 0:
					CHUsed[1] = True
					CHon[1] = True
				v = FUR_note_table.index(get_val(n,20,3))-11
				r = 0
				if not noise: # If noise long
					v = clamp(v, 0, len(NOI_lut_long))
					r = NOI_lut_long[v-1]
				else: # If noise short
					v = clamp(v, 0, len(NOI_lut_short))
					r = NOI_lut_short[v-1]
				if step_buffer[7] != r or n == 0:
					step_buffer[7] = r
					flag_buffer[7] = True

		# Vol CH4
		if get_val(n,26,1) != ".":
			if step_buffer[6] != int(get_val(n,26,1), 16) or n == 0:
				flag_buffer[6] = True
				step_buffer[6] = int(get_val(n,26,1), 16)

		# Apply per pair speed
		if step_buffer[0] != speed[n & 1]:
			step_buffer[0] = speed[n & 1]
			flag_buffer[0] = True

		
		if n >= len(fur)-1:
			over = True

		if over:
			if args.valen:
				valfx_buf[0] |= int(CHUsed[0]) << 5
				valfx_buf[0] |= int(CHUsed[1]) << 4
			if args.cbt:
				cbtfx_buf[1] = n + 1
				cbtfx_buf[0] = priority
				cbtfx_buf[0] |= int(CHUsed[0]) << 7
				cbtfx_buf[0] |= int(CHUsed[1]) << 5
				if args.sgb:
					cbtfx_buf[0] |= 0x40 # SGB Flag
			if args.toxa:
				b = [0]
				if CHon[0]:
					b[0] += 1
					if args.swapduty:
						b.append(0b00101000) # NR12 and NR14
					else:
						b.append(0b00101001) # NR22 and NR24
					b.append(0)
					b.append(0x80)

				if CHon[1]:
					b[0] += 1
					b.append(0b00101011) # NR42 and NR44
					b.append(0)
					b.append(0x80)
				toxa_buf.extend(b)
			if args.fxh:
				if n > 31:
					print("WARNING: SFX is " + str(n) + " patterns long, FX-Hammer only supports 32 patterns and lower.")
			break

		if args.cbt:
			# Convert to CBT-FX
			# Speed and pan
			cbtfx_buf.append((step_buffer[0]-1) | (128 if n == 0 or flag_buffer[1] or flag_buffer[5] else 0))

			# Pan
			if n == 0 or flag_buffer[1] or flag_buffer[5]:
				cbtfx_buf.append((step_buffer[5] & 0x88) | (step_buffer[1] & 0x22))
				#cbtfx_buf.append(0x55 | ((step_buffer[5] & 0x88) | (step_buffer[1] & 0x22)))

			# CH2 Duty
			if CHUsed[0]:
				cbtfx_buf.append(step_buffer[3] << 6)

			# Frame volume
			cbtfx_buf.append(((step_buffer[2] << 4) if CHUsed[0] else 0)| (step_buffer[6] if CHUsed[1] else 0))

			# CH2 freq
			if CHUsed[0]:
				f = get_freq(step_buffer[4], pitch_offset)
				cbtfx_buf.append(f & 255)
				cbtfx_buf.append((f >> 8) | 0x80) # We only retrigger when a new volume was set
				#cbtfx_buf.append((f >> 8) | (int(flag_buffer[2]) << 7)) # We only retrigger when a new volume was set
				# Bgb no likey volume with no triggers

			# Ch4 freq
			if CHUsed[1]:
				cbtfx_buf.append(step_buffer[7])

		if args.fxh:
			b = [0, 0, 0, 0, 0, 0, 0, 0]
			b[0] = step_buffer[0] # Speed
			if CHon[0]:
				b[1] = step_buffer[1] & 0x22
				b[2] = (step_buffer[2] << 4) | 0x08
				b[3] = step_buffer[3] << 6
				b[4] = (step_buffer[4] * 2) + 0x40
			if CHon[1]:
				b[5] = step_buffer[5] & 0x88
				b[6] = (step_buffer[6] << 4) | 0x08
				b[7] = step_buffer[7]
			for f in range(8):
				h = 0x400
				h += f
				h += n*8
				fxh_buf[h] = b[f]

		# VGM2GBSFX
		if args.toxa:
			
			pack_count = 0
			b = [0x00] # Placeholder COUNT, replace later

			# Panning
			if n == 0 or flag_buffer[1] or flag_buffer[5]:
				b.append(0b01000100) # Load NR51
				b.append(0x55 | ((step_buffer[5] & 0x88) | (step_buffer[1] & 0x22)))
				pack_count += 1

			# CH2
			if CHon[0]:
				pack_count += 1
				# We gotta order the data from lowest register to highest
				sub_b = [0b00000001]
				if args.swapduty:
					sub_b = [0b00000000] # 0 is the NR1X write command

				# Duty
				if flag_buffer[3]:
					sub_b[0] |= 0x40 # NR21 flag
					sub_b.append(step_buffer[3] << 6)

				# Volume
				if flag_buffer[2]:
					sub_b[0] |= 0x20 # NR22 flag
					sub_b.append(step_buffer[2] << 4)

				# Freq and trigger
				if flag_buffer[4]:
					sub_b[0] |= 0x18 # NR23 + NR24 flags
					f = get_freq(step_buffer[4], pitch_offset)
					sub_b.append(f & 255)
					sub_b.append((f >> 8) | (int(flag_buffer[2]) << 7)) # We only retrigger when a new volume was set

				if sub_b[0] != 1:
					b.extend(sub_b)

			if CHOver[0]:
				pack_count += 1
				if args.swapduty:
					b.append(0b00101000) # NR12 and NR14
				else:
					b.append(0b00101001) # NR22 and NR24
				b.append(0)
				b.append(0x80)

			if CHon[1]:
				pack_count += 1
				sub_b = [0b00000011]
				# Volume
				if flag_buffer[6]:
					sub_b[0] |= 0x20 # NR42 flag
					sub_b.append(step_buffer[6] << 4)
				# freq
				if flag_buffer[7]:
					sub_b[0] |= 0x10 # NR43 flag
					sub_b.append(step_buffer[7])
				# Trigger
				if flag_buffer[6]:
					sub_b[0] |= 0x08 # NR42 flag
					sub_b.append(0x80)

				if sub_b[0] != 1:
					b.extend(sub_b)

			if CHOver[1]:
				pack_count += 1
				b.append(0b00101011) # NR42 and NR44
				b.append(0)
				b.append(0x80)

			b[0] |= pack_count

			toxa_buf.extend(b)

			r = ((step_buffer[0])*args.realspeed)-1
			for i in range(r//15):
				toxa_buf.append(0xf0)
			if r%15 != 0:
				toxa_buf.append((r%15) << 4)

		# VGM
		if args.vgm:

			duty_inc = 5 # to shift between CH1 and CH2 addresses

			if args.swapduty:
				duty_inc = 0

			# Pan
			if n == 0 or flag_buffer[1] or flag_buffer[5]:
				vgm_buf.write(bytes([0xB3, 0x15, (0x55 | (step_buffer[5] & 0x88) | (step_buffer[1] & 0x22))]) )

			if CHUsed[0]:
				f = get_freq(step_buffer[4], pitch_offset)
				w = False
				# Duty
				if flag_buffer[3]:
					vgm_buf.write(bytes([0xB3, 0x01 + duty_inc, step_buffer[3] << 6]))
					w = True
				# Volume
				if flag_buffer[2]:
					vgm_buf.write(bytes([0xB3, 0x02 + duty_inc, step_buffer[2] << 4]))
					w = True
				# Freq
				if flag_buffer[4]:	
					vgm_buf.write(bytes([0xB3, 0x03 + duty_inc, f & 255]))
					w = True
				if w:
					vgm_buf.write(bytes([0xB3, 0x04 + duty_inc, (f >> 8) | (int(flag_buffer[2]) << 7)]))
				

			if CHUsed[1]:
				# Volume
				if flag_buffer[6]:
					vgm_buf.write(bytes([0xB3, 0x11, step_buffer[6] << 4]))
					
				# Freq
				if flag_buffer[7]:
					vgm_buf.write(bytes([0xB3, 0x12, step_buffer[7]]))
				
				if flag_buffer[6] or flag_buffer[7]:
					vgm_buf.write(bytes([0xB3, 0x13, 128]))

			
			# 1 256th of a second = 65535/90 ~= 730
			ad = 730
			if args.export:
				ad = 172
			wait = (step_buffer[0] * args.realspeed) * ad
			if wait > 0xffff:
				a = wait
				while 1:
					a -= 0xffff
					vgm_buf.write(bytes([0x61, 0xff, 0xff]))
					if a <= 0xffff and a  >= 0:
						vgm_buf.write(bytes([0x61, a & 255, a >> 8]))
						break
			else:
				vgm_buf.write(bytes([0x61, wait & 255, wait >> 8]))
			wait_counter += wait

		if args.libbet:
			# CH2
			p = [0x00] # Master byte

			if CHUsed[0]:
				d = step_buffer[3]
				# Since 0xFF is the terminator byte, we avoid
				# Setting duty to 3 as that could lead to 0xFF
				if d == 3:
					d = 1

				p[0] |= d

				if flag_buffer[2]:
					p[0] |= 0x20
					p.append(step_buffer[2] << 4)
				# Freq
				if flag_buffer[4]:
					p[0] |= 0x10
					p.append(step_buffer[4])
			# CH4
			elif CHUsed[1]:
				if flag_buffer[6]:
					p[0] |= 0x20 # deep parameter
					p.append(step_buffer[6] << 4)
				if flag_buffer[7]:
					p[0] |= 0x10 # Pitch change
					p.append(step_buffer[7])

			# Length
			s = step_buffer[0]-1
			if s > 15:
				p[0] |= s % 15
				for i in range(s//15):
					p.append(0x0f)
			else:
				p[0] |= s

			libbet_buf.extend(p)

		if args.valen:
			step = [0]

			# Set Speed
			if flag_buffer[0]:
				step[0] |= 0x40
				step.append(step_buffer[0]-1)
			# Set Duty
			if flag_buffer[3]:
				step[0] |= 0x20
				step.append(step_buffer[3] << 6)
			# Set Note
			if flag_buffer[4]:
				step[0] |= 0x10
				step.append(step_buffer[4] << 1)
			# Set Freq
			if flag_buffer[7]:
				step[0] |= 0x08
				step.append(step_buffer[7])
			# Set CH2 vol
			if flag_buffer[2]:
				step[0] |= 0x04
				step.append(step_buffer[2] << 4)
			# Set CH4 vol
			if flag_buffer[6]:
				step[0] |= 0x02
				step.append(step_buffer[6] << 4)
			# Set Panning
			if flag_buffer[1] or flag_buffer[5]:
				step[0] |= 0x01
				p = 0
				if CHUsed[0]:
					p |= (step_buffer[1] & 0x22)
				if CHUsed[1]:
					p |= (step_buffer[5] & 0x88)
				step.append(p)
			valfx_buf.append(step)

	if args.vgm:
		finalize_vgm(vgm_buf, CHUsed, wait_counter)
		if args.export:
			cd = os.getcwd()
			c = VGMPlay.split()
			c.append(cd + "/" + args.out + args.name + ".vgm")
			c.append("--dump-wav")
			p = subprocess.run(c, text=True, cwd=VGMPlayDir)

	if args.libbet:
		print(libbet_buf)

	if args.valen:
		valfx_buf.append(0x80)
		print(str(valfx_buf).replace("[","").replace("]",""))

	if args.toxa:
		toxa_buf.append(1) # Final packet
		toxa_buf.append(7) # Kill packet
		mask = 0xf ^ (CHUsed[0] << 2 | CHUsed[1])
		if args.swapduty:
			mask = 0xf ^ (CHUsed[0] << 3 | CHUsed[1])

		# C file
		Cfile = open(args.out + args.name + ".c", "w")
		Cfile.write("#pragma bank 255\n\n")
		Cfile.write("#include <gbdk/platform.h>\n")
		Cfile.write("#include <stdint.h>\n\n")
		Cfile.write("BANKREF(" + args.name + ")\n")
		Cfile.write("const uint8_t " + args.name + "[] = {\n")
		Cfile.write(array_to_hex(toxa_buf))
		Cfile.write("\n};\n")
		Cfile.write("void AT(" + str(mask) + ") __mute_mask_" + args.name + ";")
		Cfile.close()

		# H file
		Hfile = open(args.out + args.name + ".h", "w")
		Hfile.write("#ifndef __" + args.name + "_INCLUDE__\n")
		Hfile.write("#define __" + args.name + "_INCLUDE__\n\n")
		Hfile.write("#include <gbdk/platform.h>\n")
		Hfile.write("#include <stdint.h>\n\n")
		Hfile.write("#define MUTE_MASK_" + args.name + " " + str(mask))
		Hfile.write("\n\nBANKREF_EXTERN(" + args.name + ")\n")
		Hfile.write("extern const uint8_t " + args.name + "[];\n")
		Hfile.write("extern void __mute_mask_" + args.name + ";\n")
		Hfile.write("\n#endif")
		Hfile.close()

		print(args.name + ".c" + " succesfully written.")
		print(args.name + " Size: " + str(len(toxa_buf)) + " bytes.\n")

	if args.fxh:
		if CHUsed[0]:
			fxh_buf[0x300] |= 0x30
		if CHUsed[1]:
			fxh_buf[0x300] |= 0x03
		fxh_buf[0x200] = priority
		FXHOut = open(args.out + args.name + ".sav", "wb")
		FXHOut.write(fxh_buf)
		FXHOut.close()

	# Save C H file CBT-FX
	if args.cbt:
		# C file
		Cfile = open(args.out + args.name + ".c", "w")
		Cfile.write(_header(CHUsed, priority, cbtfx_buf[1]-1))
		Cfile.write("const unsigned char " + args.name + "[] = {\n")
		Cfile.write(array_to_hex(cbtfx_buf))
		Cfile.write("\n};")
		Cfile.close()

		# H file
		Hfile = open(args.out + args.name + ".h", "w")
		Hfile.write(_header(CHUsed, priority, cbtfx_buf[1]-1))
		Hfile.write("#ifndef __" + args.name + "_h_INCLUDE\n")
		Hfile.write("#define __" + args.name + "_h_INCLUDE\n")
		Hfile.write("#define CBTFX_PLAY_" + args.name + " CBTFX_init(&" + args.name + "[0])\n")
		Hfile.write("extern const unsigned char " + args.name + "[];\n")
		Hfile.write("#endif")
		Hfile.close()

		print(args.name + ".c" + " succesfully written.")
		print(args.name + " Size: " + str(len(cbtfx_buf)) + " bytes.\n")

if args.flist:
	flist = open(args.flist[0],"r")
	while 1:
		l = flist.readline()
		if "===" in l:
			n = l.split()[1]
			args.name = n
			stringb = ""
			args.sgb = []
			args.realspeed = 4
			args.swapduty = False

			# Get defines
			while 1:
				l = flist.readline()
				if l == "\n":
					break
				else: # Found define
					ar = l.split()

					if ar[0] == "SGB":
						args.sgb.append(ar[1])
						args.sgb.append(int(ar[2]))
						args.sgb.append(int(ar[3]))
						args.sgb.append(int(ar[4]))

					if ar[0] == "PRI":
						priority = int(ar[1])

					if ar[0] == "REALSPEED":
						args.realspeed = 1

					if ar[0] == "SWAPDUTY":
						args.swapduty = True
			# Get string
			while 1:
				l = flist.readline()
				if l == "\n" or l == "":
					break
				else: # Found sfx data
					stringb += l
			fur = stringb.split("\n")[2:]
			main()
		if "" == l:
			sys.exit()
main()
