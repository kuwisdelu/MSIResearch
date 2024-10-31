
# MSI database manager
# 
# Example usage:
# 
# from msidb import *
# db = msidb("viteklab", "/Volumes/Datasets")
# db.ls()
# db.ls(scope="Public")
# print(db["PXD001283"])
# print(db)
# hits = db.search("cancer")
# print_datasets(hits)
# 
# from msidb import *
# db = msidb("viteklab", "/Volumes/Datasets", "Magi-03", server="login.khoury.northeastern.edu")
# db.sync("Example_Continuous_imzML")
# db.ls_cache()
# cached = db.ls_cache(scope="Public", details=True)
# print_datasets(cached)
#

import os
import re
import json
from time import sleep
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

def print_bytes(x, units = "auto"):
	"""
	Print bytes
	:param x: The number of bytes
	:param units: The units (B, KB, MB, etc.)
	"""
	print(format_bytes(x, units))

def format_datasets(iterable):
	"""
	Format an iterable of datasets
	:param iterable: An iterable of datasets
	:return: A formatted string
	"""
	sl = [f"['{dataset.name}']\n{dataset}" 
		for dataset 
		in iterable]
	sl = [f"#### {len(sl)} datasets ####\n"] + sl
	return "\n".join(sl)

def print_datasets(iterable):
	"""
	Print an iterable of datasets
	:param iterable: An iterable of datasets
	"""
	print(format_datasets(iterable))

@dataclass
class msidata:
	"""
	MSI dataset metadata
	"""
	name: str
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
	
	def __init__(self, name, entry, printwidth = 60):
		"""
		Initialize an msidata instance
		:param name: The name of the dataset
		:param entry: A dict parsed from its manifest entry
		"""
		self.name = name
		self.scope = entry["scope"]
		self.group = entry["group"]
		self.title = entry["title"]
		self.description = entry["description"]
		self.sample_processing = entry["sample processing"]
		self.data_processing = entry["data processing"]
		self.contact = entry["contact"]
		self.date = entry["date"]
		self.formats = entry["formats"]
		self.keywords = entry["keywords"]
		self.notes = entry["notes"]
		self.printwidth = printwidth
	
	def __str__(self):
		"""
		Return str(self)
		"""
		return self.describe(self.printwidth)
	
	def describe(self, printwidth = None):
		"""
		Return dataset description
		"""
		dataset = asdict(self)
		printed = ["scope", "group", "description",
			"sample_processing", "data_processing",
			"formats", "keywords"]
		notprinted = set(dataset.keys()).difference(printed)
		notprinted = notprinted.difference(["name", "title"])
		if len(dataset["notes"]) > 0:
			notprinted = notprinted.difference(["notes"])
		title = self.title
		if ( len(title) > 0 ):
			sl = [f" {title}: "]
		else:
			sl = [" <Untitled>: "]
		sl.append(" {")
		for field in printed:
			value = dataset[field]
			if isinstance(value, str):
				if printwidth is not None:
					if len(value) > printwidth:
						value = value[:printwidth - 4] + "..."
			else:
				value = ", ".join(value)
			sl.append(f"  {field}: {value}")
		for i, note in enumerate(dataset["notes"]):
			if printwidth is not None:
				if len(note) > printwidth:
					note = note[:printwidth - 4] + "..."
			sl.append(f"  note {i + 1}: {note}")
		more_fields = [f"'{field}'" for field in notprinted]
		more_fields = ", ".join(more_fields)
		sl.append(f"  additional fields: {more_fields}")
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
	
	name: str
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
		self.name = dataset.name
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
		for field, match in self.hits.items():
			if len(match) > self.printwidth:
				match = match[:self.printwidth - 4] + "..."
			sl.append(f"  >{field}: {match}")
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
		:param name: The name of the dataset
		:param path: The file path to the dataset
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
		path = f" path: '{self.path}'"
		atime = f" atime: '{self.atime}'"
		mtime = f" mtime: '{self.mtime}'"
		size = f" size: {format_bytes(self.size)}"
		sl = [path, atime, mtime, size]
		return "\n".join(["{"] + sl + ["}"])

class msidb:
	"""
	MSI database manager
	"""
	
	def __init__(self, username, dbpath,
		remote_dbhost = None, remote_dbpath = None,
		server = None, server_username = None,
		port = 8080, remote_port = 22, verbose = False,
		autoconnect = True):
		"""
		Initialize an msidb instance
		:param username: Your username on remote database host
		:param dbpath: The local database path
		:param remote_dbhost: The remote database host
		:param remote_dbpath: The remote database path
		:param server: The gateway server hostname (optional)
		:param server_username: Your username on the gateway server (optional)
		:param port: The local port for gateway server SSH forwarding
		:param remote_port: The remote database host port
		"""
		if remote_dbhost is not None and remote_dbpath is None:
			remote_dbpath = dbpath
		self.username = username
		self.dbpath = normalizePath(dbpath, mustWork=True)
		self.remote_dbhost = remote_dbhost
		self.remote_dbpath = remote_dbpath
		self.server = server
		self.server_username = server_username
		self.port = port
		self.remote_port = remote_port
		self.verbose = verbose
		self._manifest = None
		self._cache = None
		if autoconnect:
			self.open()
	
	def __str__(self):
		"""
		Return str(self)
		"""
		return format_datasets(self.manifest.values())
	
	def __repr__(self):
		"""
		Return repr(self)
		"""
		user = f"username='{self.username}'"
		dbpath = f"dbpath='{self.dbpath}'"
		fields = [user, dbpath]
		if self.remote_dbhost is not None:
			remote_dbhost = f"remote_dbhost='{self.remote_dbhost}'"
			fields.append(remote_dbhost)
			if self.remote_dbpath is not None:
				remote_dbpath = f"remote_dbpath='{self.remote_dbpath}'"
				fields.append(remote_dbpath)
		if self.server is not None:
			server = f"server='{self.server}'"
			if self.server_username is None:
				server_username = f"server_username=None"
			else:
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
	
	@property
	def manifest(self):
		if self._manifest is None:
			self.open_manifest()
		return self._manifest
	
	@property
	def cache(self):
		if self._cache is None:
			self.open_cache()
		return self._cache
	
	def get(self, key):
		"""
		Return db[key]
		:param key: A dataset name or iterable of them
		:returns: An msidata instance or dict of them
		"""
		if isinstance(key, str):
			return self.manifest.get(key)
		else:
			return {ki: self.manifest[ki] for ki in key}
	
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
		if self.verbose:
			print(f"parsing '{path}'")
		with open(path) as file:
			manifest = json.load(file)
			manifest = {name: msidata(name, entry) 
				for name, entry in manifest.items()}
			self._manifest = manifest
		if self.verbose:
			print(f"manifest is searchable")
	
	def open_cache(self):
		"""
		Refresh the cache metadata
		"""
		if self.verbose:
			print("detecting cached datasets")
		cache = []
		cache.extend(self.get_cached_scope("Private"))
		cache.extend(self.get_cached_scope("Protected"))
		cache.extend(self.get_cached_scope("Public"))
		self._cache = {dataset.name: dataset for dataset in cache}
		if self.verbose:
			print(f"{len(cache)} datasets available locally")
	
	def ls(self, scope = None, group = None, details = False):
		"""
		List all datasets by name
		:param scope: Filter by scope
		:param group: Filter by group
		:param details: Return names only or dataset details?
		:returns: A list of datasets
		"""
		if scope is None and group is None:
			if details:
				return list(self.manifest.values())
			else:
				return list(self.manifest.keys())
		else:
			results = []
			for name, dataset in self.manifest.items():
				ok = True
				if scope is not None:
					ok = ok and dataset.has_scope(scope)
				if group is not None:
					ok = ok and dataset.has_group(group)
				if ok:
					if details:
						results.append(dataset)
					else:
						results.append(name)
			return results
	
	def ls_cache(self, scope = None, group = None, details = False):
		"""
		List cached datasets by name
		:param scope: Filter by scope
		:param group: Filter by group
		:param details: Return names only or dataset details?
		:returns: A list of datasets
		"""
		if scope is None and group is None:
			if details:
				return list(self.cache.values())
			else:
				return list(self.cache.keys())
		else:
			results = []
			for name in self.cache.keys():
				ok = True
				dataset = self.get(name)
				if scope is not None:
					ok = ok and dataset.has_scope(scope)
				if group is not None:
					ok = ok and dataset.has_group(group)
				if ok:
					if details:
						results.append(self.cache.get(name))
					else:
						results.append(name)
			return results
	
	def search(self, pattern = None, scope = None, group = None):
		"""
		Search all dataset metadata for a pattern
		:param pattern: The pattern to find
		:param scope: Filter by scope
		:param group: Filter by group
		:returns: A list of search hits
		"""
		hits = []
		for name, dataset in self.manifest.items():
			ok = True
			if scope is not None:
				ok = ok and dataset.has_scope(scope)
			if group is not None:
				ok = ok and dataset.has_group(group)
			if ok and pattern is not None:
				result = dataset.search(pattern)
				if result is not None:
					hits.append(result)
		return hits
	
	def search_cache(self, pattern = None, scope = None, group = None):
		"""
		Search cached dataset metadata for a pattern
		:param pattern: The pattern to find
		:param scope: Filter by scope
		:param group: Filter by group
		:returns: A list of search hits
		"""
		hits = []
		for name in self.cache.keys():
			ok = True
			dataset = self.get(name)
			if scope is not None:
				ok = ok and dataset.has_scope(scope)
			if group is not None:
				ok = ok and dataset.has_group(group)
			if ok and pattern is not None:
				result = dataset.search(pattern)
				if result is not None:
					hits.append(result)
		return hits
	
	def sync(self, name, force = False, ask = False):
		"""
		Sync a dataset to local storage
		:param name: The name of the dataset
		:param force: Should the dataset be re-synced if already cached?
		:param ask: Confirm before downloading?
		"""
		if name not in self.manifest:
			raise KeyError(f"no such dataset: '{name}'")
		if name in self.cache and not force:
			print("dataset is already cached; use force=True to re-sync")
			return
		if self.remote_dbhost is None:
			raise ConnectionError("remote host is None")
		if self.remote_dbpath is None:
			raise ConnectionError("remote path is None")
		dataset = self.get(name)
		scope = dataset.scope
		group = dataset.group
		path = os.path.join(self.dbpath, scope, group)
		path = normalizePath(path, mustWork=False)
		if not os.path.isdir(path):
			os.makedirs(path)
		src = os.path.join(self.remote_dbpath, scope, group, name)
		src = src + "/"
		dest = os.path.join(self.dbpath, scope, group, name)
		dest = dest + "/"
		try:
			con = rssh(self.username,
				destination=self.remote_dbhost,
				server=self.server,
				server_username=self.server_username,
				port=self.port,
				destination_port=self.remote_port)
			sleep(1) # allow time to connect
			con.download(src, dest, ask=ask)
			if os.path.isdir(dest):
				print("sync complete; refreshing cache metadata")
				self.open_cache()
		except:
			print("a problem occured during syncing")
		finally:
			con.close()
	
	def close(self):
		"""
		Remove the connection to the database
		"""
		self._manifest = None
		self._cache = None
