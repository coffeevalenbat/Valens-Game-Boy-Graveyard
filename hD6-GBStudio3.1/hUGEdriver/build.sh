rgbasm -DGBDK -ohUGEDriver.obj hUGEDriver.asm
python3 rgb2sdas.py -m gbz80 -b0 hUGEDriver.obj
sdar q hUGEDriver.lib hUGEDriver.o
rm hUGEDriver.o hUGEDriver.obj