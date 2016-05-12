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
from _google_drive_uploader import main as uploadFile
import urllib

SIZE_KB = 1024.0
SIZE_MB = 1048576.0 
SIZE_GB = 1073741824.0 
SIZE_TB = 1099511627776.0 

EMAIL_STARTUP_SUBJECT=u'SVVPA - Inicio del sistema'
EMAIL_STARTUP_BODY=u'El sistema SVVPA se acaba de iniciar'
TLG_STARTUP=u'El sistema SVVPA se está iniciando \U0001f440'

EMAIL_SHUTDOWN_SUBJECT=u'SVVPA - Apagado del sistema'
EMAIL_SHUTDOWN_BODY=u'El sistema SVVPA se está apagando'
TLG_SHUTDOWN=u'El sistema SVVPA se está apagando \U0001f634'

EMAIL_MOTION_SUBJECT=u'SVVPA - Movimiento detectado'
EMAIL_MOTION_BODY=u"""\
<html>
    <head></head>
    <body>
        <h3>Movimiento detectado</h3>
        <p>S.V.V.P.A. 2.0 ha detectado un nuevo movimiento en E.C. <b>{datetime}</b>. \
Adjunto a este mensaje se incluye el fotograma más representativo.</p>
        <p>Si el vídeo es interesante y deseas guardarlo en Google Drive, haz \
<a href="http://{dom}.duckdns.org:{port}/uploadVideo.php?id={id}">click aquí</a>. \
Al abrir esa página en un navegador, SVVPA iniciará la subida del vídeo y \
mostrará una web con el progreso. <b>No</b> es necesario dejar la página abierta \
hasta que termine; puedes cerrarla, cerrar el navegador o incluso apagar tu \
máquina sin que interfiera el proceso. Recuerda que, en función del tamaño del \
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
            """ if bool(int(os.environ['REMOTE_ACCESS'])) else u"""\
<html>
    <head></head>
    <body>
        <h3>Movimiento detectado</h3>
        <p>S.V.V.P.A. 2.0 ha detectado un nuevo movimiento en E.C. \
<b>{datetime}</b>. Adjunto a este mensaje se incluye el fotograma más representativo.</p>
        <p>Si piensas que el vídeo puede ser interesante (Duración:{duration}, \
tamaño:{size}) y deseas subirlo a Google Drive, haz \
<a href="mailto:{email}?subject=CMD_SVVPA GUARDAR_EN_GOOGLE_DRIVE {id}">click aquí</a> \
para enviar enviar un email con el comando correspondiente. Te recordamos que \
el consumo de datos hasta el momento ha sido de {datos}Mb de los \
{datosMensuales}Mb mensuales que incluye la tarifa.</p>
        <p>Puedes ver las capturas guardadas anteriormente en <a href="\
https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing">este enlace</a>.</p>
    </body>
</html>
"""
TLG_MOTION=u'\U0001f440 Nuevo movimiento detectado (*{}*).\n\nLa [imagen más \
representativa]({}) ha sido subida automáticamente a google drive.\nPara subir \
también el vídeo utiliza el comando /subir'

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

<p>Si aun así no funciona, avisa a Er Danié para que trate de indagar en el problema.</p> 
  </body>
</html>
'''
TLG_CAMERA_FAILURE=u'\u203c S.V.V.P.A. ha detectado que alguna de las cámaras ha dejado\
de funcionar correctamente. Si te encuentras en E.C., trata de acceder al modo \
vista en Directo para descartar un problema transitorio. Si no te encuentras en \
E.C., puedes probar a reiniciar SVVPA para ver si se soluciona el problema.\u203c'



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
        ret = os.popen(os.environ['FFMPEG_BIN'] + ' -i ' + file + '2>&1|egrep -o "Duration: [0-9:]+"|egrep -o "[0-9]{2}:[0-9]{2}$"').readlines()
        return ret[0].strip()
    
    except Exception as e:
        print >> sys.stderr, u"[{}] {}: ERROR! No se ha podido determinar la duración del vídeo:".format(datetime.datetime.now(), __file__)
        traceback.print_exc()
        return "?"



def get_size(id):
    file = os.environ['MOTION_DIR'] + id + '.' + os.environ['MOTION_VIDEO_EXT']
    try:
        'Return the file size as a human friendly KB, MB, GB, or TB string'
        B = float(os.path.getsize(file))
        
        if B < SIZE_KB:
           return u'{0} {1}'.format(B,'Bytes' if B > 1 else 'Byte')
        elif SIZE_KB <= B < SIZE_MB:
           return u'{0:.2f} KB'.format(B/SIZE_KB)
        elif SIZE_MB <= B < SIZE_GB:
           return u'{0:.2f} MB'.format(B/SIZE_MB)
        elif SIZE_GB <= B < SIZE_TB:
           return u'{0:.2f} GB'.format(B/SIZE_GB)
        elif SIZE_TB <= B:
           return u'{0:.2f} TB'.format(B/SIZE_TB)
       
    except Exception as e:
        print >> sys.stderr, u"[{}] {}: ERROR! No se ha podido determinar el tamaño del vídeo:".format(datetime.datetime.now(), __file__)
        traceback.print_exc()
        return "?"



#FIXME: coger función de _telegram_bot en lugar de duplicar
def isEmailNotif():
    try:
        output = proc.check_output(u'egrep EMAIL_NOTIF {}'.format(os.environ['BIN_DIR']+'CONSTANTS.sh'), shell=True)
        f = re.findall('"([a-zA-Z]+)"', output)
        
        if f and f[0] == 'ON':
            print u'[{}] {}: La notificación por email está activada'.format(datetime.datetime.now(), __file__)
            return True
    
    except Exception as e:
        print >> sys.stderr, u"[{}] {}: ERROR! Hubo un error inesperado al comprobar el estado de las notificaciones:".format(datetime.datetime.now(), __file__)
        traceback.print_exc()
    
    print u"[{}] {}: La notificación por email está desactivada".format(datetime.datetime.now(), __file__)
    return False
    



def sendNotif(tlg_msg, email_msg=None):    
    for n in range(1,20):
        print u"[{}] {}: Enviando notificación por telegram".format(datetime.datetime.now(), __file__)        
        try:
            bot = telepot.Bot(os.environ['TELEGRAM_TOKEN'])
            bot.sendMessage(int(os.environ['TELEGRAM_CHAT_GROUP']), tlg_msg, parse_mode="Markdown")
            break
            
        except Exception as e:
            print >> sys.stderr, u"[{}] {}: WARNING! No se ha podido enviar mensaje de telegram. Reintento: {}".format(datetime.datetime.now(), __file__, n)
            traceback.print_exc()                
            time.sleep(random.randint(20,60))
    
    
    if isEmailNotif() and email_msg:        
        s = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
        for n in range(1,10):
            print u"[{}] {}: Enviando notificación por email".format(datetime.datetime.now(), __file__)
                            
            try:
                s.connect()                
                s.send(email_msg)
                s.close()
                return
            
            except Exception as e:
                print >> sys.stderr, u"[{}] {}: WARNING! No se ha podido enviar el email (intento: {}). Se reintentará en unos segundos".format(datetime.datetime.now(), __file__, n)
                traceback.print_exc()
                time.sleep(random.randint(20,60))
            
        

        


def on_startup(arg=None):
    print u"[{}] {}: Notificación de inicio de sistema".format(datetime.datetime.now(), __file__)
    tlg_msg     = TLG_STARTUP
    
    email_msg   = gsender.Message(    
        subject = EMAIL_STARTUP_SUBJECT,
        to = os.environ['EMAIL_ADDR'],
        text = EMAIL_STARTUP_BODY)
    
    sendNotif(tlg_msg, email_msg)


def on_shutdown(arg=None):
    print u"[{}] {}: Notificación de apagado del sistema".format(datetime.datetime.now(), __file__)
    tlg_msg     = TLG_SHUTDOWN
    
    email_msg   = gsender.Message(    
        subject = EMAIL_SHUTDOWN_SUBJECT,
        to = os.environ['EMAIL_ADDR'],
        text = EMAIL_SHUTDOWN_BODY)
    
    sendNotif(tlg_msg,email_msg)



def on_cameraFailure(arg=None):
    print u"[{}] {}: Notificación de fallo en cámara".format(datetime.datetime.now(), __file__)
    tlg_msg     = TLG_CAMERA_FAILURE
    
    email_msg   = gsender.Message(    
        subject = EMAIL_CAMERA_FAILURE_SUBJECT,
        to = os.environ['EMAIL_ADDR'],
        html = EMAIL_CAMERA_FAILURE_BODY)
    
    sendNotif(tlg_msg,email_msg)




def on_motion(file):
    print u"[{}] {}: Notificación de movimiento detectado".format(datetime.datetime.now(), __file__)
    for i in range(20):
        if not file or not os.path.isfile(file):
            print >> sys.stderr, u"[{}] {}: ERROR! El archivo {} no existe o no es un archivo regular".format(datetime.datetime.now(), __file__, file)
            return
            
        link = uploadFile(file)
        
        if link:
            date        = datetime.datetime(*map(int,os.path.basename(file).split("_")[:6]))
            id          = os.path.basename(file).split(".")[0].strip()            
            tlg_msg     = TLG_MOTION.format(date.strftime("%Y/%m/%d %H:%M:%S"), link)
            email_msg   = None
            
            if isEmailNotif():      #FIXME: Redundante porque se comprueba luego en sendNotif, pero por ahora se queda así :)            
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
                                                                            duration=get_duration(id),
                                                                            size=get_size(id)),
                                            attachments    = [file])
            
            sendNotif(tlg_msg, email_msg)
            return
            
        
        else:
            print >> sys.stderr, u"[{}] {}: ERROR! No se ha podido Notificar el nuevo movimiento (intento: {}). Se reintentará en unos minutos.".format(datetime.datetime.now(), __file__, i)
            time.sleep(random.randint(60,240))
    
    print >> sys.stderr, u"[{}] {}: ERROR! No se ha podido Notificar el nuevo movimiento ya que se ha alcanzado el número máximo de reintentos!!!.".format(datetime.datetime.now(), __file__)
    









COMMANDS={
    'ON_STARTUP'        : on_startup,
    'ON_SHUTDOWN'       : on_shutdown,
    'ON_MOTION'         : on_motion,
    'ON_CAMERA_FAILURE' : on_cameraFailure,
        }




def main(cmd, arg=None):
    if cmd in COMMANDS:        
        COMMANDS[cmd](arg)
        
    else:
        print >> sys.stderr, u"[{}] {}: ERROR! No se reconoce el comando recibido! Los comandos aceptados son {}".format(datetime.datetime.now(), __file__, COMMANDS.keys())
    
    
        
    
      
         
if __name__ == "__main__":
    if len(sys.argv)>1:
        sys.exit(main(*sys.argv[1:]))
        
    else:
        print >> sys.stderr, u"USAGE: {} <cmd> <arg>\n\nLos comandos aceptados son:\n{}".format(__file__, COMMANDS.keys())
    