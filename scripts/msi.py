
# MSI database manager CLI
# 
# Example usage:
# 
# msi -h
# msi ls
# msi ls --scope="Public"
# msi ls-cache --details
# msi search "cancer"
# msi describe "PXD001283"
# msi sync "Example_Continuous_imzML"
#

import sys
import os
import argparse

import config
from msidb import *

def get_parser():
	"""
	Parse arguments for the CLI
	"""
	# help description
	description = """
		MSI database manager
		"""
	# argument parser
	parser = argparse.ArgumentParser("msi",
		description=description)
	subparsers = parser.add_subparsers(dest="cmd")
	# subcommands
	cmd_readme = subparsers.add_parser("readme", 
		help="show readme")
	cmd_ls = subparsers.add_parser("ls", 
		help="list all datasets")
	cmd_ls_cache = subparsers.add_parser("ls-cache", 
		help="list cached datasets")
	cmd_search = subparsers.add_parser("search", 
		help="search all datasets")
	cmd_search_cache = subparsers.add_parser("search-cache", 
		help="search cached datasets")
	cmd_describe = subparsers.add_parser("describe", 
		help="describe a dataset")
	cmd_sync = subparsers.add_parser("sync", 
		help="sync a dataset")
	# readme subcommand
	cmd_readme.add_argument("-w", "--width", action="store",
		help="word-wrap at width (default 70)", default=70)
	# ls subcommand
	cmd_ls.add_argument("-s", "--scope", action="store",
		help="filter by scope")
	cmd_ls.add_argument("-g", "--group", action="store",
		help="filter by group")
	cmd_ls.add_argument("-l", "--details", action="store_true",
		help="show full details")
	# ls-cache subcommand
	cmd_ls_cache.add_argument("-s", "--scope", action="store",
		help="filter by scope")
	cmd_ls_cache.add_argument("-g", "--group", action="store",
		help="filter by group")
	cmd_ls_cache.add_argument("-l", "--details", action="store_true",
		help="show full details")
	# search subcommand
	cmd_search.add_argument("pattern", action="store",
		help="search pattern (regex allowed)")
	cmd_search.add_argument("-s", "--scope", action="store",
		help="filter by scope")
	cmd_search.add_argument("-g", "--group", action="store",
		help="filter by group")
	# search-cache subcommand
	cmd_search_cache.add_argument("pattern", action="store",
		help="search pattern (regex allowed)")
	cmd_search_cache.add_argument("-s", "--scope", action="store",
		help="filter by scope")
	cmd_search_cache.add_argument("-g", "--group", action="store",
		help="filter by group")
	# describe subcommand
	cmd_describe.add_argument("name", action="store",
		help="the identifier of the dataset to describe")
	# sync subcommand
	cmd_sync.add_argument("name", action="store",
		help="the identifier of the dataset to sync")
	cmd_sync.add_argument("-a", "--ask", action="store_true",
		help="ask to confirm before syncing?")
	cmd_sync.add_argument("-f", "--force", action="store_true",
		help="force re-sync if already cached")
	cmd_sync.add_argument("-p", "--port", action="store",
		help="port forwarding", default=config.port)
	cmd_sync.add_argument("-u", "--user", action="store",
		help="remote database user", default=config.username)
	cmd_sync.add_argument("-L", "--login", action="store",
		help="gateway server user", default=config.server_username)
	cmd_sync.add_argument("-S", "--server", action="store",
		help="gateway server host", default=config.server)
	cmd_sync.add_argument("--remote-host", action="store",
		help="remote database host", default=config.remote_dbhost)
	cmd_sync.add_argument("--remote-path", action="store",
		help="remote database path", default=config.remote_dbpath)
	return parser

def open_db(dbpath = None):
	"""
	Open connection to the database
	:param dbpath: The local database path
	"""
	if dbpath is None:
		dbpath = config.dbpath
	# check for valid database path
	if not os.path.isdir(dbpath):
		raise NotADirectoryError(f"database does not exist: '{dbpath}'")
	if not os.path.isdir(os.path.join(dbpath, "MSIResearch")):
		raise FileNotFoundError(f"database is not valid: '{dbpath}'")
	# connect and return database
	db = msidb(config.username, dbpath,
		remote_dbhost=config.remote_dbhost,
		remote_dbpath=config.remote_dbpath,
		server=config.server,
		server_username=config.server_username,
		port=config.port,
		verbose=False,
		autoconnect=False)
	return db

def main(args):
	"""
	Run the CLI
	:param args: The parsed command line arguments
	"""
	# help
	if args.cmd is None:
		parser.print_help()
		sys.exit()
	# readme
	elif args.cmd == "readme":
		file = os.path.join(config.dbpath, "MSIResearch", "README.md")
		cmd = ["glow", "-p", "-w", str(args.width), file]
		subprocess.run(cmd)
		sys.exit()
	# open database
	else:
		db = open_db()
	# ls
	if args.cmd == "ls":
		datasets = db.ls(
			scope=args.scope,
			group=args.group,
			details=args.details)
		if args.details:
			print_datasets(datasets)
		else:
			for name in datasets:
				print(f"['{name}']")
	# ls-cache
	elif args.cmd == "ls-cache":
		datasets = db.ls_cache(
			scope=args.scope,
			group=args.group,
			details=args.details)
		if args.details:
			print_datasets(datasets)
		else:
			for name in datasets:
				print(f"['{name}']")
	# search
	elif args.cmd == "search":
		hits = db.search(
			pattern=args.pattern,
			scope=args.scope,
			group=args.group)
		print_datasets(hits)
	# search-cache
	elif args.cmd == "search-cache":
		hits = db.search_cache(
			pattern=args.pattern,
			scope=args.scope,
			group=args.group)
		print_datasets(hits)
	# describe
	elif args.cmd == "describe":
		dataset = db.get(args.name)
		if dataset is None:
			sys.exit(f"msi describe: error: no such dataset: '{args.name}'")
		else:
			print(dataset.describe())
	# sync
	elif args.cmd == "sync":
		if args.name in db.cache and not args.force:
			print("msi sync: dataset is already cached; use --force to re-sync")
			sys.exit()
		db.username = args.user
		db.remote_dbhost = args.remote_host
		db.remote_dbpath = args.remote_path
		db.server = args.server
		db.server_username = args.login
		db.port = args.port
		db.sync(args.name,
			force=args.force,
			ask=args.ask)
	db.close()
	sys.exit()

if __name__ == "__main__":
	parser = get_parser()
	args = parser.parse_args()
	main(args)

