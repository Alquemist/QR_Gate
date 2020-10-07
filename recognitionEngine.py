# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 16:54:32 2018

@author: Dejan
"""
import pyzbar.pyzbar as pyzbar
import math
import time
import cv2 as cv
from dbHandlers import doesCodeExists
import math
import time
import threading
import pyfirmata
from threading import Thread
from queue import Queue
from dbHandlers import dbCleaner, doesCodeExists
from RestAPI import runServer


url = "rtsp://admin:admin@192.168.1.119:554/0"
delta_t = 1.5 # uzmi frame svakih delta_t sekundi
delay = 2 # kašnjenje strem-a
board = pyfirmata.Arduino('COM3')
pin = 7 # [INT] broj pina na arduino ploči
thresh = 127 #INT; 

Qf = Queue(-1)  # queue of frames to decode
Qd = Queue(-1)  # queue of decoded data
skip_frames = max(1, math.floor(delay / delta_t))


def QR_decoder(Qf, Qd, skip_frames, delta_t):
    print('decoder started')

    i = 0
    print(skip_frames)
    while i < skip_frames:
        Qf.get()
        i += 1
    while True:
        if not Qf.empty():
            print('decoding frame')
            img = Qf.get()
            clahe = cv.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
            clached = clahe.apply(img)
            frames = [img, clached]
            frames.append(cv.threshold(img, thresh, 255, cv.THRESH_BINARY)[1])
            frames.append(cv.threshold(clached, thresh, 255, cv.THRESH_BINARY)[1])
            frames.append(cv.threshold(img, 0, 255, cv.THRESH_OTSU)[1])
            frames.append(cv.threshold(clached, 0, 255, cv.THRESH_OTSU)[1])
            for frame in frames:
                decodedQRs = pyzbar.decode(frame)
                [print('decoded: ',code.data) for code in decodedQRs]
                if decodedQRs:
                    [Qd.put(qr.data) for qr in decodedQRs] #bytestring
        time.sleep(delta_t/2)

        # print('Qd len: ', Qd.qsize())
        # print('Qf len: ', Qf.qsize())


def rollCamera(Qf, url, delta_t):
    print('Kamera: Ide!')
    cap = cv.VideoCapture(url)
    fps = math.floor(cap.get(5))
    i_lim = fps * delta_t
    i = 0
    while True:
        try:
            frame = cap.read()[1]
            i += 1
            if i >= i_lim:
                Qf.put(cv.cvtColor(frame, cv.COLOR_BGR2GRAY))
                print('got frame')
                i = 0
        except Exception as err:
            print('error taking frame', err.args)
        
    cap.release()
    cv.destroyAllWindows()

def checkAndOpen(Qd):
    while True:
        if doesCodeExists(Qd.get().decode("utf-8") ):
            print('OPENT THE GATE')
            board.digital[pin].write(1)
            time.sleep(2)
            board.digital[pin].write(0)
            time.sleep(8)
            with Qd.mutex():
                Qd.queue.clear()

     
Thread(target=rollCamera, args=(Qf, url, delta_t,)).start()
Thread(target=QR_decoder, args=(Qf, Qd, skip_frames, delta_t)).start()
Thread(target=checkAndOpen, args=(Qd,)).start()
Thread(target=dbCleaner).start()
Thread(target=runServer).start()
#https://stackoverflow.com/questions/7624765/converting-an-opencv-image-to-black-and-white