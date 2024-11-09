
# Restricted SSH manager for rsync
# 
# Example usage:
# 
# from rssh import *
# con = rssh("kuwisdelu", "Magi-02", "login.khoury.northeastern.edu")
# con.isopen()
# mkfile("~/Scratch/test")
# con.upload("~/Scratch/test", "Scratch/test")
# rmfile("~/Scratch/test")
# con.download("Scratch/test", "~/Scratch/test")
# con.rsync("Scratch/test", "Scratch/test2")
# con.rsync("Scratch/test", "Scratch/test2", target="Magi-03")
# con.ssh()
# con.close()
# 

import subprocess
import os

def askYesNo(msg = "Continue? (yes/no): "):
	"""
	Ask a user to confirm yes or no
	:param msg: The message to print
	:returns: True if yes, False if no
	"""
	while True:
		confirm = input(msg)
		if confirm in ("y", "yes"):
			return True
		elif confirm in ("n", "no"):
			return False
		else:
			print("Invalid input. Please enter yes/no.")

def normalizePath(path, mustWork = True):
	"""
	Normalize and expand paths
	:param path: The path to normalize
	:param mustWork: Must the path exist?
	:returns: The normalized path
	"""
	if "~" in path:
		path = os.path.expanduser(path)
	path = os.path.realpath(path)
	if mustWork and not os.path.exists(path):
		raise FileNotFoundError("path does not exist")
	return path

def mkfile(path):
	"""
	Create a file
	:param path: The file to create
	"""
	path = normalizePath(path, mustWork=False)
	with open(path, "a"):
		os.utime(path, None)

def rmfile(path):
	"""
	Delete a file
	:param path: The file to delete
	"""
	path = normalizePath(path, mustWork=False)
	if os.path.exists(path):
		os.remove(path)

class rssh:
	"""
	Restricted SSH manager for rsync
	"""
	
	def __init__(self, username, destination,
		server = None, server_username = None,
		port = 8080, destination_port = 22,
		autoconnect = True):
		"""
		Initialize an rssh instance
		:param username: Your username on destination machine
		:param destination: The destination machine hostname
		:param server: The gateway server hostname (optional)
		:param server_username: Your username on the gateway server (optional)
		:param port: The local port for gateway server SSH forwarding
		:param destination_port: The destination port
		:param autoconnect: Connect on initialization?
		"""
		if server is not None:
			if server_username is None:
				server_username = username
		self.username = username
		self.destination = destination
		self.server = server
		self.server_username = server_username
		self.port = port
		self.destination_port = destination_port
		self.process = None
		if autoconnect:
			self.open()
	
	def __str__(self):
		"""
		Return str(self)
		"""
		dest = f"{self.username}@{self.destination}"
		if self.isopen():
			server = f"(forwarding to {self.server} over {self.port})"
			return "ssh: " + dest + " " + server
		else:
			return "ssh: " + dest
	
	def __repr__(self):
		"""
		Return repr(self)
		"""
		user = f"username='{self.username}'"
		dest = f"destination='{self.destination}'"
		if self.isopen():
			server = f"server='{self.server}'"
			server_username = f"server_username='{self.server_username}'"
			port = f"port={self.port}"
			return f"rssh({user}, {dest}, {server}, {server_username}, {port})"
		else:
			return f"rssh({user}, {dest})"
	
	def __enter__(self):
		"""
		Enter context manager
		"""
		self.open()
		return self
	
	def __exit__(self, exc_type, exc_value, traceback):
		"""
		Exit context manager
		"""
		self.close()
	
	def __del__(self):
		"""
		Delete self
		"""
		self.close()
	
	def isopen(self):
		"""
		Check if the gateway server connection is open
		"""
		return self.process is not None

	def open(self):
		"""
		Open the connection to the gateway server
		"""
		if self.server is None or self.isopen():
			return
		print(f"connecting to {self.server}")
		if self.server_username is None:
			msg = "Please enter your username: "
			self.server_username = input(msg)
		gateway = f"{self.server_username}@{self.server}"
		target = f"{self.port}:{self.destination}:{self.destination_port}"
		cmd = ["ssh", "-NL", target, gateway]
		try:
			self.process = subprocess.Popen(cmd)
			print(f"forwarding to {self.destination} on port {self.port}")
		except:
			self.process = None
			print("failed to open connection")
	
	def copy_id(self, id_file, ask = False):
		"""
		Copy local SSH keys to the destination machine
		:param id_file: The identity file (ending in .pub)
		:param ask: Confirm before copying?
		"""
		truedest = f"{self.username}@{self.destination}"
		if self.server is None:
			dest = truedest
		else:
			if not self.isopen():
				self.open()
			dest = f"{self.username}@localhost"
		print(f"key will be uploaded from: '{id_file}'")
		print(f"key will be uploaded to: '{truedest}'")
		if ask and not askYesNo():
			return
		print(f"copying key as {self.username}@{self.destination}")
		id_file = normalizePath(id_file, mustWork=True)
		cmd = ["ssh-copy-id", "-i", id_file]
		if self.server is None:
			cmd += [dest]
			return subprocess.run(cmd)
		else:
			cmd += ["-o", "NoHostAuthenticationForLocalhost=yes"]
			cmd += ["-p", str(self.port)]
			cmd += [dest]
			return subprocess.run(cmd)
	
	def download(self, src, dest, dryrun = False, ask = False):
		"""
		Download file(s) to local storage using rsync
		:param src: The source path on the destination machine
		:param dest: The destination path on the local machine
		:param dryrun: Show what would be done without doing it?
		:param ask: Confirm before downloading?
		"""
		truesrc = f"{self.username}@{self.destination}:{src}"
		if self.server is None:
			src = truesrc
		else:
			if not self.isopen():
				self.open()
			src = f"{self.username}@localhost:{src}"
		print(f"data will be downloaded from: '{truesrc}'")
		print(f"data will be downloaded to: '{dest}'")
		if ask and not askYesNo():
			return
		print(f"downloading data as {self.username}@{self.destination}")
		dest = normalizePath(dest, mustWork=False)
		if self.server is None:
			cmd = ["rsync", "-aP", src, dest]
			if dryrun:
				cmd += ["--dry-run"]
			return subprocess.run(cmd)
		else:
			rsh = ["ssh", "-o", "NoHostAuthenticationForLocalhost=yes"]
			rsh = " ".join(rsh + ["-p", str(self.port)])
			rsh = f"--rsh='{rsh}'"
			cmd = ["rsync", "-aP", rsh, src, dest]
			cmd = " ".join(cmd)
			if dryrun:
				cmd += ["--dry-run"]
			return subprocess.run(cmd, shell=True)
	
	def upload(self, src, dest, dryrun = False, ask = False):
		"""
		Upload file(s) from local storage using rsync
		:param src: The source path on the local machine
		:param dest: The destination path on the destination machine
		:param dryrun: Show what would be done without doing it?
		:param ask: Confirm before uploading?
		"""
		truedest = f"{self.username}@{self.destination}:{dest}"
		if self.server is None:
			dest = truedest
		else:
			if not self.isopen():
				self.open()
			dest = f"{self.username}@localhost:{dest}"
		print(f"data will be uploaded from: '{src}'")
		print(f"data will be uploaded to: '{truedest}'")
		if ask and not askYesNo():
			return
		print(f"uploading data as {self.username}@{self.destination}")
		src = normalizePath(src, mustWork=True)
		if self.server is None:
			cmd = ["rsync", "-aP", src, dest]
			if dryrun:
				cmd += ["--dry-run"]
			return subprocess.run(cmd)
		else:
			rsh = ["ssh", "-o", "NoHostAuthenticationForLocalhost=yes"]
			rsh = " ".join(rsh + ["-p", str(self.port)])
			rsh = f"--rsh='{rsh}'"
			cmd = ["rsync", "-aP", rsh, src, dest]
			if dryrun:
				cmd += ["--dry-run"]
			cmd = " ".join(cmd)
			return subprocess.run(cmd, shell=True)
	
	def rsync(self, src, dest, target = None, dryrun = False, ask = False):
		"""
		Sync file(s) using rsync from destination machine
		:param src: The source path on the destination machine
		:param dest: The destination path on the target machine
		:param target: The target machine (if different from destination)
		:param dryrun: Show what would be done without doing it?
		:param ask: Confirm before syncing?
		"""
		truehost = f"{self.username}@{self.destination}"
		if self.server is None:
			host = truehost
			cmd = ["ssh", host]
		else:
			host = f"{self.username}@localhost"
			cmd = ["ssh", "-p", str(self.port), host]
		if target is None:
			target = truehost
			cmd += ["rsync", "-aP", src, dest]
		else:
			target = f"{self.username}@{target}"
			cmd += ["rsync", "-aP", src, f"{target}:{dest}"]
		print(f"data will be copied from: '{truehost}:{src}'")
		print(f"data will be copied to: '{target}:{dest}'")
		if ask and not askYesNo():
			return
		else:
			if dryrun:
				cmd += ["--dry-run"]
			return subprocess.run(cmd)
	
	def ssh(self):
		"""
		Attach an unrestricted ssh terminal session
		"""
		truedest = f"{self.username}@{self.destination}"
		if self.server is None:
			dest = truedest
		else:
			if not self.isopen():
				self.open()
			dest = f"{self.username}@localhost"
		print(f"connecting as {self.username}@{self.destination}")
		if self.server is None:
			cmd = ["ssh", dest]
			return subprocess.run(cmd)
		else:
			cmd = ["ssh", "-o", "NoHostAuthenticationForLocalhost=yes"]
			cmd += ["-p", str(self.port), dest]
			return subprocess.run(cmd)
	
	def close(self):
		"""
		Close the connection to the gateway server
		"""
		if self.process is None:
			return
		print(f"closing connection to {self.server}")
		self.process.terminate()
		self.process = None

