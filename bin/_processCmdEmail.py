#!/usr/bin/env python
#coding=utf-8

import sys, os
import re
import subprocess as proc
import gmail_sender as gsender
import gmail as greader
import datetime
import zipfile
import zlib
import md5
import time
import signal




#####################
###  E M A I L S  ###
#####################
cmd_help_subject=u'SVVPA - Ayuda'
cmd_help_html=u'''
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
			<li><b>NOTIFICAR_EMAIL acción</b> - Este comando sirve para controlar las notificaciones que se reciben por email (detección de nuevos movimientos, arranque/parada del sistema, errores, ...), donde <i>acción</i> puede tomar los valores <i>INICIAR</i> para activar (<a href="mailto:{correo}?subject=CMD_SVVPA NOTIFICAR_EMAIL INICIAR">Ver ejemplo</a>), <i>PARAR</i> para desactivar (<a href="mailto:{correo}?subject=CMD_SVVPA NOTIFICAR_EMAIL PARAR">Ver ejemplo</a>) o <i>ESTADO</i> para comprobar el estado (<a href="mailto:{correo}?subject=CMD_SVVPA NOTIFICAR_EMAIL ESTADO">Ver ejemplo</a>).</li>	
			<li><b>ACTUALIZAR_REPOSITORIO</b> - Actualiza el repositorio Github de SVVPA. Normalmente este comando solo lo ejecuta Er Danié. <a href="mailto:{correo}?subject=CMD_SVVPA ACTUALIZAR_REPOSITORIO">Ver ejemplo</a></li>
			<li><b>ACTIVAR_GESTION_REMOTA</b> - Abre un puerto en un servidor remoto para realizar un ssh reverso. Esta opción es útil para administrar SVVPA cuando no tiene conexión a internet a través de una IP pública real (ej: conexión 3g). Normalmente este comando solo lo ejecuta Er Danié. <a href="mailto:{correo}?subject=CMD_SVVPA ACTIVAR_GESTION_REMOTA">Ver ejemplo</a></li>
			<li><b>REINICIAR</b> - Reinicia el sistema. Este comando es útil cuando algo no está funcionando correctamente. El reinicio tarda aproximádamente 1 minuto. <a href="mailto:{correo}?subject=CMD_SVVPA REINICIAR">Ver ejemplo</a></li>
			<li><b>APAGAR</b> - Apaga el sistema. Cuando se envía este comando, SVVPA responde con un correo de confirmación. Para apagar correctamente SVVPA, se debe confirmar el apagado respondiendo al correo de confirmación sin modificar el asunto. Atención: Una vez apagado el sistema, solo se puede volver a iniciar desactivando y activando físicamente el mini-interruptor que está junto a las baterías. Asegúrate de <b>no ejecutar NUNCA</b> este comando cuando estés fuera de E.C. <a href="mailto:{correo}?subject=CMD_SVVPA APAGAR">Ver ejemplo</a></li>
			</ul>							
		</body>
	</html>
	'''


cmd_status_subject=u'SVVPA - Información del sistema'
cmd_status_html=u'<html><body><p>Adjunto se envían los registros más relevantes del sistema</p></body></html>'

cmd_reboot_subject=u'SVVPA - Reinicio del sistema'
cmd_reboot_html=u'<html><body><p>El sistema se está reiniciando. Este proceso tarda aproximadamente 1 minuto.</p></body></html>'

cmd_saveFile_subject_OK=u'SVVPA - Copia Google Drive correcta ({eventId})'
cmd_saveFile_subject_ERROR=u'SVVPA - Error en la subida a Google Drive ({eventId})'
cmd_saveFile_html_OK=u'<html><body><p>La imagen y el vídeo se han copiado correctamente a google drive. Puedes ver las imágenes y vídeos guardados en <a href="https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing">este enlace</a>.</p></body></html>'
cmd_saveFile_html_ERROR=u'<html><body><p>Se han producido los siguientes errores al subir los archivos a google drive:</p><p>{error}</p></body></html>'

cmd_shutdown_subject_OK=u'SVVPA - Apagando sistema'
cmd_shutdown_subject_CONFIRM=u'SVVPA - Confirmar apagado: CMD_SVVPA APAGAR {code}'
cmd_shutdown_subject_ERROR=u'SVVPA - Código de apagado erróneo'
cmd_shutdown_html_OK=u'<html><body><p>Código de confirmación de apagado aceptado. El sistema se apagará en unos segundos. Recuerda que para iniciar de nuevo el sistema es necesario desactivar y volver a activar físicamente el mini-interruptor que está junto a las baterías.</p></body></html>'
cmd_shutdown_html_CONFIRM=u'<html><body><h4>¿Confirmar apagado?</h4><p>Se va a proceder a apagar el sistema. Recuerda que una vez apagado, <ins>solo</ins> se puede volver a iniciar desactivando y activando físicamente el mini-interruptor que está junto a las baterías.</p><p>Si realmente quieres apagar el sistema <b>responde a este email <mark>sin modificar el asunto</mark></b>.</p></body></html>'
cmd_shutdown_html_ERROR=u'<html><body><p>El código de confirmación utilizado para apagar el sistema es inválido. Recuerda que los códigos caducan en una hora y no se pueden reutilizar.</p></body></html>'


cmd_openReverseSsh_subject_OPEN=u'SVVPA - Servicio SSH abierto'
cmd_openReverseSsh_subject_CLOSE=u'SVVPA - Servicio SSH cerrado'
cmd_openReverseSsh_html_OPEN=u'<html><body><p>Se ha abierto el servicio SSH en el puerto {port} del servidor {server}.El servicio estará activo <b>{time} segundos</b>.</p></body></html>'
cmd_openReverseSsh_html_CLOSE=u'<html><body>El servicio ssh reverso se ha cerrado porque ha transcurrido el tiempo de expiración.</body></html>'

cmd_motionDetection_subject_INICIAR=u'SVVPA - Detección de movimiento activada'
cmd_motionDetection_subject_PARAR=u'SVVPA - Detección de movimiento desactivada'
cmd_motionDetection_subject_PAUSAR=u'SVVPA - Detección de movimiento pausada'
cmd_motionDetection_subject_REANUDAR=u'SVVPA - Detección de movimiento reanudada'
cmd_motionDetection_html_INICIAR=u'<html><body><p>Se acaba de iniciar la detección de movimiento. A partir de ahora, todos los movimientos serán grabados y enviados por email.</p><p>Si deseas parar el servicio, envía el comando correspondiente <a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PARAR">pulsando aquí</a>. También puedes pausarlo temporalmente <a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PAUSAR 1D">pulsando aquí</a> y modificando el asunto a criterio (S, M, H o D para segundos, minutos, horas o días)</p></body></html>'
cmd_motionDetection_html_PARAR=u'<html><body>Se acaba de detener la detección de movimiento. A partir de ahora, los movimientos <b>no</b> serán grabados ni enviados por email. Para iniciarla de nuevo envía el comando correspondiente haciendo <a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO INICIAR">click aquí</a>.</body></html>'
cmd_motionDetection_html_PAUSAR=u'<html><body><p>La detección de movimiento acaba de ser pausada, pero volverá a iniciarse automáticamente en <b>{time} segundos</b>. Recuerda que, hasta entonces, los movimientos <b>no serán grabados ni enviados por email</b>.</p><p>Si deseas iniciar la detección antes de que transcurra el tiempo envía el comando correspondiente haciendo <a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO INICIAR">click aquí</a>.</p></body></html>'
cmd_motionDetection_html_REANUDAR=u'<html><body><p>La detección de movimiento se ha reanudado correctamente. Recuerda que puedes <a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PARAR">pararla</a> o <a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PAUSAR 1D">pausarla</a> en cualquier momento.</p></body></html>'

cmd_updateRepository_subject=u'SVVPA - Repositorio actualizado correctamente'
cmd_updateRepository_html=u'<html><body>El repositorio se ha actualizado correctamente</body></html>'

cmd_emailNotif_subject_INICIAR=u'SVVPA - Notificaciones activadas'
cmd_emailNotif_subject_PARAR=u'SVVPA - Notificaciones desactivadas'
cmd_emailNotif_html_INICIAR=u'<html><body>Las notificaciones por email están activadas</body></html>'
cmd_emailNotif_html_PARAR=u'<html><body>Las notificaciones por email están desactivadas</body></html>'


error_general_subject=u'SVVPA - Error al procesar el comando {command}'
error_general_html=u'<html><body>Se ha producido el siguiente error al procesar el comando "{command}":<br><i>{error}</i></body></html>'


error_sintaxis_subject=u'SVVPA - Error en comando'
error_sintaxis_html=u'<html><body>Error al procesar el comando <i>{command}</i>. Probablemente la sintaxis no es correcta. Para ver los comandos disponibles y su sintaxis envía el comando ayuda haciendo <a href="mailto:{correo}?subject=CMD_SVVPA AYUDA">click aquí</a></body></html>'



FILE_CONSTANTS = os.environ['BIN_DIR']+'CONSTANTS.sh' 







###########################
###  F U N C I O N E S  ###
###########################

def notificar_email(subject, html, attachment=None):	
	s 	 = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	msg = gsender.Message(	subject 		= subject,
									to 		 	= os.environ['EMAIL_ADDR'],
									sender		= os.environ['GMAIL_ACCOUNT_ALIAS'],
									html			= html,
									attachments	= attachment)
	s.send(msg)
	s.close()	
	


def cmd_help(a=None):
	msg_subject	= cmd_help_subject
	msg_html		= cmd_help_html.format(correo=os.environ['GMAIL_ACCOUNT_ALIAS'])
	notificar_email(msg_subject, msg_html)
	


def cmd_saveFile(eventId):
	print u"[{}] {}: Guardando archivos en google drive (id:{})".format(datetime.datetime.now(), __file__, eventId)
	errorMsg=""
	imageFile 	 = os.environ['MOTION_DIR'] +  eventId + "." + os.environ['MOTION_IMAGE_EXT']
	videoFile 	 = os.environ['MOTION_DIR'] +  eventId + "." + os.environ['MOTION_VIDEO_EXT']
	imageLogFile = "/tmp/" +  eventId + "_IMAGEN.log"
	videoLogFile = "/tmp/" +  eventId + "_VIDEO.log"
	imageCmd 	 = os.environ['RCLONE_BIN'] + " --config " + os.environ['RCLONE_CONFIG'] + " copy " + imageFile + " google:SVVPA/imagenes 2>&1 |tee " + imageLogFile
	videoCmd 	 = os.environ['RCLONE_BIN'] + " --config " + os.environ['RCLONE_CONFIG'] + " copy " + videoFile + " google:SVVPA/videos 2>&1 |tee " + videoLogFile

	msg_subject		= cmd_saveFile_subject_OK.format(eventId=eventId)
	msg_html			= cmd_saveFile_html_OK
	msg_attachment = [imageLogFile, videoLogFile]

	if not os.path.isfile(imageFile):
		print >> sys.stderr, u"[{}] {}: ERROR! No se encuentra la imagen {}.".format(datetime.datetime.now(), __file__, imageFile)
		raise Exception(u'{0}: No se encuentra la imagen del evento! Comprueba que has escrito correctamente el identificador del evento'.format(imageFile))	
	if not os.path.isfile(videoFile):
		print >> sys.stderr, u"[{}] {}: ERROR! No se encuentra el vídeo {}".format(datetime.datetime.now(), __file__, videoFile)
		raise Exception(u'{0}: No se encuentra el vídeo del evento! Es posible que aún se esté procesando. Por favor, inténtalo de nuevo más tarde'.format(videoFile))
	if len(eventId.split("_")) < 12:
		print >> sys.stderr, u"[{}] {}: ERROR! El identificador del evento ({}) tiene menos de 12 tokens".format(datetime.datetime.now(), __file__, eventId)
		raise Exception(u'Error en el identificador del evento "{0}". Recuerda que el identificador son 12 números separados por guiones bajos'.format(eventId))

	try:
		imageCmdResult = proc.call(imageCmd, shell=True)
	except Exception as e:
		print >> sys.stderr, u"[{}] {}: ERROR! Se produjeron errores al subir la imagen a google drive: {}".format(datetime.datetime.now(), __file__, repr(e))
		errorMsg+=u'Error al enviar la imagen a google drive.\n{}\n'.format(repr(e))
		#raise type(e)('Error al enviar el archivo a google drive.\n' + str(e) + '\n' + imageCmd)

	try:
		videoCmdResult = proc.call(videoCmd, shell=True)
	except Exception as e:
		print >> sys.stderr, u"[{}] {}: ERROR! Se produjeron errores al subir el vídeo a google drive: {}".format(datetime.datetime.now(), __file__, repr(e))
		errorMsg+=u'Error al enviar el vídeo a google drive.\n{}\n'.format(repr(e))
	
	if imageCmdResult or videoCmdResult or errorMsg:
		print >> sys.stderr, u"[{}] {}: Se produjeron errores al subir los archivos del evento {} a google drive".format(eventId)
		msg_subject=cmd_saveFile_subject_ERROR.format(eventId=eventId)
		msg_html=cmd_saveFile_html_ERROR.format(error=errorMsg)

	notificar_email(msg_subject, msg_html, msg_attachment)

	for f in msg_attachment:
		os.remove(f)



def cmd_status(args):	
	print u"[{}] {}: Recopilando datos del sistema".format(datetime.datetime.now(), __file__)
	zipFileName='/tmp/log_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.zip'	
	cmds={'DF' 			: 'df -h',
			'DMESG' 		: 'dmesg',
			'TOP' 		: 'top -b -n 1',
			'PS' 			: 'ps aux',
			'SERVICES'	: '/usr/sbin/service SVVPA-service check_services',
			'CPU_TEMP' 	: os.environ['BIN_DIR']+'_readInternalTemp.sh',
			'SYSLOG'		: 'tail -n 1000 /var/log/syslog'}

	msg_subject		= cmd_status_subject
	msg_html			= cmd_status_html
	msg_attachment = [zipFileName]
	
	zf = zipfile.ZipFile(zipFileName, mode='w')
	for cmdLabel in cmds:
		f='/tmp/LOG_' + cmdLabel + '.txt'						
		proc.call(cmds[cmdLabel] + ' 2>&1 > ' + f, shell=True)
		zf.write(f, os.path.basename(f), compress_type=zipfile.ZIP_DEFLATED)
	zf.write(os.environ['LOG_FILE'], os.path.basename(os.environ['LOG_FILE']), compress_type=zipfile.ZIP_DEFLATED)				
	zf.close()

	notificar_email(msg_subject, msg_html, msg_attachment)
	os.remove(f)
	



def cmd_reboot(args):
	print u"[{}] {}: Reiniciando el sistema".format(datetime.datetime.now(), __file__)
	msg_subject	= cmd_reboot_subject
	msg_html		= cmd_reboot_html
	notificar_email(msg_subject, msg_html)
	proc.call('sudo /sbin/shutdown -r now', shell=True)



def cmd_shutdown(args):
	#primera vuelta, requerir confirmación
	if not args:
		print u"[{}] {}: Enviando código de confirmación de apagado".format(datetime.datetime.now(), __file__)
		msg_subject	= cmd_shutdown_subject_CONFIRM.format(code=get_shutdownConfirmCode())
		msg_html		= cmd_shutdown_html_CONFIRM
		notificar_email(msg_subject, msg_html)
	
	#confirmación recibida
	else:	
		if args == get_shutdownConfirmCode():
			print u"[{}] {}: Código de confirmación de apagado aceptado. Apagando el sistema".format(datetime.datetime.now(), __file__)
			msg_subject	= cmd_shutdown_subject_OK
			msg_html		= cmd_shutdown_html_OK
			notificar_email(msg_subject, msg_html)
			proc.call('sudo /sbin/shutdown -r now', shell=True)

		else:
			print >> sys.stderr, u"[{}] {}: ERROR! Código de confirmación de apagado erróneo".format(datetime.datetime.now(), __file__)
			msg_subject	= cmd_shutdown_subject_ERROR
			msg_html		= cmd_shutdown_html_ERROR
			notificar_email(msg_subject, msg_html)

	

def get_shutdownConfirmCode():
	return md5.new(datetime.datetime.now().strftime("%Y%m%d") + 'CMD_SVVPA').hexdigest()



#ssh reservo a servidor túnel
def cmd_openReverseSsh(args):
	print u"[{}] {}: Abriendo servicio ssh reverso en servidor {}:{} durante {} segundos".format(datetime.datetime.now(), __file__, os.environ['SSH_REMOTE_SERVER'], os.environ['SSH_REMOTE_TUNEL_PORT'], os.environ['SSH_REMOTE_TIMEOUT'])
	try:
		timeout		= int(os.environ['SSH_REMOTE_TIMEOUT'])
		msg_subject	= cmd_openReverseSsh_subject_OPEN
		msg_html	= cmd_openReverseSsh_html_OPEN.format(port=os.environ['SSH_REMOTE_TUNEL_PORT'], server=os.environ['SSH_REMOTE_SERVER'], time=timeout)

		cmd="sshpass -e ssh -p {port} -fCNR {tunelPort}:localhost:22 {user}@{server}".format(
                        port      = os.environ['SSH_REMOTE_PORT'],
                        tunelPort = os.environ['SSH_REMOTE_TUNEL_PORT'],
                        user      = os.environ['SSH_REMOTE_USER'],
                        server    = os.environ['SSH_REMOTE_SERVER'])
	
		proc.call(cmd, shell=True)	
		pid = proc.check_output("ps aux --sort start_time|egrep '"+cmd+"'|grep -v 'grep'|tail -n 1|awk '{print $2}'",shell=True).strip()
		#proc.call('(sleep {t} && kill {p} && _notifyEmail.sh SSH_CLOSED) &'.format(t=timeout, p=pid),shell=True)
		notificar_email(msg_subject, msg_html)

		t=0
		step=1
		while t<timeout and os.path.isdir("/proc/"+pid):
			time.sleep(step)
			t+=step

	except Exception as e:
		print u"[{}] {}: Error al procesar comando ssh reverso:\n{}".format(datetime.datetime.now(), __file__, repr(e))
	
	finally:
		print u"[{}] {}: Cerrando servicio SSH (pid={})".format(datetime.datetime.now(), __file__, pid)
		if os.path.isdir("/proc/"+pid):
			os.kill(int(pid), signal.SIGKILL)  		

		msg_subject	= cmd_openReverseSsh_subject_CLOSE
		msg_html	= cmd_openReverseSsh_html_CLOSE
		notificar_email(msg_subject, msg_html)



#start/stop/delay motion
def cmd_motionDetection(args):
	regex = re.compile('(?P<action>(INICIAR)|(PARAR))|(PAUSAR[ ]*(?P<time>\d+)(?P<format>[SsMmHhDd]))')
	mult = {
		'S' 	: 1,
		'M'	: 60,
		'H'	: 3600,
		'D'	: 86400
	}

	r = regex.search(args)
	if r:
		if r.group('action') == "INICIAR":
			msg_subject	= cmd_motionDetection_subject_INICIAR
			msg_html		= cmd_motionDetection_html_INICIAR
			print u"[{}] {}: Iniciando servicio MOTION".format(datetime.datetime.now(), __file__)
			proc.call('sudo service motion restart', shell=True)
			
		elif r.group('action') == "PARAR":
			msg_subject	= cmd_motionDetection_subject_PARAR
			msg_html		= cmd_motionDetection_html_PARAR
			print u"[{}] {}: Parando servicio MOTION".format(datetime.datetime.now(), __file__)
			proc.call('sudo service motion stop', shell=True)
			
		else:
			try:
				timeout=int(r.group('time'))*mult[r.group('format')]
				print u"[{}] {}: Pausando servicio MOTION durante {} segundos".format(datetime.datetime.now(), __file__, str(timeout))
				msg_subject	= cmd_motionDetection_subject_PAUSAR
				msg_html		= cmd_motionDetection_html_PAUSAR.format(time=str(timeout), correo=os.environ['GMAIL_ACCOUNT_ALIAS'])
				proc.call('sudo service motion stop', shell=True)				
				notificar_email(msg_subject, msg_html)
				step=1
				t=0
				while t<timeout:
					time.sleep(step)
					t+=step
				
			finally:
				msg_subject	= cmd_motionDetection_subject_REANUDAR
				msg_html		= cmd_motionDetection_html_REANUDAR
				print u"[{}] {}: Reanudando servicio MOTION".format(datetime.datetime.now(), __file__)
				proc.call('sudo service motion start', shell=True)

		notificar_email(msg_subject, msg_html)			

	else:
		e=u"Error en el formato del comando DETECTAR_MOVIMIENTO."
		print >> sys.stderr, u"[{}] {}: ERROR! {}".format(datetime.datetime.now(), __file__, e)
		raise Exception(e)



def cmd_updateRepository(args):
	print u"[{}] {}: Actualizando repositorio SVVPA desde github".format(datetime.datetime.now(), __file__)
	proc.call('cd {}; git pull'.format(os.environ['SVVPA_DIR']), shell=True)

	msg_subject	= cmd_updateRepository_subject
	msg_html	= cmd_updateRepository_html
	notificar_email(msg_subject, msg_html)	



def cmd_notifEmail(args):
	regex = re.compile('(INICIAR)|(PARAR)|(ESTADO)')

	r = regex.search(args)
	if r:
		if 'INICIAR' in r.group():
			msg_subject	= cmd_emailNotif_subject_INICIAR
			msg_html	= cmd_emailNotif_html_INICIAR
			print u'[{}] {}: Activando las notificaciones por emails'.format(datetime.datetime.now(), __file__)
			cmd = u"sed -i -r 's/export EMAIL_NOTIF=\"([a-zA-Z]+)\"/export EMAIL_NOTIF=\"{}\"/g' {}".format('ON', FILE_CONSTANTS)
			proc.call(cmd, shell=True)			
			
		elif 'PARAR' in r.group():
			msg_subject	= cmd_emailNotif_subject_PARAR
			msg_html	= cmd_emailNotif_html_PARAR
			print u'[{}] {}: Parando las notificaciones por emails'.format(datetime.datetime.now(), __file__)
			cmd = u"sed -i -r 's/export EMAIL_NOTIF=\"([a-zA-Z]+)\"/export EMAIL_NOTIF=\"{}\"/g' {}".format('OFF', FILE_CONSTANTS)
			proc.call(cmd, shell=True)			
			
		else:
			try:
				output = proc.check_output(u'egrep EMAIL_NOTIF {}'.format(FILE_CONSTANTS), shell=True)
				f = re.findall('"([a-zA-Z]+)"', output)
	            
				if len(f)>0 and 'ON' in f[0]:						
					msg_subject	= cmd_emailNotif_subject_INICIAR
					msg_html	= cmd_emailNotif_html_INICIAR
	        		
				else:
					msg_subject	= cmd_emailNotif_subject_PARAR
					msg_html	= cmd_emailNotif_html_PARAR

			except Exception as e:
				print >> sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado: \n {}".format(datetime.datetime.now(), __file__, e)
	        	        
		notificar_email(msg_subject, msg_html)			

	else:
		e=u"Error en el formato del comando DETECTAR_MOVIMIENTO."
		print >> sys.stderr, u"[{}] {}: ERROR! {}".format(datetime.datetime.now(), __file__, e)
		raise Exception(e)




#############################
###  C O N S T A N T E S  ###
#############################
#define email labels
CMD_SVVPA	= 'CMD_SVVPA'
CMD_OK		= 'CMD_OK'
CMD_WORKING	= 'CMD_WORKING'
CMD_TIMEOUT	= 'CMD_TIMEOUT'
CMD_ERROR	= 'CMD_ERROR'

#Define los comandos disponibles
CMD_SVVPA={
		'AYUDA' 							: cmd_help,
		'GUARDAR_EN_GOOGLE_DRIVE'	: cmd_saveFile,
		'ESTADO_DEL_SISTEMA' 		: cmd_status,
		'ACTIVAR_GESTION_REMOTA' 	: cmd_openReverseSsh,
		'DETECTAR_MOVIMIENTO' 		: cmd_motionDetection,
#		'VISTA_EN_DIRECTO' 			: cmd_lifeView,	#Configurar motion para que guarde una captura periódica que se sobreescriba, y enviar dicho archivo
		'ACTUALIZAR_REPOSITORIO'	: cmd_updateRepository,
		'REINICIAR' 					: cmd_reboot,
		'APAGAR'							: cmd_shutdown,
		'NOTIFICAR_EMAIL'				: cmd_notifEmail		
		}



#Reconecta y obtiene un email by UID si es necesario. Importante que se llame esta función antes de modificar emails (labels, read/unread, move, ...) 
def getEmailByUid(uid, e=None):
	if not e or not e.gmail.logged_in:
		g = greader.login(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
		e = g.mailbox('CMD_SVVPA').mail(prefetch=True,uid=uid)[0]
	return e




#################
###  M A I N  ###
#################
def main(args):
	re_subject	= re.compile('CMD_SVVPA[ ]+(?P<cmd>\w+)[ ]*(?P<args>.*)')
	g  	 	= greader.login(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	emails 		= g.mailbox('CMD_SVVPA').mail(unread=True)
	uids 		= [e.uid for e in emails]
	g.logout()
		
	for uid in uids:
		e = getEmailByUid(uid)
		e.read()
		subject = e.subject.replace("\r\n","")
		
		print u"[{}] {}: Procesando comando '{}'".format(datetime.datetime.now(), __file__, subject)
		r = re_subject.search(subject)			

		if r and CMD_SVVPA.has_key(r.group('cmd')):								
			try:
				print u"[{}] {}: Ejecutando comando '{}'".format(datetime.datetime.now(), __file__, r.group('cmd'))
				e=getEmailByUid(uid, e)
				e.add_label(CMD_WORKING) 
				CMD_SVVPA[r.group('cmd')](r.group('args'))
				print u"[{}] {}: Comando '{}' ejecutado correctamente".format(datetime.datetime.now(), __file__, r.group('cmd'))
				e=getEmailByUid(uid, e)
				e.add_label(CMD_OK)  			
				e.remove_label(CMD_WORKING)
				
			except Exception, ex:
				print >> sys.stderr, u"[{}] {}: ERROR! Ha ocurrido el error '{}' al procesar el comando '{}'".format(datetime.datetime.now(), __file__, repr(ex), r.group('cmd'))
				e=getEmailByUid(uid, e)
				e.add_label(CMD_ERROR)
				msg_subject	= error_general_subject.format(command=r.group('cmd'))
				msg_html	= error_general_html.format(command=r.group('cmd'), error=ex)
				notificar_email(msg_subject, msg_html)	
					
		else:
			print >> sys.stderr, u"[{}] {}: ERROR! La sintaxis del comando '{}' no es correcta.".format(datetime.datetime.now(), __file__,r.group('cmd'))
			e=getEmailByUid(uid, e)
			e.add_label(CMD_ERROR)
			msg_subject	= error_sintaxis_subject
			msg_html		= error_sintaxis_html.format(command=r.group('cmd'), correo=os.environ['GMAIL_ACCOUNT_ALIAS'])
			notificar_email(msg_subject, msg_html)	
		


if __name__ == "__main__":
	sys.exit(main(sys.argv))


