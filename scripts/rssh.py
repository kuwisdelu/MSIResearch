
# Restricted SSH manager for rsync
# 
# Example usage:
# 
# from rssh import *
# con = rssh("kuwisdelu", "Magi-02", "login.khoury.northeastern.edu")
# con.isopen()
# print(con)
# mkfile("~/Scratch/test")
# con.upload("~/Scratch/test", "Scratch/test")
# rmfile("~/Scratch/test")
# con.download("Scratch/test", "~/Scratch/test")
# con.close()
# 

import subprocess
import os

def normalizePath(path, mustWork = True):
	"""
	Normalize and expand paths
	:param path: The path to normalize
	:param mustWork: Must the path exist?
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
		port = 8080, destination_port = 22):
		"""
		Initialize an rssh instance
		:param username: Your username on destination machine
		:param destination: The destination machine hostname
		:param server: The gateway server hostname (optional)
		:param server_username: Your username on the gateway server (optional)
		:param port: The local port for gateway server SSH forwarding
		:param destination_port: The destination port
		"""
		if server_username is None:
			server_username = username
		self.username = username
		self.destination = destination
		self.server = server
		self.server_username = server_username
		self.port = port
		self.destination_port = destination_port
		self.process = None
		self.open()
	
	def __str__(self):
		dest = f"{self.username}@{self.destination}"
		if self.isopen():
			server = f"(forwarding to {self.server} over {self.port})"
			return "ssh: " + dest + " " + server
		else:
			return "ssh: " + dest
	
	def __repr__(self):
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
		self.open()
		return self
	
	def __exit__(self, exc_type, exc_value, traceback):
		self.close()
	
	def __del__(self):
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
	
	def download(self, src, dest, ask = False):
		"""
		Download file(s) using rsync over ssh
		:param src: The source path on the remote machine
		:param dest: The destination path on the local machine
		:param ask: Confirm before downloading?
		"""
		truesrc = f"{self.username}@{self.destination}:{src}"
		if self.server is None:
			src = truesrc
		else:
			if not self.isopen():
				raise ConnectionError("connection is close; call open()")
			src = f"{self.username}@localhost:{src}"
		print(f"data will be downloaded from: '{truesrc}'")
		print(f"data will be downloaded to: '{dest}'")
		while ask:
			msg = "Continue? (yes/no): "
			confirm = input(msg)
			if confirm in ["y", "yes"]:
				ask = False
			elif confirm in ["n", "no"]:
				return
			else:
				print("Invalid input. Please enter yes/no.")
		dest = normalizePath(dest, mustWork=False)
		if self.server is None:
			cmd = ["rsync", "-aP", src, dest]
			return subprocess.run(cmd)
		else:
			rsh = ["ssh", "-o", "NoHostAuthenticationForLocalhost=yes"]
			rsh = " ".join(rsh + ["-p", str(self.port)])
			rsh = f"--rsh='{rsh}'"
			cmd = ["rsync", "-aP", rsh, src, dest]
			cmd = " ".join(cmd)
			return subprocess.run(cmd, shell=True)
	
	def upload(self, src, dest, ask = False):
		"""
		Upload file(s) using rsync over ssh
		:param src: The source path on the local machine
		:param dest: The destination path on the remote machine
		:param ask: Confirm before uploading?
		"""
		truedest = f"{self.username}@{self.destination}:{dest}"
		if self.server is None:
			dest = truedest
		else:
			if not self.isopen():
				raise ConnectionError("connection is close; call open()")
			dest = f"{self.username}@localhost:{dest}"
		print(f"data will be uploaded from: '{src}'")
		print(f"data will be uploaded to: '{truedest}'")
		while ask:
			msg = "Continue? (yes/no): "
			confirm = input(msg)
			if confirm in ["y", "yes"]:
				ask = False
			elif confirm in ["n", "no"]:
				return
			else:
				print("Invalid input. Please enter yes/no.")
		src = normalizePath(src, mustWork=True)
		if self.server is None:
			cmd = ["rsync", "-aP", src, dest]
			return subprocess.run(cmd)
		else:
			rsh = ["ssh", "-o", "NoHostAuthenticationForLocalhost=yes"]
			rsh = " ".join(rsh + ["-p", str(self.port)])
			rsh = f"--rsh='{rsh}'"
			cmd = ["rsync", "-aP", rsh, src, dest]
			cmd = " ".join(cmd)
			return subprocess.run(cmd, shell=True)
	
	def close(self):
		"""
		Close the connection to the gateway server
		"""
		if self.process is None:
			return
		print("closing connection to server")
		self.process.terminate()
		self.process = None

