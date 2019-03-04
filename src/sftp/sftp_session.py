import bcrypt
import os
import paramiko

class SftpSession(paramiko.ServerInterface):

	def __init__(self, db):
		paramiko.ServerInterface.__init__(self)
		self.__db = db
		self.__user = None


	# Authenticate the user via username and password
	def check_auth_password(self, username, password):
		user = self.__db.fetch_sftp_user(username)
		if not user:
			return paramiko.AUTH_FAILED
		if bcrypt.hashpw(password.encode(), user["password"].encode()) != user["password"].encode():
			return paramiko.AUTH_FAILED
		self.__user = user
		return paramiko.AUTH_SUCCESSFUL


	# Authenticate the user via public key
	def check_auth_publickey(self, username, key):
		return paramiko.AUTH_FAILED


	# Verify the channel request
	def check_channel_request(self, kind, channel):
		return paramiko.OPEN_SUCCEEDED


	# Get the allowed methods of authentication
	def get_allowed_auths(self, username):
		return "password"


	# Get a reference to the database
	def database(self):
		return self.__db


	# Get a reference to the authenticated user
	def user(self):
		return self.__user
