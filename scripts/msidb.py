
# MSI database manager
# 
# Example usage:
# 
# from msidb import *
# db = msidb("viteklab", "/Volumes/Datasets")
# db.ls()
# db.ls(scope="Public")
# db.get("PXD001283")
# print(db["PXD001283"])
# print(db)
# hits = db.search("cancer")
# print_search(hits)
# db.get_cached_dataset("Public", "PRIDE", "PXD001283")
# db.get_cached_group("Public", "PRIDE")
# db.get_cached_scope("Public")
#

import os
import re
import json
from dataclasses import dataclass
from dataclasses import asdict
from datetime import datetime
from rssh import *

def grep1(pattern, x, ignore_case = True, context = None):
	"""
	Search for a pattern in a string
	:param pattern: The pattern to find
	:param x: A string
	:param ignore_case: Should case be ignored?
	:param context: Width of a context window to return
	:returns: A Match or None
	"""
	if ignore_case:
		match = re.search(pattern, x, flags=re.IGNORECASE)
	else:
		match = re.search(pattern, x)
	if match is None or context is None:
		return match
	else:
		start = match.start()
		stop = match.end()
		margin = ((context - (stop - start)) // 2)
		if context > len(x):
			return x
		if context < stop - start or margin < 4:
			return x[start:stop]
		pre, post = "", ""
		if start > margin:
			start = max(0, start - margin)
			pre = "..."
		if len(x) - stop > margin:
			stop = min(len(x), stop + margin)
			post = "..."
		return pre + x[start:stop] + post

def grep(pattern, x, ignore_case = True):
	"""
	Search for a pattern in an iterable
	:param pattern: The pattern to find
	:param x: An iterable
	:param ignore_case: Should case be ignored?
	:returns: A list of matches
	"""
	return [grep1(pattern, xi, ignore_case=ignore_case) 
		for xi 
		in x]

def grepl(pattern, x, ignore_case = True):
	"""
	Search for a pattern in an iterable
	:param pattern: The pattern to find
	:param x: An iterable
	:param ignore_case: Should case be ignored?
	:returns: A list of bools
	"""
	return [match is not None 
		for match 
		in grep(pattern, x, ignore_case=ignore_case)]

def listfiles(path = ".", allnames = False):
	"""
	List files in a directory
	:param path: The directory
	:param allnames: Should hidden files be included?
	:returns: A list of file names
	"""
	path = normalizePath(path)
	if not os.path.isdir(path):
		raise NotADirectoryError("path must be a directory")
	if allnames:
		return [f 
			for f 
			in os.listdir(path)]
	else:
		return [f 
			for f 
			in os.listdir(path)
			if not f.startswith(".")]

def dirsize(path, allnames = False):
	"""
	Get size of a directory
	:param path: The directory
	:param allnames: Should hidden files be included?
	:returns: The size of the directory in bytes
	"""
	size = 0
	files = listfiles(path, allnames=allnames)
	for file in files:
		file = os.path.join(path, file)
		if os.path.isdir(file):
			size += dirsize(file, allnames=allnames)
		elif os.path.exists(file):
			size += os.path.getsize(file)
	return size

def format_bytes(x, units = "auto"):
	"""
	Format bytes
	:param x: The number of bytes
	:param units: The units (B, KB, MB, etc.)
	:returns: A string
	"""
	if units == "auto":
		if x >= 1000 ** 5:
			units = "PB"
		elif x >= 1000 ** 4:
			units = "TB"
		elif x >= 1000 ** 3:
			units = "GB"
		elif x >= 1000 ** 2:
			units = "MB"
		elif x >= 1000:
			units = "KB"
		else:
			units = "bytes"
	if units == "KB":
		x /= 1000
	elif units == "MB":
		x /= 1000 ** 2
	elif units == "GB":
		x /= 1000 ** 3
	elif units == "TB":
		x /= 1000 ** 4
	elif units == "PB":
		x /= 1000 ** 5
	x = round(x, ndigits=2)
	return f"{x} {units}"

@dataclass
class msidata:
	"""
	MSI dataset metadata
	"""
	
	scope: str
	group: str
	title: str
	description: str
	sample_processing: str
	data_processing: str
	contact: dict
	date: dict
	formats: list
	keywords: list
	notes: list
	
	def __init__(self, dataset, printwidth = 60):
		"""
		Initialize an msidata instance
		:param dataset: A dict parsed from manifest.json
		"""
		self.scope = dataset["scope"]
		self.group = dataset["group"]
		self.title = dataset["title"]
		self.description = dataset["description"]
		self.sample_processing = dataset["sample processing"]
		self.data_processing = dataset["data processing"]
		self.contact = dataset["contact"]
		self.date = dataset["date"]
		self.formats = dataset["formats"]
		self.keywords = dataset["keywords"]
		self.notes = dataset["notes"]
		self.printwidth = printwidth
	
	def __str__(self):
		"""
		Return str(self)
		"""
		dataset = asdict(self)
		printed = ["scope", "group", "description",
			"sample_processing", "data_processing"]
		notprinted = set(dataset.keys()).difference(printed)
		notprinted = notprinted.difference(["title"])
		title = self.title
		if ( len(title) > 0 ):
			sl = [f" {title}: "]
		else:
			sl = [" <Untitled>: "]
		sl.append(" {")
		for name in printed:
			desc = dataset[name]
			if len(desc) > self.printwidth:
				desc = desc[:self.printwidth - 4] + "..."
			sl.append(f"  {name}: {desc}")
		more_keys = [f"'{name}'" for name in notprinted]
		more_keys = ", ".join(more_keys)
		sl.append(f"  additional fields: {more_keys}")
		sl.append(" }")
		return "\n".join(["{"] + sl + ["}"])
	
	def search(self, pattern, context = 60):
		"""
		Search all metadata fields for a pattern
		:param pattern: The search pattern
		:param context: Width of a context window to return
		:returns: An msisearch instance or None
		"""
		search = msisearch(self, pattern, context)
		if len(search.hits) > 0:
			return search
		else:
			return None
	
	def has_scope(self, pattern):
		"""
		Detect if the dataset's scope matches a pattern
		:param pattern: The scope pattern
		:returns: bool
		"""
		return grep1(pattern, self.scope) is not None
	
	def has_group(self, pattern):
		"""
		Detect if the dataset's group matches a pattern
		:param pattern: The group pattern
		:returns: bool
		"""
		return grep1(pattern, self.group) is not None

@dataclass
class msisearch:
	"""
	MSI dataset search results
	"""
	
	title: str
	scope: str
	group: str
	pattern: str
	hits: list
	
	def __init__(self, dataset, pattern, context = 60):
		"""
		Initialize an msisearch instance
		:param dataset: An msidata instance
		:param pattern: The search pattern
		:param context: Width of a context window to return
		"""
		self.title = dataset.title
		self.scope = dataset.scope
		self.group = dataset.group
		self.pattern = pattern
		hits = {}
		title = grep1(pattern, dataset.title,
			context=context)
		description = grep1(pattern, dataset.description,
			context=context)
		sample_processing = grep1(pattern, dataset.sample_processing,
			context=context)
		data_processing = grep1(pattern, dataset.data_processing,
			context=context)
		if title is not None:
			hits["title"] = title
		if description is not None:
			hits["description"] = description
		if sample_processing is not None:
			hits["sample_processing"] = sample_processing
		if data_processing is not None:
			hits["data_processing"] = data_processing
		for contact in dataset.contact:
			if any(grepl(pattern, contact.values())):
				if "contact" not in hits:
					hits["contact"] = []
				hits["contact"].append(contact)
		if any(grepl(pattern, dataset.formats)):
			hits["formats"] = dataset.formats
		if any(grepl(pattern, dataset.keywords)):
			hits["keywords"] = dataset.keywords
		if any(grepl(pattern, dataset.notes)):
			hits["notes"] = dataset.notes
		self.hits = hits
		self.printwidth = dataset.printwidth
	
	def __str__(self):
		"""
		Return str(self)
		"""
		title = self.title
		if ( len(title) > 0 ):
			sl = [f" {title}: "]
		else:
			sl = [" <Untitled>: "]
		sl.append(" {")
		sl.append("  _search pattern_: " + self.pattern)
		sl.append("  _no. of matches_: " + str(len(self.hits)))
		sl.append("  scope: " + str(self.scope))
		sl.append("  group: " + str(self.group))
		for name, desc in self.hits.items():
			if len(desc) > self.printwidth:
				desc = desc[:self.printwidth - 4] + "..."
			sl.append(f"  >{name}: {desc}")
		sl.append(" }")
		return "\n".join(["{"] + sl + ["}"])

@dataclass
class msicache:
	"""
	MSI dataset cache metadata
	"""
	
	name: str
	path: str
	_atime: float
	_mtime: float
	size: int
	
	def __init__(self, name, path, atime, mtime, size):
		"""
		Initialize an msicache instance
		:param path: The file path to the dataset
		:param name: The name of the dataset
		:param atime: Last access time
		:param mtime: Last modified time
		:param size: Total size in storage
		"""
		self.name = name
		self.path = path
		self._atime = atime
		self._mtime = mtime
		self.size = size
	
	@property
	def atime(self):
		return datetime.fromtimestamp(self._atime)
	
	@property
	def mtime(self):
		return datetime.fromtimestamp(self._mtime)
	
	def __str__(self):
		"""
		Return str(self)
		"""
		path = f"  path: '{self.path}'"
		atime = f"  atime: '{self.atime}'"
		mtime = f"  mtime: '{self.mtime}'"
		size = f"  size: {format_bytes(self.size)}"
		sl = [" {"] + [path, atime, mtime, size] + [" }"]
		sl = [f" {self.name}: "] + sl
		return "\n".join(["{"] + sl + ["}"])

class msidb:
	"""
	MSI database manager
	"""
	
	def __init__(self, username, dbpath,
		remote_dbpath = None, remote_dbhost = None,
		server = None, server_username = None,
		port = 8080, remote_port = 22):
		"""
		Initialize an msidb instance
		:param username: Your username on remote database host
		:param dbpath: The local database path
		:param remote_dbpath: The remote database path
		:param remote_dbhost: The remote hostname
		:param server: The gateway server hostname (optional)
		:param server_username: Your username on the gateway server (optional)
		:param port: The local port for gateway server SSH forwarding
		:param remote_port: The remote database host port
		"""
		if server_username is None:
			server_username = username
		self.username = username
		self.dbpath = normalizePath(dbpath, mustWork=True)
		self.remote_dbpath = remote_dbpath
		self.remote_dbhost = remote_dbhost
		self.server = server
		self.server_username = server_username
		self.port = port
		self.remote_port = remote_port
		self._manifest = None
		self._cache = None
		self.open_manifest()
	
	def __str__(self):
		"""
		Return str(self)
		"""
		sl = [f"['{key}']\n{val}" 
			for key, val 
			in self._manifest.items()]
		return "\n".join(sl)
	
	def __repr__(self):
		"""
		Return repr(self)
		"""
		user = f"username='{self.username}'"
		dbpath = f"dbpath='{self.dbpath}'"
		fields = [user, dbpath]
		if self.remote_dbpath is not None:
			remote_dbpath = f"remote_dbpath='{self.remote_dbpath}'"
			fields.append(remote_dbpath)
		if self.remote_dbhost is not None:
			remote_dbhost = f"remote_dbhost='{self.remote_dbhost}'"
			fields.append(remote_dbhost)
		if self.server is not None:
			server = f"server='{self.server}'"
			server_username = f"server_username='{self.server_username}'"
			port = f"port={self.port}"
			fields.extend([server, server_username, port])
		fields = ", ".join(fields)
		return f"msidb({fields})"
	
	def __del__(self):
		"""
		Delete self
		"""
		self.close()
	
	def __getitem__(self, key):
		"""
		Return db[key]
		"""
		return self.get(key)
	
	def get(self, key):
		"""
		Return db[key]
		:param key: A dataset name or iterable of them
		:returns: An msidata instance or dict of them
		"""
		if self._manifest is None:
			self.open_manifest()
		if isinstance(key, str):
			return self._manifest.get(key)
		else:
			return {ki: self._manifest[ki] for ki in key}
	
	def get_cached_dataset(self, scope, group, dataset):
		"""
		Get cached dataset metadata
		:param scope: The dataset scope
		:param group: The dataset group
		:param dataset: The dataset name
		:returns: An msicache instance
		"""
		tags = ["name", "atime", "mtime", "size", "path"]
		path = os.path.join(self.dbpath, scope, group, dataset)
		path = normalizePath(path, mustWork=True)
		size = dirsize(path, allnames=True)
		atime = os.path.getatime(path)
		mtime = os.path.getmtime(path)
		return msicache(name=dataset, path=path,
			atime=atime, mtime=mtime, size=size)
	
	def get_cached_group(self, scope, group):
		"""
		Get list of cached group metadata
		:param scope: The dataset scope
		:param group: The dataset group
		:returns: A list of msicache instances
		"""
		path = os.path.join(self.dbpath, scope, group)
		path = normalizePath(path, mustWork=True)
		return [self.get_cached_dataset(scope, group, dataset)
			for dataset
			in listfiles(path)]
	
	def get_cached_scope(self, scope):
		"""
		Get list of cached scope metadata
		:param scope: The dataset scope
		:returns: A list of msicache instances
		"""
		path = os.path.join(self.dbpath, scope)
		path = normalizePath(path, mustWork=True)
		scopes = []
		for group in listfiles(path):
			scopes.extend(self.get_cached_group(scope, group))
		return scopes
	
	def isopen(self):
		"""
		Check if the database is ready
		"""
		return self._manifest is not None or self._cache is not None
	
	def open(self):
		"""
		Ready the connection to the database
		"""
		self.open_manifest()
		self.open_cache()
	
	def open_manifest(self):
		"""
		Refresh the database manifest
		"""
		path = os.path.join(self.dbpath, "MSIResearch", "manifest.json")
		path = normalizePath(path, mustWork=True)
		print(f"parsing '{path}'")
		with open(path) as file:
			manifest = json.load(file)
			manifest = {name: msidata(dataset) 
				for name, dataset in manifest.items()}
			self._manifest = manifest
		print(f"manifest is searchable")
	
	def open_cache(self):
		"""
		Refresh the cache metadata
		"""
		print("detecting cached datasets")
		cache = []
		cache.extend(self.get_cached_scope("Private"))
		cache.extend(self.get_cached_scope("Protected"))
		cache.extend(self.get_cached_scope("Public"))
		self._cache = cache
		print(f"{len(cache)} datasets cached locally")
	
	def ls(self, scope = None, group = None):
		"""
		List available datasets by name
		"""
		if self._manifest is None:
			self.open_manifest()
		if scope is None and group is None:
			return list(self._manifest.keys())
		else:
			names = []
			for name, dataset in self._manifest.items():
				ok = True
				if scope is not None:
					ok = ok and dataset.has_scope(scope)
				if group is not None:
					ok = ok and dataset.has_group(group)
				if ok:
					names.append(name)
			return names
	
	def search(self, pattern = None, scope = None, group = None):
		"""
		Search dataset metadata for a pattern
		:param pattern: The pattern to find
		:param scope: Filter by scope
		:param group: Filter by group
		"""
		if self._manifest is None:
			self.open_manifest()
		hits = {}
		for name, dataset in self._manifest.items():
			ok = True
			if scope is not None:
				ok = ok and dataset.has_scope(scope)
			if group is not None:
				ok = ok and dataset.has_group(group)
			if ok and pattern is not None:
				result = dataset.search(pattern)
				if result is not None:
					hits[name] = result
		return hits
	
	def close(self):
		"""
		Remove the connection to the database
		"""
		self._manifest = None
		self._cache = None

def format_search(hits):
	"""
	Format a dict of search hits
	:param hits: A dict of hits
	:return: A formatted string
	"""
	sl = [f"['{key}']\n{val}" 
		for key, val 
		in hits.items()]
	sl = [f"#### {len(hits)} hits ####\n"] + sl
	return "\n".join(sl)

def print_search(hits):
	"""
	Print a dict of search hits
	:param hits: A dict of hits
	"""
	print(format_search(hits))

