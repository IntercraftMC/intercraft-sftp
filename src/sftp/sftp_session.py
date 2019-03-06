import bcrypt
import paramiko
import time

class SftpSession(paramiko.ServerInterface):

	def __init__(self, server):
		super(SftpSession, self).__init__()
		self.__server = server
		self.__db     = server.database()
		self.__store  = server.vfs_store()
		self.__user   = None
		self.__vfs    = None


	# Do stuff when the login is accepted
	def accept_login(self, user):
		print("Loading session:", user["username"])
		self.__user = user
		self.__vfs  = self.__store.load(user["id"])


	# Authenticate the user via username and password
	def check_auth_password(self, username, password):
		user = self.__server.database().fetch_user(username)
		if not user:
			return paramiko.AUTH_FAILED
		if bcrypt.hashpw(password.encode(), user["password"].encode()) != user["password"].encode():
			time.sleep(2) # Throttle failed attempts
			return paramiko.AUTH_FAILED
		self.accept_login(user)
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


	# Get a reference to the VFS
	def vfs(self):
		return self.__vfs


	# Clean up the closed session
	def __del__(self):
		print("Unloading the session")
		if self.__user:
			print("Unload session:", self.__user["username"])
			self.__store.unload(self.__user["id"])
