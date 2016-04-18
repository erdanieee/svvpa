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
	bot.sendMessage(CHAT_GROUP, u'FIXME: Función no implementada!')
	return
def cmd_photo(msg):
	bot.sendMessage(CHAT_GROUP, u'FIXME: Función no implementada!')
	return
def cmd_upload_video(msg):
	bot.sendMessage(CHAT_GROUP, u'FIXME: Función no implementada!')
	return
def cmd_sensors(msg):
	bot.sendMessage(CHAT_GROUP, u'FIXME: Función no implementada!')
	return
def cmd_open_ssh(msg):
	bot.sendMessage(CHAT_GROUP, u'FIXME: Función no implementada!')
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
		bot.sendMessage(CHAT_GROUP, u'contacto añadido!', reply_to_message_id=reply_id)
		
	else:
		bot.sendMessage(CHAT_GROUP, u'ERROR! No se ha podido añadir al contacto (?!)', reply_to_message_id=reply_id)		
	return


def resp_block_user(msg):
	contact_id=re.findall('[\x80-\x9f]+', msg['reply_to_message']['text'])
	reply_id=msg['reply_to_message']['message_id']
	
	if contact_id:
		contact_id = numconv.str2int( contact_id[0], 32, ALPHABET )
		BANNED_USERS.append(contact_id)
		bot.sendMessage(CHAT_GROUP, u'El usuario será bloqueado hasta la próxima vez que se reinicie el svvpa', reply_to_message_id=reply_id)
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
		bot.sendMessage(CHAT_GROUP, u'contacto bloqueado permanentemente!', reply_to_message_id=reply_id)

	else:
		bot.sendMessage(CHAT_GROUP, u'ERROR! No se ha podido bloquear el contacto permanentemente (?!), pero tampoco ha ejecutado nada', reply_to_message_id=reply_id)		
	return


# Respuestas enviadas por el usuario. Formato: [icono], código unicode de la respuesta (\x80-\x9F), texto
R_ALLOW_USER_YES=u'\u2705\x80Sí'
R_ALLOW_USER_NO_THIS_TIME=u'\u274c\x81No por ahora'
R_ALLOW_USER_NO_NEVER=u'\u26d4\ufe0f\x82No, nunca jamás de los jamases'

# Funciones para las respuestas
responses={
	R_ALLOW_USER_YES            : resp_allow_user,
	R_ALLOW_USER_NO_THIS_TIME   : resp_block_user,
	R_ALLOW_USER_NO_NEVER       : resp_ban_user
}


def getCommand(msg):
	if 'entities' in msg and msg['entities'][0]['type']=='bot_command':
		regex = re.compile('/[a-zA-Z0-9_]+')
		r = regex.findall(msg['text'])
		if r:
			return r[0]

		else:
			return None


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
		    	u'Lo siento, pero por ahora el control de @{} por chat privado está desactivado (es pa\' controlar el percal \U0001f609).'.format(bot.getMe()['username']))
			return

		#procesa comandos
		cmd=getCommand(msg)
		if cmd in commands:
			commands[cmd](msg)
			return	

		#procesa respuestas
		if 'reply_to_message' in msg and msg['text'] in responses:
			responses[msg['text']](msg)				
			return

		#procesa comandos
		if 'entities' in msg and msg['entities'][0]['type']=='mention':
			bot.sendMessage(chat_id, u'¿Qué dices de mí?')	#FIXME: poner frases aleatorias
			return	

		#No es un comando o respuesta reconocida
		bot.sendMessage(chat_id, u'\U0001f21a\ufe0f \U0001f236\U0001f236 \U0001f238\u203c\ufe0f')
		bot.sendMessage(chat_id, u'¿Te has enterado? Pues yo tampoco se lo que quieres. Anda, hazme el favor de escribir los comandos correctamente, solo uno por mensaje y utilizar el teclado emergente para responder, que si no no se puede, aaaaaaaaes?.', reply_to_message_id=msg['message_id'])


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













TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_GROUP = int(os.environ['TELEGRAM_CHAT_GROUP'])
ALLOWED_USERS = map(int,os.environ['TELEGRAM_ALLOWED_USERS'].split(','))
BANNED_USERS = [] if not os.environ['TELEGRAM_BANNED_USERS'] else map(int,os.environ['TELEGRAM_BANNED_USERS'].split(','))

if not TOKEN or not CHAT_GROUP or not ALLOWED_USERS:
	print >> sys.stderr, "[{}] {}: ERROR! Variables de entorno TELEGRAM_TOKEN, TELEGRAM_CHAT_GROUP y TELEGRAM_ALLOWED_USERS deben estar definidas".format(datetime.datetime.now(), __file__)
	exit(1)

bot = telepot.Bot(TOKEN)
bot.notifyOnMessage({'normal': on_chat_message, 'inline_query': on_inline_query, 'chosen_inline_result': on_chosen_inline_result}, relax=1, timeout=60)

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

