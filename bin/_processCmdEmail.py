#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import re
import subprocess as proc
import gmail_sender as gsender
import gmail as greader
import datetime


#define email labels
CMD_SVVPA	= 'CMD_SVVPA'
CMD_OK		= 'CMD_OK'
CMD_WORKING	= 'CMD_WORKING'
CMD_TIMEOUT	= 'CMD_TIMEOUT'
CMD_ERROR	= 'CMD_ERROR'




def cmd_help(a=None):	
	msg = gsender.Message(	
		subject = u"Ayuda CMD_SVVPA",
		to			= os.environ['EMAIL_ADDR'],
		#	text		= u"Éste es el cuerpo del mensaje en texto plano",
		html		= u'''
			<html>
				<body>
					<h3>Ayuda del control remoto de SVVPA mediante emails</h3>
					<p>SVVPA tiene la capacidad de recibir comandos a través de correo electrónico. Para enviar un comando, manda un email a <a href="mailto:{correo}">{correo}</a> cuyo asunto contenga <i>CMD_SVVPA COMANDO ARG1 ARG2 ARG3 ... ARGn</i>, siendo <i>COMANDO</i> el comando que se desea ejecutar y <i>ARGi</i> los argumentos si son requeridos por el comando (Ej: CMD_SVVPA AYUDA). Los comandos disponibles por el momento son:
					<ul>
						<li><b>AYUDA</b> - Envía este email con la ayuda de los comandos disponibles. <a href="mailto:{correo}?subject=CMD_SVVPA AYUDA">Ver ejemplo</a></li>	
						<li><b>GUARDAR_EN_GOOGLE_DRIVE codigoDelEvento</b> - Guarda en google drive la imagen y el vídeo que corresponde al evento con código <i>codigoDelEvento</i>. El código del evento se puede obtener del asunto del email que se envía automáticamente cuando se detecta un movimiento. <a href="mailto:{correo}?subject=CMD_SVVPA GUARDAR_EN_GOOGLE_DRIVE 2016_01_02_15_30_13_12332_123_543_23_5543_12">Ver ejemplo</a></li>
						<li><b>ESTADO_DEL_SISTEMA</b></li>
						<li><b>VISTA_EN_DIRECTO</b></li>
						<li><b>REINICIAR</b></li>
					</ul>							
				</body>
			</html>
	'''.format(correo=os.environ['GMAIL_ACCOUNT_ALIAS']))

	s = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	s.send(msg)
	s.close()


def cmd_saveFile(eventId):
	errorMsg=""
	imageFile = os.environ['MOTION_DIR'] +  eventId + "." + os.environ['MOTION_IMAGE_EXT']
	videoFile = os.environ['MOTION_DIR'] +  eventId + "." + os.environ['MOTION_VIDEO_EXT']
	imageLogFile = "/tmp/" +  eventId + "_IMAGEN.log"
	videoLogFile = "/tmp/" +  eventId + "_VIDEO.log"
	imageCmd = os.environ['RCLONE_BIN'] + " --config " + os.environ['RCLONE_CONFIG'] + " copy " + imageFile + " google:SVVPA/imagenes 2>&1 |tee " + imageLogFile
	videoCmd = os.environ['RCLONE_BIN'] + " --config " + os.environ['RCLONE_CONFIG'] + " copy " + videoFile + " google:SVVPA/imagenes 2>&1 |tee " + videoLogFile

	if not os.path.isfile(imageFile):
		raise Exception('{0}: No se encuentra la imagen del evento! Comprueba que has escrito correctamente el identificador del evento'.format(imageFile))	
	if not os.path.isfile(videoFile):
		raise Exception('No se encuentra el vídeo del evento! Es posible que aún se esté procesando. Por favor, inténtalo de nuevo más tarde')
#	if len(eventId.split("_")) < 12:
#		raise Exception('Error en el identificador del evento "{0}". Recuerda que el identificador son 12 números separados por guiones bajos'.format(eventId))

	try:
		print "Enviando imagen"
		imageCmdResult = proc.call(imageCmd, shell=True)
	except Exception as e:
		errorMsg+='Error al enviar la imagen a google drive.\n' + str(e) + '\n'
		#raise type(e)('Error al enviar el archivo a google drive.\n' + str(e) + '\n' + imageCmd)

	try:
		print "Enviando vídeo"
		videoCmdResult = proc.call(videoCmd, shell=True)
	except Exception as e:
		errorMsg+='Error al enviar el vídeo a google drive.\n' + str(e) + '\n'
	
	if imageCmdResult or videoCmdResult or errorMsg:
		print "Transferencia con errores"
		asunto=u"Transferencia con ERRORES (" +  eventId + ")"
		texto=u"Ha habido errores al subir los arhivos a google drive. Adjunto se envían los logs de las transferencias.\n" + errorMsg
	else:
		print "Transferencia correcta"
		asunto=u"Transferencia correcta (" +  eventId + ")"
		texto=u"La imagen y el vídeo se han subido correctamente a google drive"
	
	s 	 = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	msg = gsender.Message(	subject 		= asunto,
									to 		 	= os.environ['EMAIL_ADDR'],
									text 			= texto,
									attachments	= [imageLogFile, videoLogFile])
	s.send(msg)
	s.close()

def cmd_status(args):
	return a

def cmd_reboot(args):
	return a

def cmd_lifeCam(args):
	return a


def main(args):
	re_subject = re.compile('CMD_SVVPA[ ]+(?P<cmd>\w+)[ ]*(?P<args>.*)')
	CMD_SVVPA={
		'AYUDA' 									: cmd_help,
		'GUARDAR_EN_GOOGLE_DRIVE'	: cmd_saveFile,
		'ESTADO_DEL_SISTEMA' 			: cmd_status,
		'VISTA_EN_DIRECTO' 				: cmd_lifeCam,
		'REINICIAR' 							: cmd_reboot		
		}

	g 		 = greader.login(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	emails = g.mailbox('CMD_SVVPA').mail(prefetch=True,unread=True)#,to=os.environ['GMAIL_ACCOUNT_ALIAS'])
	
	for e in emails:
		if e.has_label(CMD_WORKING):
			#TODO: comprobar que no lleva mucho tiempo procesándose
			d=e.sent_at
			n=datetime.datetime.now()
			if (n-d).days > 0:
				print "El comando lleva más de un día sin terminar de procesarse. Se va a intentar procesar de nuevo"
				e.add_label(CMD_TIMEOUT)
				e.remove_label(CMD_WORKING)
			else:
				print "El email ya se está procesado"
	
		else:
			r = re_subject.search(e.subject)
			print "Asunto: " + e.subject

			if r and CMD_SVVPA.has_key(r.group('cmd')):				
				print "Comando: \"" + r.group('cmd') + "\""
				print "Argumentos: \"" + r.group('args') + "\""
				try:
					print "Procesando email"
					#e.add_label(CMD_WORKING)
					CMD_SVVPA[r.group('cmd')](r.group('args'))
					print "OK"
					#e.add_label(CMD_OK)			
				
				except Exception, ex:
					print "Ha ocurrido el siguiente error al procesar el comando:"					
					print ex
					#e.add_label(CMD_ERROR)
					#TODO: enviar email de error?
		
				#e.read()
					
			else:
				print "Error en el comando "
#				e.add_label(CMD_ERROR)
#				e.read()
		

	g.logout()	




if __name__ == "__main__":
	sys.exit(main(sys.argv))



'''
procesando=[]
procesado=[]
error=[]

g =  greader.login(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])

emails =  greader.inbox().mail(prefetch=True, unread=True, to=os.environ['SMPT_USER'])


#print "Emails no leidos"
for e in emails:
if e.has_label(CMD_WORKING):
	procesando.append(e)

if e.has_label(CMD_WORKING):
	procesado.append(e)

if e.has_label(CMD_ERROR):
	error.append(e)

print "Emails procesandose"
for e in procesando:
	print e.subject

print
print "Emails procesados"
for e in procesado:
	print e.subject

print
print "Emails con errores"
for e in error:
	print e.subject



greader.logout()
'''
