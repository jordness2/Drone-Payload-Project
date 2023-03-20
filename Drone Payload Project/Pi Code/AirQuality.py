import numpy as np
import sys
import cv2
import math
import time
from ltr559 import LTR559 #light and proximity
from enviroplus import gas #gas
import logging #for logging
import smbus2
from bme280 import BME280 #temp pressure and humidity
from datetime import datetime
import requests

bme280 = BME280()
ltr559 = LTR559()

delay = 0.5  # Debounce the proximity tap
mode = 0     # The starting mode
last_page = 0
light = 1

class AirQualitySensor:

	def __init__(self):
		self.calibration_setup()
		self.temperature = 0
		self.pressure = 0

	def start(self):
		print("Starting AQS")
		return 

	def update(self):
		sensor = gas.read_all()
		self.co = sensor.reducing
		self.no2 = sensor.oxidising
		self.nh3 = sensor.nh3		
		self.light = ltr559.get_lux()
		self.proximity = ltr559.get_proximity()
		self.co_ppm = co_ppm(self.co)
		self.no2_ppm = no2_ppm(self.no2)
		self.nh3_ppm = nh3_ppm(self.nh3)
		self.temperature = self.temp()
		self.pressure = self.press()
		self.humidity = self.humid()


	def read(self):
		return self.temperature, self.pressure

	def stop(self):
		return


	# this function is run once at the start of
	# the program to find the appropriate factor for the room
	def calibration_setup(self):
		global factor
		global alt
		global NO2_cal
		global CO_cal
		global NH3_cal

		alt = 0
		factor = 1

		adj_temp = 0
		cpu_temps = []

		cpu_temp = get_cpu_temperature()
		# Smooth out with some averaging to decrease jitter
		cpu_temps = cpu_temps[1:] + [cpu_temp]
		avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))

		calibration_temp = input("Enter the current room tempurature in degrees celsius: ")

		# https://en-us.topographic-map.com/maps/vj4v/Ferny-Grove/

		alt = input("Enter the current altitude (above sea level) of your possition (in meters): ")

		gas_cal = input("Does the gas sensor require calibration? Type 'Yes' or 'No': ")
		
		start_time = time.time()
		finish_time = 0


		if str(gas_cal) == "No":
			try:
				with open("Gas_calibration.txt") as params:
					content = params.read()
					print(content)
				content = content.split(" ")
				index = 1
				for x in content:
					if x == "no2_cal":
						NO2_cal = str(content[index])

					elif x == "co_cal":
						CO_cal = str(content[index])

					elif x == "nh3_cal":
						NH3_cal = str(content[index])
					index += 1

			except:
				print("Calibration file does not exist enter values manually if known:")
				print()
				NO2_cal = input("input the NO2 calibration value (in ohms): ")
				CO_cal = input("input the CO calibration value (in ohms): ")
				NH3_cal = input("input the NH3 calibration value (in ohms): ")
			
		elif str(gas_cal) == "Yes":
			# print("wah")
			min_count = 0
			timer = 0

			while(timer < 300 ): #set this to 300 for the actual implementation as this is the minimum callibration time (5 minutes) longer would be better
				timer = finish_time - start_time
				#print(timer)
				sensor = gas.read_all()
				NO2_cal = sensor.oxidising # find the NO2 in ohms
				CO_cal = sensor.reducing # find the CO value in ohms
				NH3_cal = sensor.nh3 # find the ethanol in ohms

				finish_time = time.time()

			with open("Gas_calibration.txt", 'w') as calibration:
				calibration.write("no2_cal " + str(NO2_cal) + " co_cal " + str(CO_cal) + " nh3_cal " + str(NH3_cal))
			

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

			#print("this is the factor " + str(factor))
			#print("this is the adjusted tempurature " + str(adj_temp))
		
		# return factor

	# gets the tempurature in degrees celsius
	def temp(self):
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

	# Gets the Pressure in hPa
	def press(self):
		temp = bme280.get_temperature()
		# print (alt)
		adj = math.pow(1 - (0.0065 * float(alt)/(temp + 0.0065 * float(alt) + 273.15)), -5.257) #calibration equation provided by Roscoe27 in this forum:
		# https://github.com/pimoroni/enviroplus-python/issues/67
		# The user used linear regression on the data set to generate the perameters they seem to work within the error tollerances of the 
		# pressure sensor

		# print (adj)

		pressure = bme280.get_pressure()

		adj_pres = pressure * adj

		# print("this is the sensor pressure " + str(pressure))
		# print("this is the adjusted pressure " + str(adj_pres))

		return adj_pres

	def humid(self):
		# calibration of humidity code created by user Roscoe27 in this forum https://forums.pimoroni.com/t/enviro-readings-unrealiable/12754/58

		humi_intercept = 13.686 # was orginally at 15.686 this seems to work better 
		comp_hum_slope = 0.966

		humi = bme280.get_humidity()
		raw_temp = bme280.get_temperature()
		dew_point = (243.04 * (math.log(humi / 100) + ((17.625 * raw_temp) / (243.04 + raw_temp)))) / (17.625 - math.log(humi / 100) - (17.625 * raw_temp / (243.04 + raw_temp)))
		temp_adjusted_hum = 100 * (math.exp((17.625 * dew_point)/(243.04 + dew_point)) / math.exp((17.625 * self.temperature) / (243.04 + self.temperature)))
		comp_hum = comp_hum_slope * temp_adjusted_hum + humi_intercept

		# print("This is the dew point " + str(dew_point) + "C")
		# print("This is the sensor humidity " + str(humi) + "%")
		# print("This is the adjusted Humidity " + str(comp_hum) + "%")

		return comp_hum


	# converts the AQS data into a json object
	def to_json(self):
		self.sensor = gas.read_all()
		current_time = datetime.now().strftime("%H:%M:%S")
		# print(current_time)
		AQS_data = {"Time": current_time,"Tempurature C": float(self.temperature), "Pressure kPa": float(self.pressure)/10, "Humidity %": float(self.humidity), "Light Lux": float(self.light), "Proximity": float(self.proximity), "CO_ppm": float(self.co_ppm), "NO2_ppm": float(self.no2_ppm), "NH3_ppm": float(self.nh3_ppm)}


		return AQS_data


def co_ppm(Rs):
	R0 = float(CO_cal)
	CO_ppm = math.pow(10, -1.25 * math.log10(Rs/R0) + 0.64) # equation provided by Roscoe27 sourced from https://forums.pimoroni.com/t/enviro-ohms-to-ppm/12207/5

	# print('this is the CO ppm ' + str(CO_ppm))

	return CO_ppm

def no2_ppm(Rs):
	R0 = float(NO2_cal)
	NO2_ppm = math.pow(10, math.log10(Rs/R0) - 0.8129) # equation provided by Roscoe27 sourced from https://forums.pimoroni.com/t/enviro-ohms-to-ppm/12207/5

	# print('this is the NO2 ppm ' + str(NO2_ppm))

	return NO2_ppm

def nh3_ppm(Rs):
	R0 = float(NH3_cal)
	NH3_ppm = math.pow(10, -1.8 * math.log10(Rs/R0) - 0.163) # equation provided by Roscoe27 sourced from https://forums.pimoroni.com/t/enviro-ohms-to-ppm/12207/5

	# print('this is the NH3 ppm ' + str(NH3_ppm))

	return NH3_ppm 

def get_cpu_temperature():
		with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
			temp = f.read()
			temp = int(temp) / 1000.0
			# print('wah ' + str(temp))
		return temp


if __name__ == '__main__':
	AQS = AirQualitySensor()
# Main loop for data collection
	while True:
		AQS.update()
		# print(AQS.to_json())
		r = requests.post(url = 'http://172.19.7.122:5001/aqs/aqs', json={"data": AQS.to_json()})
		print(r)

		# time.sleep(1)

		# BME280 Sensor readings
		#temp() # corrected_temp
		#press() # pressure
		#humid() # comp_hum

		# Light and Proximity Sensor
		#light() # light
		#proximity() # prox

		#Gas Readings
		#co_ppm() # CO_ppm
		#no2_ppm() # NO2_ppm
		#nh3_ppm() # NH3_ppm
		