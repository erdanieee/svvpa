#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
import os
import smtplib
import time
import urllib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

html        = """\
<html>
  <head></head>
  <body>
    <h3>No se puede acceder a la cámara</h3>
    <p>S.V.V.P.A. (XXIPXX) ha detectado que alguna de las cámaras ha dejado de funcionar correctamente. Para descartar que se trate de un fallo transitorio sería conveniente acceder al modo <i>vista en Directo</i>. Si no te encuentras en E.C. puedes acceder remotamente a la web en <a href="http://svvpa.duckdns.org:9999/">http://svvpa.duckdns.org:9999/</a> o en <a href="http://XXIPXX:9999/">http://XXIPXX:9999/</a>.</p>

<p>Si la <i>vista en Directo</i> no muestra la imagen, prueba a reiniciar SVVPA (pestaña <i>Ajustes</i>). Si aun así no funciona, avisa a Er Danié para que trate de indagar en el problema.</p> 
  </body>
</html>
"""

def main(argv): 
	print "enviando email"
	# Construct email
	msg = MIMEText(html.replace("XXIPXX",get_ip()), 'html', 'utf-8')
	msg['To'] = os.environ['EMAIL_ADDR']
	msg['From'] = os.environ['EMAIL_FROM']
	msg['Subject'] = 'No se puede acceder a la cámara'
	msg.preamble = 'No se puede acceder a la cámara'


	#send email
	server = smtplib.SMTP(os.environ['SMPT_SERVER'],os.environ['SMPT_PORT']) #port 465 or 587
	server.ehlo()
	server.starttls()
	server.ehlo()
	server.login(os.environ['SMPT_USER'],os.environ['SMPT_PASS'])
	server.sendmail(msg['From'], msg['To'].split(","), msg.as_string())
	server.close()


def get_ip():
	url = "http://ipecho.net/plain"
	fp = urllib.urlopen(url)
	try:
		data = fp.read()
	finally:
		fp.close()
	return data


if __name__ == "__main__":
    sys.exit(main(sys.argv))
