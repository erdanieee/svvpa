#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys, os
import gmail_sender as gsender
import datetime


def main(args):
	print "[{}] {}: Enviando email de arranque del sistema SVVPA".format(datetime.datetime.now(), __file__)
	s   = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	msg = gsender.Message(	subject	= u"SVVPA se acaba de iniciar",
		to = os.environ['EMAIL_ADDR'],
		text = u'El sistema SVVPA se acaba de iniciar.')
	s.send(msg)
	s.close()



if __name__ == "__main__":
	sys.exit(main(sys.argv))

