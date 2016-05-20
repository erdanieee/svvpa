#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import gspread
import oauth2client
import oauth2client.client
import oauth2client.file
import datetime as dat




# If modifying these scopes, delete your previously saved credentials
SCOPES = 'https://spreadsheets.google.com/feeds'
CLIENT_SECRET_FILE = os.environ['CONFIG_DIR'] + 'google_drive_client_secret.json'
APPLICATION_NAME = 'SVVPA'
        
        
def get_credentials():    
    credential_path = os.path.join(os.environ['CONFIG_DIR'], 'google-drive-credentials.json')
    store           = oauth2client.file.Storage(credential_path)
    credentials     = store.get()
    if not credentials or credentials.invalid:
        flow            = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME        
        credentials     = oauth2client.tools.run_flow(flow, store, oauth2client.tools.argparser.parse_args(args=[]))
        print u"[{}] {}: Guardando credenciales en {}".format(datetime.datetime.now(), __file__, credential_path)
    return credentials
    



def main(argv):	
	if len(argv) >= 6:
		datetime	= time.strftime("%Y/%m/%d %H:%M:%S")
		cpuTemp		= argv[1]
		bmp180Temp= argv[2]
		bmp180Pres= argv[3]
		dht22Temp	= argv[4]
		dht22Hr		= argv[5]
		
		credentials = get_credentials()

		gc = gspread.authorize(credentials)
		wks = gc.open("test").sheet1
		print u"[{}] {}: Nueva fila en hoja de calculo de google drive con los datos de sensores: CPU_TEMP:{}, BMP180_TEMP:{}, BMP180_PRESS:{}, DHT22_TEMP:{}, DHT22_HR:{}".format(dat.datetime.now(), __file__,cpuTemp,bmp180Temp,bmp180Pres,dht22Temp,dht22Hr)
		wks.append_row([datetime, cpuTemp, bmp180Temp, bmp180Pres, dht22Temp, dht22Hr])

	else:
		print >> sys.stderr, u"[{}] {}: ERROR! Numero incorrecto de argumentos".format(dat.datetime.now(), __file__)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
