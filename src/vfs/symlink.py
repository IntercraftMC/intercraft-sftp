from pathlib import Path

class Symlink:

	def __init__(self, target, extra=None):
		self.__target = Path(target)
		self.__extra = extra


	def target(self):
		return self.__target


	def extra(self):
		return self.__extra


	def exists(self):
		return self.__target.exists()


	def __truediv__(self, other):
		return self.__target / other


	def __str__(self):
		return str(self.__target)
