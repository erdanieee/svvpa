#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
import os
import smtplib
import time
import urllib
from email.mime.text import MIMEText
from email.MIMEImage import MIMEImage
from email.mime.multipart import MIMEMultipart


html = """\
<html>
	<head></head>
	<body>
		<h3>Movimiento detectado</h3>
		<p>S.V.V.P.A. 2.0 ha detectado un nuevo movimiento en E.C. {datetime}. Adjunto a este mensaje se incluye el fotograma más representativo.</p>
		<p>Si el vídeo es interesante y deseas guardarlo en Google Drive, haz <a href="http://{dom}.duckdns.org:{port}/uploadVideo.php?id={id}">click aquí</a>. Al abrir esa página en un navegador, SVVPA inicia la subida del vídeo y muestra una web con el progreso. <b>No</b> es necesario dejar la página abierta hasta que termine; puedes cerrarla, cerrar el navegador o incluso apagar tu máquina sin que interfiera el proceso. Recuerda que, dependiendo del tamaño del vídeo, este proceso puede tardar varios minutos.</p>
	 	<p>Puedes ver las capturas guardadas anteriormente en <a href="https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing">este enlace</a>.</p>
		<p>Para acceder <b>de forma remota</b> a SVVPA visita <a href="http://{dom}.duckdns.org:{port}">http://{dom}.duckdns.org:{port}</a> o <a href="http://{ip}:{port}">http://{ip}:{port}</a>.	El consumo de datos hasta ahora ha sido de {datos}Mb de los {datosMensuales} Mb mensuales que incluye la tarifa.	f	 
	</body>
</html>
			"""

def main(argv): 
	if len(sys.argv) >= 2:
		if os.path.exists(sys.argv[1]):
			image 	 = sys.argv[1]
			tk	  	 = os.path.basename(image).split("_")
			datetime = ""
			
			if len(tk)>=12:
				datetime = "el " + tk[0] +"/"+ tk[1] +"/"+ tk[2] +" a las "+ tk[3] +":"+ tk[4] +":"+ tk[5]
			else:
				datetime = "el " + time.strftime("%Y/%m/%d") + " aproximadamente a las " + time.strftime("%H:%M:%S")			

			

			# Construct email
			msg = MIMEMultipart()
			msg['To'] = os.environ['EMAIL_ADDR']
			msg['From'] = os.environ['EMAIL_FROM']
			msg['Subject'] = 'Movimiento detectado ' + datetime
			msg.preamble = 'Movimiento detectado' + datetime

			# Attach html						
			msg.attach(MIMEText(html.format(ip=get_ip(), 
																			datetime=datetime, 
																			dom=os.environ['DUCKDNS_DOMAIN'], 
																			port=os.environ['APACHE_PORT'], 
																			id=os.path.basename(image).split(".")[0], 
																			datos=get_datos(), 
																			datosMensuales=os.environ['DATOS_MENSUALES']), 'html', 'utf-8'))

			#attach image
			fp=open(image,'rb')
			msg.attach(MIMEImage(fp.read()))
			fp.close()

			#send email
			server = smtplib.SMTP(os.environ['SMPT_SERVER'],os.environ['SMPT_PORT']) #port 465 or 587
			server.ehlo()
			server.starttls()
			server.ehlo()
			server.login(os.environ['SMPT_USER'],os.environ['SMPT_PASS'])
			server.sendmail(os.environ['EMAIL_FROM'], os.environ['EMAIL_ADDR'], msg.as_string())
			server.close()



		else:
			print "ERROR: file " + sys.argv[1] + " not found!"
		
	else:
		print "USAGE: " + sys.argv[0] + " <image>"
		

def get_ip():
	url = "http://ipecho.net/plain"
	fp = urllib.urlopen(url)
	try:
		data = fp.read()
	finally:
		fp.close()
	return data

def get_datos():
	ret = os.popen(os.environ['BIN_DIR'] + "getInternetUsage.sh").readlines()
	return ret[0]

if __name__ == "__main__":
    sys.exit(main(sys.argv))
