import argparse
parser = argparse.ArgumentParser()
parser.add_argument("txt", help="FamiTracker TXT Input file")
args = parser.parse_args()

with open(args.txt, 'r') as txt:
    o = txt.read().split("\n")
    i = 0
    while 1:
        # search string
        i += 1
        if 'INSTN163' in o[i]:
            w_count = int(o[i].split()[9])
            print("Wave count:",w_count)
            for n in range(w_count):
                i += 1
                w = o[i].split()
                wb = []
                for a in range(0,32):
                    wb.append(int(w[4+a]))
                fout = open(args.txt + "_" + str(n) + ".ugw","wb")
                fout.write(bytearray(wb))
                fout.close()
            break
