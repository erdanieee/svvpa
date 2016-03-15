#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


##############
### EMAILS ###
##############
cmd_help_subject=u"Ayuda CMD_SVVPA"
cmd_help_text=u"Este correo se ha enviado en formato html, pero parece que tu lector solo permite texto plano. Para ver correctamente el correo activa la opción para visualizar los emails en el formato original."
cmd_help_html=u'''
	<html>
		<body>
			<h3>Ayuda del control remoto de SVVPA mediante emails</h3>
			<p>SVVPA tiene la capacidad de recibir comandos a través de correo electrónico. Para enviar un comando, manda un email a <a href="mailto:{correo}">{correo}</a> cuyo asunto contenga <i>CMD_SVVPA COMANDO ARG1 ARG2 ARG3 ... ARGn</i>, siendo <i>COMANDO</i> el comando que se desea ejecutar y <i>ARGi</i> los argumentos si fueran requeridos por el comando (Ej: CMD_SVVPA AYUDA). Los comandos disponibles por el momento son:
			<ul>
				<li><b>AYUDA</b> - Envía este email para recordarte los comandos disponibles y cómo usarlos. <a href="mailto:{correo}?subject=CMD_SVVPA AYUDA">Ver ejemplo</a></li>	
				<li><b>GUARDAR_EN_GOOGLE_DRIVE codigoDelEvento</b> - Guarda en google drive la imagen y el vídeo que corresponde al evento con código <i>codigoDelEvento</i>. El código del evento se puede obtener del asunto del email que se envía automáticamente cuando se detecta un movimiento. <a href="mailto:{correo}?subject=CMD_SVVPA GUARDAR_EN_GOOGLE_DRIVE 2016_01_02_15_30_13_12332_123_543_23_5543_12">Ver ejemplo</a></li>
				<li><b>ESTADO_DEL_SISTEMA</b> - Envía un email con información sobre SVVP, como el espacio disponible, la temperatura de la CPU, el registro de eventos del sistema, ... <a href="mailto:{correo}?subject=CMD_SVVPA ESTADO_DEL_SISTEMA">Ver ejemplo</a></li>
			<li><b>DETECTAR_MOVIMIENTO acción tiempo</b> - Comando para iniciar, parar o pausar el servicio de detección de movimiento. Útil cuando estás en E.C. y no deseas ser grabado :). Si la acción es <i>PARAR</i> (<a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PARAR">Ver ejemplo</a>), el servicio se detiene hasta que se reciba la acción <i>INICIAR</i> (<a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO INICIAR">Ver ejemplo</a>). Si la acción es <i>PAUSAR</i> (<a href="mailto:{correo}?subject=CMD_SVVPA DETECTAR_MOVIMIENTO PAUSAR 5H">Ver ejemplo</a>), el servicio se detiene temporalmente. En este último caso se requiere también el argumento <i>tiempo</i>, que determina la pausa en formato <i>nU</i>, siendo <i>n</i> la cantidad, y <i>U</i> la unidad (S, M, H o D para segundos, minutos, horas o días. Ej: 10H para pausar durante 10 horas. 3D para pausar durante 3 días)</li>	
			<li><b>ACTUALIZAR_REPOSITORIO</b> - Actualiza el repositorio Github de SVVPA. <a href="mailto:{correo}?subject=CMD_SVVPA ACTUALIZAR_REPOSITORIO">Ver ejemplo</a></li>
			<li><b>ACTIVAR_GESTION_REMOTA</b> - Abre un puerto en un servidor remoto para realizar un ssh reverso. Esta opción es útil para administrar SVVPA cuando no tiene conexión a internet a través de una IP pública real (ej: conexión 3g). <a href="mailto:{correo}?subject=CMD_SVVPA ACTIVAR_GESTION_REMOTA">Ver ejemplo</a></li>
			<li><b>REINICIAR</b> - Reinicia el sistema. Este comando es útil cuando algo no está funcionando correctamente. El reinicio tarda aproximádamente 1 minuto. <a href="mailto:{correo}?subject=CMD_SVVPA REINICIAR">Ver ejemplo</a></li>
			<li><b>APAGAR</b> - Apaga el sistema. Cuando se envía este comando, SVVPA responde con un correo de confirmación. Para apagar correctamente SVVPA se debe responder al correo de confirmación sin modificar el asunto. Atención: Una vez apagado el sistema, solo se puede volver a iniciar desactivando y activando físicamente el mini-interruptor que está junto a las baterías. Asegúrate de no ejecutar <b>NUNCA</b> este comando cuando estés fuera de E.C. <a href="mailto:{correo}?subject=CMD_SVVPA APAGAR">Ver ejemplo</a></li>
			</ul>							
		</body>
	</html>
	'''

'''
cmd_help_subject=
cmd_help_text=
cmd_help_html=
cmd_help_attachment=

cmd_help_subject=
cmd_help_text=
cmd_help_html=
cmd_help_attachment=

cmd_help_subject=
cmd_help_text=
cmd_help_html=
cmd_help_attachment=

cmd_help_subject=
cmd_help_text=
cmd_help_html=
cmd_help_attachment=

cmd_help_subject=
cmd_help_text=
cmd_help_html=
cmd_help_attachment=

cmd_help_subject=
cmd_help_text=
cmd_help_html=
cmd_help_attachment=

cmd_help_subject=
cmd_help_text=
cmd_help_html=
cmd_help_attachment=

cmd_help_subject=
cmd_help_text=
cmd_help_html=
cmd_help_attachment=

cmd_help_subject=
cmd_help_text=
cmd_help_html=
cmd_help_attachment=
'''










def notificar_email(subject, text, html, attachment):
	s 	 = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	msg = gsender.Message(	subject 		= subject,
									to 		 	= os.environ['EMAIL_ADDR'],
									sender		= os.environ['GMAIL_ACCOUNT_ALIAS'],
									text 			= text,
									html			= html,
									attachments	= attachment)
	s.send(msg)
	s.close()	
	


def cmd_help(a=None):	
	print "[{}] {}: Enviando mensaje de ayuda".format(datetime.datetime.now(), __file__)
	notificar_email(cmd_help_subject, cmd_help_text, cmd_help_html.format(correo=os.environ['GMAIL_ACCOUNT_ALIAS']), None)
	


def cmd_saveFile(eventId):
	print "[{}] {}: Guardando archivos {} en google drive".format(datetime.datetime.now(), __file__, eventId)
	errorMsg=""
	imageFile = os.environ['MOTION_DIR'] +  eventId + "." + os.environ['MOTION_IMAGE_EXT']
	videoFile = os.environ['MOTION_DIR'] +  eventId + "." + os.environ['MOTION_VIDEO_EXT']
	imageLogFile = "/tmp/" +  eventId + "_IMAGEN.log"
	videoLogFile = "/tmp/" +  eventId + "_VIDEO.log"
	imageCmd = os.environ['RCLONE_BIN'] + " --config " + os.environ['RCLONE_CONFIG'] + " copy " + imageFile + " google:SVVPA/imagenes 2>&1 |tee " + imageLogFile
	videoCmd = os.environ['RCLONE_BIN'] + " --config " + os.environ['RCLONE_CONFIG'] + " copy " + videoFile + " google:SVVPA/videos 2>&1 |tee " + videoLogFile

	if not os.path.isfile(imageFile):
		print "[{}] {}: ERROR! No se encuentra la imagen {}.".format(datetime.datetime.now(), __file__, imageFile)
		raise Exception(u'{0}: No se encuentra la imagen del evento! Comprueba que has escrito correctamente el identificador del evento'.format(imageFile))	
	if not os.path.isfile(videoFile):
		print "[{}] {}: ERROR! No se encuentra el vídeo {}".format(datetime.datetime.now(), __file__, videoFile)
		raise Exception(u'{0}: No se encuentra el vídeo del evento! Es posible que aún se esté procesando. Por favor, inténtalo de nuevo más tarde'.format(videoFile))
	if len(eventId.split("_")) < 12:
		print "[{}] {}: ERROR! El identificador del evento ({}) tiene menos de 12 tokens".format(datetime.datetime.now(), __file__, eventId)
		raise Exception(u'Error en el identificador del evento "{0}". Recuerda que el identificador son 12 números separados por guiones bajos'.format(eventId))

	try:
		print "[{}] {}: Subiendo imagen a google drive".format(datetime.datetime.now(), __file__)
		imageCmdResult = proc.call(imageCmd, shell=True)
	except Exception as e:
		print "[{}] {}: ERROR! Error al subir la imagen a google drive: {}".format(datetime.datetime.now(), __file__, repr(e))
		errorMsg+=u'Error al enviar la imagen a google drive.\n' + str(e) + '\n'
		#raise type(e)('Error al enviar el archivo a google drive.\n' + str(e) + '\n' + imageCmd)

	try:
		print "[{}] {}: Subiendo vídeo a google drive".format(datetime.datetime.now(), __file__)
		videoCmdResult = proc.call(videoCmd, shell=True)
	except Exception as e:
		print "[{}] {}: ERROR! Error al subir el vídeo a google drive: {}".format(datetime.datetime.now(), __file__, repr(e))
		errorMsg+=u'Error al enviar el vídeo a google drive.\n' + str(e) + '\n'
	
	if imageCmdResult or videoCmdResult or errorMsg:
		print "Transferencia con errores"
		asunto=u"Transferencia con ERRORES (" +  eventId + ")"
		texto=u"Se han producido los siguientes errores al subir los archivos a google drive:\n" + errorMsg + "\nAdjunto se envían los logs de las transferencias."
	else:
		print "Transferencia correcta"
		asunto=u"Transferencia correcta (" +  eventId + ")"
		texto=u"La imagen y el vídeo se han subido correctamente a google drive"
	
	print "[{}] {}: Enviando email con el resultado de la transacción".format(datetime.datetime.now(), __file__)
	s 	 = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	msg = gsender.Message(	subject 		= asunto,
									to 		 	= os.environ['EMAIL_ADDR'],
									sender		= os.environ['GMAIL_ACCOUNT_ALIAS'],
									text 			= texto,
									attachments	= [imageLogFile, videoLogFile])
	s.send(msg)
	s.close()


def cmd_status(args):	
	print "[{}] {}: Recopilando datos del sistema".format(datetime.datetime.now(), __file__)
	zipFileName='/tmp/log_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.zip'	
	cmds={'DF' 			: 'df -h',
			'DMESG' 		: 'dmesg',
			'TOP' 		: 'top -b -n 1',
			'PS' 			: 'ps aux',
			'SERVICES'	: '/usr/sbin/service SVVPA-service check_services',
			'CPU_TEMP' 	: os.environ['BIN_DIR']+'_readInternalTemp.sh',
			'SVVPA_LOG'	: 'cat ' + os.environ['LOG_FILE']}
	
	zf = zipfile.ZipFile(zipFileName, mode='w')
	for cmdLabel in cmds:
		f='/tmp/LOG_' + cmdLabel + '.txt'						
		proc.call(cmds[cmdLabel] + ' 2>&1|tee ' + f, shell=True)
		zf.write(f, compress_type=zipfile.ZIP_DEFLATED)
				
	zf.close()

	print "[{}] {}: Enviando email con los logs del sistema".format(datetime.datetime.now(), __file__)
	s 	 = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	msg = gsender.Message(	subject 		= u"Información del sistema",
									to 		 	= os.environ['EMAIL_ADDR'],
									sender		= os.environ['GMAIL_ACCOUNT_ALIAS'],
									text 			= u"Adjunto se envían los logs más relevantes del sistema",
									attachments	= [zipFileName])
	s.send(msg)
	s.close()	


def cmd_reboot(args):
	print "[{}] {}: Reiniciando el sistema".format(datetime.datetime.now(), __file__)
	s 	 = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	msg = gsender.Message(	subject 		= u"Reinicio del sistema",
									to 		 	= os.environ['EMAIL_ADDR'],
									sender		= os.environ['GMAIL_ACCOUNT_ALIAS'],
									text 			= u"El sistema se está reiniciando. Este proceso tarda aproximadamente 1 minuto.")
	s.send(msg)
	s.close()
	
	proc.call('sudo /sbin/shutdown -r now', shell=True)

	return args


def cmd_shutdown(args):
	#primera vuelta
	if not args:
		print "[{}] {}: Enviando código de confirmación de apagado".format(datetime.datetime.now(), __file__)
		s 	 = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
		msg = gsender.Message(	subject 		= u"Confirmar apagado: CMD_SVVPA APAGAR {0}".format(get_shutdownConfirmCode()),
										to 		 	= os.environ['EMAIL_ADDR'],
										sender		= os.environ['GMAIL_ACCOUNT_ALIAS'],
										html 			= u'''
											<html><body><h4>¿Confirmar apagado?</h4><p>Se va a proceder a apagar el sistema. Recuerda que una vez apagado,  <ins>solo</ins> se puede volver a iniciar desactivando y activando físicamente el mini-interruptor que está junto a las baterías.</p> <p>Si realmente quieres apagar el sistema <b>responde a este email <mark>sin modificar</mark> el asunto</b>.</p></body></html>''')
		s.send(msg)
		s.close()
	
	#confirmación
	else:	
		if args == get_shutdownConfirmCode():
			print "[{}] {}: Código de confirmación de apagado aceptado. Apagando el sistema".format(datetime.datetime.now(), __file__)
			proc.call('sudo /sbin/shutdown -r now', shell=True)

		else:
			print "[{}] {}: ERROR! Código de confirmación de apagado erróneo".format(datetime.datetime.now(), __file__)
			s 	 = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
			msg = gsender.Message(	subject 		= u"Código de apagado erróneo",
											to 		 	= os.environ['EMAIL_ADDR'],
											sender		= os.environ['GMAIL_ACCOUNT_ALIAS'],
											text 			= u"El código de confirmación utilizado para apagar el sistema es inválido. Recuerda que los códigos caducan en una hora y no se pueden reutilizar.")
			s.send(msg)
			s.close()

	

def get_shutdownConfirmCode():
	return md5.new(datetime.datetime.now().strftime("%Y%m%d") + 'CMD_SVVPA').hexdigest()


#ssh reservo a servidor túnel
def cmd_openReverseSsh(args):
	print "[{}] {}: Abriendo servicio ssh reverso en servidor {}".format(datetime.datetime.now(), __file__, os.environ['SSH_REMOTE_SERVER'])
	try:
		timeout=int(os.environ['SSH_REMOTE_TIMEOUT'])
		pid = proc.check_output('ssh -p {port} -fCNR {tunelPort}:localhost:22 {user}@{server} 2>&1 >/dev/null; echo $$'.format( 
			port = os.environ['SSH_REMOTE_PORT'], 
			tunelPort	= os.environ['SSH_REMOTE_TUNEL_PORT'],	
			user = os.environ['SSH_REMOTE_USER'], 
			server = os.environ['SSH_REMOTE_SERVER']), shell=True)
		s	= gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
		msg = gsender.Message(	subject 		= u"Servicio SSH abierto",
											to 		 		= os.environ['EMAIL_ADDR'],
											sender		= os.environ['GMAIL_ACCOUNT_ALIAS'],
											text 			= u"Se ha abierto el servicio SSH en el puerto {0} del servidor {1}. El servicio estará activo {2} minutos".format(os.environ['SSH_REMOTE_TUNEL_PORT'],os.environ['SSH_REMOTE_SERVER'], timeout/60))
		s.send(msg)
		s.close()

		t=0
		step=1
		while os.path.isdir("/proc/"+pid) and t<timeout:
			time.sleep(step)
			t+=step
	
	finally:
		print "[{}] {}: Cerrando servicio SSH".format(datetime.datetime.now(), __file__)
		s	= gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
		msg = gsender.Message(	subject 		= u"Servicio SSH cerrado",
											to 		 		= os.environ['EMAIL_ADDR'],
											sender		= os.environ['GMAIL_ACCOUNT_ALIAS'],
											text 			= u"Se ha cerrado el servicio SSH.")
		s.send(msg)
		s.close()
		os.kill(int(pid), signal.SIGKILL)		




#start/stop/delay motion
def cmd_motionDetection(args):
	regex = re.compile('(?P<action>(INICIAR)|(PARAR))|(PAUSAR[ ]*(?P<time>\d+)(?P<format>[SMHD]))')

	mult = {
		'S' : 1,
		'M'	: 60,
		'H'	: 3600,
		'D'	: 86400
	}

	r = regex.search(args)
	if r:
		if r.group('action') == "INICIAR":
			print "[{}] {}: Iniciando servicio MOTION".format(datetime.datetime.now(), __file__)
			proc.call('sudo service motion restart',shell=True)
			return
		elif r.group('action') == "PARAR":
			print "[{}] {}: Parando servicio MOTION".format(datetime.datetime.now(), __file__)
			proc.call('sudo service motion stop',shell=True)
			return
		else:
			try:
				timeout=int(r.group('time'))*int(mult[r.group('format')])
				print "[{}] {}: Pausando servicio MOTION durante {} segundos".format(datetime.datetime.now(), __file__, timeout)
				proc.call('sudo service motion stop',shell=True)				
				step=1
				t=0
				while t<timeout:
					time.sleep(step)
					t+=step
				
			finally:
				print "[{}] {}: Reanudando servicio MOTION".format(datetime.datetime.now(), __file__)
				proc.call('sudo service motion start',shell=True)
			return

	else:
		e="Error en el formato del comando DETECTAR_MOVIMIENTO."
		print "[{}] {}: ERROR! {}".format(datetime.datetime.now(), __file__, e)
		raise Exception(e)


def cmd_updateRepository(args):
	print "[{}] {}: Actualizando repositorio SVVPA desde github".format(datetime.datetime.now(), __file__)
	proc.call('cd {}; git pull'.format(os.environ['SVVPA_DIR']), shell=True)







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
		'APAGAR'							: cmd_shutdown		
		}







def main(args):
	re_subject = re.compile('CMD_SVVPA[ ]+(?P<cmd>\w+)[ ]*(?P<args>.*)')
	

	g  = greader.login(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	emails = g.mailbox('CMD_SVVPA').mail(prefetch=True,unread=True)#,to=os.environ['GMAIL_ACCOUNT_ALIAS'])
	
	for e in emails:
		subject = e.subject.replace("\r\n","")
		if e.has_label(CMD_WORKING):
			#Comprueba que no lleva mucho tiempo procesándose
			d=e.sent_at
			n=datetime.datetime.now()
			if (n-d).days > 0:
				print "[{}] {}: El comando '{}' lleva más de un día sin terminar de procesarse. Se va a intentar procesar de nuevo".format(datetime.datetime.now(), __file__, subject)
				e.add_label(CMD_TIMEOUT)
				e.remove_label(CMD_WORKING)
			else:
				print "[{}] {}: El comando '{}' ya se está procesando".format(datetime.datetime.now(), __file__, subject)
	
		else:
			print "[{}] {}: Procesando comando '{}'".format(datetime.datetime.now(), __file__, subject)
			r = re_subject.search(subject)			

			if r and CMD_SVVPA.has_key(r.group('cmd')):				
				try:
					print "[{}] {}: Ejecutando comando '{}'".format(datetime.datetime.now(), __file__, r.group('cmd'))
					e.add_label(CMD_WORKING) 
					CMD_SVVPA[r.group('cmd')](r.group('args'))
					print "[{}] {}: Comando '{}' ejecutado correctamente".format(datetime.datetime.now(), __file__, r.group('cmd'))
					e.add_label(CMD_OK) 			
				
				except Exception, ex:
					print "[{}] {}: ERROR! Ha ocurrido el error '{}' al procesar el comando '{}'".format(datetime.datetime.now(), __file__, repr(ex), r.group('cmd'))
					e.add_label(CMD_ERROR) 
					#Envia email con el error
					s 	 = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
					msg = gsender.Message(	subject 		= u"Error al procesar el comando {0}".format(r.group('cmd')),
													to 		 	= os.environ['EMAIL_ADDR'],
													text 			= u'Se ha producido el siguiente error al procesar el comando "{0}":\n{1}'.format(r.group('cmd'), ex))
					s.send(msg)
					s.close()
		
				e.read() 
					
			else:
				print "[{}] {}: ERROR! La sintaxis del comando '{}' no es correcta.".format(datetime.datetime.now(), __file__,r.group('cmd'))
				e.add_label(CMD_ERROR)
				e.read()
				s 	 = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
				msg = gsender.Message(	subject 		= u"Error en comando",
												to 		 	= os.environ['EMAIL_ADDR'],
												text			= u'Se envió el comando "{0}" pero la sintaxis no es correcta. Para ver los comando disponibles envía el comando "CMD_SVVPA AYUDA" a {1}.'.format(r.group('cmd'), os.environ['GMAIL_ACCOUNT_ALIAS']),
												html 			= u'''
												<html><body><h3>La sintaxis del comando enviado no es correcta</h3><p>Se envió el comando "{0}" pero la sintaxis no es correcta.</p> <p>Para ver los comando disponibles envía el comando de ayuda haciendo <a href="mailto:{1}?subject=CMD_SVVPA AYUDA">click aquí</a>.</p></body></html>'''.format(r.group('cmd'), os.environ['GMAIL_ACCOUNT_ALIAS']))
				s.send(msg)
				s.close()

	g.logout()	




if __name__ == "__main__":
	sys.exit(main(sys.argv))


