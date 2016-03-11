#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
import os
import time
import datetime
import gmail_sender as gsender


def main(argv):
	print "[{}] {}: Enviando email de pérdida de señal de cámara".format(datetime.datetime.now(), __file__)
	s   = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	msg = gsender.Message(	
								subject = u'No se puede acceder a la cámara',
								to 		 	= os.environ['EMAIL_ADDR'],
								sender	= os.environ['GMAIL_ACCOUNT_ALIAS'],
								text 		= u'Se ha perido la señal con la cámara. Si el problema persiste trata de reiniciar SVVPA',
								html		=	u'''\
<html>
  <head></head>
  <body>
    <h3>No se puede acceder a la cámara</h3>
    <p>S.V.V.P.A. ha detectado que alguna de las cámaras ha dejado de funcionar correctamente. Si te encuentras en E.C., trata de acceder al modo <i>vista en Directo</i> para descartar un problema transitorio. Si no te encuentras en E.C., puedes probar a reiniciar SVVPA para ver si se soluciona el problema.</p>

<p>Si aun así no funciona, avisa a Er Danié para que trate de indagar en el problema.</p> 
  </body>
</html>
''')

	s.send(msg)
	s.close()	



if __name__ == "__main__":
    sys.exit(main(sys.argv))
