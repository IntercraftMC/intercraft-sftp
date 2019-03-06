import _thread

# A threadsafe VFS store
class VfsStore:

	def __init__(self, db, vfs_class):
		self.__db    = db
		self.__vfs   = vfs_class
		self.__store = {}
		self.__lock  = _thread.allocate_lock()


	# Load a VFS reference
	def load(self, user_id):
		with self.__lock:
			if user_id not in self.__store:
				self.__store[user_id] = {
					"sessions": 0,
					"vfs": self.__vfs(self.__db, user_id)
				}
			self.__store[user_id]["sessions"] += 1
		return self.__store[user_id]["vfs"]


	# Unload a VFS reference
	def unload(self, user_id):
		with self.__lock:
			if user_id in self.__store:
				self.__store[user_id]["sessions"] -= 1
				if self.__store[user_id]["sessions"] <= 0:
					del self.__store[user_id]
