#!/usr/bin/python

import os
import sys
import json
import time
import gspread
from oauth2client.client import SignedJwtAssertionCredentials



def main(argv):
	if len(argv) >= 6:
		datetime	= time.strftime("%Y/%m/%d %H:%M:%S")
		cpuTemp		= argv[1]
		bmp180Temp= argv[2]
		bmp180Pres= argv[3]
		dht22Temp	= argv[4]
		dht22Hr		= argv[5]

		print "Date: " + datetime
		print "CPU Temp: " + cpuTemp
		print "BMP180 Temp: " + bmp180Temp
		print "BMP180 Press: " + bmp180Pres
		print "DHT22 Temp: "  + dht22Temp
		print "DHT22 HR: "  + dht22Hr
		print 

		print "load json and credentials"
		json_key = json.load(open(os.environ['GSREAD_JSON']))
		scope = ['https://spreadsheets.google.com/feeds']
		credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)

		print "authorize gspread"
		gc = gspread.authorize(credentials)
		print "open sheet"
		wks = gc.open("test").sheet1
		print "append row"
		wks.append_row([datetime, getValue(cpuTemp), getValue(bmp180Temp), getValue(bmp180Pres), getValue(dht22Temp), getValue(dht22Hr)])

		print "DONE!"

	else:
		print "USAGE " + argv[0] + " <CPU Temp> <BMP180 Temp> <BMP180 Pres> <DHT22 Temp> <DHT22 HR>"

def getValue(a):
	if a == "NULL":
		a = "nan"
	return a.replace(".",",")

if __name__ == "__main__":
    sys.exit(main(sys.argv))
