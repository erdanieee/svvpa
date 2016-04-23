# encoding: utf-8


from json import dumps
import os
from re import match, findall, compile
from subprocess import call, check_call, check_output
import telepot
from telepot.namedtuple import InlineQueryResultPhoto, ReplyKeyboardHide,\
    InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep


#quitar cuando deje de estar en fase Beta!!!!
INLINE_KEYBOARDS_GROUP_ACTIVE = False



class Telegram_bot(telepot.Bot):
    '''
    classdocs
    '''
    MSG_NEW_USER = u'''{} {} ha enviado un comando a @{}, pero aún no tiene \
permiso. ¿Deseas añadirlo a la lista de usuarios autorizados para ejecutar \
comandos a través de Telegram?'''
    MSG_BLOCKED_PRIVATE_CHAT = u'''Lo siento, pero por ahora el control de @{} \
por chat privado está desactivado (es pa\' controlar el percal \U0001f609).\
Utiliza el chat de grupo para mandar los commandos'''
    MSG_DONT_MENTION_ME = u'''¿Qué dices de mí?'''
    MSG_DONT_UNDERSTAND = u'''\U0001f21a\ufe0f \U0001f236\U0001f236 \
\U0001f238\u203c\ufe0f\n\n¿Te has enterado? Pues yo tampoco se lo que quieres. \
Anda, hazme el favor de escribir los comandos correctamente, solo uno por mensaje \
y utilizar el teclado emergente para responder, que si no no se puede, aaaaaaaaes?.'''
    MSG_HELP = u'''Mu wenas! Me llaman @{}, el *robot telegram* diseñado \
específicamente para el control remoto de _SVVPA_ \U0001f60e. Al final de este \
mensaje puedes ver las funciones disponibles.
    
Para enviar un comando, escribe */* y pulsa sobre la opción que te interese. \
Adicionalmente, para subir un vídeo capturado a google drive, además del comando \
/subir, también puedes escribir mi nombre seguido de un espacio y pulsar sobre \
la captura.

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
    '''
    
    BUT_ALLOW_USER_YES          = u'\u2705 Sí'
    BUT_ALLOW_USER_NO_THIS_TIME = u'\u274c No por ahora'
    BUT_ALLOW_USER_NO_NEVER     = u'\u26d4\ufe0f No, nunca jamás de los jamases'
    BUT_MOTION_START            = u'\u25b6\ufe0f Iniciar'
    BUT_MOTION_STOP             = u'\u23f9 Parar'
    BUT_MOTION_PAUSE_TIME       = u'\u23f8 Pausar'
    BUT_MOTION_STATUS           = u'\u2753 Comprobar estado'
 
     
    
    def __init__(self, *args, **kwargs):    
        super(Telegram_bot, self).__init__(*args, **kwargs)
               
        self.CHAT_GROUP     = int(os.environ['TELEGRAM_CHAT_GROUP'])
        self.ALLOWED_USERS  = map(int,os.environ['TELEGRAM_ALLOWED_USERS'].split(','))
        self.BANNED_USERS   = [] if not os.environ['TELEGRAM_BANNED_USERS'] else map(int,os.environ['TELEGRAM_BANNED_USERS'].split(','))
        self.ADMIN_USER     = int(os.environ['TELEGRAM_ADMIN_USER'])
        self.FILE_CONSTANTS = os.environ['BIN_DIR']+'CONSTANTS.sh' 
        
        # Callback functions usadas para procesar las respuestas de los inline keyboards.
        self.CBQ_FUNCTION_SPLITTER       = "*"                
        self.CBQ_ADD_USER                = 'cbq_AddUser'
        self.CBQ_BLOCK_USER_ONE_TIME     = 'cbq_BlockUserOneTime'
        self.CBQ_BAN_USER                = 'cbq_BanUser'
        self.CALLBACKS={
                        self.CBQ_ADD_USER               : self.cbq_AddUser,
                        self.CBQ_BLOCK_USER_ONE_TIME    : self.cbq_BlockUserOneTime,
                        self.CBQ_BAN_USER               : self.cbq_BanUser
                        }
  
        # Commands
        self.COMMANDS={
            '/start'          : self.cmd_help,          # Descripción. Indicar también que por seguridad solo responde a comandos enviados desde el chat de grupo
            '/ayuda'          : self.cmd_help,
            '/movimiento'     : self.cmd_motion,        # iniciar, parar, pausar...
            '/foto'           : self.cmd_photo,         # Toma una instantánea            
            '/subir'          : self.cmd_upload_video,  # sube un vídeo a google drive
            '/sensores'       : self.cmd_sensors,       # muestra el estado de los sensores
            '/emails'         : self.cmd_notif_emails,  # activa/desactiva la modificación por emails
            '/ssh'            : self.cmd_open_ssh,      # abre túnel ssh en Bacmine
            '/actualizar'     : self.cmd_update,        # actualiza el repositorio github
            '/reiniciar'      : self.cmd_reboot,        # reinicia el sistema
            '/apagar'         : self.cmd_shutdown       # Apaga el sistema. Por seguridad te pide la ubicación
        }
    
  
    
    
    #############
    #  C H A T  #
    #############    
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        user_id = msg['from']['id']
        #print 'Normal message:\n%s', dumps(msg, sort_keys=True, indent=4, separators=(',', ': '))
        
        # solo permite mensajes de texto y de usuarios NO baneados o admin
        if user_id == self.ADMIN_USER or (content_type == 'text' and user_id not in self.BANNED_USERS):
            if user_id == self.ADMIN_USER or user_id in self.ALLOWED_USERS:                
                cmd=self.getCommand(msg)
                if cmd in self.COMMANDS:
                    # solo permite comandos por mensaje privado o de admin
                    if user_id == self.ADMIN_USER or chat_id == self.CHAT_GROUP:
                        self.COMMANDS[cmd](msg, chat_id)
                            
                    else:                
                        self.sendMessage(chat_id, self.MSG_BLOCKED_PRIVATE_CHAT.format(self.getMe()['username']), reply_markup=ReplyKeyboardHide())
                        
                
                # comprueba si es una respuesta
                elif 'reply_to_message' in msg:
                    pass            
                
                # comprueba si es una mención            
                elif 'entities' in msg and msg['entities'][0]['type']=='mention':                
                    self.sendMessage(chat_id, self.MSG_DONT_MENTION_ME, reply_markup=ReplyKeyboardHide())    #FIXME: poner frases aleatorias
                
                #No es un comando o respuesta reconocida               
                else:                
                    self.sendMessage(chat_id, self.MSG_DONT_UNDERSTAND, reply_to_message_id=msg['message_id'], reply_markup=ReplyKeyboardHide())
                    
            else:
                # Si es nuevo usuario... ¿Añadir a la lista de usuarios permitidos?                
                self.ask_AddNewUser(msg)            

    
    
    #######################
    #  C A L L B A C K S  #
    #######################            
    def on_callback_query(self, msg):
        query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
        funct, arg = self.string2callback(data)
        funct(msg, arg)    

    

    #############################
    #  I N L I N E   Q U E R Y  #
    #############################   
    def on_inline_query(self, msg):
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        #print 'Inline Query (queryId, fromId, query):' ,query_id, from_id, query_string

        # No permite mensaje privados
        if from_id in self.ALLOWED_USERS and from_id not in self.BANNED_USERS:                
            self.sendChatAction(self.CHAT_GROUP, 'typing')
            
            lines=check_output('node _google_drive_last_uploads.js', shell=True)[:-1]        # TODO: meter datos en MySQL para que la consulta sea rápida...
            f=[]
            for l in lines.split('\n'):
                tk = l.split('\t')
                f.append(InlineQueryResultPhoto(
                    id = tk[0], 
                    photo_url = tk[1], 
                    thumb_url = tk[1], 
                    photo_width = int(tk[2]), 
                    photo_height = int(tk[3])))
            
            #print 'Inline Query:\n:', dumps(msg, sort_keys=True, indent=4, separators=(',', ': '))    
            
            self.answerInlineQuery(query_id, f)        
        

    
    
    ################################
    #  I N L I N E    R E S U L T  #
    ################################    
    def on_chosen_inline_result(self, msg):
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        #print 'Chosen Inline Result:\n%s', dumps(msg, sort_keys=True, indent=4, separators=(',', ': '))
        



  
        
    def handle(self, msg):
        flavor = telepot.flavor(msg)
        print dumps(msg, sort_keys=True, indent=4, separators=(',', ': '))
        
        if flavor == 'chat':
            self.on_chat_message(msg)
        
        elif flavor == 'callback_query':
            self.on_callback_query(msg)
        
        elif flavor == 'inline_query':
            self.on_inline_query(msg)
        
        elif flavor == 'chosen_inline_result':
            self.on_chosen_inline_result(msg)
        
        else:
            raise telepot.BadFlavor(msg)
 
 


 
    def cmd_help(self,msg, chat_id):        
        #self.sendMessage(self.CHAT_GROUP, self.MSG_HELP.format(self.getMe()['username']), parse_mode="Markdown")
        self.ask_AddNewUser(msg)        
        

    
    def cmd_motion(self,msg, chat_id):
        self.sendMessage(self.CHAT_GROUP, u'FIXME! cmd_motion función no implementada')
        
    def cmd_photo(self,msg, chat_id):
        self.sendMessage(self.CHAT_GROUP, u'FIXME! cmd_photo función no implementada')
                    
    def cmd_upload_video(self,msg, chat_id):
        self.sendMessage(self.CHAT_GROUP, u'FIXME! cmd_upload_video función no implementada')
        
    def cmd_sensors(self,msg, chat_id):
        self.sendMessage(self.CHAT_GROUP, u'FIXME! cmd_sensors función no implementada')
        
    def cmd_notif_emails(self,msg, chat_id):
        self.sendMessage(self.CHAT_GROUP, u'FIXME! cmd_notif_emails función no implementada')
        
    def cmd_open_ssh(self,msg, chat_id):
        self.sendMessage(self.CHAT_GROUP, u'FIXME! cmd_open_ssh función no implementada')
        
    def cmd_update(self,msg, chat_id):
        self.sendMessage(self.CHAT_GROUP, u'FIXME! cmd_update función no implementada')
        
    def cmd_reboot(self,msg, chat_id):
        self.sendMessage(self.CHAT_GROUP, u'FIXME! cmd_reboot función no implementada')
        
    def cmd_shutdown(self,msg, chat_id):
        self.sendMessage(self.CHAT_GROUP, u'FIXME! cmd_shutdown función no implementada')
        
    
    
    def cbq_AddUser(self, msg, user_id):
        query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
        current_users  = check_output('grep TELEGRAM_ALLOWED_USERS {} |egrep -o \'[0-9,]+\''.format(self.FILE_CONSTANTS), shell=True).strip()
        cmd            = 'sed -i -r \'s/TELEGRAM_ALLOWED_USERS="([0-9,]+)"/TELEGRAM_ALLOWED_USERS="{},{}"/g\' {}'.format(current_users, user_id, self.FILE_CONSTANTS)
        call(cmd, shell=True)
        self.ALLOWED_USERS.append(user_id)
        bot.answerCallbackQuery(query_id, text='No previous message to edit')
        bot.sendMessage(self.CHAT_GROUP, u'contacto añadido!', reply_markup=ReplyKeyboardHide())
        
        
        
        self.sendMessage(self.CHAT_GROUP, u'FIXME! cbq_AddUser función no implementada')
        
    def cbq_BlockUserOneTime(self, msg, user_id):
        self.sendMessage(self.CHAT_GROUP, u'FIXME! cbq_BlockUserOneTime función no implementada')
        
    def cbq_BanUser(self, msg, user_id):
        self.sendMessage(self.CHAT_GROUP, u'FIXME! cbq_BanUser función no implementada')
        
 
        
    def ask_AddNewUser(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        user_id  = msg['from']['id']
        name     = msg['from']['first_name']
        lastname = msg['from']['last_name']
        botname  = self.getMe()['username']
    
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton( text=self.BUT_ALLOW_USER_YES,            callback_data=self.callback2string(self.CBQ_ADD_USER,            user_id) )],
            [InlineKeyboardButton( text=self.BUT_ALLOW_USER_NO_THIS_TIME,   callback_data=self.callback2string(self.CBQ_BLOCK_USER_ONE_TIME, user_id) )],
            [InlineKeyboardButton( text=self.BUT_ALLOW_USER_NO_NEVER,       callback_data=self.callback2string(self.CBQ_BAN_USER,            user_id) )],
        ])                
        
        #TODO: add Timer para borrar el mensaje si no se contesta en un tiempo prudencial
        bot.sendMessage(self.ADMIN_USER, self.MSG_NEW_USER.format(name, lastname, botname, id), reply_markup=markup)

   
    def callback2string(self,function, arg=None):
        if arg:
            arg = self.CBQ_FUNCTION_SPLITTER + str(arg)
        
        return function.__name__ + arg
    
    
    def string2callback(self, data):
        tk  = data.split(self.CBQ_FUNCTION_SPLITTER)
        arg = None
        
        if len(tk)>1:
            arg = tk[1]
        
        function = self.CALLBACKS[tk[0]]
        
        return (function, arg) 
    
    
    
    def getCommand(self, msg):
        if 'entities' in msg and msg['entities'][0]['type']=='bot_command':
            regex = compile('/[a-zA-Z0-9_]+')
            r = regex.findall(msg['text'])
            if r:
                return r[0]
                
        return None
    

         
        
class TimeDelay:
    """ Test """
    labels = {86400.0 : ("días","día"), 3600.0 : ("horas","hora"), 60.0 : ("minutos","minuto"), 1.0 : ("segundos","segundo")}
    
    def __init__(self):
        self._days    = 0
        self._hours   = 0
        self._minutes = 0
        self._seconds = 0
        self._time      = None
        self._flag    = 0
        
    def getTime(self):
        if not self._time:
            self._time = self._seconds + self._minutes*60 + self._hours*3600 + self._days*86400
        return self._time
    
    
    def toString(self):        
        resp=[]
        time = self.getTime()
    
        for i in self.labels:
            r = time / i
            if r>=1:
                    d=int(r)
                    resp.append( str(d) + ' ' + (self.labels[i][0] if d>1 else self.labels[i][1]) )
                    time -= d*i

        return (resp[0] if len(resp)==1 else ", ".join(resp[:-1]) + ' y ' + resp[-1])


    def isComplete(self):
        return self._flag == int("1"*len(self.labels), 2)

        
    def setDays(self, days):
        self._days = days
        self._time = None
        self._flag |= 0b1000
        
    def setHours(self, hours):
        self._hours = hours
        self._time = None
        self._flag |= 0b100
        
    def setMinutes(self, minutes):
        self._minutes = minutes
        self._time = None
        self._flag |= 0b10
        
    def setSeconds(self, seconds):
        self._seconds = seconds
        self._time = None
        self._flag |= 0b1
         
         
         
if __name__ == "__main__":
    TOKEN = os.environ['TELEGRAM_TOKEN']
    bot = Telegram_bot(TOKEN)
    #bot.message_loop({'chat': bot.on_chat_message, 'callback_query': bot.on_callback_query, 'inline_query': bot.on_inline_query, 'chosen_inline_result': bot.on_chosen_inline_result}, relax=1, timeout=60)
    bot.message_loop()    
    
    print 'Listening ...'
    
    # Keep the program running.
    while 1:
        sleep(10)
    
    #sys.exit(main(sys.argv))


     
        
        
        
        
-'''
-#####################
-##  P R I V A T E  ##
-#####################
-{
-    "chat": {
-        "first_name": "Daniel",
-        "id": 202714763,
-        "last_name": "L\u00f3pez",
-        "type": "private",
-        "username": "svvpa"
-    },
-    "date": 1460635819,
-    "from": {
-        "first_name": "Daniel",
-        "id": 202714763,
-        "last_name": "L\u00f3pez",
-        "username": "svvpa"
-    },
-    "message_id": 237,
-    "text": "G"
-}
-
-
-#####################
-##  C O M M A N D  ##
-#####################
-{
-    "chat": {
-        "id": -136404445,
-        "title": "Control remoto SVVPA",
-        "type": "group"
-    },
-    "date": 1460619355,
-    "entities": [
-        {
-            "length": 6,
-            "offset": 0,
-            "type": "bot_command"
-        }
-    ],
-    "from": {
-        "first_name": "Daniel",
-        "id": 202714763,
-        "last_name": "L\u00f3pez",
-        "username": "svvpa"
-    },
-    "message_id": 205,
-    "text": "/start"
-}
-
-
-#####################
-##  M E N T I O N  ##
-#####################
-{
-    "chat": {
-        "id": -136404445,
-        "title": "Control remoto SVVPA",
-        "type": "group"
-    },
-    "date": 1460557186,
-    "entities": [
-        {
-            "length": 9,
-            "offset": 0,
-            "type": "mention"
-        }
-    ],
-    "from": {
-        "first_name": "Daniel",
-        "id": 202714763,
-        "last_name": "L\u00f3pez",
-        "username": "svvpa"
-    },
-    "message_id": 199,
-    "text": "@svvpaBot ((&"
-}
-
-
-#################
-##  R E P L Y  ##
-#################
-{
-    "chat": {
-        "id": -136404445,
-        "title": "Control remoto SVVPA",
-        "type": "group"
-    },
-    "date": 1460618301,
-    "from": {
-        "first_name": "Daniel",
-        "id": 202714763,
-        "last_name": "L\u00f3pez",
-        "username": "svvpa"
-    },
-    "message_id": 203,
-    "reply_to_message": {
-        "chat": {
-            "id": -136404445,
-            "title": "Control remoto SVVPA",
-            "type": "group"
-        },
-        "date": 1460618219,
-        "from": {
-            "first_name": "svvpa",
-            "id": 183543111,
-            "username": "svvpaBot"
-        },
-        "message_id": 201,
-        "text": "Force reply"
-    },
-    "text": "Ggg"
-}
-
-
-###################
-##  I N L I N E  ##
-###################
-{
-    "from": {
-        "first_name": "Daniel",
-        "id": 202714763,
-        "last_name": "L\u00f3pez",
-        "username": "svvpa"
-    },
-    "id": "870653278453550833",
-    "offset": "",
-    "query": "((&"
-}
-
-
-##################################
-##  C H O S E N   I N L I N E   ##
-##################################
-{
-    "from": {
-        "first_name": "Daniel",
-        "id": 202714763,
-        "last_name": "L\u00f3pez",
-        "username": "svvpa"
-    },
-    "query": "ffatwdsdfg",
-    "result_id": "2016_04_01_19_06_20_34923_14_154_296_329_330_1.jpg"
-}-
-
-
-
-#####################################
-##  C A L L B A C K    Q U E R Y   ##
-#####################################
-{
-    "data": "notification",
-    "from": {
-        "first_name": "Daniel",
-        "id": 202714763,
-        "last_name": "L\u00f3pez",
-        "username": "svvpa"
-    },
-    "id": "870653277835729620",
-    "message": {
-        "chat": {
-            "first_name": "Daniel",
-            "id": 202714763,
-            "last_name": "L\u00f3pez",
-            "type": "private",
-            "username": "svvpa"
-        },
-        "date": 1461331145,
-        "from": {
-            "first_name": "svvpa",
-            "id": 183543111,
-            "username": "svvpaBot"
-        },
-        "message_id": 891,
-        "text": "Inline keyboard with various buttons"
-    }
-}
-
-'''
