# DMW2UGW
# Converts Deflemask Game Boy .dmw wavetable files to hUGEtracker .ugw wavetable files
#
# Parameters:
#
#	1	-	The input .dmw file		(Required)
#	2	-	The output .ugw file	(Required)

import argparse

parser = argparse.ArgumentParser(description='Converts Deflemask .dmw files to hUGEtracker .ugw files')
parser.add_argument("input", help="input .dmw file")
parser.add_argument("output", help="output .ugw file")
args = parser.parse_args()

def toint(byte):
	return int.from_bytes(byte, "big")

dmw = open(args.input,"rb")	# Open dmw as binary

# Set some extra values
buffer_wave = [0] * 32	# Empty array of 32 bytes of length
buffer_wave_display = [""] * 16
dmw_v = 0	# 0 == Old version, 1 == New version
data_length = 1	# 1 == Old, 4 == New
data_shift = 1	# 1 == Old, 25 == New

print("Length: " + str(toint(dmw.read(1))))

# Bump up the pointer to the next bit of important data
dmw.read(3)

if toint(dmw.read(1)) == 255:
	print("File version: New (>=1.0)")
	dmw_v = 1
	data_length = 4
	data_shift = 24
else:
	print("File version: Old (<1.0)")

if dmw_v:
	dmw.read(1)
	print("Depth: " + str(toint(dmw.read(1))))

for i in range(32):
	buffer_wave[i] = toint(dmw.read(data_length)) >> data_shift

# 2D Print
print("________________________________________________________________")
for i in range(16):
	for a in range(32):
		if buffer_wave[a] == i:
			buffer_wave_display[i] += "■ "
		else:
			buffer_wave_display[i] += "  "
print(*buffer_wave_display[::-1], sep = "\n")
print("________________________________________________________________")
	
# Output .ugw
ugw = open(args.output, "wb")
ugw.write(bytearray(buffer_wave))

print("Wavetable succesfully written to " + args.output)

ugw.close()
dmw.close()
