#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
import os
import time
import datetime as dat
import gmail_sender as gsender
import urllib


html = u"""\
<html>
	<head></head>
	<body>
		<h3>Movimiento detectado</h3>
		<p>S.V.V.P.A. 2.0 ha detectado un nuevo movimiento en E.C. {datetime}. Adjunto a este mensaje se incluye el fotograma más representativo.</p>
		<p>Si el vídeo es interesante y deseas guardarlo en Google Drive, haz <a href="http://{dom}.duckdns.org:{port}/uploadVideo.php?id={id}">click aquí</a>. Al abrir esa página en un navegador, SVVPA iniciará la subida del vídeo y mostrará una web con el progreso. <b>No</b> es necesario dejar la página abierta hasta que termine; puedes cerrarla, cerrar el navegador o incluso apagar tu máquina sin que interfiera el proceso. Recuerda que, en función del tamaño del vídeo, este proceso puede tardar varios minutos.</p>
	 	<p>Puedes ver las capturas guardadas anteriormente en <a href="https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing">este enlace</a>.</p>
		<p>Para acceder <b>de forma remota</b> a SVVPA visita <a href="http://{dom}.duckdns.org:{port}">http://{dom}.duckdns.org:{port}</a> o <a href="http://{ip}:{port}">http://{ip}:{port}</a>.	El consumo de datos hasta ahora ha sido de {datos}Mb de los {datosMensuales}Mb mensuales que incluye la tarifa.		 
	</body>
</html>
			""" if bool(int(os.environ['REMOTE_ACCESS'])) else u"""\
<html>
	<head></head>
	<body>
		<h3>Movimiento detectado</h3>
		<p>S.V.V.P.A. 2.0 ha detectado un nuevo movimiento en E.C. {datetime}. Adjunto a este mensaje se incluye el fotograma más representativo.</p>
		<p>Si el vídeo es interesante y deseas guardarlo en Google Drive, haz <a href="mailto:{email}?subject=CMD_SVVPA GUARDAR_EN_GOOGLE_DRIVE {id}">click aquí</a> para enviar enviar un email con el comando correspondiente. Recuerda que, en función del tamaño del vídeo, este proceso puede tardar varios minutos.</p>
	 	<p>Puedes ver las capturas guardadas anteriormente en <a href="https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing">este enlace</a>.</p>
		<p>El consumo de datos hasta el momento ha sido de {datos}Mb de los {datosMensuales}Mb mensuales que incluye la tarifa.		 
	</body>
</html>
"""

def main(argv): 
	if len(sys.argv) >= 2:
		print "[{}] {}: Enviando email con la captura".format(dat.datetime.now(), __file__)
		if os.path.exists(sys.argv[1]):
			image 	 = sys.argv[1]
			id = os.path.basename(image).split(".")[0].strip()
			tk = id.split("_")
			datetime = ""
			
			if len(tk)>=12:
				datetime = "el " + tk[0] +"/"+ tk[1] +"/"+ tk[2] + " a las "+ tk[3] +":"+ tk[4] +":"+ tk[5]
			else:
				datetime = "el " + time.strftime("%Y/%m/%d") + " aproximadamente a las " + time.strftime("%H:%M:%S")			
			s   = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
			msg = gsender.Message(	
				subject	= u"SVVPA - Movimiento detectado",
				to 	= os.environ['EMAIL_ADDR'],
				sender	= os.environ['GMAIL_ACCOUNT_ALIAS'],
				html 	= html.format(
					ip=get_ip(), 
					datetime=datetime, 
					dom=os.environ['DUCKDNS_DOMAIN'], 
					port=os.environ['APACHE_PORT'], 
					id=id, 
					datos=get_datos(), 
					datosMensuales=os.environ['DATOS_MENSUALES'],
					email=os.environ['GMAIL_ACCOUNT_ALIAS']),
				attachments	= [image])
			s.send(msg)
			s.close()


		else:
			print "[{}] {}: ERROR! No se encuentra el archivo {}".format(dat.datetime.now(), __file__,sys.argv[1])
		
	else:
		print "[{}] {}: ERROR! Número inválido de argumentos".format(dat.datetime.now(), __file__)
		

def get_ip():
	url = "http://ipecho.net/plain"
	fp = urllib.urlopen(url)
	try:
		data = fp.read()
	finally:
		fp.close()
	return data

def get_datos():
	ret = os.popen(os.environ['BIN_DIR'] + "_getInternetUsage.sh").readlines()
	return ret[0]

if __name__ == "__main__":
    sys.exit(main(sys.argv))
