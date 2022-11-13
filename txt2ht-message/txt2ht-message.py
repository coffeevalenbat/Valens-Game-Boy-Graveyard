import argparse
parser = argparse.ArgumentParser()
parser.add_argument("message")
args = parser.parse_args()
s = args.message

hexLUT = "0123456789ABCDEF"

if len(s) & 1:
	s += " "

for n in range(0, len(s), 2):
	x = ord(s[n])
	y = ord(s[n+1])
	print("|C-3{ins}...{eff}{param}".format(ins=str(x>>4).zfill(2), eff=hexLUT[x & 0xF], param='%X' % y))
