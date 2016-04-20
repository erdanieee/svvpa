# encoding: utf-8

import os, sys
import datetime
import time
import telepot
from telepot.namedtuple import *
import json
import subprocess as proc
import numconv
import re
from threading import Timer
from signal import SIGKILL

#alfabeto para codificar información usando caracteres unicode no imprimibles
ALPHABET=u'\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8A\x8B\x8C\x8D\x8E\x8F\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9A\x9B\x9C\x9D\x9E\x9F'



def cmd_help(msg):
	bot.sendMessage(CHAT_GROUP, u'''Mu wenas! Me llaman @{}, el *robot telegram* diseñado específicamente para el control remoto de _SVVPA_ \U0001f60e. Al final de este mensaje puedes ver las funciones disponibles.

Para enviar un comando, escribe */* y pulsa sobre la opción que te interese. Adicionalmente, para subir un vídeo capturado a google drive, además del comando /subir, también puedes escribir mi nombre seguido de un espacio y pulsar sobre la captura.

/ayuda - Muestra esta ayuda ayuda
/movimiento - Inicia, para o pausa la detección de movimiento
/foto - Toma una instantánea			
/subir - Sube una captura a google drive
/sensores - Muestra el estado de los sensores
/emails - Activa o desactiva la notificación por emails
/ssh - Abre túnel inverso ssh para gestión remota de SVVPA
/actualizar - actualiza el repositorio github
/reiniciar - reinicia el sistema
/apagar - Apaga el sistema
'''.format(bot.getMe()['username']), parse_mode="Markdown")
	return





def cmd_motion(msg):
	#reply_id=msg['reply_to_message']['message_id']
	keyboard = ReplyKeyboardMarkup(keyboard=[[R_MOTION_START], [R_MOTION_STOP], [R_MOTION_PAUSE_TIME], [R_MOTION_STATUS]], one_time_keyboard=True)	
	bot.sendMessage(CHAT_GROUP, u'Este comando sirve para controlar la detección de movimiento. ¿Qué quieres hacer?', reply_markup=keyboard)
	return




def cmd_photo(msg):
	devices = os.environ['CAMERA_DEVICES'].split(",")

	kb=[]
	for d in devices:
		k=[]
		k.append(d.strip())
		kb.append(k)	

	#print kb
	keyboard = ReplyKeyboardMarkup(keyboard=kb, one_time_keyboard=True)
	bot.sendMessage(CHAT_GROUP, u'Selecciona la cámara que quieres ver', reply_markup=keyboard)			

	return




def cmd_upload_video(msg):
	bot.sendMessage(CHAT_GROUP, u'FIXME: Función no implementada!')
	return
def cmd_sensors(msg):
	bot.sendMessage(CHAT_GROUP, u'FIXME: Función no implementada!')
	return
def cmd_open_ssh(msg):	
	try:
		#cerramos puerto ssh si ya está abierto para evitar problemas
		close_ssh()
		
		cmd="sshpass -e ssh -p {port} -fCNR {tunelPort}:localhost:22 {user}@{server}".format(
                        port      = os.environ['SSH_REMOTE_PORT'],
                        tunelPort = os.environ['SSH_REMOTE_TUNEL_PORT'],
                        user      = os.environ['SSH_REMOTE_USER'],
                        server    = os.environ['SSH_REMOTE_SERVER'])	
		o = proc.call(cmd,shell=True)
		
		if not o:
			bot.sendMessage(
						CHAT_GROUP, 
						u'Túnel reverso ssh accesible desde {}:{} durante {} segundos'.format(
																							os.environ['SSH_REMOTE_SERVER'],
																							os.environ['SSH_REMOTE_TUNEL_PORT'], 
																							os.environ['SSH_REMOTE_TIMEOUT']), 
						reply_markup=ReplyKeyboardHide())
			
			global timerSsh
			timerSsh = Timer(int(os.environ['SSH_REMOTE_TIMEOUT']), close_ssh)
			timerSsh.start()
			
		else:
			bot.sendMessage(CHAT_GROUP,	u'ERROR! Hubo un error inesperado al abrir el túnel ssh', reply_markup=ReplyKeyboardHide())
		
	except:
		pass
	
	return
	


def cmd_update(msg):
	bot.sendMessage(CHAT_GROUP, u'FIXME: Función no implementada!')
	return
def cmd_reboot(msg):
	bot.sendMessage(CHAT_GROUP, u'FIXME: Función no implementada!')
	return
def cmd_shutdown(msg):
	bot.sendMessage(CHAT_GROUP, u'FIXME: Función no implementada!')
	return
def cmd_cancel(msg):
	bot.sendMessage(CHAT_GROUP, u'FIXME: Función no implementada!')
	return
def cmd_notif_emails(msg):
	bot.sendMessage(CHAT_GROUP, u'FIXME: Función no implementada!')
	return



commands={
	'/start'          : cmd_help,          # Descripción. Indicar también que por seguridad solo responde a comandos enviados desde el chat de grupo
	'/ayuda'          : cmd_help,
	'/movimiento'     : cmd_motion,        # iniciar, parar, pausar...
   '/foto'           : cmd_photo,         # Toma una instantánea			
   '/subir'          : cmd_upload_video,  # sube un vídeo a google drive
   '/sensores'       : cmd_sensors,       # muestra el estado de los sensores
	'/emails'         : cmd_notif_emails,	# activa/desactiva la modificación por emails
   '/ssh'            : cmd_open_ssh,      # abre túnel ssh en Bacmine
   '/actualizar'     : cmd_update,			# actualiza el repositorio github
	'/reiniciar'      : cmd_reboot,        # reinicia el sistema
   '/apagar'         : cmd_shutdown       # Apaga el sistema. Por seguridad te pide la ubicación
   }





def resp_allow_user(msg):
	contact_id=re.findall('[\x80-\x9f]+', msg['reply_to_message']['text'])
	reply_id=msg['reply_to_message']['message_id']

	if contact_id:
		file_constants = os.environ['BIN_DIR']+'CONSTANTS.sh'
		contact_id     = numconv.str2int( contact_id[0], 32, ALPHABET )
		current_users  = proc.check_output('grep TELEGRAM_ALLOWED_USERS {} |egrep -o \'[0-9,]+\''.format(file_constants), shell=True).strip()
		cmd            = 'sed -i -r \'s/TELEGRAM_ALLOWED_USERS="([0-9,]+)"/TELEGRAM_ALLOWED_USERS="{},{}"/g\' {}'.format(current_users, contact_id, file_constants)
		#print cmd
		proc.call(cmd, shell=True)
		ALLOWED_USERS.append(contact_id)
		bot.sendMessage(CHAT_GROUP, u'contacto añadido!', reply_to_message_id=reply_id, reply_markup=ReplyKeyboardHide())
		
	else:
		bot.sendMessage(CHAT_GROUP, u'ERROR! No se ha podido añadir al contacto (?!)', reply_to_message_id=reply_id, reply_markup=ReplyKeyboardHide())		
	return




def resp_block_user(msg):
	contact_id=re.findall('[\x80-\x9f]+', msg['reply_to_message']['text'])
	reply_id=msg['reply_to_message']['message_id']
	
	if contact_id:
		contact_id = numconv.str2int( contact_id[0], 32, ALPHABET )
		BANNED_USERS.append(contact_id)
		bot.sendMessage(CHAT_GROUP, u'El usuario será bloqueado hasta la próxima vez que se reinicie el svvpa', reply_to_message_id=reply_id, reply_markup=ReplyKeyboardHide())
	return




def resp_ban_user(msg):
	contact_id = re.findall('[\x80-\x9f]+', msg['reply_to_message']['text'])
	reply_id   = msg['reply_to_message']['message_id']

	if contact_id:
		file_constants = os.environ['BIN_DIR']+'CONSTANTS.sh'
		contact_id     = numconv.str2int( contact_id[0], 32, ALPHABET )
		current_users  = proc.check_output('grep TELEGRAM_BANNED_USERS {} |egrep -o \'[0-9,]*\''.format(file_constants), shell=True).strip()
		cmd            = 'sed -i -r \'s/TELEGRAM_BANNED_USERS=".*"/TELEGRAM_BANNED_USERS="{}{}"/g\' {}'.format(current_users + ',' if current_users else '', contact_id, file_constants)
		proc.call(cmd, shell=True)
		BANNED_USERS.append(contact_id)
		bot.sendMessage(CHAT_GROUP, u'contacto bloqueado permanentemente!', reply_to_message_id=reply_id, reply_markup=ReplyKeyboardHide())

	else:
		bot.sendMessage(CHAT_GROUP, u'ERROR! No se ha podido bloquear el contacto permanentemente (?!), pero tampoco ha ejecutado nada', reply_to_message_id=reply_id, reply_markup=ReplyKeyboardHide())		
	return




def resp_motion_start(msg):
	reply_id = msg['message_id']
	
	#comprueba si hay thread de pausa y lo cancela
	if timerMotion:
		timerMotion.cancel()

	try:
		proc.check_call('sudo service motion restart', shell=True)
		bot.sendMessage(CHAT_GROUP, u'La detección de movimiento se ha activado correctamente. \U0001f440', reply_markup=ReplyKeyboardHide())
	except:
		bot.sendMessage(CHAT_GROUP, u'Hubo un error al iniciar el servicio de detección de movimiento (?!)', reply_to_message_id=reply_id, reply_markup=ReplyKeyboardHide())
		pass	
	return




def resp_motion_stop(msg):
	reply_id = msg['message_id']

	#comprueba si hay thread de pausa y lo cancela
	if timerMotion:
		timerMotion.cancel()

	try:
		proc.check_call('sudo service motion stop', shell=True)
		bot.sendMessage(CHAT_GROUP, u'La detección de movimiento se ha detenido. Utiliza el comando /movimiento para volver a iniciarla.', reply_markup=ReplyKeyboardHide())
	except:
		bot.sendMessage(CHAT_GROUP, u'Hubo un error al detener el servicio de detección de movimiento (?!)', reply_to_message_id=reply_id, reply_markup=ReplyKeyboardHide())
		pass	
	return




def pause2text(time):
	a={86400.0 : ("días","día"), 3600.0 : ("horas","hora"), 60.0 : ("minutos","minuto"), 1.0 : ("segundos","segundo")}
	resp=[]

	for i in a:
		     r = time / i
		     if r>=1:
		             d=int(r)
		             resp.append( str(d) + ' ' + (a[i][0] if d>1 else a[i][1]) )
		             time-=d*i

	return (resp[0] if len(resp)==1 else ", ".join(resp[:-1]) + ' y ' + resp[-1])




def  resp_motion_pause(msg):
	reply_id = msg['message_id']	
	bot.sendMessage(CHAT_GROUP, u'Dime cuánto tiempo quieres pausar la detección de movimiento. Utiliza el formato _nU_, siendo _n_ el número y _U_ la unidad (_M_, _H_, _D_ para minutos, horas y días respectívamente). Ej: _3D_ (3 días), _1D3H_ (1 día y 3 horas)', reply_to_message_id=reply_id, parse_mode="Markdown", reply_markup=ForceReply())
	return
		



def  resp_motion_pause_2(msg):
	r = re.findall('([0-9]+[smhd])', msg['text'].lower())

	#comprueba si hay thread de pausa y lo cancela	
	global timerMotion
	if timerMotion:
		timerMotion.cancel()
	
	time=0
	mult=0
	for t in r:
		if 's' in t:
			mult=1
		elif 'm' in t:
			mult=60
		elif 'h' in t:
			mult=3600
		elif 'd' in t:
			mult=86400
		time+=int(t[:-1])*mult
	
	bot.sendMessage(CHAT_GROUP, u'La detección de movimiento estará pausada durante %s' % (pause2text(time)), reply_markup=ReplyKeyboardHide())
	proc.call('sudo service motion stop', shell=True)	
	timerMotion = Timer(time, resp_motion_start, args=(msg,))
	timerMotion.start()
	return	





def resp_motion_status(msg):
	if get_motion_status():
		bot.sendMessage(CHAT_GROUP, u'La detección de movimiento está activa \U0001f440', reply_markup=ReplyKeyboardHide())
	
	else:
		bot.sendMessage(CHAT_GROUP, u'La detección de movimiento está inactiva \U0001f648', reply_markup=ReplyKeyboardHide())
			
	return



# Respuestas enviadas por el usuario. Formato: [icono], código unicode de la respuesta (\x80-\x9F), texto
R_ALLOW_USER_YES          = u'\u2705\x80Sí'
R_ALLOW_USER_NO_THIS_TIME = u'\u274c\x81No por ahora'
R_ALLOW_USER_NO_NEVER     = u'\u26d4\ufe0f\x82No, nunca jamás de los jamases'
R_MOTION_START            = u'\u25b6\ufe0f\x83Iniciar'
R_MOTION_STOP             = u'\u23f9\x84Parar'
R_MOTION_PAUSE_TIME       = u'\u23f8\x85Pausar'
R_MOTION_STATUS           = u'\u2753\x86Comprobar estado'




# Funciones para las respuestas
responses={
	R_ALLOW_USER_YES            : resp_allow_user,
	R_ALLOW_USER_NO_THIS_TIME   : resp_block_user,
	R_ALLOW_USER_NO_NEVER       : resp_ban_user,
	R_MOTION_START              : resp_motion_start,
	R_MOTION_STOP               : resp_motion_stop,
	R_MOTION_PAUSE_TIME         : resp_motion_pause,
	R_MOTION_STATUS             : resp_motion_status
}



def close_ssh():
	r=False
	try:
		if timerSsh:
			timerSsh.cancel()
		
		o = proc.check_output('ps aux', shell=True)
		for l in o.splitlines():
			if ('ssh' and os.environ['SSH_REMOTE_SERVER'] and 'localhost') in l:
				pid = int(l.split()[1])
				os.kill(pid, SIGKILL)
				print "matado ssh con PID %s" % str(pid)
				r=True
				break
	
	except:
		pass
	
	return r
	
	







def get_motion_status():
	try:
		return proc.call('sudo service motion status', shell=True)
		
	except:
		pass
					
	return False





def getCommand(msg):
	if 'entities' in msg and msg['entities'][0]['type']=='bot_command':
		regex = re.compile('/[a-zA-Z0-9_]+')
		r = regex.findall(msg['text'])
		if r:
			return r[0]

		else:
			return None




def send_photo(device):
	if get_motion_status():
		snapshot = os.environ['MOTION_DIR'] + '.snapshot-' + str(int(device[-1:])+1) + '.jpg'
		
		if os.path.isfile(snapshot):
			try:
				f=open(snapshot, 'r')
				bot.sendPhoto(CHAT_GROUP, f, datetime.datetime.now(), reply_markup=ReplyKeyboardHide())
				f.close()
				
			except:
				bot.sendMessage(CHAT_GROUP, u'ERROR! Hubo un error inesperado al mandar la foto (?!)', reply_markup=ReplyKeyboardHide())
				pass
	
	else:
		fileout="/tmp/snapshot.jpg"
		f=None
	
		try:
			proc.check_call([os.environ['FSWEBCAM_BIN'], "--config", os.environ['FSWEBCAM_CONFIG'], "--device", device, "/tmp/snapshot.jpg"],shell=True)	
			f=open(fileout, 'rb')	#open read-only in binary mode
			bot.sendPhoto(CHAT_GROUP, f, caption=str(datetime.datetime.now()))
			f.close()
	
		except Exception as e:
			print e
			bot.sendMessage(CHAT_GROUP, u'ERROR! Hubo un problema al capturar la imagen', reply_markup=ReplyKeyboardHide())
			pass
	
		finally:
			if f:
				f.close()

	return




# Procesa mensajes privados (private chat), menciones (@svvpaBot ####), comandos (/####), o respuestas
# Para las respuestas, incorporar el id del mensaje y la información necesaria necesaria para procesar la respuesta si fuera necesario al final del mensaje separados por espacios. Ej: Pregunta: u'¿Quieres acelgas?\x81\x82\x83 \x81\x85 \x83\x87\x81\x81\x86 \x89\x85'
def on_chat_message(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
	user_id=msg['from']['id']
	print 'Normal message:\n%s', json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': '))

	# solo permite mensajes de texto y de usuarios NO baneados
	if content_type != 'text' or user_id in BANNED_USERS:
		return

	# solo usuarios permitidos		
	if user_id in ALLOWED_USERS:
		# solo desde el chat de grupo
		if chat_id!=CHAT_GROUP:	#TODO: allow admin user
			bot.sendMessage(
				chat_id, 
		    	u'Lo siento, pero por ahora el control de @{} por chat privado está desactivado (es pa\' controlar el percal \U0001f609).'.format(bot.getMe()['username']), reply_markup=ReplyKeyboardHide())
			return

		#procesa comandos
		cmd=getCommand(msg)
		if cmd in commands:
			commands[cmd](msg)
			return	

		#procesa respuestas
		if 'reply_to_message' in msg:
			if msg['text'] in responses:
				responses[msg['text']](msg)	
			
			elif re.match('^([0-9]+[SsMmHhDd]+)+$', msg['text']):
				resp_motion_pause_2(msg)

			elif re.match('/dev/[a-z0-9_]+' , msg['text']):
				send_photo(msg['text'])
			return

		#procesa menciones
		if 'entities' in msg and msg['entities'][0]['type']=='mention':
			bot.sendMessage(chat_id, u'¿Qué dices de mí?', reply_markup=ReplyKeyboardHide())	#FIXME: poner frases aleatorias
			return	

		#No es un comando o respuesta reconocida
		bot.sendMessage(chat_id, u'\U0001f21a\ufe0f \U0001f236\U0001f236 \U0001f238\u203c\ufe0f')
		bot.sendMessage(chat_id, u'¿Te has enterado? Pues yo tampoco se lo que quieres. Anda, hazme el favor de escribir los comandos correctamente, solo uno por mensaje y utilizar el teclado emergente para responder, que si no no se puede, aaaaaaaaes?.', reply_to_message_id=msg['message_id'], reply_markup=ReplyKeyboardHide())

	else:
		#TODO: nuevo usuario, permitir?
		name     = msg['from']['first_name']
		lastname = msg['from']['last_name']
		botname  = bot.getMe()['username']
		id       = numconv.int2str(user_id, 32, ALPHABET)

		keyboard = ReplyKeyboardMarkup(keyboard=[[R_ALLOW_USER_YES], [R_ALLOW_USER_NO_THIS_TIME], [R_ALLOW_USER_NO_NEVER]], one_time_keyboard=True)
		
		bot.sendMessage(
			CHAT_GROUP, 
       	u'{} {} ha enviado un comando a @{}, pero aún no tiene permiso. ¿Deseas añadirlo a la lista de usuarios autorizados para ejecutar comandos a través de Telegram?{}'.format(name, lastname, botname, id), 
        	reply_markup=keyboard)







# Envía sugerencias cuando se escribe `@svvpaBot ####`, y antes de dar a enviar o elegir una de las sugerencias
def on_inline_query(msg):
	query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
	#print 'Inline Query (queryId, fromId, query):' ,query_id, from_id, query_string

	bot.sendChatAction(CHAT_GROUP, 'typing')

	lines=proc.check_output('node _google_drive_last_uploads.js', shell=True)[:-1]		# TODO: meter datos en MySQL para que la consulta sea rápida...
	f=[]
	for l in lines.split('\n'):
		tk = l.split('\t')
		f.append(InlineQueryResultPhoto(id = tk[0], 
												  photo_url = tk[1], 
												  thumb_url = tk[1], 
												  photo_width = int(tk[2]), 
												  photo_height = int(tk[3])))

	print 'Inline Query:\n:', json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': '))	

	bot.answerInlineQuery(query_id, f)
	#answerer.answer(msg, compute_answer)







# Procesa la sugerencia elegida en la `inline_query`
def on_chosen_inline_result(msg):
	result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
	print 'Chosen Inline Result:\n%s', json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': '))
	# bot.sendMessage(, 'Elegida opción '+result_id)
	# Remember the chosen answer to do better next time













TOKEN         = os.environ['TELEGRAM_TOKEN']
CHAT_GROUP    = int(os.environ['TELEGRAM_CHAT_GROUP'])
ALLOWED_USERS = map(int,os.environ['TELEGRAM_ALLOWED_USERS'].split(','))
BANNED_USERS  = [] if not os.environ['TELEGRAM_BANNED_USERS'] else map(int,os.environ['TELEGRAM_BANNED_USERS'].split(','))

if not TOKEN or not CHAT_GROUP or not ALLOWED_USERS:
	print >> sys.stderr, "[{}] {}: ERROR! Variables de entorno TELEGRAM_TOKEN, TELEGRAM_CHAT_GROUP y TELEGRAM_ALLOWED_USERS deben estar definidas".format(datetime.datetime.now(), __file__)
	exit(1)

timerMotion = None
timerSsh    = None

bot = telepot.Bot(TOKEN)
bot.message_loop({'chat': on_chat_message, 'inline_query': on_inline_query, 'chosen_inline_result': on_chosen_inline_result}, relax=1, timeout=60)

print 'Listening ...'

# Keep the program running.
while 1:
	 time.sleep(10)








'''
#####################
##  P R I V A T E  ##
#####################
{
    "chat": {
        "first_name": "Daniel",
        "id": 202714763,
        "last_name": "L\u00f3pez",
        "type": "private",
        "username": "svvpa"
    },
    "date": 1460635819,
    "from": {
        "first_name": "Daniel",
        "id": 202714763,
        "last_name": "L\u00f3pez",
        "username": "svvpa"
    },
    "message_id": 237,
    "text": "G"
}


#####################
##  C O M M A N D  ##
#####################
{
    "chat": {
        "id": -136404445,
        "title": "Control remoto SVVPA",
        "type": "group"
    },
    "date": 1460619355,
    "entities": [
        {
            "length": 6,
            "offset": 0,
            "type": "bot_command"
        }
    ],
    "from": {
        "first_name": "Daniel",
        "id": 202714763,
        "last_name": "L\u00f3pez",
        "username": "svvpa"
    },
    "message_id": 205,
    "text": "/start"
}


#####################
##  M E N T I O N  ##
#####################
{
    "chat": {
        "id": -136404445,
        "title": "Control remoto SVVPA",
        "type": "group"
    },
    "date": 1460557186,
    "entities": [
        {
            "length": 9,
            "offset": 0,
            "type": "mention"
        }
    ],
    "from": {
        "first_name": "Daniel",
        "id": 202714763,
        "last_name": "L\u00f3pez",
        "username": "svvpa"
    },
    "message_id": 199,
    "text": "@svvpaBot ((&"
}


#################
##  R E P L Y  ##
#################
{
    "chat": {
        "id": -136404445,
        "title": "Control remoto SVVPA",
        "type": "group"
    },
    "date": 1460618301,
    "from": {
        "first_name": "Daniel",
        "id": 202714763,
        "last_name": "L\u00f3pez",
        "username": "svvpa"
    },
    "message_id": 203,
    "reply_to_message": {
        "chat": {
            "id": -136404445,
            "title": "Control remoto SVVPA",
            "type": "group"
        },
        "date": 1460618219,
        "from": {
            "first_name": "svvpa",
            "id": 183543111,
            "username": "svvpaBot"
        },
        "message_id": 201,
        "text": "Force reply"
    },
    "text": "Ggg"
}


###################
##  I N L I N E  ##
###################
{
    "from": {
        "first_name": "Daniel",
        "id": 202714763,
        "last_name": "L\u00f3pez",
        "username": "svvpa"
    },
    "id": "870653278453550833",
    "offset": "",
    "query": "((&"
}


##################################
##  C H O S E N   I N L I N E   ##
##################################
{
    "from": {
        "first_name": "Daniel",
        "id": 202714763,
        "last_name": "L\u00f3pez",
        "username": "svvpa"
    },
    "query": "ffatwdsdfg",
    "result_id": "2016_04_01_19_06_20_34923_14_154_296_329_330_1.jpg"
}



'''

