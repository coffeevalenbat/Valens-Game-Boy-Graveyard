### eUGEne.py - a hUGEDriver dissasembler

# This tool allows you to decompile hUGEDriver tracks from a ROM file back into .uge files, 
# all you need is the memory address (AKA what the gameboy sees) and the bank number

# Caveats:
#	- Only supports v5 songs, so a few homebrew games such as G-ZERO and 
#	  Shock Lobster + any GB Studio 3/3.1 games using hUGEDriver.
#	- No special forks/mods of hUGEDriver, since there's no way to guess what's what, thus
#	  mods such as the realtime compression fork or fortISSImo are gonna output garblo data.

# This tool is NOT made for theft, the last thing I want is to hurt any fellow composers by 
# having their music be stolen with this tool, this is merely a tool of research and 
# reverse engineering, with useful casepoints such as recovering a song source from a 
# compiled ROM, learning how other people's songs do certain effects or doing High Quality
# rips.

# If you steal other people's songs using this tool, fuck you! :) And hope hell has a shitty dark spot for u <3
# - Valen

# TODO:
# Noise instruments still seem fucked, specially length

class DutyInstrument:
	index = 0
	name = ""
	length = 0
	duty_cycle = 0
	initial_volume = 0
	volume_sweep_change = 0
	volume_sweep_direction = 1
	frequency_sweep_time = 0
	frequency_sweep_shift = 0

class WaveInstrument:
	index = 0
	name = ""
	length = 0
	volume = 0
	wave_index = 0

class NoiseInstrument:
	index = 0
	name = ""
	length = 0
	initial_volume = 0
	volume_sweep_change = 0
	volume_sweep_direction = 1
	shift_clock_mask = 0
	dividing_ratio = 0
	bit_count = 0
	noise_macro = []

class Song:
	name = ""
	artist = ""
	comment = ""
	duty_instruments = []
	wave_instruments = []
	noise_instruments = []
	waves = []
	ticks_per_row = 0
	patterns = []
	orders = [[],[],[],[]]
	order_cnt = 0

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("rom", help="Input ROM to decompile from.")
parser.add_argument("addr", help="Address of the track to decompile.")
parser.add_argument("bank", help="Bank of the track to decompile.")
parser.add_argument("out", help="Name for the output .uge file.")

noteConsts = ["C_3","Cs3","D_3","Ds3","E_3","F_3","Fs3","G_3","Gs3","A_3","As3","B_3","C_4","Cs4","D_4","Ds4","E_4","F_4","Fs4","G_4","Gs4","A_4","As4","B_4","C_5","Cs5","D_5","Ds5","E_5","F_5","Fs5","G_5","Gs5","A_5","As5","B_5","C_6","Cs6","D_6","Ds6","E_6","F_6","Fs6","G_6","Gs6","A_6","As6","B_6","C_7","Cs7","D_7","Ds7","E_7","F_7","Fs7","G_7","Gs7","A_7","As7","B_7","C_8","Cs8","D_8","Ds8","E_8","F_8","Fs8","G_8","Gs8","A_8","As8","B_8"]

hexLUT = "0123456789ABCDEF"

args = parser.parse_args()
args.addr = int(args.addr, 16)
args.bank = int(args.bank, 16)
addr = args.addr

with open(args.rom,"rb") as f:
	o = 0
	if args.bank != 0:
		o = 0x4000 * (args.bank)
		args.addr &= 0x3fff
	rom = f.read()[o:o+0x4000]

offset = args.addr
#with open("debug.bin","wb") as o:
	#o.write(rom)
ticks_per_row = rom[offset]
offset += 1

order_cnt_addr = int.from_bytes(rom[offset:offset + 2], "little") & 0x3fff
offset += 2

order_ch1_addr = int.from_bytes(rom[offset:offset + 2], "little") & 0x3fff
offset += 2

order_ch2_addr = int.from_bytes(rom[offset:offset + 2], "little") & 0x3fff
offset += 2

order_ch3_addr = int.from_bytes(rom[offset:offset + 2], "little") & 0x3fff
offset += 2

order_ch4_addr = int.from_bytes(rom[offset:offset + 2], "little") & 0x3fff
offset += 2

duty_ins_addr = int.from_bytes(rom[offset:offset + 2], "little") & 0x3fff
offset += 2

wave_ins_addr = int.from_bytes(rom[offset:offset + 2], "little") & 0x3fff
offset += 2

noise_ins_addr = int.from_bytes(rom[offset:offset + 2], "little") & 0x3fff
offset += 2

routines_addr = int.from_bytes(rom[offset:offset + 2], "little")  & 0x3fff
offset += 2

waves_addr = int.from_bytes(rom[offset:offset + 2], "little") & 0x3fff

song = Song()

# To avoid messing with banks, we AND out to reset offset to whatever bank were in
args.addr = 0
offset = args.addr
song.ticks_per_row = ticks_per_row
song.order_cnt = rom[order_cnt_addr] >> 1

# Collect waves
offset += waves_addr
for n in range(16):
	w = []
	for m in range(16):
		a = (rom[offset] & 0xF0) >> 4
		b = (rom[offset] & 0x0F)
		w.append(a)
		w.append(b)
		offset += 1
	song.waves.append(w)

# get addresses for patterns to decompile
orders_d = [order_ch1_addr, order_ch2_addr, order_ch3_addr, order_ch4_addr]
todo_patterns_ad = []
for n in range(4):

	# Reset to bank start again
	offset = args.addr

	offset += orders_d[n]

	for m in range(song.order_cnt):
		ad = int.from_bytes(rom[offset:offset + 2], "little") & 0x3fff
		if ad not in todo_patterns_ad:
			todo_patterns_ad.append(ad)
		index = todo_patterns_ad.index(ad)
		song.orders[n].append(index)
		offset += 2

# Decompile patterns
for m in range(len(todo_patterns_ad)):
	offset = args.addr
	offset += todo_patterns_ad[m]

	p = []
	for i in range(64):
		note = rom[offset]
		offset += 1
		inst = rom[offset] >> 4
		effc = rom[offset] & 0xF
		offset += 1
		param = rom[offset]
		offset += 1
		p.append([note, inst, effc, param])
	song.patterns.append(p)

# Decompile instruments

# Duty
offset = args.addr
offset += duty_ins_addr
for n in range(15):
	ins = DutyInstrument()
	
	NR10 = rom[offset]
	offset += 1

	NR11 = rom[offset]
	offset += 1

	NR12 = rom[offset]
	offset += 1

	mask = rom[offset]
	offset += 1

	ins.frequency_sweep_time = NR10 >> 4
	ins.frequency_sweep_shift = NR10 & 7
	if NR10 & 0x08:
		ins.frequency_sweep_shift = - ins.frequency_sweep_shift

	ins.duty_cycle = NR11 >> 6
	
	ins.length = (NR11 & 0x3F) if (NR11 & 0x3F) != 0 else None

	ins.initial_volume = NR12 >> 4

	ins.volume_sweep_change = NR12 & 0x7

	if NR12 & 0x8:
		ins.volume_sweep_direction = 0

	song.duty_instruments.append(ins)


# Wave
offset = args.addr
offset += wave_ins_addr
for n in range(15):
	ins = WaveInstrument()
	
	NR31 = rom[offset]
	offset += 1
	
	NR32 = rom[offset]
	offset += 1
	
	wave_index = rom[offset]
	offset += 1

	NR34 = rom[offset]
	offset += 1

	ins.length = None if NR31 == 0 else NR31
	ins.volume = NR32 >> 5
	ins.wave_index = wave_index

	song.wave_instruments.append(ins)

# Noise
offset = args.addr
offset += noise_ins_addr
for n in range(15):
	ins = NoiseInstrument()
	
	NR42 = rom[offset]
	offset += 1

	mask = rom[offset]
	offset += 1

	ins.noise_macro = []
	for m in range(6):
		macro = int.from_bytes([rom[offset]],"little",signed=True)
		ins.noise_macro.append(macro)
		offset += 1

	ins.initial_volume = NR42 >> 4

	ins.volume_sweep_change = NR42 & 0x7

	if NR42 & 0x8:
		ins.volume_sweep_direction = 0

	ins.length = mask & 0x3f if mask & 0x40 else None
	ins.bit_count = 7 if mask & 0x80 else 15
	
	song.noise_instruments.append(ins)

song.comment = """Ripped from {rom} using eUGEne.py.
Song starting address: {ad}
Song Bank: {bk}

eUGEne.py written by Valen. do NOT use this tool for theft :).""".format(rom=args.rom,ad=hex(addr),bk=hex(args.bank))

song.name = "Song from " + args.rom

song.artist = "eUGEne!"

# Write output file
idx = 0

buffer = bytearray([0] * 1024 * 1024)

def addUint8(n):
	global idx
	buffer[idx] = n.to_bytes(1,"little")[0]
	idx += 1

def addUint32(n):
	global idx
	b = n.to_bytes(4,"little")
	buffer[idx] = b[0]
	buffer[idx + 1] = b[1]
	buffer[idx + 2] = b[2]
	buffer[idx + 3] = b[3]
	idx += 4

def addInt8(n):
	global idx
	buffer[idx] = n.to_bytes(1,"little",signed=True)[0]
	idx += 1

def addShortString(s):
	global idx
	addUint8(len(s))

	for n in range(255):
		buffer[idx] = ord(s[n] if n < len(s) else chr(0x69))
		idx += 1

def addDutyInstrument(type, i):
	addUint32(type)

	addShortString(i.name)
	addUint32(i.length if i.length != None else 0)
	addUint8(0 if i.length == None else 1)

	addUint8(i.initial_volume)

	addUint32(i.volume_sweep_direction)

	addUint8(i.volume_sweep_change)

	addUint32(i.frequency_sweep_time)
	addUint32(1 if i.frequency_sweep_shift < 0 else 0)
	addUint32(abs(i.frequency_sweep_shift))

	addUint8(i.duty_cycle)

	addUint32(0)
	addUint32(0)

	addUint32(0)
	addUint32(0)
	addUint32(0)

	for n in range(6):
		addInt8(0)

def addWaveInstrument(type, i):
	addUint32(type)

	addShortString(i.name)
	addUint32(i.length if i.length != None else 0)
	addUint8(0 if i.length == None else 1)

	addUint8(0)

	addUint32(0)

	addUint8(0)

	addUint32(0)
	addUint32(0)
	addUint32(0)

	addUint8(0)

	addUint32(i.volume)
	addUint32(i.wave_index)

	addUint32(0)
	addUint32(0)
	addUint32(0)

	for n in range(6):
		addInt8(0)

def addNoiseInstrument(type, i):
	addUint32(type)

	addShortString(i.name)
	addUint32(i.length if i.length != None else 0)
	addUint8(0 if i.length == None else 1)

	addUint8(i.initial_volume)

	addUint32(i.volume_sweep_direction)

	addUint8(i.volume_sweep_change)

	addUint32(0)
	addUint32(0)
	addUint32(0)

	addUint8(0)

	addUint32(0)
	addUint32(0)

	addUint32(0)
	addUint32(1 if i.bit_count == 7 else 0)
	addUint32(0)

	for n in range(6):
		addInt8(i.noise_macro[n])


addUint32(5) # Version
addShortString(song.name)
addShortString(song.artist)
addShortString(song.comment)

for n in range(15):
	addDutyInstrument(0, song.duty_instruments[n])

for n in range(15):
	addWaveInstrument(1, song.wave_instruments[n])

for n in range(15):
	addNoiseInstrument(2, song.noise_instruments[n])

for n in range(16):
	for m in range(32):
		addUint8(song.waves[n][m])

addUint32(song.ticks_per_row)

addUint32(len(song.patterns))

for n in range(len(song.patterns)):
	addUint32(n)
	for m in range(64):
		t = song.patterns[n][m]
		# In case any garblo data makes it in and errors out hT
		addUint32(t[0] if t[0] < 90 else 90)
		addUint32(t[1])
		addUint32(t[2])
		addUint8(t[3])

# Orders

for n in range(4):
	addUint32(len(song.orders[n]) + 1) # Off by one error
	for m in range(len(song.orders[n])):
		addUint32(song.orders[n][m])
	addUint32(0) # Off by one bug

# Empty routines
for n in range(16):
	addUint32(0)

with open(args.out,"wb") as out:
	out.write(buffer[0:idx])
