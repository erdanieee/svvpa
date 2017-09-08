# encoding: utf-8

#from __future__ import print_function
import os, sys, traceback
import random
import telepot
import datetime
import gmail_sender as gsender
import subprocess as proc
import re
import time
from _google_drive_uploader import main as fileuploader
import urllib
import MySQLdb

SIZE_KiB = 1024.0
SIZE_MiB = 1048576.0 
SIZE_GiB = 1073741824.0 
SIZE_TiB = 1099511627776.0 

EMAIL_STARTUP_SUBJECT=u'SVVPA - Inicio del sistema'
EMAIL_STARTUP_BODY=u'El sistema SVVPA se acaba de iniciar'
TLG_STARTUP=u'El sistema SVVPA se esta iniciando \U0001f440'

EMAIL_SHUTDOWN_SUBJECT=u'SVVPA - Apagado del sistema'
EMAIL_SHUTDOWN_BODY=u'El sistema SVVPA se está apagando'
TLG_SHUTDOWN=u'El sistema SVVPA se está apagando \U0001f634'

EMAIL_MOTION_SUBJECT=u'SVVPA - Movimiento detectado'
EMAIL_MOTION_BODY=u'''\
<html>
    <head></head>
    <body>
        <h3>Movimiento detectado</h3>
        <p>S.V.V.P.A. 2.0 ha detectado un nuevo movimiento en E.C. <b>{datetime}</b>. \
Adjunto a este mensaje se incluye el fotograma mas representativo.</p>
        <p>Si el video es interesante y deseas guardarlo en Google Drive, haz \
<a href="http://{dom}.duckdns.org:{port}/uploadVideo.php?id={id}">click aqui</a>. \
Al abrir esa pagina en un navegador, SVVPA iniciara la subida del vídeo y \
mostrara una web con el progreso. <b>No</b> es necesario dejar la pagina abierta \
hasta que termine; puedes cerrarla, cerrar el navegador o incluso apagar tu \
ordenador sin que interfiera el proceso. Recuerda que, en funcion del tamaño del \
vídeo, este proceso puede tardar varios minutos.</p>
        <p>Puedes ver las capturas guardadas anteriormente en <a href="\
https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing">\
este enlace</a>.</p>
        <p>Para acceder <b>de forma remota</b> a SVVPA visita <a href="\
http://{dom}.duckdns.org:{port}">http://{dom}.duckdns.org:{port}</a> o <a href="\
http://{ip}:{port}">http://{ip}:{port}</a>. El consumo de datos hasta ahora ha \
sido de {datos}Mb de los {datosMensuales}Mb mensuales que incluye la tarifa.         
    </body>
</html>
            ''' if bool(int(os.environ['REMOTE_ACCESS'])) else u'''\
<html>
    <head></head>
    <body>
        <h3>Movimiento detectado</h3>
        <p>S.V.V.P.A. 2.0 ha detectado un nuevo movimiento en E.C. \
<b>{datetime}</b>. Adjunto a este mensaje se incluye el fotograma mas representativo.</p>
        <p>Si piensas que el vídeo puede ser interesante (Duracion:{duration}, \
tamaño:{size}) y deseas subirlo a Google Drive, haz \
<a href="mailto:{email}?subject=CMD_SVVPA GUARDAR_EN_GOOGLE_DRIVE {id}">click aqui</a> \
para enviar enviar un email con el comando correspondiente. Te recordamos que \
el consumo de datos hasta el momento ha sido de {datos}Mb de los \
{datosMensuales}Mb mensuales que incluye la tarifa.</p>
        <p>Puedes ver las capturas guardadas anteriormente en <a href="\
https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing">este enlace</a>.</p>
    </body>
</html>
'''
TLG_MOTION=u'\U0001f440 Nuevo movimiento detectado (*{}*) \U0001f440\n\nLa [imagen más \
representativa]({}) ha sido subida automáticamente a google drive.\n\nPara subir \
también el video utiliza el comando /subir'

EMAIL_CAMERA_FAILURE_SUBJECT=u'SVVPA - Error en la cámara'
EMAIL_CAMERA_FAILURE_BODY=u'''\
<html>
  <head></head>
  <body>
    <h3>No se puede acceder a la cámara</h3>
    <p>S.V.V.P.A. ha detectado que alguna de las cámaras ha dejado de funcionar \
correctamente. Si te encuentras en E.C., trata de acceder al modo \
<i>vista en Directo</i> para descartar un problema transitorio. Si no te \
encuentras en E.C., puedes probar a reiniciar SVVPA para ver si se soluciona el problema.</p>

<p>Si aun asi no funciona, avisa a Er Danié para que trate de indagar en el problema.</p> 
  </body>
</html>
'''
TLG_CAMERA_FAILURE=u'\u203c S.V.V.P.A. ha detectado un error en alguna de las cámaras. \
Si te encuentras en E.C., trata de acceder al modo vista en Directo para \
descartar un problema transitorio. Si no te encuentras en E.C., puedes probar a \
reiniciar SVVPA para ver si se soluciona el problema.\u203c'


EMAIL_TELEGRAM_BOT_SUBJECT_ON=u'SVVPA - Bot telegram activado'
EMAIL_TELEGRAM_BOT_SUBJECT_OFF=u'SVVPA - Bot telegram desactivado'
EMAIL_TELEGRAM_BOT_BODY_ON=u'El bot de telegram se ha activado correctamente. A partir de ahora se podrán enviar comandos a SVVPA mediante el chat de grupo de telegram.'
EMAIL_TELEGRAM_BOT_BODY_OFF=u'Se ha detenido el bot de telegram. A partir de ahora no se podrán enviar comandos a por telegram, aunque sí se recibirán notificaciones por este canal.'
TLG_TELEGRAM_BOT_ON="El servicio bot telegram se acaba de activar"
TLG_TELEGRAM_BOT_OFF="El servicio bot telegram se ha desactivado"

           


def run_query(query=''): 
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
        



def get_ip():
    url = "http://ipecho.net/plain"
    fp = urllib.urlopen(url)
    try:
        data = fp.read()
        
    finally:
        traceback.print_exc()
        fp.close()
    return data



def get_datos():
    ret = os.popen(os.environ['BIN_DIR'] + "_getInternetUsage.sh").readlines()
    return ret[0].strip()



def get_duration(id):
    file = os.environ['MOTION_DIR'] + id + '.' + os.environ['MOTION_VIDEO_EXT']     
    try:
        ret = os.popen(os.environ['FFMPEG_BIN'] + ' -i ' + file + ' 2>&1|egrep -o "Duration: [0-9:]+"|egrep -o "[0-9]{2}:[0-9]{2}$"').readlines()
        return ret[0].strip()
    
    except Exception as e:
        print >> sys.stderr, u'[{}] {}: ERROR! No se ha podido determinar la duracion del video:'.format(datetime.datetime.now(), __file__)
        traceback.print_exc()
        return u"?"



def get_size(id):
    file = os.environ['MOTION_DIR'] + id + '.' + os.environ['MOTION_VIDEO_EXT']
    try:
        'Return the file size as a human friendly KB, MB, GB, or TB string'
        B = float(os.path.getsize(file))
        
        if B < SIZE_KiB:
           return u'{0} {1}'.format(B,'Bytes' if B > 1 else 'Byte')
        elif SIZE_KiB <= B < SIZE_MiB:
           return u'{0:.2f} KB'.format(B/SIZE_KiB)
        elif SIZE_MiB <= B < SIZE_GiB:
           return u'{0:.2f} MB'.format(B/SIZE_MiB)
        elif SIZE_GiB <= B < SIZE_TiB:
           return u'{0:.2f} GB'.format(B/SIZE_GiB)
        elif SIZE_TiB <= B:
           return u'{0:.2f} TB'.format(B/SIZE_TiB)
       
    except Exception as e:
        print >> sys.stderr, u'[{}] {}: ERROR! No se ha podido determinar el size del video:'.format(datetime.datetime.now(), __file__)
        traceback.print_exc()
        return u"?"


   


def get_humanSize(bytes):
    if bytes < SIZE_KiB:
        return u'{0} {1}'.format(bytes,'Bytes' if bytes > 1 else 'Byte')
    
    elif SIZE_KiB <= bytes < SIZE_MiB:
        return u'{0:.2f} KiB'.format(bytes/SIZE_KiB)
    
    elif SIZE_MiB <= bytes < SIZE_GiB:
        return u'{0:.2f} MiB'.format(bytes/SIZE_MiB)
    
    elif SIZE_GiB <= bytes < SIZE_TiB:
        return u'{0:.2f} GiB'.format(bytes/SIZE_GiB)
    
    elif SIZE_TiB <= bytes:
        return u'{0:.2f} TiB'.format(bytes/SIZE_TiB)
 
    
 



#FIXME: coger funcion de _telegram_bot en lugar de duplicar
def isEmailNotif():
    try:
        output = proc.check_output(u'egrep EMAIL_NOTIF {}'.format(os.environ['BIN_DIR']+'CONSTANTS.sh'), shell=True)
        f = re.findall('"([a-zA-Z]+)"', output)
        
        if f and f[0] == 'ON':
            print u'[{}] {}: La notificacion por email esta activada'.format(datetime.datetime.now(), __file__)
            return True
    
    except Exception as e:
        print >> sys.stderr, u'[{}] {}: ERROR! Hubo un error inesperado al comprobar el estado de las notificaciones:'.format(datetime.datetime.now(), __file__)
        traceback.print_exc()
    
    print u'[{}] {}: La notificacion por email esta desactivada'.format(datetime.datetime.now(), __file__)
    return False
    



def sendNotif(tlg_msg, email_msg=None):    
    for n in range(1,20):
        print u'[{}] {}: Enviando notificacion por telegram'.format(datetime.datetime.now(), __file__)        
        try:
            bot = telepot.Bot(os.environ['TELEGRAM_TOKEN'])
            bot.sendMessage(int(os.environ['TELEGRAM_CHAT_GROUP']), tlg_msg, parse_mode="Markdown")
            break
            
        except Exception as e:
            print >> sys.stderr, u'[{}] {}: WARNING! No se ha podido enviar mensaje de telegram. Reintento: {}'.format(datetime.datetime.now(), __file__, n)
            traceback.print_exc()                
            time.sleep(random.randint(20,60))
    
    
    if isEmailNotif() and email_msg:        
        s = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
        for n in range(1,10):
            print u'[{}] {}: Enviando notificacion por email'.format(datetime.datetime.now(), __file__)
                            
            try:
                s.connect()                
                s.send(email_msg)
                s.close()
                return
            
            except Exception as e:
                print >> sys.stderr, u'[{}] {}: WARNING! No se ha podido enviar el email (intento: {}). Se reintentara en unos segundos'.format(datetime.datetime.now(), __file__, n)
                traceback.print_exc()
                time.sleep(random.randint(20,60))
            
        

        


def on_startup(arg=None):
    print u'[{}] {}: Notificacion de inicio de sistema'.format(datetime.datetime.now(), __file__)
    tlg_msg     = TLG_STARTUP
    
    email_msg   = gsender.Message(    
        subject = EMAIL_STARTUP_SUBJECT,
        to = os.environ['EMAIL_ADDR'],
        text = EMAIL_STARTUP_BODY)
    
    sendNotif(tlg_msg, email_msg)


def on_shutdown(arg=None):
    print u'[{}] {}: Notificacion de apagado del sistema'.format(datetime.datetime.now(), __file__)
    tlg_msg     = TLG_SHUTDOWN
    
    email_msg   = gsender.Message(    
        subject = EMAIL_SHUTDOWN_SUBJECT,
        to = os.environ['EMAIL_ADDR'],
        text = EMAIL_SHUTDOWN_BODY)
    
    sendNotif(tlg_msg,email_msg)



def on_cameraFailure(arg=None):
    print u'[{}] {}: Notificacion de fallo en camara'.format(datetime.datetime.now(), __file__)
    tlg_msg     = TLG_CAMERA_FAILURE
    
    email_msg   = gsender.Message(    
        subject = EMAIL_CAMERA_FAILURE_SUBJECT,
        to = os.environ['EMAIL_ADDR'],
        html = EMAIL_CAMERA_FAILURE_BODY)
    
    sendNotif(tlg_msg,email_msg)




def on_motion(file):
    print u'[{}] {}: Notificacion de movimiento detectado'.format(datetime.datetime.now(), __file__)
    for i in range(20):
        if not file or not os.path.isfile(file):
            print >> sys.stderr, u'[{}] {}: ERROR! El archivo {} no existe o no es un archivo regular'.format(datetime.datetime.now(), __file__, file)
            return
            
        #fileuploader(file)   
        
        id       = os.path.basename(file)[:-4]    
        data_img = run_query("select link from images where id like '{}'".format(id))
        data_vid = run_query("select duration, size from videos where id like '{}'".format(id))
            
        if data_img: 
            date        = datetime.datetime(*map(int,os.path.basename(file).split("_")[:6]))
            link        = data_img[0][0]     
            duration    = data_vid[0][0] if data_vid[0][0] else get_duration(id) 
            size        = get_humanSize(data_vid[0][1]) if data_vid[0][1] else get_size(id)
            tlg_msg     = TLG_MOTION.format(date.strftime("%Y/%m/%d %H:%M:%S"), link)             
            email_msg   = None
            
            if isEmailNotif():      #FIXME: Redundante porque se comprueba luego en sendNotif, pero por ahora se queda asi :)            
                email_msg = gsender.Message(subject = EMAIL_MOTION_SUBJECT,
                                            to = os.environ['EMAIL_ADDR'],
                                            html = EMAIL_MOTION_BODY.format(ip=get_ip(), 
                                                                            datetime=date.strftime("%Y/%m/%d %H:%M:%S"), 
                                                                            dom=os.environ['DUCKDNS_DOMAIN'], 
                                                                            port=os.environ['APACHE_PORT'], 
                                                                            id=id, 
                                                                            datos=get_datos(), 
                                                                            datosMensuales=os.environ['DATOS_MENSUALES'],
                                                                            email=os.environ['GMAIL_ACCOUNT_ALIAS'],
                                                                            duration=duration,  
                                                                            size=size),         
                                            attachments    = [file])
            
            sendNotif(tlg_msg, email_msg)
            return
            
        
        else:
            print >> sys.stderr, u'[{}] {}: ERROR! No se ha podido Notificar el nuevo movimiento (intento: {}). Se reintentara en unos minutos.'.format(datetime.datetime.now(), __file__, i)
            time.sleep(random.randint(60,240))
    
    print >> sys.stderr, u'[{}] {}: ERROR! No se ha podido Notificar el nuevo movimiento ya que se ha alcanzado el numero maximo de reintentos!!!.'.format(datetime.datetime.now(), __file__)
    


def on_telegramBot(arg=None):
	arg=arg.upper()	

	if "ON" in arg:
		print u'[{}] {}: Notificacion de inicio bot telegram'.format(datetime.datetime.now(), __file__)
		tlg_msg     = TLG_TELEGRAM_BOT_ON

		email_msg   = gsender.Message(    
			  subject 	= EMAIL_TELEGRAM_BOT_SUBJECT_ON,
			  to 			= os.environ['EMAIL_ADDR'],
			  html 		= EMAIL_TELEGRAM_BOT_BODY_ON)

	elif "OFF" in arg:
		print u'[{}] {}: Notificacion de parada de bot telegram'.format(datetime.datetime.now(), __file__)
		tlg_msg     = TLG_TELEGRAM_BOT_OFF

		email_msg   = gsender.Message(    
			  subject 	= EMAIL_TELEGRAM_BOT_SUBJECT_OFF,
			  to 			= os.environ['EMAIL_ADDR'],
			  html 		= EMAIL_TELEGRAM_BOT_BODY_OFF)
	    
	sendNotif(tlg_msg,email_msg)




COMMANDS={
    'ON_STARTUP'        : on_startup,
    'ON_SHUTDOWN'       : on_shutdown,
    'ON_MOTION'         : on_motion,
    'ON_CAMERA_FAILURE' : on_cameraFailure,
	 'ON_TELEGRAM_BOT'	: on_telegramBot
        }




def main(cmd, arg=None):
    if cmd in COMMANDS:        
        COMMANDS[cmd](arg)
        
    else:
        print >> sys.stderr, u'[{}] {}: ERROR! No se reconoce el comando recibido! Los comandos aceptados son {}'.format(datetime.datetime.now(), __file__, COMMANDS.keys())
    
    
        
    
      
         
if __name__ == "__main__":
    if len(sys.argv)>1:
        sys.exit(main(*sys.argv[1:]))
        
    else:
        print >> sys.stderr, u'USAGE: {} <cmd> <arg>\n\nLos comandos aceptados son:\n{}'.format(__file__, COMMANDS.keys())
    
