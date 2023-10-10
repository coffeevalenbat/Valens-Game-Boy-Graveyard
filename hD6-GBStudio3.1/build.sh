rgbasm -DGBDK -ohUGEDriver.obj -i.. hUGEDriver.asm
python3 rgb2sdas.py -b0 hUGEDriver.obj
sdar q hUGEDriver.lib hUGEDriver.o
rm hUGEDriver.o hUGEDriver.obj