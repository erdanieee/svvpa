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
import logging
from logging import config

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'verbose': {
			'format': '%(levelname)s %(module)s P%(process)d T%(thread)d %(message)s'
		},
	},
	'handlers': {
		'stdout': {
			'class': 'logging.StreamHandler',
			'stream': sys.stdout,
			'formatter': 'verbose',
		},
		'sys-logger6': {
			'class': 'logging.handlers.SysLogHandler',
			'address': '/dev/log',
			'facility': "local6",
			'formatter': 'verbose',
		},
	},
	'loggers': {
		'my-logger': {
			'handlers': ['sys-logger6','stdout'],
			'level': logging.DEBUG,
			'propagate': True,
		},
	}
}
logger = logging.getLogger("my-logger")


def get_percent_free_disk_space(rootfolder):
	st = os.statvfs(rootfolder)
	free = st.f_bavail * st.f_frsize / 1024
	total = st.f_blocks * st.f_frsize / 1024
	pfree = (free/float(total))
	logger.debug("Free disk space: {:.2%}".format(pfree))
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

	while file_list:
		if get_percent_free_disk_space(rootfolder) >= free_percent_required:
			logger.debug("Minimum free disk space threshold reached")
			return
		file = file_list.pop()
		logger.debug("removing {0}".format(file))
		os.remove(file)    

	logger.warning("No files found!!")


def main(argv=None): 
	config.dictConfig(LOGGING)

	try:
		working_dir = str(os.environ['APACHE_DIR']+os.environ['MOTION_DIR'])
		percent_threshold = float(os.environ['FREE_DISK_PERCENT_THRESHOLD'])
		extension = ("."+os.environ['MOTION_VIDEO_EXT'], "."+os.environ['MOTION_VIDEO_EXT_RAW'], "."+os.environ['MOTION_IMAGE_EXT'])

		logger.debug("USER: " + (pwd.getpwuid(os.getuid())[0]) + " Checking {0}".format(working_dir))
		free_space_up_to(percent_threshold, working_dir, extension)

	except Exception, e: 
		logger.error(os.path.basename(sys.argv[0]) + ", USER: " + (pwd.getpwuid(os.getuid())[0]) + ", ERR: " + repr(e) + "\n")
		return 2


if __name__ == '__main__':    
	sys.exit(main())
