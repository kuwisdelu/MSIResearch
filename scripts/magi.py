
# Magi cluster utilities + CLI
# 
# Example usage:
# 
# magi -h
#

import sys
import os
import subprocess
import argparse
from time import sleep

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
	parser.add_argument("-m", "--readme", action="store_true",
		help="display readme file")
	parser.add_argument("-p", "--pager", action="store",
		help="program to display readme (default 'glow')")
	parser.add_argument("-w", "--width", action="store",
		help="word-wrap readme at width (default 70)", default=70)
	subparsers = parser.add_subparsers(dest="cmd")
	# subcommands
	cmd_run = subparsers.add_parser("run", 
		help="run command (e.g., login shell) on a Magi node")
	cmd_copy_id = subparsers.add_parser("copy-id", 
		help="copy ssh keys to a Magi node")
	cmd_download = subparsers.add_parser("download", 
		help="download file(s) from a Magi node")
	cmd_upload = subparsers.add_parser("upload", 
		help="upload file(s) to a Magi node")
	# common arguments
	def add_common_args(p):
		p.add_argument("-01", action="append_const",
			help="Magi-01", dest="nodes", const="01")
		p.add_argument("-02", action="append_const",
			help="Magi-02", dest="nodes", const="02")
		p.add_argument("-03", action="append_const",
			help="Magi-03", dest="nodes", const="03")
		p.add_argument("-p", "--port", action="store",
			help="port forwarding", default=config.port)
		p.add_argument("-u", "--user", action="store",
			help="Magi user", default=config.username)
		p.add_argument("-L", "--login", action="store",
			help="gateway server user", default=config.server_username)
		p.add_argument("-S", "--server", action="store",
			help="gateway server host", default=config.server)
	# run subcommand
	add_common_args(cmd_run)
	# copy-id subcommand
	add_common_args(cmd_copy_id)
	cmd_copy_id.add_argument("identity_file", action="store",
		help="ssh key identity file")
	# download subcommand
	cmd_download.add_argument("src", action="store",
		help="source file/directory")
	cmd_download.add_argument("dest", action="store",
		help="destination file/directory")
	cmd_download.add_argument("-a", "--ask", action="store_true",
		help="ask to confirm before downloading?")
	cmd_download.add_argument("-n", "--dry-run", action="store_true",
		help="show what would be transferred?")
	add_common_args(cmd_download)
	# upload subcommand
	cmd_upload.add_argument("src", action="store",
		help="source file/directory")
	cmd_upload.add_argument("dest", action="store",
		help="destination file/directory")
	cmd_upload.add_argument("-a", "--ask", action="store_true",
		help="ask to confirm before uploading?")
	cmd_upload.add_argument("-n", "--dry-run", action="store_true",
		help="show what would be transferred?")
	add_common_args(cmd_upload)
	return parser

def get_node_from_list(nodes = None):
	"""
	Get Magi nodename from a list of Magi node ids
	:param nodes: A list of nodes ('01', '02', etc.)
	"""
	if nodes is None or len(nodes) < 1:
		sys.exit("magi: error: missing Magi host (-01, -02, -03)")
	if len(nodes) > 1:
		sys.exit("magi: error: must specify exactly _one_ Magi host")
	host = f"Magi-{nodes[0]}"
	if config.is_Magi:
		if host.casefold() == config.localhost.casefold():
			host = "localhost"
		else:
			host += ".local"
	return host

def open_ssh(user = None, node = None,
	login = None, server = None, port = None):
	"""
	Open connection to a Magi node
	:param user: Magi username
	:param node: Magi nodename
	:param login: Login gateway username
	:param server: Login gateway server
	:param port: Port used for gateway forwarding
	"""
	if user is None:
		user = config.username
	if node is None:
		node = config.remote_dbhost
	if login is None:
		login = config.server_username
	if server is None:
		server = config.server
	if port is None:
		port = config.port
	# connect and return the session
	session = rssh(user, node,
		server=server,
		server_username=login,
		port=port,
		autoconnect=True)
	return session

def main(args):
	"""
	Run the CLI
	:param args: The parsed command line arguments
	"""
	# readme
	if args.readme:
		file = os.path.join(config.dbpath, "MSIResearch", "Magi-README.md")
		if args.pager is None:
			cmd = ["glow", "-p", "-w", str(args.width)]
		else:
			cmd = [args.pager, file]
		cmd += [file]
		subprocess.run(cmd)
		sys.exit()
	# help
	elif args.cmd is None:
		parser.print_help()
		sys.exit()
	# open ssh
	else:
		con = open_ssh(args.user,
			node=get_node_from_list(args.nodes),
			login=args.login, server=args.server,
			port=args.port)
		sleep(1) # allow time to connect
	# run
	if args.cmd == "run":
		con.ssh()
	# copy-id
	elif args.cmd == "copy-id":
		con.copy_id(args.identity_file)
	# download
	elif args.cmd == "download":
		con.download(args.src, args.dest,
			dryrun=args.dry_run, ask=args.ask)
	# upload
	elif args.cmd == "upload":
		con.upload(args.src, args.dest,
			dryrun=args.dry_run, ask=args.ask)
	sys.exit()

if __name__ == "__main__":
	parser = get_parser()
	args = parser.parse_args()
	main(args)

