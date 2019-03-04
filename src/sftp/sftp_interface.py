import paramiko

class SftpInterface (paramiko.SFTPServerInterface):

	def __init__(self, session, *largs, **kwargs):
		paramiko.SFTPServerInterface.__init__(self, session, *largs, **kwargs)
		self.__session = session
