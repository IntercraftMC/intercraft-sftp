import os
from pathlib import Path
import paramiko
from paramiko import SFTPAttributes, SFTPServer
from . sftp_handle import SftpHandle
from . import utils

class SftpInterface(paramiko.SFTPServerInterface):

	def __init__(self, session, *largs, **kwargs):
		super(SftpInterface, self).__init__(session, *largs, **kwargs)
		self.__session = session
		self.__vfs     = session.vfs()


	def __realpath(self, path):
		return str(Path("/" + path).resolve())


	def list_folder(self, path):
		path = self.__realpath(path)
		try:
			result = []
			for file in self.__vfs.listdir(path):
				stat = self.__vfs.stat(os.path.join(path, file))
				attr = SFTPAttributes.from_stat(stat)
				attr.filename = file
				result.append(attr)
			return result
		except OSError as e:
			return SFTPServer.convert_errno(e.errno)


	def stat(self, path):
		path = self.__realpath(path)
		try:
			return SFTPAttributes.from_stat(self.__vfs.stat(path))
		except OSError as e:
			return SFTPServer.convert_errno(e.errno)


	def lstat(self, path):
		path = self.__realpath(path)
		try:
			return SFTPAttributes.from_stat(self.__vfs.stat(path))
		except OSError as e:
			return SFTPServer.convert_errno(e.errno)


	def open(self, path, flags, attr):
		path = self.__realpath(path)

		# Attempt to get a file descriptor
		fd = None
		try:
			binary_flag = getattr(os, "O_BINARY", 0)
			flags |= binary_flag
			mode = getattr(attr, "st_mode", None)
			fd = self.__vfs.open(path, flags, mode or 0o666)
		except OSError as e:
			print(e)
			return SFTPServer.convert_errno(e.errno)

		try:
			f = os.fdopen(fd, utils.file_open_mode(flags))
		except OSError as e:
			return SFTPServer.convert_errno(e.errno)

		# Create the file handle
		fobj = SftpHandle(flags)
		fobj.filename = path
		fobj.readfile = f
		fobj.writefile = f
		return fobj


	def remove(self, path):
		path = self.__realpath(path)
		try:
			self.__vfs.remove(path)
		except OSError as e:
			return SFTPServer.convert_errno(e.errno)
		return paramiko.SFTP_OK


	def rename(self, old_path, new_path):
		old_path = self.__realpath(old_path)
		new_path = self.__realpath(new_path)
		try:
			self.__vfs.rename(old_path, new_path)
		except OSError as e:
			return SFTPServer.convert_errno(e.errno)
		return paramiko.SFTP_OK


	def mkdir(self, path, attr):
		path = self.__realpath(path)
		try:
			self.__vfs.mkdir(path)
		except OSError as e:
			return SFTPServer.convert_errno(e.errno)
		return paramiko.SFTP_OK


	def rmdir(self, path):
		path = self.__realpath(path)
		try:
			self.__vfs.rmdir(path)
		except OSError as e:
			return SFTPServer.convert_errno(e.errno)
		return paramiko.SFTP_OK

