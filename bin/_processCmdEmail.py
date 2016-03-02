#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import re
import subprocess as proc
import gmail_sender as gsender
import gmail as greader


def cmd_help(a):	
	msg1 = gsender.Message(	
		subject = u"Ayuda CMD_SVVPA",
		to			= os.environ['EMAIL_ADDR'],
#		text		= u"Éste es el cuerpo del mensaje en texto plano",
		html		= u'''
						<html>
							<body>
								<h3>Ayuda del control remoto de SVVPA mediante emails</h3>
								<p>SVVPA tiene la capacidad de recibir comandos a través de correo electrónico. Para enviar un comando, manda un <b>email</b> a <a href="mailto:{correo}">{correo}</a> cuyo <b>asunto</b> contenga <b>CMD_SVVPA <i>COMANDO ARG1 ARG2 ARG3 ... ARGn</i></b>, siendo <i>COMANDO</i> el comando que se desea ejecutar y <i>ARGi</i> los argumentos si son requeridos por el comando (Ej: CMD_SVVPA AYUDA). Los comandos disponibles por el momento son:
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
	s.send(msg1)
	s.close()
	return a

def cmd_saveFile(a):
	imageFile = a + "." + os.environ['MOTION_IMAGE_EXT']
	videoFile = a + "." + os.environ['MOTION_VIDEO_EXT']
	imageLogFile = "/tmp/" + a + "_IMAGEN.log"
	videoLogFile = "/tmp/" + a + "_VIDEO.log"
	imageCmd = os.environ['RCLONE_BIN'] + " --config " + os.environ['RCLONE_CONFIG'] + " copy " + os.environ['MOTION_DIR'] + imageFile + " google:SVVPA/imagenes 2>&1 > " + imageLogFile
	videoCmd = os.environ['RCLONE_BIN'] + " --config " + os.environ['RCLONE_CONFIG'] + " copy " + os.environ['MOTION_DIR'] + videoFile + " google:SVVPA/imagenes 2>&1 > " + videoLogFile

	cmdTEMPORAL = os.environ['RCLONE_BIN'] + " --config " + os.environ['RCLONE_CONFIG'] + " copy /home/dlopez/temp/x.py google:SVVPA/imagenes 2>&1 > " + videoLogFile

	imageStatus = proc.call(cmdTEMPORAL)
	videoStatus = proc.call(cmdTEMPORAL)

	if imageStatus and videoStatus:
		asunto="Transferencia correcta (" + a + ")"
		texto="La imagen y el vídeo se han subido correctamente"
	else:
		asunto="Transferencia con ERRORES (" + a + ")"
		texto="Ha habido errores al subir los arhivos a google drive. Adjunto se envían los logs de las transferencias."

	s = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	msg1 = gsender.Message(	subject 		= "asunto sin sunto, A!",
													to 		 			= os.environ['EMAIL_ADDR'],
													text 				= u"Éste es el cuerpo del mensaje en texto plano",
													attachments = [imageLogFile, videoFile])
	s.send(msg1)
	s.close()
	return a

def cmd_status(a):
	return a

def cmd_reboot(a):
	return a

def cmd_lifeCam(a):
	return a


def main(args):
	re_subject = re.compile('CMD_SVVPA (?P<cmd>\w+)(?P<args>.*)')
	CMD_SVVPA={
		'AYUDA' 									: cmd_help,
		'GUARDAR_EN_GOOGLE_DRIVE'	: cmd_saveFile,
		'ESTADO_DEL_SISTEMA' 			: cmd_status,
		'VISTA_EN_DIRECTO' 				: cmd_lifeCam,
		'REINICIAR' 							: cmd_reboot		
		}

	g = greader.login(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	emails =  g.mailbox('CMD_SVVPA').mail(prefetch=True,unread=True,to=os.environ['GMAIL_ACCOUNT_ALIAS'])
	
	for e in emails:
		if e.has_label('procesando'):
			#comprobar que no lleva mucho tiempo procesándose...
			print "El email ya se está procesado"
			continue
	
		else:
			r = re_subject.search(e.subject)

			if r and CMD_SVVPA.has_key(r.group('cmd')):
				print "Comando recibido: " + r.group('cmd') + " " + r.group('args')
				try:
					print "procesando"
					e.add_label('procesando')
					CMD_SVVPA[r.group('cmd')](r.group('args'))
					print "OK"
					e.add_label('OK')			
				
				except Exception, ex:
					print "Ha ocurrido algún error al procesar el comando"					
					print ex
					e.add_label('CMD_ERROR')
					#enviar email de error!
		
				e.read()
					
			else:
				e.add_label('CMD_ERROR')
				e.read()

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
if e.has_label('procesando'):
	procesando.append(e)

if e.has_label('procesado'):
	procesado.append(e)

if e.has_label('error'):
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
