from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD
from w1thermsensor import W1ThermSensor, Sensor

from datetime import datetime

import time
import requests
import calendar

def safe_exit(signum, frame):
	exit(1)

def get_temperature(attempts = 0):
	temp_sensor = W1ThermSensor(Sensor.DS18B20)

	# going to make sure the reading is accurate, so we'll do it over a loop and take the average
	# this is because the sensor can be a bit flaky
	i = 0
	acceptable_variance = 2
	avg = 0
	last_reading = 0
	total = 0
	while (i < 3):
		last_reading = temp_sensor.get_temperature()
		total += last_reading
		i += 1

	avg = total / i

	# if the average is more than 1 degree different from the current reading, we'll try again, but only five times
	if (attempts < 5 and avg != 0 and last_reading != 0 and abs(avg - last_reading) > acceptable_variance):
		log("Average and Last Reading are more than 1 degree different, trying again")
		return get_temperature((attempts + 1))
	
	fahrenheit = (avg * 9/5) + 32;
	return str(round(fahrenheit,2))

def initialize_lcd():
	lcd = LCD()
	clear_lcd(lcd)
	return lcd

def write_to_lcd(lcd, text, line):
	lcd.text(text, line)

def clear_lcd(lcd):
	lcd.clear()

def post_temperature(temp, unit):
	currentGMT = time.gmtime()
	tstamp = calendar.timegm(currentGMT)

	url = 'https://chatuge-water-temperature.glitch.me/store-temperature'
	postData = {'temperature':temp, 'unit':'F', 'timestamp': tstamp}

	# try to post the temperature to the server a few times, if it fails, just give up
	i = 0
	while (i < 3):
		try:
			r = requests.post(url, data = postData)
			if (r.status_code == 200):
				log("Temperature posted successfully")
				return
			else:
				log("Error posting temperature to server, will try again in 5 seconds")
				time.sleep(5)
		except:
			i += 1
			log("Error posting temperature to server, will try again in 5 seconds")
			time.sleep(5)
	

def log(message):
	now = datetime.now()
	date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
	print(date_time_str + ': ' + message)

# main program
try:
	signal(SIGTERM, safe_exit)
	signal(SIGHUP, safe_exit)

	lcd = None
	try:
		lcd = initialize_lcd()
	except:
		log("Error initializing LCD, will output to console instead")


	log("Will exit in 5 seconds\nOr press CTRL + C to exit")
	
	temperature = get_temperature()

	if (lcd):
		write_to_lcd(lcd, "Temperature: " + temperature + " F", 1)
		write_to_lcd(lcd, datetime.datetime.today().strftime("%b %d %I:%M%p"), 2)
	else:
		log("Temperature: " + temperature + " F")
	
	post_temperature(temperature, 'F')

	time.sleep(5)
except KeyboardInterrupt:
	pass
finally:
	if (lcd): clear_lcd(lcd)

exit()
