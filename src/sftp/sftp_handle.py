import paramiko

class SftpHandle (paramiko.SFTPHandle):

	def stat(self):
		pass

	def chattr(self, attr):
		pass
