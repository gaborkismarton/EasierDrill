from machine import Pin, ADC
import _thread
from ultra import ultra
from accelerometer import Accelerometer
from machine import Pin, ADC
from utime import sleep_ms
from math import sqrt

# Joystick pins
xAxis = ADC(Pin(27))
yAxis = ADC(Pin(26))
        
accA = Accelerometer()
accB = Accelerometer()
accC = Accelerometer()

def core1():
    # Joystick input
    x = xAxis.read_u16()
    y = yAxis.read_u16()
    sleep_ms(100)
    if sqrt(x*x+y*y) > 0.8:
        if x > 0.7 or x < -0.7:
            if x > 0.7:
                dir = "up"
            else:
                dir = "down"
        else:
            if y > 0.7:
                dir = "right"
            else:
                dir = "left"
    else:
        dir = None
    # Ultrasonic sensor
    distance = ultra()
    # Accelerometers
    xa, ya, za = accA.acceleration(bus=1, sda=Pin(6), scl=Pin(7))
    xb, yb, zb = accB.acceleration(bus=0, sda=Pin(8), scl=Pin(9))
    xc, yc, zc = accC.acceleration(bus=0, sda=Pin(10), scl=Pin(11))

def core2():
    pass

if __name__ == "__main__":
    _thread.start_new_thread(core2, ())
    core1()
    