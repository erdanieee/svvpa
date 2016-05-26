#!/usr/bin/env python
#coding=utf-8

import sys, os, traceback
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
			<h3>Control de SVVPA mediante correos electronicos</h3>
			<p>SVVPA tiene la capacidad de ejecutar acciones recibidas mediante correo electronico. Para ello, solo hay que mandar un email a <a href="mailto:{correo}">{correo}</a> cuyo asunto contenga la accion a ejecutar y esperar a la recepcion del correo de confirmacion que indica que la ejecucion se ha realizado correctamente. La sintaxis de las acciones sigue el siguiente formato:<br>
			<i>CMD_SVVPA COMANDO ARG1 ARG2 ARG3 ... ARGn</i><br>
		donde <i>COMANDO</i> indica el comando que se desea ejecutar y <i>ARGi</i> los argumentos de ese comando (algunos comandos no necesitan argumentos). A continuacion se muestran los comandos y argumentos disponibles por el momento:
			<ul>
				<li><b>AYUDA</b> - Envia este email, recordandote los comandos y argumentos disponibles y ejemplos de como usarlos. Haciendo click en los enlaces de los <a href="mailto:{correo}?subject=CMD_SVVPA AYUDA">ejemplos como este</a>, se compone automaticamente un email que puede ser enviado tal cual o modificado a criterio.</li>	
				<li><b>GUARDAR_EN_GOOGLE_DRIVE codigoDelEvento</b> - Guarda en google drive la imagen y el video que corresponde al evento con codigo <i>codigoDelEvento</i>. El codigo del evento se puede obtener del asunto del email que se envia automaticamente cuando se detecta un movimiento. <a href="mailto:{correo}?subject=CMD_SVVPA GUARDAR_EN_GOOGLE_DRIVE 2016_01_02_15_30_13_12332_123_543_23_5543_12">Ver ejemplo</a></li>
				<li><b>ESTADO_DEL_SISTEMA</b> - Envia un email con informacion sobre SVVP, como el espacio disponible, la temperatura de la CPU, el registro de eventos del sistema, ... <a href="mailto:{correo}?subject=CMD_SVVPA ESTADO_DEL_SISTEMA">Ver ejemplo</a></li>
			<li><b>DETECTAR_MOVIMIENTO accion tiempo</b> - Comando para iniciar, parar o pausar el servicio de deteccion de movimiento. Util cuando estas en E.C. y no deseas ser grabado :). Si la accion es <i>PARAR</i> (<a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PARAR">Ver ejemplo</a>), el servicio se detiene hasta que se reciba la accion <i>INICIAR</i> (<a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO INICIAR">Ver ejemplo</a>). Si la accion es <i>PAUSAR</i> (<a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PAUSAR 5H">Ver ejemplo</a>), el servicio se detiene temporalmente. En este ultimo caso se requiere tambien el argumento <i>tiempo</i>, que determina la pausa en formato <i>nU</i>, siendo <i>n</i> la cantidad, y <i>U</i> la unidad (S, M, H o D para segundos, minutos, horas o dias. Ej: 10H para pausar durante 10 horas. 3D para pausar durante 3 dias)</li>
			<li><b>NOTIFICAR_EMAIL accion</b> - Este comando sirve para controlar las notificaciones que se reciben por email (deteccion de nuevos movimientos, arranque/parada del sistema, errores, ...), donde <i>accion</i> puede tomar los valores <i>INICIAR</i> para activar (<a href="mailto:{correo}?subject=CMD_SVVPA NOTIFICAR_EMAIL INICIAR">Ver ejemplo</a>), <i>PARAR</i> para desactivar (<a href="mailto:{correo}?subject=CMD_SVVPA NOTIFICAR_EMAIL PARAR">Ver ejemplo</a>) o <i>ESTADO</i> para comprobar el estado (<a href="mailto:{correo}?subject=CMD_SVVPA NOTIFICAR_EMAIL ESTADO">Ver ejemplo</a>).</li>	
			<li><b>ACTUALIZAR_REPOSITORIO</b> - Actualiza el repositorio Github de SVVPA. Normalmente este comando solo lo ejecuta Er Danie. <a href="mailto:{correo}?subject=CMD_SVVPA ACTUALIZAR_REPOSITORIO">Ver ejemplo</a></li>
			<li><b>ACTIVAR_GESTION_REMOTA</b> - Abre un puerto en un servidor remoto para realizar un ssh reverso. Esta opcion es util para administrar SVVPA cuando no tiene conexion a internet a traves de una IP publica real (ej: conexion 3g). Normalmente este comando solo lo ejecuta Er Danie. <a href="mailto:{correo}?subject=CMD_SVVPA ACTIVAR_GESTION_REMOTA">Ver ejemplo</a></li>
			<li><b>REINICIAR</b> - Reinicia el sistema. Este comando es util cuando algo no esta funcionando correctamente. El reinicio tarda aproximadamente 1 minuto. <a href="mailto:{correo}?subject=CMD_SVVPA REINICIAR">Ver ejemplo</a></li>
			<li><b>APAGAR</b> - Apaga el sistema. Cuando se envia este comando, SVVPA responde con un correo de confirmacion. Para apagar correctamente SVVPA, se debe confirmar el apagado respondiendo al correo de confirmacion sin modificar el asunto. Atencion: Una vez apagado el sistema, solo se puede volver a iniciar desactivando y activando fisicamente el mini-interruptor que esta junto a las baterias. Asegurate de <b>no ejecutar NUNCA</b> este comando cuando estes fuera de E.C. <a href="mailto:{correo}?subject=CMD_SVVPA APAGAR">Ver ejemplo</a></li>
			</ul>							
		</body>
	</html>
	'''


cmd_status_subject=u'SVVPA - Informacion del sistema'
cmd_status_html=u'<html><body><p>Adjunto se envian los registros mas relevantes del sistema</p></body></html>'

cmd_reboot_subject=u'SVVPA - Reinicio del sistema'
cmd_reboot_html=u'<html><body><p>El sistema se esta reiniciando. Este proceso tarda aproximadamente 1 minuto.</p></body></html>'

cmd_saveFile_subject_OK=u'SVVPA - Copia Google Drive correcta ({eventId})'
cmd_saveFile_subject_ERROR=u'SVVPA - Error en la subida a Google Drive ({eventId})'
cmd_saveFile_html_OK=u'<html><body><p>La imagen y el video se han copiado correctamente a google drive. Puedes ver las imagenes y videos guardados en <a href="https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing">este enlace</a>.</p></body></html>'
cmd_saveFile_html_ERROR=u'<html><body><p>Se han producido los siguientes errores al subir los archivos a google drive:</p><p>{error}</p></body></html>'

cmd_shutdown_subject_OK=u'SVVPA - Apagando sistema'
cmd_shutdown_subject_CONFIRM=u'SVVPA - Confirmar apagado: CMD_SVVPA APAGAR {code}'
cmd_shutdown_subject_ERROR=u'SVVPA - Codigo de apagado erroneo'
cmd_shutdown_html_OK=u'<html><body><p>Codigo de confirmacion de apagado aceptado. El sistema se apagara en unos segundos. Recuerda que para iniciar de nuevo el sistema es necesario desactivar y volver a activar fisicamente el mini-interruptor que esta junto a las baterias.</p></body></html>'
cmd_shutdown_html_CONFIRM=u'<html><body><h4>¿Confirmar apagado?</h4><p>Se va a proceder a apagar el sistema. Recuerda que una vez apagado, <ins>solo</ins> se puede volver a iniciar desactivando y activando fisicamente el mini-interruptor que esta junto a las baterias.</p><p>Si realmente quieres apagar el sistema <b>responde a este email <mark>sin modificar el asunto</mark></b>.</p></body></html>'
cmd_shutdown_html_ERROR=u'<html><body><p>El codigo de confirmacion utilizado para apagar el sistema es invalido. Recuerda que los codigos caducan en una hora y no se pueden reutilizar.</p></body></html>'


cmd_openReverseSsh_subject_OPEN=u'SVVPA - Servicio SSH abierto'
cmd_openReverseSsh_subject_CLOSE=u'SVVPA - Servicio SSH cerrado'
cmd_openReverseSsh_html_OPEN=u'<html><body><p>Se ha abierto el servicio SSH en el puerto {port} del servidor {server}.El servicio estara activo <b>{time} segundos</b>.</p></body></html>'
cmd_openReverseSsh_html_CLOSE=u'<html><body>El servicio ssh reverso se ha cerrado porque ha transcurrido el tiempo de expiracion.</body></html>'

cmd_motionDetection_subject_INICIAR=u'SVVPA - Deteccion de movimiento activada'
cmd_motionDetection_subject_PARAR=u'SVVPA - Deteccion de movimiento desactivada'
cmd_motionDetection_subject_PAUSAR=u'SVVPA - Deteccion de movimiento pausada'
cmd_motionDetection_subject_REANUDAR=u'SVVPA - Deteccion de movimiento reanudada'
cmd_motionDetection_html_INICIAR=u'<html><body><p>Se acaba de iniciar la deteccion de movimiento. A partir de ahora, todos los movimientos seran grabados y enviados por email.</p><p>Si deseas parar el servicio, envia el comando correspondiente <a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PARAR">pulsando aqui</a>. Tambien puedes pausarlo temporalmente <a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PAUSAR 1D">pulsando aqui</a> y modificando el asunto a criterio (S, M, H o D para segundos, minutos, horas o dias)</p></body></html>'
cmd_motionDetection_html_PARAR=u'<html><body>Se acaba de detener la deteccion de movimiento. A partir de ahora, los movimientos <b>no</b> seran grabados ni enviados por email. Para iniciarla de nuevo envia el comando correspondiente haciendo <a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO INICIAR">click aqui</a>.</body></html>'
cmd_motionDetection_html_PAUSAR=u'<html><body><p>La deteccion de movimiento acaba de ser pausada, pero volvera a iniciarse automaticamente en <b>{time} segundos</b>. Recuerda que, hasta entonces, los movimientos <b>no seran grabados ni enviados por email</b>.</p><p>Si deseas iniciar la deteccion antes de que transcurra el tiempo envia el comando correspondiente haciendo <a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO INICIAR">click aqui</a>.</p></body></html>'
cmd_motionDetection_html_REANUDAR=u'<html><body><p>La deteccion de movimiento se ha reanudado correctamente. Recuerda que puedes <a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PARAR">pararla</a> o <a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PAUSAR 1D">pausarla</a> en cualquier momento.</p></body></html>'

cmd_updateRepository_subject=u'SVVPA - Repositorio actualizado correctamente'
cmd_updateRepository_html=u'<html><body>El repositorio se ha actualizado correctamente</body></html>'

cmd_emailNotif_subject_INICIAR=u'SVVPA - Notificaciones activadas'
cmd_emailNotif_subject_PARAR=u'SVVPA - Notificaciones desactivadas'
cmd_emailNotif_html_INICIAR=u'<html><body>Las notificaciones por email estan activadas</body></html>'
cmd_emailNotif_html_PARAR=u'<html><body>Las notificaciones por email estan desactivadas</body></html>'

cmd_shell_subject=u'SVVPA - Comando shell'
cmd_help_html=u'<html><body>Se ha ejecutado el comando "{}" con la siguiente salida:<br>{}</body></html>'


error_general_subject=u'SVVPA - Error al procesar el comando {command}'
error_general_html=u'<html><body>Se ha producido el siguiente error al procesar el comando "{command}":<br><i>{error}</i></body></html>'


error_sintaxis_subject=u'SVVPA - Error en comando'
error_sintaxis_html=u'<html><body>Error al procesar el comando <i>{command}</i>. Probablemente la sintaxis no es correcta. Para ver los comandos disponibles y su sintaxis envia el comando ayuda haciendo <a href="mailto:{correo}?subject=CMD_SVVPA AYUDA">click aqui</a></body></html>'



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
		print >> sys.stderr, u"[{}] {}: ERROR! No se encuentra el video {}".format(datetime.datetime.now(), __file__, videoFile)
		raise Exception(u'{0}: No se encuentra el video del evento! Es posible que aun se este procesando. Por favor, intentalo de nuevo mas tarde'.format(videoFile))
	if len(eventId.split("_")) < 12:
		print >> sys.stderr, u"[{}] {}: ERROR! El identificador del evento ({}) tiene menos de 12 tokens".format(datetime.datetime.now(), __file__, eventId)
		raise Exception(u'Error en el identificador del evento "{0}". Recuerda que el identificador son 12 numeros separados por guiones bajos'.format(eventId))

	try:
		imageCmdResult = proc.call(imageCmd, shell=True)
	except Exception as e:
		print >> sys.stderr, u"[{}] {}: ERROR! Se produjeron errores al subir la imagen a google drive:".format(datetime.datetime.now(), __file__)
		traceback.print_exc()
		errorMsg+=u'Error al enviar la imagen a google drive.\n{}\n'.format(repr(e))
		#raise type(e)('Error al enviar el archivo a google drive.\n' + str(e) + '\n' + imageCmd)

	try:
		videoCmdResult = proc.call(videoCmd, shell=True)
	except Exception as e:
		print >> sys.stderr, u"[{}] {}: ERROR! Se produjeron errores al subir el video a google drive:".format(datetime.datetime.now(), __file__)
		traceback.print_exc()
		errorMsg+=u'Error al enviar el video a google drive.\n{}\n'.format(repr(e))
	
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
	#primera vuelta, requerir confirmacion
	if not args:
		print u"[{}] {}: Enviando codigo de confirmacion de apagado".format(datetime.datetime.now(), __file__)
		msg_subject	= cmd_shutdown_subject_CONFIRM.format(code=get_shutdownConfirmCode())
		msg_html		= cmd_shutdown_html_CONFIRM
		notificar_email(msg_subject, msg_html)
	
	#confirmacion recibida
	else:	
		if args == get_shutdownConfirmCode():
			print u"[{}] {}: Codigo de confirmacion de apagado aceptado. Apagando el sistema".format(datetime.datetime.now(), __file__)
			msg_subject	= cmd_shutdown_subject_OK
			msg_html		= cmd_shutdown_html_OK
			notificar_email(msg_subject, msg_html)
			proc.call('sudo /sbin/shutdown -r now', shell=True)

		else:
			print >> sys.stderr, u"[{}] {}: ERROR! Codigo de confirmacion de apagado erroneo".format(datetime.datetime.now(), __file__)
			msg_subject	= cmd_shutdown_subject_ERROR
			msg_html		= cmd_shutdown_html_ERROR
			notificar_email(msg_subject, msg_html)

	

def get_shutdownConfirmCode():
	return md5.new(datetime.datetime.now().strftime("%Y%m%d") + 'CMD_SVVPA').hexdigest()



#ssh reservo a servidor tunel
def cmd_openReverseSsh(args):
	print u"[{}] {}: Abriendo servicio ssh reverso en servidor {}:{} durante {} segundos".format(datetime.datetime.now(), __file__, os.environ['SSH_REMOTE_SERVER'], os.environ['SSH_REMOTE_TUNEL_PORT'], os.environ['SSH_REMOTE_TIMEOUT'])
	try:
		timeout		= int(os.environ['SSH_REMOTE_TIMEOUT'])
		msg_subject	= cmd_openReverseSsh_subject_OPEN
		msg_html	= cmd_openReverseSsh_html_OPEN.format(port=os.environ['SSH_REMOTE_TUNEL_PORT'], server=os.environ['SSH_REMOTE_SERVER'], time=timeout)

		cmd="sshpass -e ssh -oStrictHostKeyChecking=no -p {port} -fCNR {tunelPort}:localhost:22 {user}@{server}".format(
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
		print u"[{}] {}: Error al procesar comando ssh reverso:".format(datetime.datetime.now(), __file__)
		traceback.print_exc()
	
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
	
	
def cmd_updateRepository(args):
	print u"[{}] {}: Ejecutando comando bash".format(datetime.datetime.now(), __file__)
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
				print >> sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado:".format(datetime.datetime.now(), __file__)
				traceback.print_exc()
	        	        
		notificar_email(msg_subject, msg_html)			

	else:
		e=u"Error en el formato del comando DETECTAR_MOVIMIENTO."
		print >> sys.stderr, u"[{}] {}: ERROR! {}".format(datetime.datetime.now(), __file__, e)
		raise Exception(e)



		
	def cmd_shell(cmd):
		if not cmd:
			msg_subject	= error_general_subject
			msg_html	= error_general_html
		   
		else:		
			try:			
				p = proc.check_output(cmd, shell=True).strip()
				msg_subject	= cmd_shell_subject
				msg_html	= cmd_help_html.format(cmd, p)
					 
			except Exception as e:
				print >>sys.stderr, u"[{}] {}: ERROR! Se produjo un error inesperado al ejecutar el comando bash:".format(datetime.datetime.now(), __file__)
				traceback.print_exc()
				raise Exception(e)				   
 
		notificar_email(msg_subject, msg_html)




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
#		'VISTA_EN_DIRECTO' 			: cmd_lifeView,	#Configurar motion para que guarde una captura periodica que se sobreescriba, y enviar dicho archivo
		'ACTUALIZAR_REPOSITORIO'	: cmd_updateRepository,
		'REINICIAR' 				: cmd_reboot,
		'APAGAR'					: cmd_shutdown,
		'NOTIFICAR_EMAIL'			: cmd_notifEmail,
		'SHELL'						: cmd_shell		
		}



#Reconecta y obtiene un email by UID si es necesario. Importante que se llame esta funcion antes de modificar emails (labels, read/unread, move, ...) 
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


