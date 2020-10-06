import pyfirmata
import time
from RestAPI import webServerRun

board = pyfirmata.Arduino('COM3')

def f():
    while True:
        board.digital[7].write(1)
        time.sleep(1)
        board.digital[7].write(0)
        time.sleep(1)

webServerRun()
f()
print('ardu started')
