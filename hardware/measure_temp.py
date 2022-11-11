from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD
from w1thermsensor import W1ThermSensor, Sensor
import time
import datetime

def safe_exit(signum, frame):
	exit(1)

try:
	signal(SIGTERM, safe_exit)
	signal(SIGHUP, safe_exit)
	lcd = LCD()
	temp_sensor = W1ThermSensor(Sensor.DS18B20)
	celcius = temp_sensor.get_temperature()
	fahrenheit = (celcius * 9/5) + 32;
	lcd.text(str(round(fahrenheit,2)) + " F", 1)
	lcd.text(datetime.datetime.today().strftime("%b %d %I:%M%p"), 2)
	pause()
except KeyboardInterrupt:
	pass
finally:
	lcd.clear()

exit()
