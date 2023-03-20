import numpy as np
import sys
import cv2
import math
from ltr559 import LTR559 #light and proximity
from bme280 import BME280 #temp pressure and humidity
from datetime import datetime
import ST7735
import socket
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import RobotoMedium as UserFont
import logging
import time


bme280 = BME280()
ltr559 = LTR559()

delay = 0.5  # Debounce the proximity tap
mode = 0     # The starting mode
last_page = 0
light = 1

# Create LCD class instance.
disp = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)

def get_cpu_temperature():
		with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
			temp = f.read()
			temp = int(temp) / 1000.0
			# print('wah ' + str(temp))
		return temp

def calibration_setup():
    global factor

    alt = 0
    factor = 1

    adj_temp = 0
    cpu_temps = []

    cpu_temp = get_cpu_temperature()
    # Smooth out with some averaging to decrease jitter
    cpu_temps = cpu_temps[1:] + [cpu_temp]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))

    calibration_temp = input("Enter the current room tempurature in degrees celsius: ")

    print("Calibrating the perameters: ")

    start_time = time.time()
    finish_time = 0
    timer = 0

    while(timer  < 10 ):
        timer = finish_time - start_time
        #print(timer)
        cpu_temp = get_cpu_temperature()
        # Smooth out with some averaging to decrease jitter
        cpu_temps = cpu_temps[1:] + [cpu_temp]
        avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))

        # print("this is the avg CPU temp " + str(avg_cpu_temp))
        finish_time = time.time()

    while(adj_temp < float(calibration_temp)):
        raw_temp = bme280.get_temperature()
        adj_temp = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
        factor += 0.01

def temp():
		# print(factor)

		cpu_temps = []

		unit = "C"
		cpu_temp = get_cpu_temperature()
		# Smooth out with some averaging to decrease jitter
		cpu_temps = cpu_temps[1:] + [cpu_temp]
		avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))

		# print("this is the avg CPU temp " + str(avg_cpu_temp))

		raw_temp = bme280.get_temperature()
		# print("this is the adjusted tempurature " + str(raw_temp))
		corrected_temp = raw_temp - ((avg_cpu_temp - raw_temp) / factor)

		# print("this is the adjusted tempurature " + str(corrected_temp))
		# display_text(variables[mode], data, unit)
		return corrected_temp

def get_ip():
    start_time = time.time()
    end_time = time.time()
    run = True
    while(run or (end_time - start_time > 20)):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        end_time = time.time()
        # print("Elapsed Time: " + str(end_time - start_time) + "/20")
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
            run = False
            #print("Found IP: "+ str(IP))
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
    return IP

def lcd_text_dis(mes):
    # Width and height to calculate text position.
    WIDTH = disp.width
    HEIGHT = disp.height

    # New canvas to draw on.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Text settings.
    font_size = 25
    font = ImageFont.truetype(UserFont, font_size)
    text_colour = (255, 255, 255)
    back_colour = (0, 170, 170)


    # ip = ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] 
    # if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), 
    # s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, 
    # socket.SOCK_DGRAM)]][0][1]]) if l][0][0])


    message = str(mes)
    size_x, size_y = draw.textsize(message, font)

    # Calculate text position
    x = (WIDTH - size_x) / 2
    y = (HEIGHT / 2) - (size_y / 2)

    # Draw background rectangle and write text.
    draw.rectangle((0, 0, 160, 80), back_colour)
    draw.text((x, y), message, font=font, fill=text_colour)
    disp.display(img)

if __name__ == '__main__':

    calibration_setup()
    # Initialize display.
    disp.begin()

    while(1):
        end_time = time.time()
        proximity = ltr559.get_proximity()
        if proximity > 1500 and time.time() - last_page > delay:
            mode += 1
            if mode == 3:
                mode = 0
            last_page = time.time()
        
        if mode == 0:
            print(get_ip())
            lcd_text_dis(get_ip())

        if mode == 1:
            print(temp())
            lcd_text_dis(str(round(temp(),3)) + " C")

        if mode == 2:
            # This is the image display
            print("wah")