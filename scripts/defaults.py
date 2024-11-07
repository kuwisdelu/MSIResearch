
import os
import platform

# get global defaults
known_hosts = ["Magi-01", "Magi-02", "Magi-03"]

# get local environment
dbpath = os.getenv("MSI_DBPATH", default="/Volumes/Datasets/")
localhost = platform.node().replace(".local", "")
localuser = os.getlogin()

# set up local defaults
if localhost in known_hosts:
	# Magi host defaults
	username = localuser
	remote_dbhost = "Magi-03.local"
	remote_dbpath = "/Volumes/Datasets"
	server = None
	server_username = None
	port = 8080
else:
	# remote client defaults
	username = "viteklab"
	remote_dbhost = "Magi-03"
	remote_dbpath = "/Volumes/Datasets"
	server = "login.khoury.northeastern.edu"
	server_username = None
	port = 8080
