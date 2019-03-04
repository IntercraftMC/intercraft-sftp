import os

# Convert flags into an open mode string for a file
def file_open_mode(flags):
	if flags & os.O_WRONLY:
		if flags & os.O_APPEND:
			return "ab"
		else:
			return "wb"
	elif flags & os.O_RDWR:
		if flags & os.O_APPEND:
			return "a+b"
		else:
			return "r+b"
	return "rb"
