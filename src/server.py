import os
import paramiko
import socket
import time
import _thread

from . database import Database
from . sftp import SftpHandle, SftpInterface, SftpSession

class Server:

	def __init__(self):

		# Connect to the database
		self.__db = Database()

		# Load the host key file
		self.__host_key = paramiko.RSAKey.from_private_key_file(os.getenv("SFTP_PRIVATE_KEY"))


	# Set the level of log output
	def set_log_level(self, level):
		paramiko_level = getattr(paramiko.common, level)
		paramiko.common.logging.basicConfig(level=paramiko_level)


	# Create and set up the server socket
	def create_socket(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
		server.bind(("", int(os.getenv("SFTP_PORT"))))
		server.listen(int(os.getenv("SFTP_BACKLOG")))
		return server


	def run(self):

		# Set the log level
		self.set_log_level(os.getenv("SFTP_LOG_LEVEL"))

		# Create the server socket
		server = self.create_socket()

		while True:
			# Accept the incoming connection and run it in a separate thread
			print("Waiting for connection...")
			conn, addr = server.accept()
			_thread.start_new_thread(self.run_thread, (conn, addr))


	# Run a connection thread
	def run_thread(self, conn, addr):

		print("Connection established")

		# Set up SSH/SFTP stuff and perform Handshake
		transport = paramiko.Transport(conn)
		transport.add_server_key(self.__host_key)
		transport.set_subsystem_handler("sftp", paramiko.SFTPServer, SftpInterface)

		# Create the session instance
		session = SftpSession(self.__db)
		transport.start_server(server=session)

		# Accept the communication channel
		channel = transport.accept()
		while transport.is_active():
			time.sleep(1)

		# Close the connection when finished
		conn.close()
