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

	# Fetch a user row from the database
	def fetch_user(self, username):
		c     = self.__db.cursor(dictionary=True)
		query = "SELECT * FROM `users` WHERE `username`=%s"
		c.execute(query, (username,))
		result = c.fetchone()
		self.__db.commit()
		return result


	# Fetch the filesystems that belong to the given user
	def fetch_filesystems(self, user_id):
		c     = self.__db.cursor(dictionary=True)
		query = "SELECT * FROM `filesystems` WHERE `user_id`=%s"
		c.execute(query, (user_id,))
		result = c.fetchall()
		self.__db.commit()
		print(result)
		return result


	# Update the filesystem's virtual path
	def set_filesystem_path(self, fs_id, path):
		c     = self.__db.cursor()
		query = "UPDATE `filesystems` SET `path`=%s WHERE `id`=%s"
		c.execute(query, (path, fs_id))
		self.__db.commit()
