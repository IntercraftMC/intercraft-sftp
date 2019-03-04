import mysql.connector
import os

class Database:

	def __init__(self):
		self.__db = mysql.connector.connect(
			host     = os.getenv("DB_HOST"),
			port     = int(os.getenv("DB_PORT")),
			user     = os.getenv("DB_USERNAME"),
			passwd   = os.getenv("DB_PASSWORD"),
			database = os.getenv("DB_DATABASE")
		)

	# Fetch an sftp_user row from the database
	def fetch_sftp_user(self, username):
		c     = self.__db.cursor(dictionary=True)
		query = "SELECT * FROM `sftp_users` WHERE `username`=%s"
		c.execute(query, (username,))
		return c.fetchone()


	def fetch_filesystems(self, user_id):
		c     = self.__db.cursor(dictionary=True)
		query = "SELECT * FROM `filesystems` WHERE `user_id`=%s"
		c.execute(query, (user_id,))
		return c.fetchall()
