#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
import os
import smtplib
import time
import urllib
from email.mime.text import MIMEText
from email.MIMEImage import MIMEImage
from email.mime.multipart import MIMEMultipart

addr_to     = 'erdanieee@gmail.com'
addr_from   = 'SVVPA@elcarabo.com'
smtp_server = 'smtp.gmail.com'
smtp_port   = 587
smtp_user   = 'svvpaec@gmail.com'
smtp_pass   = 'elojoquetodolove'
html        = """\
<html>
  <head></head>
  <body>
    <h3>Movimiento detectado</h3>
    <p>S.V.V.P.A. (XXIPXX) ha detectado un nuevo movimiento en E.C. Adjunto a este mensaje se incluye el fotograma más representativo.</p>
    <p>Si el vídeo es interesante y deseas guardarlo en Google Drive haz <a href="http://svvpa.duckdns.org:9999/uploadVideo.php?id=XXIDXX">click aquí</a>. Recuerda que el vídeo puede tardar unos minutos en subir y que este disponible en la nube.</p>
   <p>Puedes ver las capturas guardadas anteriormente en <a href="https://drive.google.com/folderview?id=0Bwse_WnehFNKT2I3N005YmlYMms&usp=sharing">este enlace</a>.</p>			 
  </body>
</html>
"""

def main(argv): 
	if len(sys.argv) >= 2:
		if os.path.exists(sys.argv[1]):
			image 	 = sys.argv[1]
			tk	  	 = os.path.basename(image).split("_")
			datetime = ""
			
			if len(tk)>=12:
				datetime = "el " + tk[0] +"/"+ tk[1] +"/"+ tk[2] +" a las "+ tk[3] +":"+ tk[4] +":"+ tk[5]
			else:
				datetime = "el " + time.strftime("%Y/%m/%d") + " aproximadamente a las " + time.strftime("%H:%M:%S")			

			

			# Construct email
			msg = MIMEMultipart()
			msg['To'] = addr_to
			msg['From'] = addr_from
			msg['Subject'] = 'Movimiento detectado ' + datetime
			msg.preamble = 'Movimiento detectado' + datetime

			# Attach html
			msg.attach(MIMEText(html.replace("XXIDXX",os.path.basename(image).split(".")[0]).replace("XXIPXX",get_ip()), 'html', 'utf-8'))

			#attach image
			fp=open(image,'rb')
			msg.attach(MIMEImage(fp.read()))
			fp.close()

			#send email
			server = smtplib.SMTP(smtp_server,smtp_port) #port 465 or 587
			server.ehlo()
			server.starttls()
			server.ehlo()
			server.login(smtp_user,smtp_pass)
			server.sendmail(addr_from, addr_to, msg.as_string())
			server.close()



		else:
			print "ERROR: file " + sys.argv[1] + " not found!"
		
	else:
		print "USAGE: " + sys.argv[0] + " <image>"
		

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
