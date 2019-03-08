import os
from pathlib import Path
from . vfs import Vfs
from . vfs import Symlink
import pprint

class IntercraftVfs(Vfs):

	# Initialize the symlinks in the VFS
	def update_symlinks(self):
		self.update_oc_symlinks()


	# Update the OpenComputers symlinks
	def update_oc_symlinks(self):
		# Remove the OpenComputers directory first if it exists
		if "OpenComputers" in self.root():
			del self.root()["OpenComputers"]

		self.add_system_path("/OpenComputers/Creative", True)
		self.add_system_path("/OpenComputers/Survival", True)

		# Add the symlinks
		for fs in self.db().fetch_filesystems(self.user_id()):
			if fs["is_creative"]:
				real_path    = Path(os.getenv("FS_CREATIVE")) / fs["uuid"]
				virtual_path = Path("/OpenComputers/Creative")
			else:
				real_path    = Path(os.getenv("FS_SURVIVAL")) / fs["uuid"]
				virtual_path = Path("/OpenComputers/Survival")
			self.add_symlink(virtual_path / (fs["path"] or fs["uuid"]), real_path, True, {
				"fs": fs
			})


	# Update the database when an FS symlink is moved
	def validate_virtual_rename(self, old_path, new_path):
		opath = self.resolve_path(old_path)
		if Path(new_path).name == "__UUID__":
			if isinstance(opath, Symlink) and "fs" not in opath.extra():
				return False
			if not isinstance(opath, Symlink):
				return False
		return True


	# Change the name of the symlink if applicable
	def adjust_symlink_name(self, symlink, name):
		if "fs" in symlink.extra():
			if name == "__UUID__":
				return symlink.extra()["fs"]["uuid"]
		return name


	# Update the symlink path in the database
	def update_symlink_path(self, symlink, path):
		if "fs" in symlink.extra():
			self.db().set_filesystem_path(symlink.extra()["fs"]["id"], str(path))
