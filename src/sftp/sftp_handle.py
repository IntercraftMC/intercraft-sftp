import os
import paramiko

class SftpHandle(paramiko.SFTPHandle):

	def stat(self):
		try:
			return paramiko.SFTPAttributes.from_stat(os.fstat(self.readfile.fileno()))
		except OSError as e:
			return paramiko.SFTPServer.convert_errno(e.errno)

	def chattr(self, attr):
		pass
