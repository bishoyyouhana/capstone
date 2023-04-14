# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Quick test of RA8875 with Feather M4

import time
import busio
import digitalio
import board
import adafruit_ds3231
from time import struct_time


class BMP:
    def __init__(self, filename):
        self.filename = filename
        self.colors = None
        self.data = 0
        self.data_size = 0
        self.bpp = 0
        self.width = 0
        self.height = 0
        self.read_header()

    def read_header(self):
        if self.colors:
            return
        with open(self.filename, "rb") as f:
            f.seek(10)
            self.data = int.from_bytes(f.read(4), "little")
            f.seek(18)
            self.width = int.from_bytes(f.read(4), "little")
            self.height = int.from_bytes(f.read(4), "little")
            f.seek(28)
            self.bpp = int.from_bytes(f.read(2), "little")
            f.seek(34)
            self.data_size = int.from_bytes(f.read(4), "little")
            f.seek(46)
            self.colors = int.from_bytes(f.read(4), "little")

    def draw(self, disp, x=0, y=0):
        print("{:d}x{:d} image".format(self.width, self.height))
        print("{:d}-bit encoding detected".format(self.bpp))
        line = 0
        line_size = self.width * (self.bpp // 8)
        if line_size % 4 != 0:
            line_size += 4 - line_size % 4
        current_line_data = b""
        with open(self.filename, "rb") as f:
            f.seek(self.data)
            disp.set_window(x, y, self.width, self.height)
            for line in range(self.height):
                current_line_data = b""
                line_data = f.read(line_size)
                for i in range(0, line_size, self.bpp // 8):
                    if (line_size - i) < self.bpp // 8:
                        break
                    if self.bpp == 16:
                        color = convert_555_to_565(line_data[i] | line_data[i + 1] << 8)
                    if self.bpp in (24, 32):
                        color = color565(
                            line_data[i + 2], line_data[i + 1], line_data[i]
                        )
                    current_line_data = current_line_data + struct.pack(">H", color)
                disp.setxy(x, self.height - line + y)
                disp.push_pixels(current_line_data)
            disp.set_window(0, 0, disp.width, disp.height)

'''
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN)

while True:
    if GPIO.input(12) == 1:
        print ("LIGHT 1")
        time.sleep(1)
    elif GPIO.input(12) == 0:
        print ("LIGHT 0")
        time.sleep(1)
    else:
        pass
'''
try:
    import struct
except ImportError:
    import ustruct as struct

def convert_555_to_565(rgb):
    return (rgb & 0x7FE0) << 1 | 0x20 | rgb & 0x001F

from adafruit_ra8875 import ra8875
from adafruit_ra8875.ra8875 import color565

BLACK = color565(0, 0, 0)
RED = color565(255, 0, 0)
BLUE = color565(0, 255, 0)
GREEN = color565(0, 0, 255)
YELLOW = color565(255, 255, 0)
CYAN = color565(0, 255, 255)
MAGENTA = color565(255, 0, 255)
WHITE = color565(255, 255, 255)

# Configuration for CS and RST pins:
cs_pin = digitalio.DigitalInOut(board.GP10)
rst_pin = digitalio.DigitalInOut(board.GP9)

light_pin =  digitalio.DigitalInOut(board.GP12)
# True means it's dark


print("light pin val")
print("\n\n", light_pin.value)

# Config for display baudrate (default max is 6mhz):
BAUDRATE = 6000000

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=board.GP2, MOSI=board.GP3, MISO=board.GP4)
# Create and setup the RA8875 display:
display = ra8875.RA8875(spi, cs=cs_pin, rst=rst_pin, baudrate=BAUDRATE)
display.init()
display.brightness(255)
rtc = adafruit_ds3231.DS3231(busio.I2C(board.GP7, board.GP6))
t = rtc.datetime
tmp = rtc.force_temperature_conversion()

bitmap = BMP("/thermometer.bmp")
x_position = (display.width//50 )
y_position = (display.height // 10) - (bitmap.height // 2)
print("x position: ", x_position, "y position: ", y_position)
bitmap.draw(display, x_position, y_position)

bitmap = BMP("/humidity.bmp")
x_position = (700)
y_position = (display.height // 10) - (bitmap.height // 2)
print("x position: ", x_position, "y position: ", y_position)
bitmap.draw(display, x_position, y_position)

bitmap = BMP("/speed.bmp")
x_position = (display.width // 2) - (bitmap.width // 2)
y_position = (display.height // 2) - (bitmap.height // 2)
print("x position: ", x_position, "y position: ", y_position)
bitmap.draw(display, x_position, y_position)

display.txt_set_cursor(340, display.height // 2 +10)
display.txt_color(WHITE, BLACK)
display.txt_size(4)
display.txt_write("km/h")

prev_val_light = True # true means darkness

bitmap = BMP("/sun.bmp")
x_position = (display.width // 2) - (bitmap.width // 2)
y_position = 30
print("x position: ", x_position, "y position: ", y_position)
bitmap.draw(display, x_position, y_position)

display.txt_set_cursor(600, display.height // 10 - 20)
display.txt_color(WHITE, BLACK)
display.txt_size(2)
display.txt_write("52%")
display.txt_set_cursor(360, display.height // 2 - 50)
display.txt_color(WHITE, BLACK)
display.txt_size(10)
display.txt_write("23")
t = time.struct_time((2023, 4, 14, 11, 14, 15, 0, -1, -1))
rtc.datetime = t
# rtc.datetime(struct_time(tm_year=2010, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=23, tm_sec=59, tm_wday=0, tm_yday=-1, tm_isdst=-1))

while(1):
    print("Value of light pin\n", light_pin.value)
    
    if(prev_val_light is not light_pin.value):
        if(light_pin.value):
            bitmap = BMP("/moon.bmp")
            x_position = (display.width // 2) - (bitmap.width // 2)
            y_position = 30
            print("x position: ", x_position, "y position: ", y_position)
            bitmap.draw(display, x_position, y_position)
            prev_val_light = True
        else: 
            bitmap = BMP("/sun.bmp")
            x_position = (display.width // 2) - (bitmap.width // 2)
            y_position = 30
            print("x position: ", x_position, "y position: ", y_position)
            bitmap.draw(display, x_position, y_position)
            prev_val_light = False
            
    
    t = rtc.datetime
    print("datettime")
    print("{}".format(t))
    display.txt_set_cursor(300, 400)
    display.txt_color(WHITE, BLACK)
    display.txt_size(4)
    display.txt_write(" {}:{}".format(t.tm_hour, t.tm_min))
    # struct_time(tm_year=2010, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=23, tm_sec=59, tm_wday=0, tm_yday=-1, tm_isdst=-1)
    
    tmp = rtc.force_temperature_conversion()
    print("tmp")
    print("{}".format(tmp))
    display.txt_set_cursor((display.width//8 ), display.height // 10 - 20)
    display.txt_color(WHITE, BLACK)
    display.txt_size(2)
    display.txt_write("{}°C".format(tmp))
    
    time.sleep(1)
    



bitmap = BMP("/sun.bmp")
x_position = (display.width // 2) - (bitmap.width // 2)
y_position = 30
print("x position: ", x_position, "y position: ", y_position)
bitmap.draw(display, x_position, y_position)

'''
display.txt_set_cursor((display.width//8 ), display.height // 10 - 20)
display.txt_color(WHITE, BLACK)
display.txt_size(2)
display.txt_write("24°C")
'''

display.txt_set_cursor(600, display.height // 10 - 20)
display.txt_color(WHITE, BLACK)
display.txt_size(2)
display.txt_write("52%")
display.txt_set_cursor(360, display.height // 2 - 50)
display.txt_color(WHITE, BLACK)
display.txt_size(10)
display.txt_write("23")
'''
display.txt_set_cursor(300, 400)
display.txt_color(WHITE, BLACK)
display.txt_size(4)
display.txt_write("10:37 PM")
'''
'''
bitmap = BMP("/moon.bmp")
x_position = (display.width // 2) - (bitmap.width // 2)
y_position = 30
print("x position: ", x_position, "y position: ", y_position)
bitmap.draw(display, x_position, y_position)
'''
'''
display.fill(WHITE)

time.sleep(0.500)
display.fill(YELLOW)
time.sleep(0.500)
display.fill(BLUE)
time.sleep(0.500)
display.fill(CYAN)
time.sleep(0.500)
display.fill(MAGENTA)
time.sleep(0.500)
display.fill(BLACK)
display.circle(100, 100, 50, BLACK)
display.fill_circle(100, 100, 49, BLUE)

display.fill_rect(10, 10, 400, 200, GREEN)
display.rect(10, 10, 400, 200, BLUE)
display.fill_round_rect(200, 10, 200, 100, 10, RED)
display.round_rect(200, 10, 200, 100, 10, BLUE)
display.pixel(10, 10, BLACK)
display.pixel(11, 11, BLACK)
display.line(10, 10, 200, 100, RED)
display.fill_triangle(200, 15, 250, 100, 150, 125, YELLOW)
display.triangle(200, 15, 250, 100, 150, 125, BLACK)
display.fill_ellipse(300, 100, 100, 40, BLUE)
display.ellipse(300, 100, 100, 40, RED)
display.curve(50, 100, 80, 40, 2, BLACK)
display.fill_curve(50, 100, 78, 38, 2, WHITE)

display.txt_set_cursor(display.width // 2 - 200, display.height // 2 - 20)
display.txt_trans(WHITE)
display.txt_size(2)
testvar = 99
display.txt_write("Hello guys!!!!")

# display.touch_init(int_pin)
display.touch_enable(True)

x_scale = 1024 / display.width
y_scale = 1024 / display.height

# Main loop:
while True:
    if display.touched():
        coords = display.touch_read()
        display.fill_circle(
            int(coords[0] / x_scale), int(coords[1] / y_scale), 4, MAGENTA
        )
        display.txt_color(WHITE, BLACK)
        display.txt_set_cursor(display.width // 2 - 220, display.height // 2 - 20)
        display.txt_size(2)
        display.txt_write(
            "Position ("
            + str(int(coords[0] / x_scale))
            + ", "
            + str(int(coords[1] / y_scale))
            + ")"
        )


'''