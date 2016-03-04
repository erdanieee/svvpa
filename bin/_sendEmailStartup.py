import sys, os
import gmail_sender as gsender


def main(args):
	s   = gsender.GMail(os.environ['SMPT_USER'], os.environ['SMPT_PASS'])
	msg = gsender.Message(	subject	= u"SVVPA se acaba de iniciar",
		to = os.environ['EMAIL_ADDR'],
		text = u'El sistema SVVPA está ahora operativo.')
	s.send(msg)
	s.close()



if __name__ == "__main__":
	sys.exit(main(sys.argv))

