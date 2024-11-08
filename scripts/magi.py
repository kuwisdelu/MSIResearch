
# Magi cluster utilities + CLI
# 
# Example usage:
# 
# magi -h
#

import sys
import os
import argparse

import config
from rssh import *

def get_parser():
	"""
	Parse arguments for the CLI
	"""
	# help description
	description = """
		Magi cluster utilities
		"""
	# argument parser
	parser = argparse.ArgumentParser("magi",
		description=description)
	subparsers = parser.add_subparsers(dest="cmd")
	# subcommands
	cmd_connect = subparsers.add_parser("connect", 
		help="connect ssh session to a Magi node")
	cmd_copy_id = subparsers.add_parser("copy-id", 
		help="copy ssh keys to a Magi node")
	cmd_download = subparsers.add_parser("download", 
		help="download file(s) from Magi")
	cmd_upload = subparsers.add_parser("upload", 
		help="upload file(s) to Magi")
	cmd_sync = subparsers.add_parser("sync", 
		help="sync file(s) across Magi nodes")
	# common arguments
	def add_common_args(p):
		p.add_argument("-01", action="append_const",
			help="Magi-01", dest="node", const="01")
		p.add_argument("-02", action="append_const",
			help="Magi-02", dest="node", const="02")
		p.add_argument("-03", action="append_const",
			help="Magi-03", dest="node", const="03")
		p.add_argument("-p", "--port", action="store",
			help="port forwarding", default=config.port)
		p.add_argument("-u", "--user", action="store",
			help="Magi user", default=config.username)
		p.add_argument("-L", "--login", action="store",
			help="gateway server user", default=config.server_username)
		p.add_argument("-S", "--server", action="store",
			help="gateway server host", default=config.server)
	# connect subcommand
	add_common_args(cmd_connect)
	# copy-id subcommand
	add_common_args(cmd_copy_id)
	# download subcommand
	cmd_download.add_argument("src", action="store",
		help="source file/directory")
	cmd_download.add_argument("dest", action="store",
		help="destination file/directory")
	cmd_download.add_argument("-a", "--ask", action="store_true",
		help="ask to confirm before downloading?")
	add_common_args(cmd_download)
	# upload subcommand
	cmd_upload.add_argument("src", action="store",
		help="source file/directory")
	cmd_upload.add_argument("dest", action="store",
		help="destination file/directory")
	cmd_upload.add_argument("-a", "--ask", action="store_true",
		help="ask to confirm before uploading?")
	add_common_args(cmd_upload)
	return parser

def open_ssh(user = None, host = None, port = None):
	"""
	Open connection to a Magi node
	:param user: Magi username
	:param host: Magi hostname
	"""
	if user is None:
		user = config.username
	if host is None:
		host = config.remote_dbhost
	if port is None:
		port = config.port
	# connect and return the session
	session = rssh(user, host,
		server=config.server,
		server_username=config.server_username,
		port=port,
		autoconnect=True)
	return session

def main(args):
	"""
	Run the CLI
	:param args: The parsed command line arguments
	"""
	# help
	if args.cmd is None:
		parser.print_help()
	else:
		print(args)

if __name__ == "__main__":
	parser = get_parser()
	args = parser.parse_args()
	main(args)

