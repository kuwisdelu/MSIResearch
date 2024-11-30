
import os
import platform

import rssh

# Shell environment variables:
# $MSI_DBPATH = /path/to/database
# $MAGI_LOGIN = <khoury-username>
# $MAGI_USER =  <magi-username>

# get global defaults
known_hosts = ["Magi-01", "Magi-02", "Magi-03"]
known_hosts = [host.casefold() for host in known_hosts]

# get local environment
dbpath = os.getenv("MSI_DBPATH", default="/Volumes/Datasets/")
localhost = platform.node().replace(".local", "")
localuser = os.getlogin()
port = rssh.findport()

# check if running on a Magi node
is_Magi = localhost.casefold() in known_hosts

# set up defaults
if is_Magi:
	# Magi host defaults
	username = localuser
	remote_dbhost = "Magi-03.local"
	remote_dbpath = "/Volumes/Datasets"
	server = None
	server_username = None
else:
	# remote client defaults
	username = os.getenv("MAGI_USER", default="viteklab")
	remote_dbhost = "Magi-03"
	remote_dbpath = "/Volumes/Datasets"
	server = "login.khoury.northeastern.edu"
	server_username = os.getenv("MAGI_LOGIN", default=None)
