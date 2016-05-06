# encoding: utf-8

#from __future__ import print_function
import os, sys
import random
import telepot
import httplib2
from apiclient import discovery
from apiclient.http import MediaFileUpload
import oauth2client
#from oauth2client import client
#from oauth2client import tools
import json


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = os.environ['CONFIG_DIR'] + 'google_drive_client_secret.json'
APPLICATION_NAME = 'SVVPA'


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
        <p>S.V.V.P.A. 2.0 ha detectado un nuevo movimiento en E.C. <b>{datetime}</b>. Adjunto a este mensaje se incluye el fotograma más representativo.</p>
        <p>Si el vídeo es interesante y deseas guardarlo en Google Drive, haz <a href="http://{dom}.duckdns.org:{port}/uploadVideo.php?id={id}">click aquí</a>. Al abrir esa página en un navegador, SVVPA iniciará la subida del vídeo y mostrará una web con el progreso. <b>No</b> es necesario dejar la página abierta hasta que termine; puedes cerrarla, cerrar el navegador o incluso apagar tu máquina sin que interfiera el proceso. Recuerda que, en función del tamaño del vídeo, este proceso puede tardar varios minutos.</p>
        <p>Puedes ver las capturas guardadas anteriormente en <a href="https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing">este enlace</a>.</p>
        <p>Para acceder <b>de forma remota</b> a SVVPA visita <a href="http://{dom}.duckdns.org:{port}">http://{dom}.duckdns.org:{port}</a> o <a href="http://{ip}:{port}">http://{ip}:{port}</a>.    El consumo de datos hasta ahora ha sido de {datos}Mb de los {datosMensuales}Mb mensuales que incluye la tarifa.         
    </body>
</html>
            """ if bool(int(os.environ['REMOTE_ACCESS'])) else u"""\
<html>
    <head></head>
    <body>
        <h3>Movimiento detectado</h3>
        <p>S.V.V.P.A. 2.0 ha detectado un nuevo movimiento en E.C. <b>{datetime}</b>. Adjunto a este mensaje se incluye el fotograma más representativo.</p>
        <p>Si piensas que el vídeo puede ser interesante (Duración:{duration}, tamaño:{size}) y deseas subirlo a Google Drive, haz <a href="mailto:{email}?subject=CMD_SVVPA GUARDAR_EN_GOOGLE_DRIVE {id}">click aquí</a> para enviar enviar un email con el comando correspondiente. Te recordamos que el consumo de datos hasta el momento ha sido de {datos}Mb de los {datosMensuales}Mb mensuales que incluye la tarifa.</p>
        <p>Puedes ver las capturas guardadas anteriormente en <a href="https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing">este enlace</a>.</p>
    </body>
</html>
"""
TLG_MOTION=u'Se ha detectado un nuevo movimiento. La imagen más representativa ha sido subida automáticamente a google drive. Para subir también el vídeo utiliza el comando /subir\n[{} {}]({})'

EMAIL_CAMERA_FAILURE_SUBJECT=u'SVVPA - Error en la cámara'
EMAIL_CAMERA_FAILURE_BODY=u'''\
<html>
  <head></head>
  <body>
    <h3>No se puede acceder a la cámara</h3>
    <p>S.V.V.P.A. ha detectado que alguna de las cámaras ha dejado de funcionar correctamente. Si te encuentras en E.C., trata de acceder al modo <i>vista en Directo</i> para descartar un problema transitorio. Si no te encuentras en E.C., puedes probar a reiniciar SVVPA para ver si se soluciona el problema.</p>

<p>Si aun así no funciona, avisa a Er Danié para que trate de indagar en el problema.</p> 
  </body>
</html>
'''
TLG_CAMERA_FAILURE=u'SVVPA ha detectado que alguna de las cámaras no funciona correctamente. Si no estás en E.C. prueba a reiniciar el sistema por si cae la breva...'



def get_ip():
    url = "http://ipecho.net/plain"
    fp = urllib.urlopen(url)
    try:
        data = fp.read()
    finally:
        fp.close()
    return data



def get_datos():
    ret = os.popen(os.environ['BIN_DIR'] + "_getInternetUsage.sh").readlines()
    return ret[0].strip()



def get_duration(id):
    f=""     
    ret = os.popen(os.environ['FFMPEG_BIN'] + ' -i /var/www/svvpa/www/motion/2016_03_19_13_29_09_8665_13_64_194_32_325_1.mp4 2>&1|egrep -o "Duration: [0-9:]+"|egrep -o "[0-9]{2}:[0-9]{2}$"').readlines()
    return ret[0].strip()



def get_size(id):
    'Return the file size as a human friendly KB, MB, GB, or TB string'
    B = float(os.path.getsize(file))
    
    if B < self.SIZE_KB:
       return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
    elif SIZE_KB <= B < SIZE_MB:
       return '{0:.2f} KB'.format(B/SIZE_KB)
    elif SIZE_MB <= B < SIZE_GB:
       return '{0:.2f} MB'.format(B/SIZE_MB)
    elif SIZE_GB <= B < SIZE_TB:
       return '{0:.2f} GB'.format(B/SIZE_GB)
    elif SIZE_TB <= B:
       return '{0:.2f} TB'.format(B/SIZE_TB)


def isEmailNotif():
    try:
        output = proc.check_output(u'egrep EMAIL_NOTIF {}'.format(self.FILE_CONSTANTS), shell=True)
        f = re.findall('"([a-zA-Z]+)"', output)
        
        if len(f)>0 and f[0] == 'ON':
            print u'[{}] {}: La notificación por email está activada'.format(datetime.datetime.now(), __file__)
            return True
    
    except Exception as e:
        print u"[{}] {}: ERROR! Hubo un error inesperado al comprobar el estado de las notificaciones:\n{}".format(datetime.datetime.now(), __file__, repr(e))
    
    print u"[{}] {}: La notificación por email está desactivada".format(datetime.datetime.now(), __file__)
    return False
    



def sendNotif(email_msg, tlg_msg):
    if isEmailNotif():
        s = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
        for n in range(1,20):
            if s.is_connected():                
                try:                
                    s.send(email_msg)
                    s.close()
                    return
                
                except Exception as e:
                    print u"[{}] {}: ERROR! Hubo un error inesperado al tratar de enviar el email:\n{}".format(datetime.datetime.now(), __file__, repr(e))
            
            else:
                print u"[{}] {}: WARNING! No se ha podido enviar el email. Reintento: {}".format(datetime.datetime.now(), __file__, n)                
                time.sleep(random.randint(20,60))
                s.connect()
                
    else:
        for n in range(1,20):        
            try:
                bot = telepot.Bot(os.environ['TELEGRAM_TOKEN'])
                bot.sendMessage(int(os.environ['TELEGRAM_CHAT_GROUP']), tlg_msg)
                return
                
            except Exception as e:
                print u"[{}] {}: WARNING! No se ha podido enviar mensaje de telegram. Reintento: {}".format(datetime.datetime.now(), __file__, n)                
                time.sleep(random.randint(20,60))
        
        
        
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """    
    credential_path = os.path.join(os.environ['CONFIG_DIR'], 'google-drive-credentials.json')
    store           = oauth2client.file.Storage(credential_path)
    credentials     = store.get()
    if not credentials or credentials.invalid:
        flow            = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME        
        credentials     = tools.run(flow, store)
        print u"[{}] {}: Guardando credenciales en {}".format(datetime.datetime.now(), __file__, credential_path)
    return credentials
        
        
   
def uploadFile(file):
    try:
        credentials     = get_credentials()
        http            = credentials.authorize(httplib2.Http())
        service         = discovery.build('drive', 'v3', http=http)
        file_metadata   = { 'name' : os.path.basename(file)}
        media           = MediaFileUpload(file, mimetype='image/jpg')#, resumable=True)
        data            = service.files().create(body=file_metadata,        #FIXME: en principio solo hace falta el id y la URL
                                                 media_body=media, 
                                                 fields=('id','webContentLink')).execute()
        #print ('File ID: %s' % data.get('id'))
        return data
    
    except Exception as e:
        print u"[{}] {}: ERROR! Hubo un error inesperado al subir el archivo a google drive:\n{}".format(datetime.datetime.now(), __file__, repr(e))
    

        


def on_startup(arg=None):
    tlg_msg     = TLG_STARTUP
    
    email_msg   = gsender.Message(    
        subject = EMAIL_STARTUP_SUBJECT,
        to = os.environ['EMAIL_ADDR'],
        text = EMAIL_STARTUP_BODY)
    
    sendNotif(email_msg, tlg_msg)


def on_shutdown(arg=None):
    tlg_msg     = TLG_SHUTDOWN
    
    email_msg   = gsender.Message(    
        subject = EMAIL_SHUTDOWN_SUBJECT,
        to = os.environ['EMAIL_ADDR'],
        text = EMAIL_SHUTDOWN_BODY)
    
    sendNotif(email_msg, tlg_msg)



def on_cameraFailure(arg=None):
    tlg_msg     = TLG_CAMERA_FAILURE
    
    email_msg   = gsender.Message(    
        subject = EMAIL_CAMERA_FAILURE_SUBJECT,
        to = os.environ['EMAIL_ADDR'],
        html = EMAIL_CAMERA_FAILURE_BODY)
    
    sendNotif(email_msg, tlg_msg)




def on_motion(file):
    for i in range(20):
        data = uploadFile(file)
        
        if data:
            y,m,d,H,M = os.path.basename(file).split("_")[:5]
            
            tlg_msg     = TLG_MOTION.format()   #FIXME!!!!!!
            
            email_msg   = gsender.Message(    
                subject = EMAIL_MOTION_SUBJECT,
                to = os.environ['EMAIL_ADDR'],
                text = EMAIL_MOTION_BODY.format())      #FIXME!!!!
            
            sendNotif(email_msg, tlg_msg)
        
        else:
            time.sleep(random.randint(20,60))
    











COMMANDS={
    'ON_STARTUP'        : on_startup,
    'ON_SHUTDOWN'       : on_shutdown,
    'ON_MOTION'         : on_motion,
    'ON_CAMERA_FAILURE' : on_cameraFailure,
        }


