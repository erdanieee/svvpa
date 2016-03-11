#!/usr/bin/python
# encoding: utf-8

''' 
	Este programa comprueba el espacio en disco para un determinado directorio
	y, si supera un porcentaje dado, borra archivos en ese directorio por
	orden cronológico 
'''


import sys
import os
import pwd
import datetime


def get_percent_free_disk_space(rootfolder):
	st = os.statvfs(rootfolder)
	free = st.f_bavail * st.f_frsize / 1024
	total = st.f_blocks * st.f_frsize / 1024
	pfree = (free/float(total))
	print "[{}] {}: Espacio libre {:.2%}".format(datetime.datetime.now(), __file__, pfree)	
	return pfree*100


def files_to_delete(rootfolder, extension):
	return sorted(
		(os.path.join(dirname, filename) 
		for dirname, dirnames, filenames in os.walk(rootfolder) 
		for filename in filenames if filename.endswith(extension)),
		key=lambda fn: os.stat(fn).st_mtime,
		reverse=True)


def free_space_up_to(free_percent_required, rootfolder, extension):
	file_list = files_to_delete(rootfolder, extension)

	while get_percent_free_disk_space(rootfolder) <= free_percent_required:
		if file_list:
			file = file_list.pop()
			print "[{}] {}: eliminando archivo {}".format(datetime.datetime.now(), __file__, file)
			os.remove(file)    			
		
		else:
			print "[{}] {}: No se puede liberar más espacio porque no quedan imágenes o vídeos que se puedan borrar".format(datetime.datetime.now(), __file__)
			return

	
	print "[{}] {}: Espacio libre ({:.0f}%) es mayor que el mínimo requerido ({:.0f}%). No se borrarán más archivos.".format(datetime.datetime.now(), __file__, get_percent_free_disk_space(rootfolder), free_percent_required)
	return

	





def main(argv=None): 
	try:
		working_dir = str(os.environ['MOTION_DIR'])
		percent_threshold = float(os.environ['FREE_DISK_PERCENT_THRESHOLD'])
		extension = ("."+os.environ['MOTION_VIDEO_EXT'], "."+os.environ['MOTION_VIDEO_EXT_RAW'], "."+os.environ['MOTION_IMAGE_EXT'])

		print "[{}] {}: Comprobando espacio en disco. ".format(datetime.datetime.now(), __file__)
		free_space_up_to(percent_threshold, working_dir, extension)

	except Exception, e: 
		print "[{}] {}: ERROR! {}".format(datetime.datetime.now(), __file__, repr(e))
		return -1


if __name__ == '__main__':    
	sys.exit(main())
