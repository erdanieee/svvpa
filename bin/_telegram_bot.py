# encoding: utf-8


import os, sys, traceback
import re
import subprocess as proc
import telepot
from telepot.namedtuple import InlineQueryResultPhoto, InlineKeyboardMarkup, InlineKeyboardButton
import time
import threading
import MySQLdb
import signal
import datetime
from _google_drive_uploader import main as fileuploader

try:
    from Queue import Queue	#python 2.7
except ImportError:
    from queue import Queue	#python 3


#poner a TRUE cuando deje de estar en fase Beta!!!!
INLINE_KEYBOARDS_GROUP_ACTIVE = True




class Telegram_bot(telepot.Bot):
    '''
    classdocs
    '''
    MSG_NEW_USER = u'''{} {} ha enviado un comando a {}, pero aún no tiene \
permiso. ¿Quieres añadir al menda a la lista de usuarios autorizados para ejecutar \
comandos a traves de Telegram?'''
    MSG_BLOCKED_PRIVATE_CHAT = u'''Lo siento, pero por ahora el control de {} \
por chat privado esta desactivado (es pa\' controlar el percal \U0001f609).\
Utiliza el chat de grupo para mandar los commandos'''
    MSG_DONT_MENTION_ME = u'''¿Que dices de mi?'''
    MSG_DONT_UNDERSTAND = u'''\U0001f21a\ufe0f \U0001f236\U0001f236 \
\U0001f238\u203c\ufe0f\n\n¿Te has enterado? Pues yo tampoco se lo que quieres. \
Anda, hazme el favor de escribir los comandos correctamente y solo uno por mensaje \
, que si no no se puede, aaaaaaaaes?.'''
    MSG_CMD_HELP = u'''Mu wenas! Soy {}, el *robot telegram* diseñado \
específicamente para el control remoto de _SVVPA_ \U0001f60e. Al final de este \
mensaje puedes ver los comandos disponibles. Para más información visita este \
[enlace](https://docs.google.com/document/d/1L5-JcmTxsYVXZKHnDxlkZrFGeXPqNvtwgtptdFnbYlc/edit?usp=sharing).
    
Para enviar un comando, escribe */* (o usa el icono) y pulsa sobre la opcion que \
te interese. Adicionalmente, para subir un video capturado a google drive, ademas \
del comando /subir, también puedes escribir mi nombre seguido de un espacio y \
pulsar sobre la captura que te interese.

/ayuda - Muestra esta ayuda
/movimiento - Inicia/para/pausa la detección de movimiento
/foto - Toma una instantánea            
/subir - Sube una captura a google drive
/sensores - Muestra el estado de los sensores
/wifi - Activa/desactiva la wifi de El Cárabo
/emails - Activa/desactiva la notificación por emails
/ssh - Abre tunel inverso ssh para gestión remota de SVVPA
/actualizar - actualiza el repositorio github
/reiniciar - reinicia el sistema
/apagar - Apaga el sistema
    '''
    MSG_USER_ADDED = u'''{} ha añadido a {} {} a la lista de usuarios autorizados. \
A partir de este momento {} puede ejecutar comandos a traves de telegram!'''
    MSG_ERROR_ADDING_USER = u'''ERROR! Hubo un problema al añadir el usuario a la \
lista de usuarios autorizados (!?)'''
    MSG_BLOCKED_USER = u'''Se ha bloqueado a {} {}. Este usuario no podra enviar \
comandos por telegram hasta la proxima vez que se reinicie el sistema'''
    MSG_BANN_USER = u'''{} ha bloqueado permanentemente a {} {}. Este usuario no \
podra volver a enviar comandos a traves de telegram!'''
    MSG_ERROR_BANNING_USER = u'''ERROR! Hubo un problema al bloquear permanentemente \
el usuario (!?)'''
    MSG_CMD_MOTION = u'''Este comando te permite ajustar la deteccion de movimiento. \
¿Que quieres hacer?'''
    MSG_CMD_WIFI = u'''Este comando te permite controlar la wifi "El Cárabo". \
¿Que quieres hacer?'''
    MSG_ERROR_NO_CAMERAS = u'''ERROR! No hay cámaras configuradas'''
    MSG_SELECT_DEVICE = u'''Selecciona la cámara que quieres usar para tomar la foto'''
    MSG_SSH_OPENED = u'''Se ha abierto un tunel reverso ssh que será accesible \
desde {}:{} durante {} segundos'''
    MSG_ERROR_SSH = u'ERROR! No se ha podido abrir el tunel ssh (ret={})'
    MSG_ERROR_UNEXPECTED = u'''ERROR! Se ha producido un error inesperado (?!):
```{}```'''
    MSG_MOTION_NO_EVENTS = u'''Todavía no hay eventos capturados'''
    MSG_CMD_UPLOAD = u'''Este comando sirve para subir los videos capturados a \
Google Drive (las imagenes mas representativas se suben automaticamente). \
Selecciona el video del evento que quieres subir a Google Drive (el gasto \
actual de datos es de {} de los {}MB que incluye la tarifa).'''
    MSG_CMD_SENSORS = u'''A continuacion se muestran los datos tomados  el dia \
*{}* a las *{}*:
        
```
T. CPU: {}ºC
T. ext: {}ºC
T. int: {}ºC
H. rel: {}%
P. atm: {}hPa
```
'''
    MSG_CMD_UPDATE = u'''Repositorio actualizado con exito\n```{}```'''
    MSG_CMD_REBOOT = u'''Se esta reiniciando el sistema. Este proceso deberia \
tardar aproximadamente 1 minuto'''
    MSG_CMD_SHUTDOWN = u'''Se va a proceder a apagar SVVPA. Este comando deberia \
ejecutarse *SIEMPRE* desde E.C., ya que para volver a iniciar el sistema es \
necesario desactivar y volver a activar fisicamente el miniinterruptor que esta \
junto a las baterias. ¿Realmente quieres apagar el sistema?'''
    MSG_CMD_EMAIL_NOTIF =u'''Este comando sirve para activar o desactivar las \
notificaciones (nuevo movimiento, arranque/parada sistema, errores, ...) \
mediante correo electronico. Actualmente este servicio esta {}. 
¿Que deseas hacer?'''
    MSG_ERROR_FAKE = u'''ERROR! DIVISION ENTRE CERO!.\nSVVPA esta a punto de \
arder por intentar pausar cero segundos!! \U0001f602\U0001f602\U0001f602'''
    MSG_CMD_MOTION_PAUSE = u'''La deteccion de movimiento se iniciará \
automaticamente dentro de {}.'''
    MSG_CMD_MOTION_TIME_SET = u'''Selecciona el numero de {} que quieres pausar \
el servicio {}'''
    MSG_MOTION_START = u'''La detección de movimiento se ha activado \
correctamente \U0001f440.'''
    MSG_CMD_MOTION_STOP = u'''La detección de movimiento se ha detenido \U0001f648 '''
    MSG_CMD_MOTION_ENABLED = u'''La detección de movimiento esta activa \U0001f440'''
    MSG_CMD_MOTION_DISABLED = u'''La detección de movimiento esta inactiva \U0001f648'''
    MSG_CMD_WIFI_START = u'''La wifi El Cárabo se acaba de activar'''
    MSG_CMD_WIFI_STOP = u'''La wifi El Cárabo se ha desactivado'''    
    MSG_CMD_WIFI_ENABLED = u'''La wifi El Cárabo está activa'''
    MSG_CMD_WIFI_DISABLED = u'''La wifi El Cárabo está inactiva'''
    MSG_CMD_SNAPSHOT = u'''Capturando foto...'''
    MSG_CMD_EMAIL_NOTIF_ENABLED = u'''Las notificaciones por email estan \
actualmente activadas \u2709\ufe0f'''
    MSG_CMD_EMAIL_NOTIF_DISABLED = u'''Las notificaciones por email estan \
actualmente desactivadas \U0001f64a'''
    MSG_CMD_UPLOAD_DONE = u'El video *{}* se ha subido correctamente a google \
drive. A partir de ahora, puedes reproducirlo todas las veces que quieras y sin \
consumir datos en [este enlace]({}). Recuerda que puedes ver todos los archivos \
subidos a google drive en [este enlace](https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing)'
    MSG_ERROR_UPLOAD_MAX_TRIES = u'ERROR! No se ha podido subir el archivo {} a \
google drive. Inténtalo de nuevo más tarde'
    MSG_SHUTTING_DOWN = u'El sistema se apagará en unos segundos. Recuerda que \
para volver a iniciarlo es necesario desactivar y activar físicamente el \
miniinterruptor que está junto a las baterías'
    MSG_ERROR_NO_SHELL_CMD = u'Este comando sirve para ejecutar un comando shell en SVVPA. \
Debes especificar el comando a ejecutar despues del comando shell. Para ello, \
envía el mensaje /shell comando'
    MSG_ERROR_SHELL_CMD = u'ERROR! Se produjo un error inesperado al ejecutar \
el comando bash'
    MSG_ERROR_CMD = u'\u203c\ufe0fERROR! Se ha producido un error inesperado al procesar el comando'
    

    
    BUT_CANCEL                  = u'Cancelar'
    BUT_ALLOW_USER_YES          = u'\u2705 Si'
    BUT_ALLOW_USER_NO_THIS_TIME = u'\u274c No por ahora'
    BUT_ALLOW_USER_NO_NEVER     = u'\u26d4\ufe0f No, nunca jamás de los jamases'
    BUT_MOTION_START            = u'\u25b6\ufe0f Iniciar'
    BUT_MOTION_STOP             = u'\u23f9 Parar'
    BUT_MOTION_PAUSE            = u'\u23f8 Pausar'
    BUT_MOTION_STATUS           = u'\u2753 Estado'
    BUT_WIFI_START              = u'\u25b6\ufe0f Iniciar'
    BUT_WIFI_STOP               = u'\u23f9 Parar'
    BUT_WIFI_STATUS             = u'\u23f8 Estado'
    BUT_SHUTDOWN_NO             = u'\u2620 No'
    BUT_SHUTDOWN_NOTSURE        = u'\u2620 No totalmente'
    BUT_SHUTDOWN_MAYBE          = u'\u2620 Creo que sí'
    BUT_SHUTDOWN_YES            = u'\U0001f44c\U0001f3fc Absolutamente'
    BUT_NOTIF_ENABLE            = u'\u2705 Activar'
    BUT_NOTIF_DISABLE           = u'\u274c Desactivar'
                     
    FUNCTION_SPLITTER  = u'*'                 
    MOTION_DAYS        = 'd'
    MOTION_HOURS       = 'h'
    MOTION_MINUTES     = 'm'
    MOTION_SECONDS     = 's'
    SHUTDOWN_CONFIRM   = u'True'
    EMAIL_NOTIF_ON     = u'ON'
    EMAIL_NOTIF_OFF    = u'OFF'

    TIMER_MOTION    = u'motionTimer'
    TIMER_WIFI      = u'wifiTimer'
    TIMER_SSH       = u'sshTimer'
    TIMER_UPDATE	= u'updateTimer'

    
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
    CBQ_WIFI_START          = u'cbq_wifiStart'
    CBQ_WIFI_STOP           = u'cbq_wifiStop'
    CBQ_WIFI_STATUS         = u'cbq_wifiStatus'    
    CBQ_SNAPSHOT            = u'cbq_snapshot'
    CBQ_UPLOAD_FILE         = u'cbq_uploadVideo'
    CBQ_SHUTDOWN            = u'cbq_shutdown'
    CBQ_EMAIL_NOTIF         = u'cbq_emailNotif'  

    
    RETRIES_MAX     = 10
    RETRIES_WAIT    = 50
    
    SIZE_KB = 1024.0
    SIZE_MB = 1048576.0 
    SIZE_GB = 1073741824.0 
    SIZE_TB = 1099511627776.0
    
    GET_MORE = u'more' 



    def update_queue(self):		
        print u"[{}] {}: Iniciando cola telegram".format(datetime.datetime.now(), __file__)
        _update_offset 	= None
        _update_timeout	= int(os.environ['TELEGRAM_UPDATE_TIMEOUT'])
        _update_steps	= int(os.environ['TELEGRAM_UPDATE_STEPS'])
        _update_base	= float(os.environ['TELEGRAM_UPDATE_BASE'])
        _update_factor	= float(os.environ['TELEGRAM_UPDATE_FACTOR'])

        _step_times = []
        for i in range(1,_update_steps+1):
            _step_times.append([(_update_base**i), (_update_base**i)**2*_update_factor ])
    
        print u"[{}] {}: Array tiempos de refresco: {}".format(datetime.datetime.now(), __file__, ' '.join( "%.1f|%s" %(_step_times[x][0],datetime.timedelta(seconds=int(_step_times[x][1]))) for x in range(len(_step_times)) ))
		

        def add_queue(update):
            self._queue.put(update)
            return update['update_id']


        def update_time(curr_step=0):
            m = self._timers.pop(self.TIMER_UPDATE, None)
            if m:
                #print u"[{}] {}: Cancelando timer update".format(datetime.datetime.now(), __file__)
                m.cancel()

            self._update_time = _step_times[curr_step][0]
            
            if curr_step < _update_steps:                                
                aux = _step_times[curr_step][1]         
                self._timers[self.TIMER_UPDATE] = threading.Timer(aux, update_time, args=(curr_step+1,))
                self._timers[self.TIMER_UPDATE].start()
                print u"[{}] {}: Estableciendo update cada {:.1f} s durante {}".format(datetime.datetime.now(), __file__, self._update_time, datetime.timedelta(seconds=int(aux)))
    
            else:
                print u"[{}] {}: Estableciendo update cada {:.1f}".format(datetime.datetime.now(), __file__, self._update_time)
            


        update_time()
        while 1:
            try:
                #print u"[{}] {}: Update Telegram queue".format(datetime.datetime.now(), __file__) 
                result = self.getUpdates(offset=_update_offset) #, timeout=_update_timeout)

                if len(result) > 0:
                    _update_offset	= max([add_queue(update) for update in result]) + 1		#No se ordena; confiamos en que el servidor de telegram
                    update_time()

            except:
                print >>sys.stderr, u"[{}] {}: ERROR! Se produjo un error inesperado al actualizar la cola:".format(datetime.datetime.now(), __file__)
                traceback.print_exc()

            finally:
                time.sleep(self._update_time)		




        def handle(self, msg):
            flavor = telepot.flavor(msg)
            #print json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': '))
            print u"[{}] {}: Msg:\n{}".format(datetime.datetime.now(), __file__, msg)
            print u"[{}] {}: Flavor: {}".format(datetime.datetime.now(), __file__, flavor)

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



    #############
    #  I N I T  #
    #############    
    def __init__(self, *args, **kwargs):    
        super(Telegram_bot, self).__init__(*args, **kwargs)
        
        print u"[{}] {}: Iniciando Telegram_bot".format(datetime.datetime.now(), __file__)
               
        self.CHAT_GROUP     = int(os.environ['TELEGRAM_CHAT_GROUP'])
        self.ALLOWED_USERS  = map(int,os.environ['TELEGRAM_ALLOWED_USERS'].split(','))
        self.BANNED_USERS   = [] if not os.environ['TELEGRAM_BANNED_USERS'] else map(int,os.environ['TELEGRAM_BANNED_USERS'].split(','))
        self.ADMIN_USER     = int(os.environ['TELEGRAM_ADMIN_USER'])
        self.FILE_CONSTANTS = os.environ['BIN_DIR']+'CONSTANTS.sh' 
        self.BOT_NAME       = "SVVPA" #self.getMe()['username']
        self.MSG_TIMEOUT    = int(os.environ['TELEGRAM_MSG_TIMEOUT'])
        #self.MSG_TIMEOUT    = 3600
        
        self._timers        = {}
        self._motionDelay   = None
        self._queue 		= Queue()
        self._update_time	= None
        
            
        self.CALLBACKS={
                        self.CBQ_FUNCTION_CANCEL        : self.cbq_cancel,
                        self.CBQ_ADD_USER               : self.cbq_AddUser,
                        self.CBQ_BLOCK_USER_ONE_TIME    : self.cbq_BlockUserOneTime,
                        self.CBQ_BAN_USER               : self.cbq_BanUser,
                        self.CBQ_MOTION_SET_TIME        : self.cbq_MotionSetTime,
                        self.CBQ_MOTION_ASK_TIME        : self.cbq_MotionAskTime,
                        self.CBQ_MOTION_START           : self.cbq_motionStart,
                        self.CBQ_MOTION_STOP            : self.cbq_motionStop,
                        self.CBQ_MOTION_STATUS          : self.cbq_motionStatus,
                        self.CBQ_WIFI_START             : self.cbq_wifiStart,
                        self.CBQ_WIFI_STOP              : self.cbq_wifiStop,
                        self.CBQ_WIFI_STATUS            : self.cbq_wifiStatus,                        
                        self.CBQ_SNAPSHOT               : self.cbq_snapshot,
                        self.CBQ_UPLOAD_FILE            : self.cbq_uploadVideo,
                        self.CBQ_SHUTDOWN               : self.cbq_shutdown,
                        self.CBQ_EMAIL_NOTIF            : self.cbq_emailNotif
                        }
  
        # Commands
        self.COMMANDS={
            '/start'          : self.cmd_help,          # Descripcion. Indicar tambien que por seguridad solo responde a comandos enviados desde el chat de grupo
            '/ayuda'          : self.cmd_help,
            '/movimiento'     : self.cmd_motion,        # iniciar, parar, pausar...
            '/wifi'           : self.cmd_wifi,          # iniciar/parar/status de la wifi El Cárabo
            '/foto'           : self.cmd_photo,         # Toma una instantanea            
            '/subir'          : self.cmd_upload_video,  # sube un video a google drive
            '/sensores'       : self.cmd_sensors,       # muestra el estado de los sensores            
            '/emails'         : self.cmd_notif_emails,  # activa/desactiva la modificacion por emails
            '/ssh'            : self.cmd_open_ssh,      # abre tunel ssh en Bacmine
            '/actualizar'     : self.cmd_update,        # actualiza el repositorio github !!!A VECES REQUIERE REINICIO DE TELEGRAM
            '/reiniciar'      : self.cmd_reboot,        # reinicia el sistema
            '/apagar'         : self.cmd_shutdown,
            '/shell'          : self.cmd_shell
        }
    
        self.message_loop(callback=self.handle, source=self._queue)
        t = threading.Thread(target=self.update_queue)
        t.daemon = True
        t.start()
  
  
  
    
    
    #############
    #  C H A T  #
    #############    
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        user_id = msg['from']['id']
        #print 'Normal message:\n%s', json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': '))
        
        # solo permite mensajes de texto y de usuarios NO baneados o admin
        if content_type == 'text' and user_id not in self.BANNED_USERS:
            if user_id == self.ADMIN_USER or user_id in self.ALLOWED_USERS:                
                cmd=self.getCommand(msg)
                if cmd in self.COMMANDS:
                    # solo permite comandos por mensaje privado o de admin
                    if user_id == self.ADMIN_USER or chat_id == self.CHAT_GROUP:
                        try:
	                        self.COMMANDS[cmd](msg) #TODO: Meter comandos en un thread para que no se bloquee el bot (comprobar concurrencia)

                        except:
                            print >>sys.stderr, u"[{}] {}: ERROR! Se ha producido un error inesperado al procesar el comando".format(datetime.datetime.now(), __file__)
                            traceback.print_exc()
                            self.sendMessage(chat_id, self.MSG_ERROR_CMD, reply_to_message_id=msg['message_id'])
                            
                    else:                
                        print >> sys.stderr, u"[{}] {}: WARNING! El comando no ha sido enviado al chat de grupo. Ignorando msg...".format(datetime.datetime.now(), __file__)
                        self.sendMessage(chat_id, self.MSG_BLOCKED_PRIVATE_CHAT.format(self.BOT_NAME))
                        
                # comprueba si es una respuesta
                elif 'reply_to_message' in msg:
                    print u"[{}] {}: Respuesta recibida... pero por ahora se ignora".format(datetime.datetime.now(), __file__)
                
                # comprueba si es una mencion            
                elif 'entities' in msg and msg['entities'][0]['type']=='mention':
                    print u"[{}] {}: Mencion recibida... pero por ahora se ignora".format(datetime.datetime.now(), __file__)                
                    self.sendMessage(chat_id, self.MSG_DONT_MENTION_ME)    #FIXME: poner frases aleatorias
                
                #No es un comando o respuesta reconocida               
                else:                
                    print >> sys.stderr, u"[{}] {}: ERROR! Comando o estructura del mensaje no reconocida".format(datetime.datetime.now(), __file__)
                    self.sendMessage(chat_id, self.MSG_DONT_UNDERSTAND, reply_to_message_id=msg['message_id'])
                    
            else:
                print u"[{}] {}: Se ha captura un mensaje de un nuevo usuario. Este usuario no podra ejecutar comandos hasta que este en la lista de autorizados".format(datetime.datetime.now(), __file__)
                self.ask_AddNewUser(msg)            

        else:
            print >>sys.stderr, u"[{}] {}: El mensaje no es de texto o proviene de un usuario bloqueado. Ignorando msg...".format(datetime.datetime.now(), __file__)
            

    
    
    #######################
    #  C A L L B A C K S  #
    #######################            
    def on_callback_query(self, msg):
        print u"[{}] {}: Callback recibido: {}".format(datetime.datetime.now(), __file__, msg['data'])        
        self.cancelMsgTimeout(*self.getMsgChatId(msg))        
        funct, arg = self.string2callback(msg['data'])
        funct(msg, *arg)    #TODO: en un futuro se puede lanzar un thread por callback, pero por ahora se queda así

    


    #############################
    #  I N L I N E   Q U E R Y  #
    #############################   
    def on_inline_query(self, msg):
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        #print 'Inline Query (queryId, fromId, query):' ,query_id, from_id, query_string

        if from_id in self.ALLOWED_USERS and from_id not in self.BANNED_USERS:
            print u"[{}] {}: Procesando peticion inline".format(datetime.datetime.now(), __file__)                
            self.sendChatAction(self.CHAT_GROUP, 'typing')
            
            query = 'select id,link,width,height from images where link is not NULL order by id desc limit 20'
            data = self.run_query(query)
            
            f=[]
            for d in data:
                f.append(InlineQueryResultPhoto(
                    id = d[0], 
                    photo_url = d[1], 
                    thumb_url = d[1], 
                    photo_width = d[2], 
                    photo_height = d[3] ))
                            
            self.answerInlineQuery(query_id, f)        
            
        else:
            print >>sys.stderr, u"[{}] {}: WARNING! Peticion inline proviene de un usuario NO autorizado. Ignorando msg...".format(datetime.datetime.now(), __file__)
            

    
    
    ################################
    #  I N L I N E    R E S U L T  #
    ################################    
    def on_chosen_inline_result(self, msg):
        #result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        #print 'Chosen Inline Result:\n%s', json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': '))        
        self.cbq_uploadVideo(None, msg['result_id'])






    ###########################################################################
    #                            C O M M A N D S  
    ###########################################################################  
    def cmd_help(self,msg):
        print u"[{}] {}: Enviando mensaje de ayuda".format(datetime.datetime.now(), __file__)
        self.sendMessage(self.CHAT_GROUP, self.MSG_CMD_HELP.format(self.BOT_NAME), parse_mode="Markdown")
  
    
    def cmd_motion(self,msg):
        self._motionDelay = TimeDelay()
            
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton( text=self.BUT_MOTION_START,  callback_data=self.callback2string( self.CBQ_MOTION_START ) )],
            [InlineKeyboardButton( text=self.BUT_MOTION_STOP,   callback_data=self.callback2string( self.CBQ_MOTION_STOP ) )],
            [InlineKeyboardButton( text=self.BUT_MOTION_PAUSE,  callback_data=self.callback2string( self.CBQ_MOTION_ASK_TIME, [self.MOTION_DAYS] ) )],
            [InlineKeyboardButton( text=self.BUT_MOTION_STATUS, callback_data=self.callback2string( self.CBQ_MOTION_STATUS ) )],
            [InlineKeyboardButton( text=self.BUT_CANCEL,        callback_data=self.callback2string(self.CBQ_FUNCTION_CANCEL) )],
        ])                
                        
        chat    = self.CHAT_GROUP if INLINE_KEYBOARDS_GROUP_ACTIVE else msg['from']['id']    
        m       = self.sendMessage(chat, self.MSG_CMD_MOTION, reply_markup=markup)
        self.addMsgTimeout(*self.getMsgChatId(m))
        

    def cmd_wifi(self,msg):            
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton( text=self.BUT_WIFI_START,  callback_data=self.callback2string( self.CBQ_WIFI_START ) )],
            [InlineKeyboardButton( text=self.BUT_WIFI_STOP,   callback_data=self.callback2string( self.CBQ_WIFI_STOP ) )],
            [InlineKeyboardButton( text=self.BUT_WIFI_STATUS, callback_data=self.callback2string( self.CBQ_WIFI_STATUS ) )],
            [InlineKeyboardButton( text=self.BUT_CANCEL,        callback_data=self.callback2string(self.CBQ_FUNCTION_CANCEL) )],
        ])                
                        
        chat    = self.CHAT_GROUP if INLINE_KEYBOARDS_GROUP_ACTIVE else msg['from']['id']    
        m       = self.sendMessage(chat, self.MSG_CMD_WIFI, reply_markup=markup)
        self.addMsgTimeout(*self.getMsgChatId(m))        
 
        
    def cmd_photo(self,msg):
        devices = os.environ['CAMERA_DEVICES'].split(",")
        
        if len(devices)==0:
            print >>sys.stderr, u"[{}] {}: ERROR! No existen dispositivos de camaras configurados".format(datetime.datetime.now(), __file__)            
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_NO_CAMERAS)
        
        elif len(devices)==1:
            self.cbq_snapshot(None, devices[0])

        else:
            buttons=[]
            for d in devices:
                d=d.strip()
                buttons.append([ InlineKeyboardButton( text=d, callback_data=self.callback2string(self.CBQ_SNAPSHOT, [d])) ])
                
            buttons.append([ InlineKeyboardButton( text=self.BUT_CANCEL, callback_data=self.callback2string(self.CBQ_FUNCTION_CANCEL) ) ])    
        
            markup  = InlineKeyboardMarkup(inline_keyboard=buttons)
            chat    = self.CHAT_GROUP if INLINE_KEYBOARDS_GROUP_ACTIVE else msg['from']['id']            
            m       = self.sendMessage(chat, self.MSG_SELECT_DEVICE, reply_markup=markup)
            self.addMsgTimeout(*self.getMsgChatId(m))            


    #FIXME: abrir el ssh puede tardar en algunas ocasiones. Hacer en thread independiente     
    def cmd_open_ssh(self, msg):
        try:            
            m = self._timers.pop(self.TIMER_SSH, None)
            if m:
                print u"[{}] {}: Cancelando timer ssh".format(datetime.datetime.now(), __file__)
                m.cancel()
            
            #cerramos puerto ssh si ya esta abierto para evitar problemas
            self.close_ssh()
            
            cmd="sshpass -e ssh -oStrictHostKeyChecking=no -p {port} -fCNR {tunelPort}:localhost:22 {user}@{server}".format(
                            port      = os.environ['SSH_REMOTE_PORT'],
                            tunelPort = os.environ['SSH_REMOTE_TUNEL_PORT'],
                            user      = os.environ['SSH_REMOTE_USER'],
                            server    = os.environ['SSH_REMOTE_SERVER'])    
            ret = proc.call(cmd,shell=True)
            
            if ret==0:
                print u"[{}] {}: Tunel ssh abierto".format(datetime.datetime.now(), __file__)
                self.sendMessage(self.CHAT_GROUP, self.MSG_SSH_OPENED.format(os.environ['SSH_REMOTE_SERVER'], 
                                                                            os.environ['SSH_REMOTE_TUNEL_PORT'], 
                                                                            os.environ['SSH_REMOTE_TIMEOUT']))
                                                
                self._timers[self.TIMER_SSH] = threading.Timer(int(os.environ['SSH_REMOTE_TIMEOUT']), self.close_ssh)
                self._timers[self.TIMER_SSH].start()
                
            else:
                print >>sys.stderr, u"[{}] {}: ERROR! Hubo un problema al abrir el puerto ssh (ret={})".format(datetime.datetime.now(), __file__, ret)                
                self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_SSH.format(ret))
            
        except Exception as e:
            print >>sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al abrir el tunel ssh:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()            
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e)))
        
        
                    
    def cmd_upload_video(self, msg, count=5, onlyUpdate=False):
        videos = self.run_query('select id,size from videos where uid is NULL or link is NULL order by id desc limit {}'.format(count))
                        
        if len(videos)==0:
            print u"[{}] {}: Todavia no hay eventos capturados".format(datetime.datetime.now(), __file__)            
            self.sendMessage(self.CHAT_GROUP, self.MSG_MOTION_NO_EVENTS)
        
        else:
            buttons=[]
            for v in videos:
                idd       = v[0]
                y,m,d,H,M = idd.split("_")[:5]
                size      = self.get_humanSize(v[1]) if v[1] else u'?'
                t         = u'{}/{}/{} {}:{} ({})'.format(y, m, d, H, M, size)
                
                buttons.append([ InlineKeyboardButton( text=t, callback_data=self.callback2string(self.CBQ_UPLOAD_FILE, [idd])) ])
                                
            buttons.append([ InlineKeyboardButton( text=u'Más antiguos', callback_data=self.callback2string(self.CBQ_UPLOAD_FILE, [self.GET_MORE, count])) ])
            buttons.append([ InlineKeyboardButton( text=self.BUT_CANCEL, callback_data=self.callback2string(self.CBQ_FUNCTION_CANCEL) ) ])
                      
            markup  = InlineKeyboardMarkup(inline_keyboard=buttons)
            
            if onlyUpdate:
                m = self.editMessageReplyMarkup(self.getMsgChatId(msg), markup)
                
            else:    
                chat = self.CHAT_GROUP if INLINE_KEYBOARDS_GROUP_ACTIVE else msg['from']['id']            
                m    = self.sendMessage(chat, self.MSG_CMD_UPLOAD.format(self.get_datosConsumidos(), os.environ['DATOS_MENSUALES']), reply_markup=markup)
            
            self.addMsgTimeout(*self.getMsgChatId(m))             
           
        
    def cmd_sensors(self,msg):
        print u"[{}] {}: Enviando informacion sobre los sensores".format(datetime.datetime.now(), __file__)
        self.sendChatAction(self.CHAT_GROUP, 'typing')
        query = "select * from sensors order by date desc limit 1"        
        date, cpu_temp, bmp180_temp, bmp180_press, dht22_temp, dht22_hr = self.run_query(query)[0]
        text = self.MSG_CMD_SENSORS.format(date.strftime("%Y/%m/%d"),		 
                                                                      date.strftime("%H:%M"), 
                                                                      cpu_temp,
                                                                      dht22_temp,
                                                                      bmp180_temp,  
                                                                      dht22_hr,
                                                                      bmp180_press)        
        
        self.sendMessage(self.CHAT_GROUP, text.replace('None', '? '), parse_mode="Markdown")
      
      
    def restart_telegram(self):
        with open(os.environ['TELEGRAM_RESTART_FILE'], 'w') as f:
            f.write("")     #touch file
            
        
    #FIXME: meter en un thread para no bloquear el bot
    def cmd_update(self,msg):
        self.sendChatAction(self.CHAT_GROUP, 'typing')
        try:
            print u"[{}] {}: Actualizando repositorio".format(datetime.datetime.now(), __file__)
            output = proc.check_output('cd {}; git pull'.format(os.environ['SVVPA_DIR']), shell=True)            
            self.sendMessage(self.CHAT_GROUP, self.MSG_CMD_UPDATE.format(output), parse_mode='Markdown')
            if "bin/_telegram_bot.py" in output:
                self.restart_telegram()
            
        except Exception as e:
            print >>sys.stderr, u"[{}] {}: ERROR! Se ha producido un error inesperado al actualizar el repositorio git:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e)))
        
        
 
        
    def cmd_reboot(self,msg):
        print u"[{}] {}: Reiniciando el sistema...".format(datetime.datetime.now(), __file__)        
        self.sendMessage(self.CHAT_GROUP, self.MSG_CMD_REBOOT)
        t = threading.Timer(20, self.reboot)
        t.setDaemon(True)
        t.start()
        

  

    def cmd_shutdown(self,msg):            
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton( text=self.BUT_SHUTDOWN_NO,       callback_data=self.callback2string( self.CBQ_FUNCTION_CANCEL ) )],
            [InlineKeyboardButton( text=self.BUT_SHUTDOWN_NOTSURE,  callback_data=self.callback2string( self.CBQ_FUNCTION_CANCEL ) )],
            [InlineKeyboardButton( text=self.BUT_SHUTDOWN_MAYBE,    callback_data=self.callback2string( self.CBQ_FUNCTION_CANCEL ) )],
            [InlineKeyboardButton( text=self.BUT_SHUTDOWN_YES,      callback_data=self.callback2string( self.CBQ_SHUTDOWN ) )],
            [InlineKeyboardButton( text=self.BUT_CANCEL,            callback_data=self.callback2string( self.CBQ_FUNCTION_CANCEL) )],
        ])                
                        
        chat    = self.CHAT_GROUP if INLINE_KEYBOARDS_GROUP_ACTIVE else msg['from']['id']
        m       = self.sendMessage(chat, self.MSG_CMD_SHUTDOWN, reply_markup=markup, parse_mode='Markdown')
        self.addMsgTimeout(*self.getMsgChatId(m))

        
    def cmd_notif_emails(self, msg):
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton( text=self.BUT_NOTIF_ENABLE,  callback_data=self.callback2string( self.CBQ_EMAIL_NOTIF, [self.EMAIL_NOTIF_ON] ) )],
            [InlineKeyboardButton( text=self.BUT_NOTIF_DISABLE, callback_data=self.callback2string( self.CBQ_EMAIL_NOTIF, [self.EMAIL_NOTIF_OFF] ) )],
            [InlineKeyboardButton( text=self.BUT_CANCEL,        callback_data=self.callback2string( self.CBQ_FUNCTION_CANCEL) )],
        ])                
                        
        chat    = self.CHAT_GROUP if INLINE_KEYBOARDS_GROUP_ACTIVE else msg['from']['id']    
        m       = self.sendMessage(chat, self.MSG_CMD_EMAIL_NOTIF.format(u"activado" if self.isEmailNotif() else u"desactivado"), reply_markup=markup)
        self.addMsgTimeout(*self.getMsgChatId(m))

     

        
    def cmd_shell(self, msg):        
        t = threading.Timer(3, self.exec_cmd, args=(msg,))
        t.setDaemon(True)
        t.start()        
        


    def exec_cmd(self, msg):
        cmd=re.sub("/[a-zA-Z]+ ", "", msg['text']).strip()
        
        if not cmd:
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_NO_SHELL_CMD)
           
        else:        
            try:            
                p = proc.Popen(cmd, shell=True, stdout=proc.PIPE)
                p.wait()            
                self.sendMessage(msg['chat']['id'], u'''{}\nRET:{}'''.format("".join(p.stdout), p.returncode))                
                                 
            except:
                print >>sys.stderr, u"[{}] {}: ERROR! Se produjo un error inesperado al ejecutar el comando bash:".format(datetime.datetime.now(), __file__)
                traceback.print_exc()            
                self.sendMessage(msg['chat']['id'], self.MSG_ERROR_SHELL_CMD)       
 
     
     
     
     
    ###########################################################################
    #                          C A L L B A C K S  
    ###########################################################################          
    def cbq_AddUser(self, msg, arg):
        user_id         = int(arg)
        from_name       = msg['from']['first_name']
        tk              = msg['message']['text'].split(" ")
        user_name       = tk[0]
        user_lastname   = tk[1]
        
        print u"[{}] {}: Usuario {} {} ({}) se ha incluido en la lista de usuarios con autorizacion para enviar comandos por telegram".format(datetime.datetime.now(), __file__, user_name, user_lastname, user_id)
        
        #añadimos usuario en la ejecucion actual
        self.ALLOWED_USERS.append( user_id )
        
        try:
            #Añadimos usuario en el fichero de configuracion
            cmd     = 'grep TELEGRAM_ALLOWED_USERS {}'.format(self.FILE_CONSTANTS)
            p       = proc.check_output(cmd, shell=True).strip()
            users   = set(re.findall('[0-9]+', p))
            users.add(str(user_id))
            
            cmd     = 'sed -i -r \'s/TELEGRAM_ALLOWED_USERS="([0-9,]+)"/TELEGRAM_ALLOWED_USERS="{}"/g\' {}'.format(",".join(users), self.FILE_CONSTANTS)
            proc.call(cmd, shell=True) 
                        
            text = self.MSG_USER_ADDED.format(from_name, user_name, user_lastname, user_name)        
            self.editMessageText( self.getMsgChatId(msg), text)
            
            if not INLINE_KEYBOARDS_GROUP_ACTIVE:
                self.sendMessage(self.CHAT_GROUP, text)
                 
        except:
            print >>sys.stderr, u"[{}] {}: ERROR! Se produjo un error inesperado al incluir un nuevo usuario en la lista de usuarios autorizados:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()            
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_ADDING_USER) 
        
      
      
    def cbq_cancel(self, msg):
        print u"[{}] {}: Comando cancelado".format(datetime.datetime.now(), __file__)
        self.deleteMsg(*self.getMsgChatId(msg))

      
    
    def cbq_MotionSetTime(self, msg, unit, num):        
        if not self._motionDelay:
            self._motionDelay = TimeDelay()
        
        if unit == self.MOTION_DAYS:
            print u"[{}] {}: Configurando motion_delay_days: {}".format(datetime.datetime.now(), __file__, num)
            self._motionDelay.setDays(num)                
        elif unit == self.MOTION_HOURS:
            print u"[{}] {}: Configurando motion_delay_hours: {}".format(datetime.datetime.now(), __file__, num)
            self._motionDelay.setHours(num)            
        elif unit == self.MOTION_MINUTES:
            print u"[{}] {}: Configurando motion_delay_minutes: {}".format(datetime.datetime.now(), __file__, num)
            self._motionDelay.setMinutes(num)            
        elif unit == self.MOTION_SECONDS:
            print u"[{}] {}: Configurando motion_delay_seconds: {}".format(datetime.datetime.now(), __file__, num)
            self._motionDelay.setSeconds(num)
        
        if not self._motionDelay.isDaysSetted():
            self.cbq_MotionAskTime(msg, self.MOTION_DAYS)        
        elif not self._motionDelay.isHoursSetted():
            self.cbq_MotionAskTime(msg, self.MOTION_HOURS)        
        #elif not self._motionDelay.isMinutesSetted():
        #    self.cbq_MotionAskTime(msg, self.MOTION_MINUTES)        
        #elif not self._motionDelay.isSecondsSetted():
        #    self.cbq_MotionAskTime(msg, self.MOTION_SECONDS)
            
        else:
            if self._motionDelay.getTime()==0:
                #huevo de pascua                
                self.editMessageText(self.getMsgChatId(msg), self.MSG_ERROR_FAKE)
                return
               
            self.cbq_motionStop()
            
            text = self.MSG_CMD_MOTION_PAUSE.format(self._motionDelay.toString())
            self.editMessageText(self.getMsgChatId(msg), text)
            
            if not INLINE_KEYBOARDS_GROUP_ACTIVE:
                self.sendMessage(self.CHAT_GROUP, text)
            
            m = self._timers.pop(self.TIMER_MOTION, None)
            if m:
                print u"[{}] {}: Cancelando timer motion".format(datetime.datetime.now(), __file__)
                m.cancel()
                                            
            self._timers[self.TIMER_MOTION] = threading.Timer(self._motionDelay.getTime(), self.cbq_motionStart)
            self._timers[self.TIMER_MOTION].start()
            
            
            
    def cbq_MotionAskTime(self, msg, unit):
        units = []
                             
        if unit == self.MOTION_DAYS:
            for i in (0,1,2,3,4,5,6,7,14,21):
                units.append(unicode(i))
            text = u'dias'
        
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
        
        #chat    = self.CHAT_GROUP if INLINE_KEYBOARDS_GROUP_ACTIVE else msg['from']['id']
        t       = u"\n(Actualmente: " + self._motionDelay.toString() + u")" if self._motionDelay.getTime()>0 else ""
        m       = self.editMessageText( self.getMsgChatId(msg), self.MSG_CMD_MOTION_TIME_SET.format(text.upper(), t), reply_markup=markup)
        self.addMsgTimeout(*self.getMsgChatId(m))

      
      
    def cbq_motionStart(self, msg=None):
        try:
            m = self._timers.pop(self.TIMER_MOTION, None)
            if m:
                print u"[{}] {}: Cancelando timer motion".format(datetime.datetime.now(), __file__)
                m.cancel()

            print u"[{}] {}: Reiniciando servicio motion".format(datetime.datetime.now(), __file__)
            proc.call('sudo service motion restart', shell=True)
            if os.path.exists(os.environ['FILE_MOTION_OFF']):
	        os.remove(os.environ['FILE_MOTION_OFF'])
            
            
            if msg:
                self.editMessageText(self.getMsgChatId(msg), self.MSG_MOTION_START)
            
            if not INLINE_KEYBOARDS_GROUP_ACTIVE:        
                self.sendMessage(self.CHAT_GROUP, self.MSG_MOTION_START)            
        
        except Exception as e:
            print >> sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al trata de reiniciar motion:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e)))
        
                
        
    def cbq_motionStop(self, msg=None):            
        try:
            m = self._timers.pop(self.TIMER_MOTION, None)
            if m:
                print u"[{}] {}: Cancelando timer motion".format(datetime.datetime.now(), __file__)
                m.cancel()

            print u"[{}] {}: Parando servicio motion".format(datetime.datetime.now(), __file__)
            proc.call('sudo service motion stop 2>&1 >/dev/null', shell=True)
            with open(os.environ['FILE_MOTION_OFF'], 'w') as f:
                f.write("")     #touch file	
            
            if msg:
                self.editMessageText(self.getMsgChatId(msg), self.MSG_CMD_MOTION_STOP)
            
            if not INLINE_KEYBOARDS_GROUP_ACTIVE:
                self.sendMessage(self.CHAT_GROUP, self.MSG_CMD_MOTION_STOP)
            
        except Exception as e:
            print >>sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al detener el servicio motion:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e)))
            
         
        
    def cbq_motionStatus(self, msg):
        try:
            if self.isMotionEnabled():                
                self.editMessageText(self.getMsgChatId(msg),  self.MSG_CMD_MOTION_ENABLED)
            
            else:                
                self.editMessageText(self.getMsgChatId(msg),  self.MSG_CMD_MOTION_DISABLED)
            
        except Exception as e:         
            print >> sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al comprobar el estado del servicio motion:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e)))
        

 
    def cbq_wifiStart(self, msg=None):
        try:
            m = self._timers.pop(self.TIMER_WIFI, None)
            if m:
                print u"[{}] {}: Cancelando timer wifi".format(datetime.datetime.now(), __file__)
                m.cancel()

            print u"[{}] {}: Iniciando wifi".format(datetime.datetime.now(), __file__)
            proc.call('ssh root@192.168.1.1 "manageWifi start"', shell=True)
            
            if msg:
                self.editMessageText(self.getMsgChatId(msg), self.MSG_CMD_WIFI_START)
            
            if not INLINE_KEYBOARDS_GROUP_ACTIVE:        
                self.sendMessage(self.CHAT_GROUP, self.MSG_CMD_WIFI_START)            
        
        except Exception as e:
            print >> sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al iniciar la wifi:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e)))
        
                
        
    def cbq_wifiStop(self, msg=None):            
        try:
            m = self._timers.pop(self.TIMER_WIFI, None)
            if m:
                print u"[{}] {}: Cancelando timer wifi".format(datetime.datetime.now(), __file__)
                m.cancel()

            print u"[{}] {}: Desabilitando la wifi".format(datetime.datetime.now(), __file__)
            proc.call('ssh root@192.168.1.1 "manageWifi stop"', shell=True)
            
            if msg:
                self.editMessageText(self.getMsgChatId(msg), self.MSG_CMD_WIFI_STOP)
            
            if not INLINE_KEYBOARDS_GROUP_ACTIVE:
                self.sendMessage(self.CHAT_GROUP, self.MSG_CMD_WIFI_STOP)
            
        except Exception as e:
            print >>sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al detener la wifi:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e)))
            
         
        
    def cbq_wifiStatus(self, msg):
        try:
            if self.isWifiEnabled():                
                self.editMessageText(self.getMsgChatId(msg),  self.MSG_CMD_WIFI_ENABLED)
            
            else:                
                self.editMessageText(self.getMsgChatId(msg),  self.MSG_CMD_WIFI_DISABLED)
            
        except Exception as e:         
            print >> sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al comprobar el estado de la wifi:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e))) 
 

        
        
    def cbq_BlockUserOneTime(self, msg, arg):
        user_id         = int(arg)
        tk              = msg['message']['text'].split(" ")
        user_name       = tk[0]
        user_lastname   = tk[1]
            
        print u"[{}] {}: Bloqueando usuario {} {} ({}) durante esta ejecucion.".format(datetime.datetime.now(), __file__, user_name, user_lastname, user_id)
                
        self.BANNED_USERS.append(user_id)
                
        text    = self.MSG_BLOCKED_USER.format(user_name, user_lastname)        
        self.editMessageText( self.getMsgChatId(msg), text)
        
        if not INLINE_KEYBOARDS_GROUP_ACTIVE:
            self.sendMessage(self.CHAT_GROUP, text)

        
        
    def cbq_BanUser(self, msg, arg): 
        user_id         = int(arg)
        from_name       = msg['from']['first_name']
        tk              = msg['message']['text'].split(" ")
        user_name       = tk[0]
        user_lastname   = tk[1]
                
        print u"[{}] {}: Bloqueando al usuario {} {} ({}) permanentemente".format(datetime.datetime.now(), __file__, user_name, user_lastname, user_id)
                
        #añadimos usuario en la ejecucion actual
        self.BANNED_USERS.append( user_id )
        
        try:
            #Añadimos usuario en el fichero de configuracion
            cmd     = 'grep TELEGRAM_BANNED_USERS {}'.format(self.FILE_CONSTANTS)
            users   = set(re.findall('[0-9]+', proc.check_output(cmd, shell=True).strip()))
            users.add(str(user_id))
            
            cmd     = 'sed -i -r \'s/TELEGRAM_BANNED_USERS="([0-9,]*)"/TELEGRAM_BANNED_USERS="{}"/g\' {}'.format(",".join(users), self.FILE_CONSTANTS)
            proc.call(cmd, shell=True) 
                        
            text    = self.MSG_BANN_USER.format(from_name, user_name, user_lastname, user_name)        
            self.editMessageText( self.getMsgChatId(msg), text)
                        
            if not INLINE_KEYBOARDS_GROUP_ACTIVE:
                self.sendMessage(self.CHAT_GROUP, text)
                 
        except Exception as e:
            print >>sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al bloquear permanentemente un usuario".format(datetime.datetime.now(), __file__)
            traceback.print_exc()           
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e))) 
      
   
      
    def cbq_snapshot(self, msg, device):                
        if msg:            
            self.editMessageText(self.getMsgChatId(msg), self.MSG_CMD_SNAPSHOT)
                        
        if self.isMotionEnabled():
            fileout = os.environ['MOTION_DIR'] + '.snapshot-' + str(int(device[-1])+1) + '.' + os.environ['MOTION_IMAGE_EXT']
            print u"[{}] {}: Capturando foto de motion_snapshots".format(datetime.datetime.now(), __file__)
            
        else:
            print u"[{}] {}: Capturando foto directamente del dispositivo {}".format(datetime.datetime.now(), __file__, device)
            fileout = '/tmp/snapshot.jpg'
            
            try:
                proc.check_call(os.environ['FSWEBCAM_BIN'] + " --config " + os.environ['FSWEBCAM_CONFIG'] + " --device " + device + " " + fileout, shell=True)
                
            except Exception as e:
                print >> sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al capturar la imagen:".format(datetime.datetime.now(), __file__)
                traceback.print_exc()
                self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e)))                
                 
        t = threading.Thread(target=self.send_snapshot, args=(fileout,))
        t.daemon = True
        t.start()
                       
           
      
    def cbq_uploadVideo(self, msg, eventId, count=5):
        if eventId in self.GET_MORE:
            self.cmd_upload_video(msg, '%s' % (int(count)+10), True )
            
        else:        
            f = os.environ['MOTION_DIR'] + eventId + '.' + os.environ['MOTION_VIDEO_EXT']
            
            t = threading.Thread(target=self.upload_video, args=(f,msg,))
            t.daemon = True
            t.start()
                      




    def cbq_shutdown(self, msg):
        print u"[{}] {}: Apagando el sistema".format(datetime.datetime.now(), __file__)        
        self.editMessageText(self.getMsgChatId(msg), self.MSG_SHUTTING_DOWN)
        if not INLINE_KEYBOARDS_GROUP_ACTIVE:
            self.sendMessage(self.CHAT_GROUP, self.MSG_SHUTTING_DOWN)
                    
        t = threading.Timer(20, self.shutdown)
        t.setDaemon(True)
        t.start()
         
        
        
  
        
        
    def cbq_emailNotif(self, msg, state):            
        try:
            print u"[{}] {}: {}ctivando las notificaciones por email".format(datetime.datetime.now(), __file__, u"A" if state==self.EMAIL_NOTIF_ON else u"Desa")
            cmd = u"sed -i -r 's/export EMAIL_NOTIF=\"([a-zA-Z]*)\"/export EMAIL_NOTIF=\"{}\"/g' {}".format(state, self.FILE_CONSTANTS)
            proc.check_call(cmd, shell=True)
            
            if state==self.EMAIL_NOTIF_ON:                
                text = self.MSG_CMD_EMAIL_NOTIF_ENABLED
                
            else:                
                text = self.MSG_CMD_EMAIL_NOTIF_DISABLED
            
            self.editMessageText(self.getMsgChatId(msg), text)
            
            if not INLINE_KEYBOARDS_GROUP_ACTIVE:
                self.sendMessage(self.CHAT_GROUP, text)            
                
            
        except Exception as e:
            print >> sys.stderr, u"[{}] {}: ERROR! Hubo un problema inesperado al modificar la notificacion por email:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
            self.editMessageText(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e)))







    ###########################################################################
    #                           O T H E R S
    ###########################################################################   
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
        
        chat    = self.ADMIN_USER   #self.CHAT_GROUP if INLINE_KEYBOARDS_GROUP_ACTIVE else self.ADMIN_USER    
        m       = self.sendMessage(chat, self.MSG_NEW_USER.format(name, lastname, self.BOT_NAME, id), reply_markup=markup)
        self.addMsgTimeout(*self.getMsgChatId(m))

            
       
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
            regex = re.compile('/[a-zA-Z0-9_]+')
            r = regex.findall(msg['text'])
            if r:
                print u"[{}] {}: Comando {} recibido".format(datetime.datetime.now(), __file__, r[0])
                return r[0]
            
        print >> sys.stderr, u"[{}] {}: ERROR! Comando erroneo".format(datetime.datetime.now(), __file__)

    
    
    def deleteMsg(self, chat_id, msg_id):
        print u"[{}] {}: Borrando mensaje {} {}".format(datetime.datetime.now(), __file__, chat_id, msg_id)
        self.cancelMsgTimeout(chat_id, msg_id)
        self.editMessageText( (chat_id, msg_id), u'\U0001f914')

    
    
    def addMsgTimeout(self, chat_id, msg_id):
        print u"[{}] {}: Nuevo msg_timeout {} {}".format(datetime.datetime.now(), __file__, chat_id, msg_id)
        self._timers[chat_id, msg_id] = threading.Timer(self.MSG_TIMEOUT, self.deleteMsg, [chat_id, msg_id])        
        self._timers[chat_id, msg_id].start()        

           
           
    def cancelMsgTimeout(self, chat_id, msg_id):
        print u"[{}] {}: Cancelando msg_timeout {} {}".format(datetime.datetime.now(), __file__, chat_id, msg_id)
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

    
    
    def isMotionEnabled(self):
        try:
            if proc.call('sudo service motion status 2>&1 >/dev/null', shell=True) == 0:
            #if proc.call('ps aux|egrep "\bmotion\b"|grep -v grep', shell=True) == 0:
                print u"[{}] {}: Servicio MOTION esta activo".format(datetime.datetime.now(), __file__)
                return True
        
        except:
            print >> sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al comprobar el estado de motion:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
        
        print u"[{}] {}: Servicio motion esta inactivo".format(datetime.datetime.now(), __file__)



    def isWifiEnabled(self):
        try:
            o = proc.check_output('ssh root@192.168.1.1 "manageWifi status"', shell=True)
            if o.strip() in "enabled":
                print u"[{}] {}: wifi activa".format(datetime.datetime.now(), __file__)
                return True
        
        except:
            print >> sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al comprobar el estado de la wifi:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
        
        print u"[{}] {}: wifi inactiva".format(datetime.datetime.now(), __file__)

    
    
    def close_ssh(self):
        try:            
            o = proc.check_output('ps aux', shell=True)
            for l in o.splitlines():
                if ('ssh' and os.environ['SSH_REMOTE_SERVER'] and 'localhost') in l:
                    pid = int(l.split()[1])
                    print u"[{}] {}: Cerrando servicio ssh".format(datetime.datetime.now(), __file__)
                    os.kill(pid, signal.SIGKILL)
                    break
        
        except:
            print >> sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al cerrar el servicio ssh:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()



    def upload_video(self, filePath, msg=None):
        print u"[{}] {}: Subiendo archivo a google drive ({})".format(datetime.datetime.now(), __file__, filePath)
        
        if msg:        
            self.editMessageText(self.getMsgChatId(msg), u'Subiendo archivo {}...'.format(os.path.basename(filePath)))
            
        else:
            msg = self.sendMessage(self.CHAT_GROUP, u'Subiendo archivo {}...'.format(os.path.basename(filePath)))
        
        try:            
            self.sendChatAction(self.CHAT_GROUP, 'upload_video')
            fileuploader(filePath)   
            
            query = "select link from videos where id like '{}'".format(os.path.basename(filePath)[:-4])
            data  = self.run_query(query)
            
            if data:
                text = self.MSG_CMD_UPLOAD_DONE.format(os.path.basename(filePath), data[0][0])            
                self.editMessageText(self.getMsgChatId(msg), text, parse_mode='Markdown')
                
                if not INLINE_KEYBOARDS_GROUP_ACTIVE:
                    self.sendMessage(self.CHAT_GROUP, text, parse_mode='Markdown')
                
            else:
                print >> sys.stderr, u"[{}] {}: ERROR! No se ha podido subir el archivo {} a google drive. Se han agotado los intentos".format(datetime.datetime.now(), __file__, filePath)
                self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UPLOAD_MAX_TRIES.format(os.path.basename(filePath)))
                            
        except Exception as e:
            print >> sys.stderr, u"[{}] {}: ERROR! Se produjo un error inesperado al subir el video a google drive:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e)))
            
    
    
    def send_snapshot(self, filePath):
        if os.path.isfile(filePath):
            try:
                print u"[{}] {}: Enviando snapshot".format(datetime.datetime.now(), __file__)
                self.sendChatAction(self.CHAT_GROUP, 'upload_photo')
                fd = open(filePath, 'rb')
                self.sendPhoto(self.CHAT_GROUP, fd, datetime.datetime.fromtimestamp(os.path.getctime(filePath)).strftime("%Y/%m/%d %H:%M:%S"))
                fd.close()
                
            except Exception as e:
                print >> sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al enviar la foto:".format(datetime.datetime.now(), __file__)
                traceback.print_exc()
                if fd:
                    fd.close()
                self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e)))
            
        else:
            print >> sys.stderr, u"ERROR! No existe el archivo {}".format(filePath)
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(u'No existe el archivo ' + filePath))
            
            

    
    def run_query(self, query=''): 
        datos = ['localhost', os.environ['MYSQL_USER'], os.environ['MYSQL_PASS'], os.environ['MYSQL_DB']] 
        
        conn = MySQLdb.connect(*datos) # Conectar a la base de datos 
        cursor = conn.cursor()         # Crear un cursor 
        cursor.execute(query)          # Ejecutar una consulta 
        
        if query.upper().startswith('SELECT'): 
            data = cursor.fetchall()   # Traer los resultados de un select 
        else: 
            conn.commit()              # Hacer efectiva la escritura de datos 
            data = None 
        
        cursor.close()                 # Cerrar el cursor 
        conn.close()                   # Cerrar la conexion 
        
        return data            
            
        
        
    def isEmailNotif(self):
        try:
            output = proc.check_output(u'egrep EMAIL_NOTIF {}'.format(self.FILE_CONSTANTS), shell=True)
            f = re.findall('"([a-zA-Z]+)"', output)
            
            if len(f)>0 and f[0] == self.EMAIL_NOTIF_ON:
                print u"[{}] {}: La notificacion por email esta activada".format(datetime.datetime.now(), __file__)
                return True
        
        except:
            traceback.print_exc()
        
        print u"[{}] {}: La notificacion por email esta desactivada".format(datetime.datetime.now(), __file__)
        


    def get_datosConsumidos(self):
        try:
            cmd = "sudo " + os.environ['BIN_DIR'] + "_getInternetUsage.sh"     
            b = proc.check_output(cmd, shell=True).strip()
            return u'{}'.format(self.get_humanSize(float(b)))
        
        except:
            print >> sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado calcular los megas consumidos:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
            
        return u"?"


      
        
    def reboot(self):        
        try:
            proc.check_call('sudo /sbin/shutdown -r now', shell=True)
            
        except Exception as e:
            print >>sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al intentar reiniciar el sistema:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e)))




    def shutdown(self):
        try:
            proc.check_call('sudo /sbin/shutdown -h now', shell=True)
            
        except Exception as e:
            print >> sys.stderr, u"[{}] {}: ERROR! Hubo un problema inesperado al tratar de apagar el sistema:".format(datetime.datetime.now(), __file__)
            traceback.print_exc()
            self.sendMessage(self.CHAT_GROUP, self.MSG_ERROR_UNEXPECTED.format(repr(e)))
   
    

 
    def get_humanSize(self, mBytes):
        if mBytes < self.SIZE_KB:
            return u'{0}{1}'.format(mBytes,'B')
        
        elif self.SIZE_KB <= mBytes < self.SIZE_MB:
            return u'{0:.2f}KB'.format(mBytes/self.SIZE_KB)
        
        elif self.SIZE_MB <= mBytes < self.SIZE_GB:
            return u'{0:.2f}MB'.format(mBytes/self.SIZE_MB)
        
        elif self.SIZE_GB <= mBytes < self.SIZE_TB:
            return u'{0:.2f}GB'.format(mBytes/self.SIZE_GB)
        
        else: 
            return u'{0:.2f}TB'.format(mBytes/self.SIZE_TB)
            
    
    
    
    

        
class TimeDelay:
    """ Test """
    labels = {86400.0 : (u"dias",u"dia"), 3600.0 : (u"horas",u"hora"), 60.0 : (u"minutos",u"minuto"), 1.0 : (u"segundos",u"segundo")}
    
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

        return (resp[0] if len(resp)==1 else u", ".join(resp[:-1]) + u' y ' + resp[-1])

        
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
      
         

def main():
    TOKEN = os.environ['TELEGRAM_TOKEN']
    bot = Telegram_bot(TOKEN)
    #bot.message_loop({'chat': bot.on_chat_message, 'callback_query': bot.on_callback_query, 'inline_query': bot.on_inline_query, 'chosen_inline_result': bot.on_chosen_inline_result}, relax=1, timeout=60)
    #bot.message_loop(relax=5, timeout=120)    
    #bot.message_loop(relax=int(os.environ['TELEGRAM_UPDATE_TIME']), timeout=240) 
	
    # Keep the program running.
    while 1:
        time.sleep(10)
    
         
         
if __name__ == "__main__":
    sys.exit(main())

     
        
        
        
        
        
        
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
'''
