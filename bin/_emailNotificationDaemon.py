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
import signal


subject_newImage=u"SVVPA - Movimiento detectado"
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

subject_cameraLost=u"SVVPA - No se puede acceder a la cámara"
html_cameraLost=u"""\
<html>
  <head></head>
  <body>
    <h3>No se puede acceder a la cámara</h3>
    <p>S.V.V.P.A. ha detectado que alguna de las cámaras ha dejado de funcionar correctamente. Si te encuentras en E.C., trata de acceder al modo <i>vista en Directo</i> para descartar un problema transitorio. Si no te encuentras en E.C., puedes probar a reiniciar SVVPA para ver si se soluciona el problema.</p>

<p>Si aun así no funciona, avisa a Er Danié para que trate de indagar en el problema.</p> 
  </body>
</html>
"""

subject_startup=u"SVVPA - El sistema se acaba de iniciar"
html_startup=u"""\
<html>
  <body>
    <h3>Arranque del sistema</h3>
    <p>S.V.V.P.A 2.0 se ha iniciado correctamente.</p> 
  </body>
</html>
"""

subject_shutdown=u"SVVPA - Apagando el sistema"
html_shutdown=u"""\
<html>
  <body>
    <h3>Apagado del sistema</h3>
    <p>S.V.V.P.A 2.0 se está apagando. Recuerda que para arrancarlo es necesario desactivar y volver a activar físicamente el mini-interruptor que está junto a las baterías.</p> 
  </body>
</html>
"""

subject_reboot==u'SVVPA - Reinicio del sistema'
html_reboot==u'<html><body><p>El sistema se está reiniciando. Este proceso tarda aproximadamente 1 minuto.</p></body></html>'


subject_ayuda=u'SVVPA - Ayuda'
html_ayuda=u'''
<html>
	<body>
	<h3>Control de SVVPA mediante correos electrónicos</h3>
	<p>SVVPA tiene la capacidad de ejecutar acciones recibidas mediante correo electrónico. Para ello, solo hay que mandar un email a <a href="mailto:{correo}">{correo}</a> cuyo asunto contenga la acción a ejecutar y esperar a la recepción del correo de confirmación que indica que la ejecución se ha realizado correctamente. La sintaxis de las acciones sigue el siguiente formato:<br>
	<i>CMD_SVVPA COMANDO ARG1 ARG2 ARG3 ... ARGn</i><br>
	donde <i>COMANDO</i> indica el comando que se desea ejecutar y <i>ARGi</i> los argumentos de ese comando (algunos comandos no necesitan argumentos). A continuación se muestran los comandos y argumentos disponibles por el momento:
	<ul>
		<li><b>AYUDA</b> - Envía este email, recordándote los comandos y argumentos disponibles y ejemplos de cómo usarlos. Haciendo click en los enlaces de los <a href="mailto:{correo}?subject=CMD_SVVPA AYUDA">ejemplos como éste</a>, se compone automáticamente un email que puede ser enviado tal cual o modificado a criterio.</li>     
		<li><b>GUARDAR_EN_GOOGLE_DRIVE codigoDelEvento</b> - Guarda en google drive la imagen y el vídeo que corresponde al evento con código <i>codigoDelEvento</i>. El código del evento se puede obtener del asunto del email que se envía automáticamente cuando se detecta un movimiento. <a href="mailto:{correo}?subject=CMD_SVVPA GUARDAR_EN_GOOGLE_DRIVE 2016_01_02_15_30_13_12332_123_543_23_5543_12">Ver ejemplo</a></li>
		<li><b>ESTADO_DEL_SISTEMA</b> - Envía un email con información sobre SVVP, como el espacio disponible, la temperatura de la CPU, el registro de eventos del sistema, ... <a href="mailto:{correo}?subject=CMD_SVVPA ESTADO_DEL_SISTEMA">Ver ejemplo</a></li>
		<li><b>DETECTAR_MOVIMIENTO acción tiempo</b> - Comando para iniciar, parar o pausar el servicio de detección de movimiento. Útil cuando estás en E.C. y no deseas ser grabado :). Si la acción es <i>PARAR</i> (<a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PARAR">Ver ejemplo</a>), el servicio se detiene hasta que se reciba la acción <i>INICIAR</i> (<a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO INICIAR">Ver ejemplo</a>). Si la acción es <i>PAUSAR</i> (<a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PAUSAR 5H">Ver ejemplo</a>), el servicio se detiene temporalmente. En este último caso se requiere también el argumento <i>tiempo</i>, que determina la pausa en formato <i>nU</i>, siendo <i>n</i> la cantidad, y <i>U</i> la unidad (S, M, H o D para segundos, minutos, horas o días. Ej: 10H para pausar durante 10 horas. 3D para pausar durante 3 días)</li> 
		<li><b>ACTUALIZAR_REPOSITORIO</b> - Actualiza el repositorio Github de SVVPA. Normalmente este comando solo lo ejecuta Er Danié. <a href="mailto:{correo}?subject=CMD_SVVPA ACTUALIZAR_REPOSITORIO">Ver ejemplo</a></li>
		<li><b>ACTIVAR_GESTION_REMOTA</b> - Abre un puerto en un servidor remoto para realizar un ssh reverso. Esta opción es útil para administrar SVVPA cuando no tiene conexión a internet a través de una IP pública real (ej: conexión 3g). Normalmente este comando solo lo ejecuta Er Danié. <a href="mailto:{correo}?subject=CMD_SVVPA ACTIVAR_GESTION_REMOTA">Ver ejemplo</a></li>
		<li><b>REINICIAR</b> - Reinicia el sistema. Este comando es útil cuando algo no está funcionando correctamente. El reinicio tarda aproximádamente 1 minuto. <a href="mailto:{correo}?subject=CMD_SVVPA REINICIAR">Ver ejemplo</a></li>
		<li><b>APAGAR</b> - Apaga el sistema. Cuando se envía este comando, SVVPA responde con un correo de confirmación. Para apagar correctamente SVVPA, se debe confirmar el apagado respondiendo al correo de confirmación sin modificar el asunto. Atención: Una vez apagado el sistema, solo se puede volver a iniciar desactivando y activando físicamente el mini-interruptor que está junto a las baterías. Asegúrate de <b>no ejecutar NUNCA</b> este comando cuando estés fuera de E.C. <a href="mailto:{correo}?subject=CMD_SVVPA APAGAR">Ver ejemplo</a></li>
	</ul>                                                   
	</body>
</html>
'''

subject_status=u'SVVPA - Información del sistema'
html_status=u'<html><body><p>Adjunto se envían los registros más relevantes del sistema</p></body></html>'

subject_saveFile_OK=u'SVVPA - Copia en Google Drive correcta'
subject_saveFile_ERROR=u'SVVPA - Error al subir la imagen o el video a Google Drive'
html_saveFile_OK=u'<html><body><p>La imagen y el vídeo correspondientes al evento {eventId} se han subido correctamente a google drive. Puedes ver las imágenes y vídeos guardados en <a href="https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing">este enlace</a>.</p></body></html>'
html_saveFile_ERROR=u'<html><body><p>Se ha producido un error al subir la imagen o el vídeo del evento {eventId} a google drive:</p><p>{error}</p></body></html>'


subject_shutdown_OK=u'SVVPA - Apagando sistema'
subject_shutdown_CONFIRM=u'SVVPA - Confirmar apagado: CMD_SVVPA APAGAR {code}'
subject_shutdown_ERROR=u'SVVPA - Código de apagado erróneo'
html_shutdown_OK=u'<html><body><p>Código de confirmación de apagado aceptado. El sistema se apagará en unos segundos. Recuerda que para iniciar de nuevo el sistema es necesario desactivar y volver a activar físicamente el mini-interruptor que está junto a las baterías.</p></body></html>'
html_shutdown_CONFIRM=u'<html><body><h4>¿Confirmar apagado?</h4><p>Se va a proceder a apagar el sistema. Recuerda que una vez apagado, <ins>solo</ins> se puede volver a iniciar desactivando y activando físicamente el mini-interruptor que está junto a las baterías.</p><p>Si realmente quieres apagar el sistema <b>responde a este email <mark>sin modificar el asunto</mark></b>.</p></body></html>'
html_shutdown_ERROR=u'<html><body><p>El código de confirmación utilizado para apagar el sistema es inválido. Recuerda que los códigos caducan en una hora y no se pueden reutilizar.</p></body></html>'





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



def exit_handler(signal,frame):
	print "[{}] {}: Cerrando demonio".format(datetime.datetime.now(), __file__)
	if f and not f.closed:
		try:
			f.close()
		except:
			pass
	if os.path.exists(ff):
		try:
			os.unlink(ff)
		except:
			pass
	sys.exit(0)
	


#argv[0] -> <imagePath>
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
		subject = subject_newImage,
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
	print "[{}] {}: Notificación de nuevo evento ({}) detectado enviada correctamente".format(datetime.datetime.now(), __file__, id)



def cameraLost(*argv):
	msg = gsender.Message(	
		subject = subject_cameraLost,
		to      = os.environ['EMAIL_ADDR'],
		sender  = os.environ['GMAIL_ACCOUNT_ALIAS'],
		html    = html_cameraLost
	sendEmail(msg)
	print "[{}] {}: Notificación de pérdida de señal de la cámara enviada correctamente".format(datetime.datetime.now(), __file__)	




def startup(*argv):
	msg = gsender.Message(	
		subject = subject_startup,
		to      = os.environ['EMAIL_ADDR'],
		sender  = os.environ['GMAIL_ACCOUNT_ALIAS'],
		html    = html_startup
	sendEmail(msg)
	print "[{}] {}: Notificación de arranque del sistema enviada correctamente".format(datetime.datetime.now(), __file__)	



def shutdown(*argv):
	msg = gsender.Message(	
		subject = subject_shutdown,
		to      = os.environ['EMAIL_ADDR'],
		sender  = os.environ['GMAIL_ACCOUNT_ALIAS'],
		html    = html_shutdown
	sendEmail(msg)
	print "[{}] {}: Notificación de apagado del sistema enviada correctamente".format(datetime.datetime.now(), __file__)	



def ayuda(*argv):
	msg = gsender.Message(	
		subject = subject_ayuda,
		to      = os.environ['EMAIL_ADDR'],
		sender  = os.environ['GMAIL_ACCOUNT_ALIAS'],
		html    = html_ayuda
	sendEmail(msg)
	print "[{}] {}: Email de ayuda enviado correctamente".format(datetime.datetime.now(), __file__)	



def status(*argv):
	msg = gsender.Message(	
		subject = subject_status,
		to      = os.environ['EMAIL_ADDR'],
		sender  = os.environ['GMAIL_ACCOUNT_ALIAS'],
		html    = html_status
	sendEmail(msg)
	print "[{}] {}: Email de estado del sistema enviado correctamente".format(datetime.datetime.now(), __file__)	



def reboot(*argv):
	msg = gsender.Message(	
		subject = subject_reboot,
		to      = os.environ['EMAIL_ADDR'],
		sender  = os.environ['GMAIL_ACCOUNT_ALIAS'],
		html    = html_reboot
	sendEmail(msg)
	print "[{}] {}: Email de reinicio enviado correctamente".format(datetime.datetime.now(), __file__)	



#argv[0] -> <enventId>
#argv[1:] -> [error]
def saveFile(*argv):
	eventId=argv[0]
	error=" ".join(argv[1:])
	if error:
		msg = gsender.Message(	
			subject = subject_saveFile_ERROR,
			to      = os.environ['EMAIL_ADDR'],
			sender  = os.environ['GMAIL_ACCOUNT_ALIAS'],
			html    = html_saveFile_ERROR.format(eventId=eventId, error=error)

	else:
		msg = gsender.Message(	
			subject = subject_saveFile_OK,
			to      = os.environ['EMAIL_ADDR'],
			sender  = os.environ['GMAIL_ACCOUNT_ALIAS'],
			html    = html_saveFile_OK.format(eventId=eventId)
	sendEmail(msg)
	print "[{}] {}: Email de archivo guardado en google drive enviado correctamente".format(datetime.datetime.now(), __file__)	



#argv[0] -> [ [confirmCode] | ['ERROR' <error>] ]
def shutdown(*argv):
	

	msg = gsender.Message(	
		subject = subject_reboot,
		to      = os.environ['EMAIL_ADDR'],
		sender  = os.environ['GMAIL_ACCOUNT_ALIAS'],
		html    = html_reboot
	sendEmail(msg)
	print "[{}] {}: Email de reinicio enviado correctamente".format(datetime.datetime.now(), __file__)	




emails = {
	"E_NEW_IMAGE"   : newImage,	#argv[0] <imagePath> 
	"E_CAMERA_LOST" : cameraLost,
	"E_STARTUP"     : startup,
	"E_SHUTDOWN"    : shutdown,
	"E_AYUDA"       : ayuda,
	"E_REBOOT"      : reboot,
	"E_STATUS"      : status,
	"E_SAVE_FILE"   : saveFile		#argv[0] <enventId>     argv[1:] [error]
	}



ff = os.environ['FIFO_EMAIL_NOTIF']
f  = None
fd = None



def main():
	print "[{}] {}: Iniciando demonio para gestión de notificaciones por correo electrónico".format(datetime.datetime.now(), __file__)
	signal.signal(signal.SIGTERM, exit_handler)
	signal.signal(signal.SIGINT, exit_handler)

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


		except Exception  as e:
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



