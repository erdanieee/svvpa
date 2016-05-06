# encoding: utf-8


EMAIL_STARTUP_SUBJECT=u'SVVPA - Inicio del sistema'
EMAIL_STARTUP_BODY=u'El sistema SVVPA se está iniciando'
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
TLG_MOTION=u''

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
TLG_CAMERA_FAILURE=u''



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


#FIXME: copiar de _telegram_bot.py, que allí está implementada!!
def get_size(id):
    return 0




def on_startup(args):
    return


def on_shutdown(args):
    return


def on_motion(args):
    return


def on_cameraFailure(args):
    return










COMMANDS={
    'ON_STARTUP'        : on_startup,
    'ON_SHUTDOWN'       : on_shutdown,
    'ON_MOTION'         : on_motion,
    'ON_CAMERA_FAILURE' : on_cameraFailure,
        }


