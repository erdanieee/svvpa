import ephem
import os,sys
import subprocess as proc


DEBUG=False


#el archivo FILE_MOTION_OFF se crea cuando se para o pausa motion por telegram/email
if not os.path.exists(os.environ['FILE_MOTION_OFF']):
	if DEBUG:
		print "_daylightMotion: file FILE_MOTION_OFF not exists"
	o=ephem.Observer()
	o.lat=os.environ['LATITUD']
	o.long=os.environ['LONGITUD']

	s=ephem.Sun()
	s.compute()

	r=ephem.localtime(o.next_rising(s))
	s=ephem.localtime(o.next_setting(s))
	if DEBUG:
		print "_daylightMotion: next sunrise %s" % r
		print "_daylightMotion: next sunset %s" % s

	motionStatus=proc.call('sudo service motion status 2>&1 >/dev/null', shell=True)
	if DEBUG:	
		print "_daylightMotion: motion status return code: %s" % motionStatus

	if r>s: # dia
		if DEBUG:
			print "_daylightMotion: r>s (dia)"
		if motionStatus != 0:	# motion inactivo
			if DEBUG:
				print "_daylightMotion: motion stopped. RET code 1"
			sys.exit(1)

	else:	# noche
		if DEBUG:
			print "_daylightMotion: r<s (noche)"
		if motionStatus == 0:	# motion activo
			if DEBUG:
				print "_daylightMotion: motion running. RET code 2"
			sys.exit(2)

else:
	if DEBUG:
		print "_daylightMotion: file FILE_MOTION_OFF exists"
	if proc.call('sudo service motion status 2>&1 >/dev/null', shell=True) == 0:
		print "WARNING!!!: FILE_MOTION_OFF existe pero motion esta funcionando!!"
