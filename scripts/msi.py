
# MSI database manager CLI
# 
# Example usage:
# 
# msi -h
# msi ls
# msi ls --scope="Public"
# msi ls-cache --details
# msi search "cancer"
# msi info "PXD001283"
# msi sync "Example_Continuous_imzML"
#

import sys
import os
import platform
import argparse
from msidb import *

# set up defaults

dbpath = os.getenv("MSI_DBPATH", default="/Volumes/Datasets/")
known_hosts = ["Magi-01", "Magi-02", "Magi-03"]
host = platform.node().replace(".local", "")
user = os.getlogin()

if host in known_hosts:
	# local Magi defaults
	defaults = {"username": user,
		"dbpath": dbpath,
		"remote_dbhost": "Magi-03.local",
		"remote_dbpath": "/Volumes/Datasets",
		"server": None,
		"server_username": None,
		"port": 8080}
else:
	# remote client defaults
	defaults = {"username": "viteklab",
		"dbpath": dbpath,
		"remote_dbhost": "Magi-03",
		"remote_dbpath": "/Volumes/Datasets",
		"server": "login.khoury.northeastern.edu",
		"server_username": None,
		"port": 8080}

help_description ="""
	MSI database manager -
	stored in $MSI_DBPATH (defaults to /Volumes/Datasets/)
	"""

# argument parser
parser = argparse.ArgumentParser("msi",
	description=help_description)
subparsers = parser.add_subparsers(dest="cmd")

# subcommands
cmd_ls = subparsers.add_parser("ls", 
	help="list all datasets")
cmd_ls_cache = subparsers.add_parser("ls-cache", 
	help="list cached datasets")
cmd_search = subparsers.add_parser("search", 
	help="search all datasets")
cmd_search_cache = subparsers.add_parser("search-cache", 
	help="search cached datasets")
cmd_info = subparsers.add_parser("info", 
	help="describe a dataset")
cmd_sync = subparsers.add_parser("sync", 
	help="sync a dataset")

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

# info subcommand
cmd_info.add_argument("name", action="store",
	help="the identifier of the dataset to describe")

# sync subcommand
cmd_sync.add_argument("name", action="store",
	help="the identifier of the dataset to sync")
cmd_sync.add_argument("-f", "--force", action="store_true",
	help="force re-sync if already cached")
cmd_sync.add_argument("-p", "--port", action="store",
	help="port forwarding",
	default=defaults["port"])
cmd_sync.add_argument("-u", "--user", action="store",
	help="remote database user", default=defaults["username"])
cmd_sync.add_argument("-H", "--remote-host", action="store",
	help="remote database host", default=defaults["remote_dbhost"])
cmd_sync.add_argument("-D", "--remote-path", action="store",
	help="remote database path", default=defaults["remote_dbpath"])
cmd_sync.add_argument("-l", "--login", action="store",
	help="gateway server user", default=defaults["server_username"])
cmd_sync.add_argument("-g", "--server", action="store",
	help="gateway server host", default=defaults["server"])

cmd_sync.add_argument("--ask", action="store_true",
	help="ask to confirm before syncing?")

# parse command arguments
args = parser.parse_args()

# connect to database
if not os.path.isdir(dbpath):
	raise NotADirectoryError(f"database does not exist: '{dbpath}'")

if not os.path.isdir(os.path.join(dbpath, "MSIResearch")):
	raise FileNotFoundError(f"database is not valid: '{dbpath}'")

db = msidb(None, dbpath, verbose=False, autoconnect=False)

# help
if args.cmd is None:
	parser.print_help()
# ls
elif args.cmd == "ls":
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
# info
elif args.cmd == "info":
	dataset = db.get(args.name)
	if dataset is None:
		raise KeyError(f"no such dataset: '{args.name}'")
	else:
		print(dataset.describe())
# sync
elif args.cmd == "sync":
	if args.name in db.cache and not args.force:
		print("dataset is already cached; use --force to re-sync")
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

