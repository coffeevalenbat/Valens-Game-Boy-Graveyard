rgbasm -DGBDK -ohUGEDriver.obj -i.. hUGEDriver.asm
./rgb2sdas -b0 hUGEDriver.obj
sdar q hUGEDriver.lib hUGEDriver.obj.o
rm hUGEDriver.obj.o hUGEDriver.obj