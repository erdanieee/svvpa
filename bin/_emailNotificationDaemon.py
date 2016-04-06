#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os, sys
import errno
import time, datetime
import gmail_sender as gsender
import urllib
import stat
import fcntl
import traceback


html_newImage = u"""\
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
		<p>Si piensas que el vídeo puede ser interesante y deseas guardarlo en Google Drive, haz <a href="mailto:{email}?subject=CMD_SVVPA GUARDAR_EN_GOOGLE_DRIVE {id}">click aquí</a> para enviar enviar un email con el comando correspondiente. Recuerda que, en función del tamaño del vídeo, este proceso puede tardar varios minutos.</p>
	 	<p>Puedes ver las capturas guardadas anteriormente en <a href="https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing">este enlace</a>.</p>
		<p>El consumo de datos estimado hasta el momento ha sido de {datos}Mb de los {datosMensuales}Mb mensuales que incluye la tarifa.		 
	</body>
</html>
"""



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
	return ret[0].strip()


#argv[0] - image path
def newImage(*argv):
	image = argv[0]
	id = os.path.basename(image).split(".")[0].strip()
	tk = id.split("_")
	dt = ""
			
	if len(tk)>=12:
		dt = "el " + tk[0] +"/"+ tk[1] +"/"+ tk[2] + " a las "+ tk[3] +":"+ tk[4] +":"+ tk[5]
	else:
		dt = "el " + time.strftime("%Y/%m/%d") + " aproximadamente a las " + time.strftime("%H:%M:%S")		

	msg = gsender.Message(	
		subject = u"SVVPA - Movimiento detectado",
		to      = os.environ['EMAIL_ADDR'],
		sender  = os.environ['GMAIL_ACCOUNT_ALIAS'],
		html    = html_newImage.format(
			ip       = get_ip(), 
			datetime = dt, 
			dom      = os.environ['DUCKDNS_DOMAIN'], 
			port     = os.environ['APACHE_PORT'], 
			id       = id, 
			datos    = get_datos(), 
			datosMensuales = os.environ['DATOS_MENSUALES'],
			email    = os.environ['GMAIL_ACCOUNT_ALIAS']),
		attachments	= [image])	
	sendEmail(msg)
	print "[{}] {}: Notificación correcta para id: {}".format(datetime.datetime.now(), __file__, id)



emails = {
	"E_NEW_IMAGE" : newImage
	}


def main():
	print "[{}] {}: Iniciando demonio para gestión de notificaciones por correo electrónico".format(datetime.datetime.now(), __file__)
	ff = os.environ['FIFO_EMAIL_NOTIF']
	f  = None
	fd = None
	

	while True:
		try:
			if not os.path.exists(ff):
				print "creando fifo"
				os.mkfifo(ff)
				print os.path.exists(ff)
			
			elif not stat.S_ISFIFO(os.stat(ff).st_mode):
				print "fifo incorrecto. Creando de nuevo"
				os.unlink(ff)
				os.mkfifo(ff)
			
			#try:
			#	os.fstat(fd)
			#except Exception as e:
			fd = os.open(ff, os.O_RDONLY | os.O_NONBLOCK)
			print "File descriptor: %s" % fd
			#	print e
			#	pass

			f 	= os.fdopen(fd)
			input = f.read()

			#with os.fdopen(fd) as f:	
			#	input = f.read()
		
			if input:
				for e in input.split('\n')[:-1]:
					print "[{}] {}: Comando recibido: {}".format(datetime.datetime.now(), __file__, e)
					tk = e.split()
					if emails.has_key(tk[0]):
						emails.get(tk[0])(*tk[1:])
					else:
						print "[{}] {}: ERROR! Comando no encontrado: {}".format(datetime.datetime.now(), __file__, e)
			
			#f.close()					 
			#os.close(fd)
			time.sleep(1)		


		except Exception as e:
			traceback.print_exc()
			print
			print "[{}] {}: ERROR! {}".format(datetime.datetime.now(), __file__, e)
			if f and not f.closed:
				f.close()
			if os.path.exists(ff):
				os.unlink(ff)
			time.sleep(1)
			continue
			
	
							
	






def sendEmail(msg):
	s = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	for n in range(1,60):
		if not s.is_connected():
			print "."
			time.sleep(2)	#FIXME: incremento gradual
			s.connect()
		else:
			break			
	s.send(msg)
	s.close()


if __name__ == "__main__":
	sys.exit(main())



