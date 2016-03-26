#!/usr/bin/python

from Adafruit_IO import Client
from PIL import Image
import base64

aio = Client('SECRET')
BASE_DIR='/home/pi/'
SRC_FILE=BASE_DIR+'lastsnap.jpg'
DST_FILE=BASE_DIR+'lastsmall.jpg'

fd_img = open(SRC_FILE, 'r')
img = Image.open(fd_img)
size = 320, 240
img.thumbnail(size)
img.save(DST_FILE, img.format)
fd_img.close()
 
with open(DST_FILE, "rb") as imageFile:
    str = base64.b64encode(imageFile.read())
  
aio.send('pic', str )
