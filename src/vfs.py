import os
from pathlib import Path

# The VirtualFilesystem will allow us to have custom
# home folder structures held entirely in memory.
class Vfs:

	def __init__(self, filesystems):

		# The VFS file tree
		self.__fs   = {}

		# Initialize the VFS symlinks
		self.init_symlinks(filesystems)


	# Initialize the symlinks in the VFS
	def init_symlinks(self, filesystems):
		PATH_CREATIVE = Path(os.getenv("FS_CREATIVE"))
		PATH_SURVIVAL = Path(os.getenv("FS_SURVIVAL"))

		for fs in filesystems:
			if fs["is_creative"]:
				self.add_symlink("/OpenComputers/Creative/"+fs["uuid"], PATH_CREATIVE / fs["uuid"])
			else:
				self.add_symlink("/OpenComputers/Survival/"+fs["uuid"], PATH_SURVIVAL / fs["uuid"])


	# Add a symlink to the VFS
	def add_symlink(self, virtual_path, target):
		vpath = Path(virtual_path).resolve()
		current = self.root()
		for part in self.split_path(vpath)[:-1]:
			if part not in current:
				current[part] = {}
			current = current[part]
		current[vpath.parts[-1]] = target


	# Normalize and split a path into parts
	def split_path(self, path):
		if isinstance(path, str):
			path = Path(path)
		if path.resolve().parts[0] == '/':
			return path.parts[1:] # Trim off the leading slash `/`
		return path.parts


	# Get the root folder
	def root(self):
		return self.__fs


	# Resolve the path to a virtual or physical directory
	def resolvePath(self, path):
		parts = self.split_path(path)
		current = self.root()
		for i, part in enumerate(parts):
			if part not in current:
				return None
			if isinstance(current[part], Path):
				return current[part] / str.join('/', parts[i+1:])
			current = current[part]
		return current

	# Custom methods to replace the usual `os` functions regarding the filesystem ------------------

	# List the directories in a folder
	def listdir(self, path):
		dir = self.resolvePath(path)
		if dir is None:
			raise OSError()
		if isinstance(dir, Path):
			return os.listdir(str(dir))
		return list(dir.keys())


	# Stat a directory
	def stat(self, path):
		dir = self.resolvePath(path)
		if dir is None:
			raise OSError()
		if isinstance(dir, Path):
			return os.stat(str(dir))
		return os.stat_result((16877, 2, 66310, 24, 0, 0, 4096, 0, 0, 0))


	# Remove a file
	def remove(self, path):
		dir = self.resolvePath(path)
		if dir is None:
			raise OSError()
		if isinstance(dir, Path):
			return os.remove(str(dir))
		return OSError()


	# Rename/move a file
	def rename(self, old_path, new_path):
		old_dir = self.resolvePath(old_path)
		new_dir = self.resolvePath(new_path)
		if isinstance(old_dir, Path) and isinstance(new_dir, Path):
			return os.rename(str(old_dir), str(new_dir))
		raise OSError()


	# Create a directory
	def mkdir(self, path):
		dir = self.resolvePath(path)
		if isinstance(dir, Path):
			return os.mkdir(str(dir))
		raise OSError()


	# Remove a directory
	def rmdir(self, path):
		dir = self.resolvePath(path)
		if isinstance(dir, Path):
			return os.rmdir(str(dir))
		raise OSError()


	# Open a file
	def open(self, path, flags, mode):
		dir = self.resolvePath(path)
		if isinstance(dir, Path):
			return os.open(str(dir), flags, mode)
		return OSError()
