from random import randint
import time
import base64
import pygame
from pygame.locals import *
import os
from Adafruit_IO import MQTTClient
import feed
import sys
import signal

# Set to your Adafruit IO key & username below.
ADAFRUIT_IO_KEY      = 'SECRET'
ADAFRUIT_IO_USERNAME = 'SECRET'  # See https://accounts.adafruit.com to find your username.

PIC_FEED = 'pic'
TEMP_FEED = 'deck-temp'
OUT_DIR = '/home/pi/adaiot/'

os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
pygame.init()
pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode((320, 240))
lcd.fill((0,0,0))
font_big = pygame.font.Font(None, 40)
BLACK = 0,0,0
GREEN = 0,255,0
RED = 255,0,0
WHITE = 255,255,255

image_surface = None
text_surface = None
lum = 100
page = 0
# Define callback functions which will be called when certain events happen.
def connected(client):
    print 'MQTT Connected'
    client.subscribe(PIC_FEED)
    client.subscribe(TEMP_FEED)

def disconnected(client):
    print 'MQTT Disconnected from Adafruit IO!'

def message(client, feed_id, payload):
    global image_surface, text_surface, lum
    if feed_id == PIC_FEED:
        print 'MQTT received pic'
        fh = open(OUT_DIR+"testjr.jpg", "wb")
        fh.write(payload.decode('base64'))
        fh.close()
        image_surface = pygame.image.load(OUT_DIR+"testjr.jpg")
        col = image_surface.get_at((30,220))
        lum = (0.299*col.r + 0.587*col.g + 0.114*col.b)
        # IF RESIZE REQUIRED
        #surf = pygame.transform.scale(surf, (320, 240))
    elif feed_id == TEMP_FEED:
        print 'MQTT received temp: {0}'.format(payload)
        if lum < 75:
            col = WHITE
        else:
            col = BLACK
        text_surface = font_big.render(payload+u'\u00B0C', True, col)
    show_dash()

def show_dash():
    if page == 0:
        if image_surface:
            lcd.blit(image_surface, (0,0))
        else:
            lcd.fill((0,0,0))
        if text_surface:
            rect = text_surface.get_rect()
            rect.x = 10
            rect.y = 240-rect.height-2
            lcd.blit(text_surface, rect)
    elif page == 1:
        feed_surface = pygame.image.load(OUT_DIR+"temps.png")
        lcd.blit(feed_surface, (0,0))

    pygame.display.update()

def switch_page():
    global page
    if page == 1:
        page = 0
    else:
        page += 1

    show_dash()

def signal_handler(signal, frame):
    print 'Received signal - exitting'
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

# Connect to the Adafruit IO server.
print 'Attempting to connect MQTT...'
client.connect()

client.loop_background()
chart_counter = 0
while True:
    for event in pygame.event.get():
        if event.type is MOUSEBUTTONUP:
            switch_page()
    time.sleep(0.1)
    # Create a new chart approx every 5 mins
    chart_counter += 1
    if chart_counter == 3000:
        chart_counter = 0
        feed.ChartThread(ADAFRUIT_IO_KEY, TEMP_FEED, OUT_DIR).start()
