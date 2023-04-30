import time
import busio
import digitalio
import board
import adafruit_ds3231
from time import struct_time
import adafruit_dht
# Initialize variables
pulse_count = 0
pulse_time = 1
last_pulse_time = time.monotonic()
hall_pin = digitalio.DigitalInOut(board.GP16)
print(“value of hall pin : “, hall_pin.value)
print(“value of hall pin : “, hall_pin.value)
last_true = 0
global_time_counter = 1
speed = 0
circumference = 0.14*2*3.14
humidity = 53
#humidity = adafruit_dht.DHT22(board.GP28).humidity
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
        with open(self.filename, “rb”) as f:
            f.seek(10)
            self.data = int.from_bytes(f.read(4), “little”)
            f.seek(18)
            self.width = int.from_bytes(f.read(4), “little”)
            self.height = int.from_bytes(f.read(4), “little”)
            f.seek(28)
            self.bpp = int.from_bytes(f.read(2), “little”)
            f.seek(34)
            self.data_size = int.from_bytes(f.read(4), “little”)
            f.seek(46)
            self.colors = int.from_bytes(f.read(4), “little”)
    def draw(self, disp, x=0, y=0):
        print(“{:d}x{:d} image”.format(self.width, self.height))
        print(“{:d}-bit encoding detected”.format(self.bpp))
        line = 0
        line_size = self.width * (self.bpp // 8)
        if line_size % 4 != 0:
            line_size += 4 - line_size % 4
        current_line_data = b”"
        with open(self.filename, “rb”) as f:
            f.seek(self.data)
            disp.set_window(x, y, self.width, self.height)
            for line in range(self.height):
                current_line_data = b”"
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
                    current_line_data = current_line_data + struct.pack(“>H”, color)
                disp.setxy(x, self.height - line + y)
                disp.push_pixels(current_line_data)
            disp.set_window(0, 0, disp.width, disp.height)
‘’'
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN)
while True:
    if GPIO.input(12) == 1:
        print (“LIGHT 1")
        time.sleep(1)
    elif GPIO.input(12) == 0:
        print (“LIGHT 0”)
        time.sleep(1)
    else:
        pass
‘’'
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
# True means it’s dark
print(“light pin val”)
print(“\n\n”, light_pin.value)
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
bitmap = BMP(“/thermometer.bmp”)
x_position = (display.width//50 )
y_position = (display.height // 10) - (bitmap.height // 2)
print(“x position: “, x_position, “y position: “, y_position)
bitmap.draw(display, x_position, y_position)
bitmap = BMP(“/humidity.bmp”)
x_position = (700)
y_position = (display.height // 10) - (bitmap.height // 2)
print(“x position: “, x_position, “y position: “, y_position)
bitmap.draw(display, x_position, y_position)
bitmap = BMP(“/speed.bmp”)
x_position = (display.width // 2) - (bitmap.width // 2)
y_position = (display.height // 2) - (bitmap.height // 2)
print(“x position: “, x_position, “y position: “, y_position)
bitmap.draw(display, x_position, y_position)
display.txt_set_cursor(340, display.height // 2 +10)
display.txt_color(WHITE, BLACK)
display.txt_size(4)
display.txt_write(“km/h”)
prev_val_light = True # true means darkness
bitmap = BMP(“/sun.bmp”)
x_position = (display.width // 2) - (bitmap.width // 2)
y_position = 30
print(“x position: “, x_position, “y position: “, y_position)
bitmap.draw(display, x_position, y_position)
#display.txt_set_cursor(600, display.height // 10 - 20)
#display.txt_color(WHITE, BLACK)
#display.txt_size(2)
#display.txt_write(“{}%“.format(humdity = adafruit_dht.DHT22(board.GP28).humdity))
display.txt_set_cursor(360, display.height // 2 - 50)
display.txt_color(WHITE, BLACK)
display.txt_size(10)
display.txt_write(“0”)
t = time.struct_time((2023, 4, 14, 11, 14, 15, 0, -1, -1))
rtc.datetime = t
bike_speed = 0
bike_speed_2 = 0
# rtc.datetime(struct_time(tm_year=2010, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=23, tm_sec=59, tm_wday=0, tm_yday=-1, tm_isdst=-1))
while(1):
    print(“value of hall pin :{}“, hall_pin.value)
    print(“Value of light pin\n”, light_pin.value)
    if(prev_val_light is not light_pin.value):
        if(light_pin.value):
            bitmap = BMP(“/moon.bmp”)
            x_position = (display.width // 2) - (bitmap.width // 2)
            y_position = 30
            print(“x position: “, x_position, “y position: “, y_position)
            bitmap.draw(display, x_position, y_position)
            prev_val_light = True
        else:
            bitmap = BMP(“/sun.bmp”)
            x_position = (display.width // 2) - (bitmap.width // 2)
            y_position = 30
            print(“x position: “, x_position, “y position: “, y_position)
            bitmap.draw(display, x_position, y_position)
            prev_val_light = False
    t = rtc.datetime
    # print(“datettime”)
    # print(“{}“.format(t))
    display.txt_set_cursor(300, 400)
    display.txt_color(WHITE, BLACK)
    display.txt_size(4)
    display.txt_write(” {}:{}“.format(t.tm_hour, t.tm_min))
    # struct_time(tm_year=2010, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=23, tm_sec=59, tm_wday=0, tm_yday=-1, tm_isdst=-1)
    tmp = rtc.force_temperature_conversion()
    print(“tmp”)
    print(“{}“.format(tmp))
    display.txt_set_cursor((display.width//8 ), display.height // 10 - 20)
    display.txt_color(WHITE, BLACK)
    display.txt_size(2)
    display.txt_write(“{}°C”.format(tmp))
    i = 0
    while i < 100:
        if not hall_pin.value:
            #last_true = time.monotonic()
            #speed = (circumference / ((time.monotonic()+1 - last_true)))*3.6
            current_time = time.monotonic()
            pulse_count += 1
            # Calculate the time since the last pulse
            pulse_time = current_time - last_pulse_time
            # Calculate the speed based on the pulse frequency
            #if pulse_time ==0:
            pulse_frequency = 1.0 / (pulse_time)
            wheel_circumference = 2 * 3.14159 * 5.5 * 0.04# Assuming a wheel diameter of 1 inch
            bike_speed = pulse_frequency * wheel_circumference * 60 / 12
            # Print the bike speed
            print(“hello”)
            print(“Bike speed: {:.1f} MPH”.format(bike_speed))
            if(bike_speed > 80):
                bike_speed =0
            # Reset the pulse count and last pulse time
            pulse_count = 0
            last_pulse_time = current_time
        #bike_speed_2 = pulse_frequency * wheel_circumference * 60 / 12
        #print(“Bike speed_2: {:.1f} MPH”.format(bike_speed_2))
        time.sleep(0.01)
        i+=1
        global_time_counter+=1
    display.txt_set_cursor(360, display.height // 2 - 50)
    display.txt_color(WHITE, BLACK)
    display.txt_size(10)
    display.txt_write(”   “)
    display.txt_set_cursor(360, display.height // 2 - 50)
    display.txt_color(WHITE, BLACK)
    display.txt_size(10)
    display.txt_write(“{}“.format(int(bike_speed)))
    display.txt_set_cursor(600, display.height // 10 - 20)
    display.txt_color(WHITE, BLACK)
    display.txt_size(2)
    #humidity = adafruit_dht.DHT22(board.GP28).humidity
    display.txt_write(“{}%“.format(humidity))
    #print(“SPEEEEDDDDD: “, speed)
    print(“Bike speed: {:.1f} MPH”.format(bike_speed))
