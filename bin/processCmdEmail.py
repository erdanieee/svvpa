#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import re
import subprocess as p
import gmail_sender as g
import gmail as c


def cmd_help(a):
    gmail = g.GMail("svvpaec@gmail.com","elojoquetodolove")
    msg1 = g.Message(subject="asunto sin sunto, A!",
                  to="dlopez@bacmine.com,erdanieee@yahoo.es",
                  #cc=",".join(results.cc),
                  text=u"Éste es el cuerpo del mensaje en texto plano",
                  html=u'''
                  <html>
                    <body>
                        <h3>Título de la prueba</h3>
                        Éste es el cuerpo del asunto en formato HTML
                    </body>
                  </html>
                  ''')#,
                  #attachments="/home/dlopez/temp/svvpa/bin/cron_update_ip.sh")
    gmail.send(msg1)
    gmail.close()

    return a

def cmd_saveFile(a):
    imageFile = a + "." + os.environ['MOTION_IMAGE_EXT']
    videoFile = a + "." + os.environ['MOTION_VIDEO_EXT']
    imageLogFile = "/tmp/" + a + "_IMAGEN.log"
    videoLogFile = "/tmp/" + a + "_VIDEO.log"
    imageCmd = os.environ['RCLONE_BIN'] + " --config " + os.environ['RCLONE_CONFIG'] + " copy " + os.environ['MOTION_DIR'] + imageFile + " google:SVVPA/imagenes 2>&1 > " + imageLogFile
    videoCmd = os.environ['RCLONE_BIN'] + " --config " + os.environ['RCLONE_CONFIG'] + " copy " + os.environ['MOTION_DIR'] + videoFile + " google:SVVPA/imagenes 2>&1 > " + videoLogFile

    cmdTEMPORAL = os.environ['RCLONE_BIN'] + " --config " + os.environ['RCLONE_CONFIG'] + " copy /home/dlopez/temp/x.py google:SVVPA/imagenes 2>&1 > " + videoLogFile

    imageStatus = p.call(cmdTEMPORAL)
    videoStatus = p.call(cmdTEMPORAL)

    if imageStatus and videoStatus:
        asunto="Transferencia correcta (" + a + ")"
        texto="La imagen y el vídeo se han subido correctamente"
    else:
        asunto="Transferencia con ERRORES (" + a + ")"
        texto="Ha habido errores al subir los arhivos a google drive. Adjunto se envían los logs de las transferencias."

    gmail = g.GMail("svvpaec@gmail.com","elojoquetodolove")
    msg1 = g.Message(subject="asunto sin sunto, A!",
                  to="dlopez@bacmine.com,erdanieee@yahoo.es",
                  text=u"Éste es el cuerpo del mensaje en texto plano",
                  attachments=[imageLogFile, videoFile])
    gmail.send(msg1)
    gmail.close()


    return a

def cmd_status(a):
    return a

def cmd_reboot(a):
    return a

def cmd_lifeCam(a):
    return a


def main(args):
    re_subject = re.compile('(CMD_SVVPA (?P<cmd>\w+)(?P<args>.*))|(Movimiento detectado [(](?P<file>(\d+_?){12,})[)])')
    CMD_SVVPA={
        'AYUDA' : cmd_help,
        'GUARDAR': cmd_saveFile,
        'ESTADO' : cmd_status,
        'REINICIA' : cmd_reboot,
        'DIRECTO' : cmd_lifeCam
    }

    g = c.login("svvpaec", "elojoquetodolove")
    emails = g.inbox().mail(prefetch=True, unread=True, to="svvpaec@gmail.com")

    #procesa todos los emails NO LEIDOS
    for e in emails:
        r = re_subject.search(e.subject)

        if r:
            if r.group('cmd'):
                try:
                    resultado = CMD_SVVPA[r.group('cmd')](r.group('args'))
                    print "CMD: " + str(r.group('cmd'))

                except:
                    print "Función no válida"

            elif r.group('file'):
                cmd_saveFile(r.group('file'))
            print

        else:
            e.read()

    g.logout()




if __name__ == "__main__":
    sys.exit(main(sys.argv))



'''
procesando=[]
procesado=[]
error=[]

g = gmail.login("svvpaec", "elojoquetodolove")

emails = g.inbox().mail(prefetch=True, unread=True, to="svvpaec@gmail.com")


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


g.logout()
'''
