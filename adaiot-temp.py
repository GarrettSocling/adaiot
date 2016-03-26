import time
import Adafruit_MCP9808.MCP9808 as MCP9808
from Adafruit_IO import Client

aio = Client('SECRET')
  
sensor = MCP9808.MCP9808()
sensor.begin()

def get_temperature():
        temp = sensor.readTempC()
        return '{0:0.3F}'.format(temp)

while True:
    try:
        aio.send('deck-temp', get_temperature() )
    except:
        print "Failed to send"
    time.sleep(30)
