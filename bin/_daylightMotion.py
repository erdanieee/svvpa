import ephem
import os,sys
import subprocess as proc



#el archivo FILE_MOTION_OFF se crea cuando se para o pausa motion por telegram/email
if not os.path.exists(os.environ['FILE_MOTION_OFF']):
	o=ephem.Observer()
	o.lat=os.environ['LATITUD']
	o.long=os.environ['LONGITUD']

	s=ephem.Sun()
	s.compute()

	r=ephem.localtime(o.next_rising(s))
	s=ephem.localtime(o.next_setting(s))

	motionStatus=proc.call('sudo service motion status 2>&1 >/dev/null', shell=True)

	if r>s: # dia
		if motionStatus != 0:	# motion inactivo
			#proc.call('sudo service motion restart', shell=True)
			sys.exit(1)

	else:	# noche
		if motionStatus == 0:	# motion activo
			#proc.call('sudo service motion stop', shell=True)		
			sys.exit(-1)

else:
	if proc.call('sudo service motion status 2>&1 >/dev/null', shell=True) == 0:
		print "WARNING!!!: FILE_MOTION_OFF existe pero motion esta funcionando!!"
