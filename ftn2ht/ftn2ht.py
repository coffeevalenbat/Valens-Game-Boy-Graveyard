import pyperclip
ft = pyperclip.paste().split("\n")[1:]
t = ""
for i in range(len(ft)-1):
	note = str(ft[i]).split()[3]
	n = note[:2]
	o = note[-1:]
	if o.isdigit():
		o = str(int(o) + 2)
	t += "|" + n + o + "\n"
pyperclip.copy(t)