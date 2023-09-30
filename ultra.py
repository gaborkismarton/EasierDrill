from machine import Pin
from utime import ticks_us, sleep_us

trigger = Pin(16, Pin.OUT)
echo = Pin(17, Pin.IN)
def ultra():
   trigger.low()
   sleep_us(2)
   trigger.high()
   sleep_us(5)
   trigger.low()
   while echo.value() == 0:
       signaloff = ticks_us()
   while echo.value() == 1:
       signalon = ticks_us()
   timepassed = signalon - signaloff
   distance = (timepassed * 0.0343) / 2
   return distance