### hUGEYE - A ROM analizer for finding hUGEDriver tracks

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("rom", help="Input ROM to analize.")
parser.add_argument("-t","--tolerance", help="Number of instruments to check, helps with optimized songs (0-15)",type=int, default=15)
args = parser.parse_args()

with open(args.rom, "rb") as r:
	rom = r.read()

# Store "Possible" addresses here, filter out later
huge_tracks = []

# CHECKS FOR VALID HUGE TRACK:
# - 10 words following the first byte are less than 0x8000
# - Each word should be at least 

for i in range(len(rom)):
	idx = i + 1 # Skip tempo byte
	if rom[i] == 0 or rom[i] > 20:
		continue

	valid = True


	for n in range(10):
		# Order count address
		if int.from_bytes(rom[idx:idx + 2], "little") >= 0x7fff:
			valid = False
		idx += 2

	if valid == True:
		huge_tracks.append(i)

# Filter results 
for n in huge_tracks:

	# Get current bank
	b = int((n & ~0x3fff) / 0x4000)
	ad = n & 0x3fff
	r = rom[(b * 0x4000):(b + 1) * 0x4000]

	valid = True

	# Check duty instruments
	ins_ad = int.from_bytes(r[ad + 11:ad + 13], "little") & 0x3fff
	idx = 0
	for m in range(args.tolerance):
		# CHECKS TO PASS:
		# - Highmask & 0x80
		# - Highmask & 0x3F == 0
		# - NR10 & 0x80 == 0
		NR10 = r[(ins_ad + idx) & 0x3fff]
		idx += 1
		NR11 = r[(ins_ad + idx) & 0x3fff]
		idx += 1
		NR12 = r[(ins_ad + idx) & 0x3fff]
		idx += 1
		MASK = r[(ins_ad + idx) & 0x3fff]
		idx += 1

		if MASK & 0x80 == 0:
			valid = False
		if MASK & 0x3f != 0:
			valid = False
		if NR10 & 0x80 != 0:
			valid = False


	# Check wave instruments
	ins_ad = int.from_bytes(r[ad + 13:ad + 15], "little") & 0x3fff
	idx = 0
	for m in range(args.tolerance):
		# CHECKS TO PASS:
		# - NR32 & 0x9f == 0
		# - Wave index < 16
		# - highmask & 0x80
		# - Highmask & 0x3F == 0

		NR31 = r[(ins_ad + idx) & 0x3fff]
		idx += 1
		NR32 = r[(ins_ad + idx) & 0x3fff]
		idx += 1
		INDX = r[(ins_ad + idx) & 0x3fff]
		idx += 1
		MASK = r[(ins_ad + idx) & 0x3fff]
		idx += 1

		if NR32 & 0x9F != 0:
			valid = False

		if INDX > 15:
			valid = False

		if MASK & 0x80 == 0:
			valid = False

		if MASK & 0x3f != 0:
			valid = False

	if valid:
		print("VALID HEADER FOUND AT ADDRESS {ad} BANK {bk}".format(ad=hex(ad), bk=hex(b)))