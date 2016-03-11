import sys, os
import gmail_sender as gsender
import datetime


def main(args):
	print "[{}] {}: Enviando email de confirmación de apagado de SVVPA".format(datetime.datetime.now(), __file__)
	s   = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	msg = gsender.Message(	subject	= u"Apagando SVVPA",
		to = os.environ['EMAIL_ADDR'],
		text = u'El sistema SVVPA se está apagando. Para arrancarlo es necesario desactivar y volver a activar físicamente el mini-interruptor que está junto a las baterías.')
	s.send(msg)
	s.close()



if __name__ == "__main__":
	sys.exit(main(sys.argv))

