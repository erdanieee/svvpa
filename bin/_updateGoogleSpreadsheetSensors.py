#!/usr/bin/python

import os
import sys
import json
import time
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import datetime as dat



def main(argv):	
	if len(argv) >= 6:
		datetime	= time.strftime("%Y/%m/%d %H:%M:%S")
		cpuTemp		= argv[1]
		bmp180Temp= argv[2]
		bmp180Pres= argv[3]
		dht22Temp	= argv[4]
		dht22Hr		= argv[5]

		json_key = json.load(open(os.environ['GSREAD_JSON']))
		scope = ['https://spreadsheets.google.com/feeds']
		credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)

		gc = gspread.authorize(credentials)
		wks = gc.open("test").sheet1
		print "[{}] {}: Añadiendo fila en hoja de cálculo de google drive con los datos de sensores: CPU_TEMP:{}, BMP180_TEMP:{}, BMP180_PRESS:{}, DHT22_TEMP:{}, DHT22_HR:{}".format(dat.datetime.now(), __file__,cpuTemp,bmp180Temp,bmp180Pres,dht22Temp,dht22Hr)
		wks.append_row([datetime, cpuTemp, bmp180Temp, bmp180Pres, dht22Temp, dht22Hr])

		print "[{}] {}: Hoja de excel remota de los sensores actualizada correctamente".format(dat.datetime.now(), __file__)

	else:
		print "[{}] {}: ERROR! Número incorrecto de argumentos".format(dat.datetime.now(), __file__)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
