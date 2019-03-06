import os
from pathlib import Path
from . symlink import Symlink

# The VirtualFilesystem will allow us to have custom
# home folder structures held entirely in memory.
class Vfs:

	def __init__(self, db, user_id):

		self.__db = db
		self.__user_id = user_id

		# The VFS file tree
		self.__fs   = {
			"dirs" : {},
			"write": False
		}

		# Update the symlinks
		self.update_symlinks()


	# Get the reference to the database
	def db(self):
		return self.__db


	# Get a reference to the user ID
	def user_id(self):
		return self.__user_id


	# Initialize the symlinks in the VFS
	def update_symlinks(self):
		pass


	# Validate the virtual mkdir
	def validate_virtual_mkdir(self, path):
		return True


	def validate_virtual_rename(self, old_path, new_path):
		return False


	def adjust_symlink_name(self, symlink, name):
		return name


	def update_symlink_path(self, symlink, path):
		return None


	# Create a system virtual directory/path
	def add_system_path(self, path, write=False):
		vpath = Path(path).resolve()
		current = self.root()
		for part in self.split_path(vpath):
			if part not in current["dirs"]:
				current["dirs"][part] = {
					"dirs" : {},
					"write": write and current["write"]
				}
			current = current["dirs"][part]
		current["write"] = write
		return current


	# Add a symlink to the VFS
	def add_symlink(self, virtual_path, target, dynamic=False, extra=None):
		vpath = Path(virtual_path).resolve()
		vdir = self.add_system_path(vpath.parent, dynamic)
		vdir["dirs"][vpath.name] = Symlink(target, extra)


	# Normalize and split a path into parts
	def split_path(self, path):
		if isinstance(path, str):
			path = Path(path)
		if path.resolve().parts[0] == '/':
			return path.parts[1:] # Trim off the leading slash `/`
		return path.parts


	# Resolve the path to a virtual or physical directory
	def resolve_path(self, path):
		parts = self.split_path(path)
		current = self.root()
		for i, part in enumerate(parts):
			if isinstance(current, Symlink):
				return current / str.join('/', parts[i:])
			if part not in current["dirs"]:
				return None
			current = current["dirs"][part]
		return current


	def can_virtual_move(self, old_path, new_path):
		opath = Path(old_path).resolve().parent
		npath = Path(new_path).resolve().parent
		deepest = [None, None]
		for i, path in enumerate((opath, npath)):
			current = self.root()
			for part in self.split_path(path):
				if part not in current["dirs"]:
					raise OSError(os.errno.ENOENT, "")
				if not current["write"] and current["dirs"][part]["write"]:
					deepest[i] = current["dirs"][part]
				current = current["dirs"][part]
		return deepest[0] is not None and deepest[0] is deepest[1]


	# Get the root folder
	def root(self):
		return self.__fs

	# Custom methods to replace the usual `os` functions regarding the filesystem ------------------

	# List the directories in a folder
	def listdir(self, path):
		dir = self.resolve_path(path)
		if dir is None:
			raise OSError()
		if isinstance(dir, Symlink) or isinstance(dir, Path):
			return os.listdir(str(dir))
		return list(dir["dirs"].keys())


	# Stat a directory
	def stat(self, path):
		dir = self.resolve_path(path)
		if dir is None:
			raise OSError()
		if isinstance(dir, Path):
			return os.stat(str(dir))
		return os.stat_result((16877, 2, 66310, 24, 0, 0, 4096, 0, 0, 0))


	# Remove a file
	def remove(self, path):
		dir = self.resolve_path(path)
		if dir is None:
			raise OSError()
		if isinstance(dir, Path):
			return os.remove(str(dir))
		return OSError()


	# Rename/move a file
	def rename(self, old_path, new_path):
		old_dir = self.resolve_path(old_path)
		new_dir = self.resolve_path(new_path)
		if old_dir is None:
			raise OSError(os.errno.ENOENT, "")
		elif isinstance(old_dir, Path):
			if isinstance(new_dir, Path):
				return os.rename(str(old_dir), str(new_dir))
			raise OSError(os.errno.EACCES)
		elif isinstance(new_dir, Path):
			raise OSError(os.errno.EPERM)
		elif new_dir:
			raise OSError(os.errno.EEXIST, "")
		elif old_dir and self.can_virtual_move(old_path, new_path):
			if self.validate_virtual_rename(old_path, new_path):
				if isinstance(old_dir, Symlink):
					new_name = self.adjust_symlink_name(old_dir, Path(new_path).name)
					if new_name:
						new_path = Path(new_path).parent / new_name
					self.update_symlink_path(old_dir, new_path)
				# Move the virtual folder to the new location in the structure
				del self.resolve_path(Path(old_path).parent)["dirs"][Path(old_path).name]
				self.resolve_path(Path(new_path).parent)["dirs"][Path(new_path).name] = old_dir
				return
		raise OSError()


	# Create a directory
	def mkdir(self, path):
		dir = self.resolve_path(path)
		if isinstance(dir, Path):
			return os.mkdir(str(dir), 0o766)
		elif dir is not None:
			raise OSError(os.errno.EEXIST, "")

		# Create a virtual directory
		vpath = Path(path).resolve()
		parent = self.resolve_path(vpath.parent)
		if not parent:
			raise OSError(os.errno.ENOENT, "")
		if not parent["write"]:
			raise OSError(os.errno.EACCES, "")
		if vpath.name in parent["dirs"]:
			raise OSError(os.errno.EEXIST)
		if self.validate_virtual_mkdir(vpath):
			parent["dirs"][vpath.name] = {
				"dirs" : {},
				"write": True
			}
		else:
			raise OSError()


	# Remove a directory
	def rmdir(self, path):
		dir = self.resolve_path(path)
		if isinstance(dir, Path):
			return os.rmdir(str(dir))
		elif dir is None:
			raise OSError(os.errno.ENOENT, "")
		elif isinstance(dir, Symlink):
			raise OSError(os.errno.EACCES, "")

		# Attempt to remove a virtual directory
		vpath  = Path(path).resolve()
		parent = self.resolve_path(vpath.parent)
		child = parent["dirs"][vpath.name]
		if not parent["write"] or isinstance(child, str):
			raise OSError(os.errno.EACCES, "")
		if len(child["dirs"]) > 0:
			raise OSError(os.errno.ENOTEMPTY, "")
		del parent["dirs"][vpath.name]


	# Open a file
	def open(self, path, flags, mode):
		dir = self.resolve_path(path)
		if dir is None:
			return OSError(os.errno.ENOENT, "")
		if isinstance(dir, Path):
			return os.open(str(dir), flags, ((mode | 0o666) & (0xffb6)))
		return OSError()
