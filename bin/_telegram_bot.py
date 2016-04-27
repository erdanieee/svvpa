# encoding: utf-8


from json import dumps
import os
from re import match, findall, compile
import subprocess as proc
import telepot
from telepot.namedtuple import InlineQueryResultPhoto, ReplyKeyboardHide,\
    InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
import threading
from threading import Timer
import pdb

#poner a TRUE cuando deje de estar en fase Beta!!!!
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
    MSG_CMD_HELP = u'''Mu wenas! Me llaman @{}, el *robot telegram* diseñado \
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
    MSG_USER_ADDED = u'{} ha añadido a {} {} a la lista de usuarios autorizados. \
A partir de este momento {} puede ejecutar comandos a través de telegram!'
    MSG_ERROR_ADDING_USER = u'ERROR! Hubo un problema al añadir el usuario a la \
lista de usuarios autorizados (!?)'
    MSG_BLOCKED_USER = u'Se ha bloqueado a {} {}. Este usuario no podrá enviar \
comandos por telegram hasta la próxima vez que se reinicie el sistema'
    MSG_BANN_USER = u'{} ha bloqueado permanentemente a {} {}. Este usuario no \
podrá volver a enviar comandos a través de telegram!'
    MSG_ERROR_BANNING_USER = u'ERROR! Hubo un problema al bloquear permanentemente \
el usuario (!?)'
    MSG_CMD_MOTION = u'Este comando sirve para controlar la detección de movimiento. \
¿Qué quieres hacer?'

    
    BUT_CANCEL                  = u'Cancelar'
    BUT_ALLOW_USER_YES          = u'\u2705 Sí'
    BUT_ALLOW_USER_NO_THIS_TIME = u'\u274c No por ahora'
    BUT_ALLOW_USER_NO_NEVER     = u'\u26d4\ufe0f No, nunca jamás de los jamases'
    BUT_MOTION_START            = u'\u25b6\ufe0f Iniciar'
    BUT_MOTION_STOP             = u'\u23f9 Parar'
    BUT_MOTION_PAUSE            = u'\u23f8 Pausar'
    BUT_MOTION_STATUS           = u'\u2753 Comprobar estado'
                     
    FUNCTION_SPLITTER  = u'*'                 
    MOTION_DAYS        = 'd'
    MOTION_HOURS       = 'h'
    MOTION_MINUTES     = 'm'
    MOTION_SECONDS     = 's'
    MOTION_TIMER       = u'motionTimer'
    
    # Callback functions usadas para procesar las respuestas de los inline keyboards.
    CBQ_FUNCTION_CANCEL     = u'Cancelar'           
    CBQ_ADD_USER            = u'cbq_AddUser'
    CBQ_BLOCK_USER_ONE_TIME = u'cbq_BlockUserOneTime'
    CBQ_BAN_USER            = u'cbq_BanUser'
    CBQ_MOTION_SET_TIME     = u'cbq_MotionSetTime'
    CBQ_MOTION_ASK_TIME     = u'cbq_MotionAskTime'        
    CBQ_MOTION_START        = u'cbq_motionStart'
    CBQ_MOTION_STOP         = u'cbq_motionStop'
    CBQ_MOTION_STATUS       = u'cbq_motionStatus'  
     
    
    def __init__(self, *args, **kwargs):    
        super(Telegram_bot, self).__init__(*args, **kwargs)
               
        self.CHAT_GROUP     = int(os.environ['TELEGRAM_CHAT_GROUP'])
        self.ALLOWED_USERS  = map(int,os.environ['TELEGRAM_ALLOWED_USERS'].split(','))
        self.BANNED_USERS   = [] if not os.environ['TELEGRAM_BANNED_USERS'] else map(int,os.environ['TELEGRAM_BANNED_USERS'].split(','))
        self.ADMIN_USER     = int(os.environ['TELEGRAM_ADMIN_USER'])
        self.FILE_CONSTANTS = os.environ['BIN_DIR']+'CONSTANTS.sh' 
        self.BOT_NAME       = self.getMe()['username']
        #self.MSG_TIMEOUT    = int(os.environ['TELEGRAM_MSG_TIMEOUT'])
        self.MSG_TIMEOUT    = 3600
        
        self._timers        = {}
        self._motionDelay   = None
        
            
        self.CALLBACKS={
                        self.CBQ_FUNCTION_CANCEL            : self.cbq_cancel,
                        self.CBQ_ADD_USER               : self.cbq_AddUser,
                        self.CBQ_BLOCK_USER_ONE_TIME    : self.cbq_BlockUserOneTime,
                        self.CBQ_BAN_USER               : self.cbq_BanUser,
                        self.CBQ_MOTION_SET_TIME        : self.cbq_MotionSetTime,
                        self.CBQ_MOTION_ASK_TIME        : self.cbq_MotionAskTime,
                        self.CBQ_MOTION_START           : self.cbq_motionStart,
                        self.CBQ_MOTION_STOP            : self.cbq_motionStop,
                        self.CBQ_MOTION_STATUS          : self.cbq_motionStatus
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
        if content_type == 'text' and user_id not in self.BANNED_USERS:
            if user_id == self.ADMIN_USER or user_id in self.ALLOWED_USERS:                
                cmd=self.getCommand(msg)
                if cmd in self.COMMANDS:
                    # solo permite comandos por mensaje privado o de admin
                    if user_id == self.ADMIN_USER or chat_id == self.CHAT_GROUP:
                        self.COMMANDS[cmd](msg, chat_id)
                            
                    else:                
                        self.sendMessage(chat_id, self.MSG_BLOCKED_PRIVATE_CHAT.format(self.BOT_NAME()))
                        
                
                # comprueba si es una respuesta
                elif 'reply_to_message' in msg:
                    pass            
                
                # comprueba si es una mención            
                elif 'entities' in msg and msg['entities'][0]['type']=='mention':                
                    self.sendMessage(chat_id, self.MSG_DONT_MENTION_ME())    #FIXME: poner frases aleatorias
                
                #No es un comando o respuesta reconocida               
                else:                
                    self.sendMessage(chat_id, self.MSG_DONT_UNDERSTAND, reply_to_message_id=msg['message_id']())
                    
            else:
                # Si es nuevo usuario... ¿Añadir a la lista de usuarios permitidos?
                self.ask_AddNewUser(msg)            

    
    
    #######################
    #  C A L L B A C K S  #
    #######################            
    def on_callback_query(self, msg):
        self.cancelMsgTimeout(*self.getMsgChatId(msg))        
        funct, arg = self.string2callback(msg['data'])
        funct(msg, *arg)

    

    #############################
    #  I N L I N E   Q U E R Y  #
    #############################   
    def on_inline_query(self, msg):
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        #print 'Inline Query (queryId, fromId, query):' ,query_id, from_id, query_string

        # No permite mensaje privados
        if from_id in self.ALLOWED_USERS and from_id not in self.BANNED_USERS:                
            self.sendChatAction(self.CHAT_GROUP, 'typing')
            
            lines=proc.check_output('node {}_google_drive_last_uploads.js'.format(os.environ['BIN_DIR']), shell=True)[:-1]        # TODO: meter datos en MySQL para que la consulta sea rápida...
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
        self.sendMessage(self.CHAT_GROUP, self.MSG_CMD_HELP.format(self.BOT_NAME, parse_mode="Markdown"))
        

    
    def cmd_motion(self,msg, chat_id):
        self._motionDelay = TimeDelay()
        #self.cbq_MotionAskTime(msg, self.MOTION_DAYS)   #FIXME: Preguntar si quiere iniciar, parar o pausar
            
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton( text=self.BUT_MOTION_START,  callback_data=self.callback2string( self.CBQ_MOTION_START ) )],
            [InlineKeyboardButton( text=self.BUT_MOTION_STOP,   callback_data=self.callback2string( self.CBQ_MOTION_STOP ) )],
            [InlineKeyboardButton( text=self.BUT_MOTION_PAUSE,  callback_data=self.callback2string( self.CBQ_MOTION_ASK_TIME, [self.MOTION_DAYS] ) )],
            [InlineKeyboardButton( text=self.BUT_MOTION_STATUS, callback_data=self.callback2string( self.CBQ_MOTION_STATUS ) )],
        ])                
                        
        chat = self.CHAT_GROUP if INLINE_KEYBOARDS_GROUP_ACTIVE else self.ADMIN_USER    
        m = bot.sendMessage(chat, self.MSG_CMD_MOTION, reply_markup=markup)
        self.addMsgTimeout(*self.getMsgChatId(msg))
  
        
        
        
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
        
 
        
    def ask_AddNewUser(self, msg):
        user_id  = msg['from']['id']
        name     = msg['from']['first_name']
        lastname = msg['from']['last_name']
    
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton( text=self.BUT_ALLOW_USER_YES,            callback_data=self.callback2string(self.CBQ_ADD_USER,            [user_id]) )],
            [InlineKeyboardButton( text=self.BUT_ALLOW_USER_NO_THIS_TIME,   callback_data=self.callback2string(self.CBQ_BLOCK_USER_ONE_TIME, [user_id]) )],
            [InlineKeyboardButton( text=self.BUT_ALLOW_USER_NO_NEVER,       callback_data=self.callback2string(self.CBQ_BAN_USER,            [user_id]) )],
            [InlineKeyboardButton( text=self.BUT_CANCEL,                    callback_data=self.callback2string(self.CBQ_FUNCTION_CANCEL)  )],
        ])                
        
        #TODO: add Timer para borrar el mensaje si no se contesta en un tiempo prudencial        
        chat = self.CHAT_GROUP if INLINE_KEYBOARDS_GROUP_ACTIVE else self.ADMIN_USER    
        m = bot.sendMessage(chat, self.MSG_NEW_USER.format(name, lastname, self.BOT_NAME, id), reply_markup=markup)
        self.addMsgTimeout(*self.getMsgChatId(msg))
        
      
    def cbq_cancel(self, msg):
        self.deleteMsg(*self.getMsgChatId(msg))
      
    
    def cbq_MotionSetTime(self, msg, unit, num):        
        if not self._motionDelay:
            self._motionDelay = TimeDelay()
        
        if unit == self.MOTION_DAYS:
            self._motionDelay.setDays(num)                
        elif unit == self.MOTION_HOURS:
            self._motionDelay.setHours(num)            
        elif unit == self.MOTION_MINUTES:
            self._motionDelay.setMinutes(num)            
        elif unit == self.MOTION_SECONDS:
            self._motionDelay.setSeconds(num)
        
        if not self._motionDelay.isDaysSetted():
            self.cbq_MotionAskTime(msg, self.MOTION_DAYS)        
        elif not self._motionDelay.isHoursSetted():
            self.cbq_MotionAskTime(msg, self.MOTION_HOURS)        
        elif not self._motionDelay.isMinutesSetted():
            self.cbq_MotionAskTime(msg, self.MOTION_MINUTES)        
        elif not self._motionDelay.isSecondsSetted():
            self.cbq_MotionAskTime(msg, self.MOTION_SECONDS)
            
        else:            
            self.cbq_motionStop()
            
            text = u'La detección de movimiento se iniciará automáticamente dentro de {}.'.format(self._motionDelay.toString())
            bot.editMessageText(self.getMsgChatId(msg), text)
            if not INLINE_KEYBOARDS_GROUP_ACTIVE:
               bot.sendMessage(self.CHAT_GROUP, text)
            
                    
            
            m = self._timers.pop(self.MOTION_TIMER, None)
            if m:
                m.cancel()
                                            
            self._timers[self.MOTION_TIMER] = Timer(self._motionDelay.getTime(), self.cbq_motionStart)
            self._timers[self.MOTION_TIMER].start()
            
            
            
    def cbq_MotionAskTime(self, msg, unit):
        units = []
                             
        if unit == self.MOTION_DAYS:
            for i in (0,1,2,3,4,5,6,7,14,21):
                units.append(unicode(i))
            text = u'días'
        
        elif unit == self.MOTION_HOURS:
            for i in (0,1,2,3,4,5,6,7,8,9,10,12,14,16,20):
                units.append(unicode(i))
            text = u'horas'
        
        elif unit == self.MOTION_MINUTES:
            for i in (0,1,2,3,4,5,10,15,20,25,30,35,40,45,50):
                units.append(unicode(i))
            text = u'minutos'
            
        elif unit == self.MOTION_SECONDS:
            for i in (0,5,10,15,20,25,30,35,40,45):
                units.append(unicode(i))
            text = u'segundos'
            
        buttons=[]
        aux=[]
        i=1
        for a in units:
            t = a + unit.upper()            
            aux.append( InlineKeyboardButton( text=t, callback_data=self.callback2string(self.CBQ_MOTION_SET_TIME, [unit, a]) ))
                                
            if not i%5 or i==len(units):
                buttons.append(aux)
                aux = []
                
            i+=1
                      
        aux.append(InlineKeyboardButton( text=self.BUT_CANCEL, callback_data=self.callback2string(self.CBQ_FUNCTION_CANCEL) ))
        buttons.append(aux)
                  
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)                
        
        #TODO: add Timer para borrar el mensaje si no se contesta en un tiempo prudencial        
        chat = self.CHAT_GROUP if INLINE_KEYBOARDS_GROUP_ACTIVE else msg['from']['id']
        print chat
        print self.getMsgChatId(msg)
        print self.CHAT_GROUP
        bot.editMessageText( self.getMsgChatId(msg), u'Selecciona el número de {} que quieres pausar el servicio'.format(text.upper()), reply_markup=markup)
        self.addMsgTimeout(*self.getMsgChatId(msg))
      
      
    def cbq_motionStart(self, msg=None):
        try:
            proc.call('echo sudo service motion restart', shell=True)
            
            text = u'La detección de movimiento se ha activado correctamente \U0001f440.'
            
            if msg and INLINE_KEYBOARDS_GROUP_ACTIVE:
                bot.editMessageText(self.getMsgChatId(msg), text)
            
            else:        
                bot.sendMessage(self.CHAT_GROUP, text)            
        
        except Exception as e:
            bot.sendMessage(self.CHAT_GROUP, u'ERROR! Hubo un problema al iniciar el servicio de detección de movimiento (!?)')
            
  
        
                
        
    def cbq_motionStop(self, msg=None):
        try:
            proc.call('echo sudo service motion stop', shell=True)
            
            text = u'La detección de movimiento se ha detenido \U0001f648 '
            
            if msg and INLINE_KEYBOARDS_GROUP_ACTIVE:
                bot.editMessageText(self.getMsgChatId(msg), text)
            
            else:
               bot.sendMessage(self.CHAT_GROUP, text)
                      
 
            
        except Exception as e:
            bot.sendMessage(self.CHAT_GROUP, u'ERROR! Hubo un problema al parar el servicio de detección de movimiento (!?)')
            
         
        
        
    def cbq_motionStatus(self, msg):
        try:
            if proc.call('echo sudo service motion status', shell=True) == 0:
                bot.editMessageText(self.getMsgChatId(msg),  u'La detección de movimiento está activa \U0001f440')
            
            else:
                bot.editMessageText(self.getMsgChatId(msg),  u'La detección de movimiento está inactiva \U0001f648')
            
        except:         
            bot.sendMessage(self.CHAT_GROUP, u'ERROR! Hubo un problema al comprobar el estado del servicio de detección de movimiento (!?)')
              
        
        
          
    def cbq_AddUser(self, msg, arg):
        user_id         = int(arg)
        from_name       = msg['from']['first_name']
        tk              = msg['message']['text'].split(" ")
        user_name       = tk[0]
        user_lastname   = tk[1]
        
        
        #añadimos usuario en la ejecución actual
        self.ALLOWED_USERS.append( user_id )
        
        try:
            #Añadimos usuario en el fichero de configuración
            cmd     = 'grep TELEGRAM_ALLOWED_USERS {}'.format(self.FILE_CONSTANTS)
            p       = proc.check_output(cmd, shell=True).strip()
            users   = set(findall('[0-9]+', p))
            users.add(str(user_id))
            
            cmd     = 'sed -i -r \'s/TELEGRAM_ALLOWED_USERS="([0-9,]+)"/TELEGRAM_ALLOWED_USERS="{}"/g\' {}'.format(",".join(users), self.FILE_CONSTANTS)
            proc.call(cmd, shell=True) 
                        
            text = self.MSG_USER_ADDED.format(from_name, user_name, user_lastname, user_name)        
            bot.editMessageText( self.getMsgChatId(msg), text)
            
            if not INLINE_KEYBOARDS_GROUP_ACTIVE:
                bot.sendMessage(self.CHAT_GROUP, text)
                 
        except Exception as e:
            print e            
            bot.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_ADDING_USER) 
        
        
        
    def cbq_BlockUserOneTime(self, msg, arg):
        user_id         = int(arg)
        tk              = msg['message']['text'].split(" ")
        user_name       = tk[0]
        user_lastname   = tk[1]
                
        self.BANNED_USERS.append(user_id)
                
        text = self.MSG_BLOCKED_USER.format(user_name, user_lastname)        
        bot.editMessageText( self.getMsgChatId(msg), text)
        
        if not INLINE_KEYBOARDS_GROUP_ACTIVE:
            bot.sendMessage(self.CHAT_GROUP, text)
        
        
    def cbq_BanUser(self, msg, arg): 
        user_id         = int(arg)
        from_name       = msg['from']['first_name']
        tk              = msg['message']['text'].split(" ")
        user_name       = tk[0]
        user_lastname   = tk[1]
                
        #añadimos usuario en la ejecución actual
        self.BANNED_USERS.append( user_id )
        
        try:
            #Añadimos usuario en el fichero de configuración
            cmd     = 'grep TELEGRAM_BANNED_USERS {}'.format(self.FILE_CONSTANTS)
            users   = set(findall('[0-9]+', proc.check_output(cmd, shell=True).strip()))
            users.add(str(user_id))
            
            cmd     = 'sed -i -r \'s/TELEGRAM_BANNED_USERS="([0-9,]*)"/TELEGRAM_BANNED_USERS="{}"/g\' {}'.format(",".join(users), self.FILE_CONSTANTS)
            proc.call(cmd, shell=True) 
                        
            text = self.MSG_BANN_USER.format(from_name, user_name, user_lastname, user_name)        
            bot.editMessageText( self.getMsgChatId(msg), text)
                        
            if not INLINE_KEYBOARDS_GROUP_ACTIVE:
                bot.sendMessage(self.CHAT_GROUP, text)
                 
        except Exception as e:
            print e            
            bot.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_BANNING_USER) 
          
            
       
    def callback2string(self,function, arg=None):
        ret = function
        if arg:
            for i in arg:
                ret += self.FUNCTION_SPLITTER + str(i)
        
        return ret
    
    
    def string2callback(self, data):
        tk  = data.split(self.FUNCTION_SPLITTER)
        arg = []
        
        if len(tk)>1:
            arg = tk[1:]
        
        function = self.CALLBACKS[tk[0]]
        
        return (function, arg) 
    
    
    
    def getCommand(self, msg):
        if 'entities' in msg and msg['entities'][0]['type']=='bot_command':
            regex = compile('/[a-zA-Z0-9_]+')
            r = regex.findall(msg['text'])
            if r:
                return r[0]
                
        return None
    
    
    def deleteMsg(self, chat_id, msg_id):
        self.cancelMsgTimeout(chat_id, msg_id)
        bot.editMessageText( (chat_id, msg_id), u'\U0001f914')
    
    
    def addMsgTimeout(self, chat_id, msg_id):
        self._timers[chat_id, msg_id] = Timer(self.MSG_TIMEOUT, self.deleteMsg, [chat_id, msg_id])        
        self._timers[chat_id, msg_id].start()        
           
           
    def cancelMsgTimeout(self, chat_id, msg_id):
        timer = self._timers.pop((chat_id, msg_id), None)
        if timer:
            timer.cancel()
             
      


    def getMsgChatId(self, msg):
        if 'message' in msg:
            msg_id  = msg['message']['message_id']
            chat_id = msg['message']['chat']['id']            
            
        else:
            msg_id  = msg['message_id']
            chat_id = msg['chat']['id']
                        
        return chat_id, msg_id   

        
class TimeDelay:
    """ Test """
    labels = {86400.0 : ("días","día"), 3600.0 : ("horas","hora"), 60.0 : ("minutos","minuto"), 1.0 : ("segundos","segundo")}
    
    def __init__(self):
        self._days    = None
        self._hours   = None
        self._minutes = None
        self._seconds = None
        self._time    = None
        
    def getTime(self):
        if not self._time:
            self._time = 0
            
            if self._seconds:
                self._time += self._seconds
            if self._minutes:
                self._time += self._minutes*60
            if self._hours:
                self._time += self._hours*3600
            if self._days:
                self._time += self._days*86400
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

        
    def setDays(self, days):
        self._days = int(days)
        self._time = None
        
    def setHours(self, hours):
        self._hours = int(hours)
        self._time = None
        
    def setMinutes(self, minutes):
        self._minutes = int(minutes)
        self._time = None
        
    def setSeconds(self, seconds):
        self._seconds = int(seconds)
        self._time = None
         
    def isDaysSetted(self):
        return self._days != None
        
    def isHoursSetted(self):
        return self._hours != None
        
    def isMinutesSetted(self):
        return self._minutes != None
        
    def isSecondsSetted(self):
        return self._seconds != None
      
         
         
         
         
         
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
