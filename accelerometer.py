from machine import Pin, I2C
from utime import sleep_ms
from ustruct import unpack

# Registers
_R_WHOAMI = 0x0F
_ID = 0x33
_I2C_ADDRESS = 0x19
_OUT_X_L = 0x28
_CTRL_REG_1 = 0x20
_CTRL_REG_2 = 0x21
_CTRL_REG_3 = 0x22
_CTRL_REG_4 = 0x23
_CTRL_REG_5 = 0x25
_INT1_SRC = 0x31
_CLICK_CFG = 0x38
_CLICKSRC = 0x39
_CLICK_THS = 0x3A
_TIME_LIMIT = 0x3B
_TIME_LATENCY=0x3C
_TIME_WINDOW = 0x3D
_STATUS_REG = 0x27

# Helper functions    
def _set_bit(x, n):
    return x | (1 << n)

def _clear_bit(x, n):
    return x & ~(1 << n)

def _write_bit(x, n, b):
    if b == 0:
        return _clear_bit(x, n)
    else:
        return _set_bit(x, n)
    
def _read_bit(x, n):
    return x & 1 << n != 0
    
def _write_crumb(x, n, c):
    x = _write_bit(x, n, _read_bit(c, 0))
    return _write_bit(x, n+1, _read_bit(c, 1))

class Accelerometer():    
    def __init__(self, bus=0, freq=400000, sda=Pin(8), scl=Pin(9), _range=2, rate=400):
        self.addr = _I2C_ADDRESS
        self.i2c = I2C(bus, sda=sda, scl=scl)
        x = self.i2c.readfrom_mem(self.addr, _R_WHOAMI, 1)
        sleep_ms(5) # guarantee startup
        # Write basic, unchanging settings to the CTRL_REG1,4
        d = 0x07 # Enable X,Y,Z axes
        x = int.to_bytes(d,1,'big')
        self.i2c.writeto_mem(self.addr, _CTRL_REG_1, x)
        d = 0x88 # Block Data Update an High Resolution Mode
        x = int.to_bytes(d,1,'big')
        self.i2c.writeto_mem(self.addr, _CTRL_REG_4, x)
        # Range setting
        self.range = _range
        valid_ranges = {2:0b00, 4:0b01, 8:0b10, 16:0b11} # key:value -> range[g] : binary code for register
        rr = valid_ranges[_range]
        val = self.i2c.readfrom_mem(self.addr, _CTRL_REG_4, 1)
        val = int.from_bytes(val, 'little')
        val = _write_crumb(val, 4, rr) # Write new range code
        self.i2c.writeto_mem(self.addr, _CTRL_REG_4, int.to_bytes(val,1,'big'))
        # Rate setting
        self.rate = rate
        valid_rates = {0:0b0000, 1:0b0001, 10:0b0010, 25:0b0011, 50:0b0100, 100:0b0101, 200:0b0110, 400:0b0111} # key:value -> rate[Hz] : binary code for register
        rr = valid_rates[rate]
        val = self.i2c.readfrom_mem(self.addr, _CTRL_REG_1, 1)  # Get value from register
        val = int.from_bytes(val, 'little')
        val &= 0x0F # mask off last 4 bits
        val = val | rr << 4
        self.i2c.writeto_mem(self.addr, _CTRL_REG_1, int.to_bytes(val,1,'little'))

    def acceleration(self):
        """Return x,y,z acceleration in a 3-tuple. unit: :math:`m/s^2"""
        d = bytes(self.i2c.readfrom_mem(self.addr, (_OUT_X_L | 0x80) | 0x80, 6))
        x, y, z = unpack('<hhh', d)
        divisors = {2:1670.295, 4:835.1476, 8:417.6757, 16:139.1912} # (LSB/1g) / 9.80665
        den = divisors[self.range]
        x /= den
        y /= den
        z /= den
        return (x, y, z)