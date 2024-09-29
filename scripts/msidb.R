
# MSI database manager
# 
# Example usage:
# 
# source("MSIData/scripts/msidb.R")
# db <- msidb("viteklab", "/Volumes/Datasets/")
# db$ls()
# db$search("tumor")
# db$search("example")
# db$remote_dbpath <- "/Volumes/MagiCache"
# db$remote_dbhost <- "Magi-03"
# db$server <- "login.khoury.northeastern.edu"
# db$server_username <- "kuwisdelu"
# db$sync("Example_Continuous_imzML")
# db$sync("Example_Processed_imzML")
# db$cached(full=TRUE)
# 

if ( !requireNamespace("jsonlite", quietly=TRUE) )
	install.packages("jsonlite")

if ( !requireNamespace("BiocManager", quietly=TRUE) )
	install.packages("BiocManager")

if ( !requireNamespace("matter", quietly=TRUE) )
	BiocManager::install("matter")

setClassUnion("environment_OR_NULL", c("environment", "NULL"))

.msidb <- setRefClass("msidb",
	fields = c(
		username = "character",
		dbpath = "character",
		remote_dbpath = "character",
		remote_dbhost = "character",
		server = "character",
		server_username = "character",
		port = "integer",
		manifest = "environment_OR_NULL"))

.msidb$methods(
	open = function() {
		if ( !is.na(dbpath) && !isopen() )
		{
			dbpath <<- normalizePath(dbpath)
			if ( !exists("rssh") ) {
				rsshpath <- file.path(dbpath, "MSIData", "scripts", "rssh.R")
				rsshpath <- normalizePath(rsshpath)
				source(rsshpath)
			}
			file <- file.path(dbpath, "MSIData", "manifest.json")
			file <- normalizePath(file)
			message("parsing ", sQuote(file))
			db <- jsonlite::fromJSON(file)
			db <- lapply(db, structure, class="msidata")
			manifest <<- list2env(db, parent=emptyenv())
			message("checking for cached datasets")
			scopes <- c("Private", "Protected", "Public")
			scopes <- intersect(scopes, dir(dbpath))
			scopes <- normalizePath(file.path(dbpath, scopes))
			groups <- lapply(scopes, dir)
			groups <- unlist(unname(Map(file.path, scopes, groups)))
			datasets <- lapply(groups, dir)
			datasets <- unlist(unname(Map(file.path, groups, datasets)))
			message("detected ", length(datasets),
				" cached datasets in ", dbpath)
			if ( length(datasets) > 0L )
			{
				atime <- file.info(datasets)$atime
				files <- lapply(datasets, list.files, recursive=TRUE)
				files <- Map(file.path, datasets, files)
				size <- lapply(files, file.size)
				size <- vapply(size, sum, numeric(1L))
				size <- matter::size_bytes(size)
				dbcache <- data.frame(id=basename(datasets),
					time=atime, size=size, path=datasets,
					row.names=NULL)
				manifest[[".dbcache"]] <<- dbcache
			}
			message("database is ready")
		}
		if ( is.na(dbpath) )
			warning("couldn't find database; please set $dbpath")
	},
	isopen = function() {
		!is.null(manifest)
	},
	ls = function() {
		if ( !isopen() ) {
			character(0L)
		} else {
			base::ls(manifest)
		}
	},
	search = function(pattern) {
		if ( !isopen() || missing(pattern) ) {
			results <- as.list(manifest)
		} else {
			is_hit <- function(x) any(grepl(pattern, unlist(x)))
			hits <- eapply(manifest, is_hit)
			hits <- names(hits)[which(as.logical(unlist(hits)))]
			results <- mget(hits, manifest)
		}
		results
	},
	sync = function(id, force = FALSE, ask = FALSE) {
		if ( !isopen() )
			stop("database is not ready; please call $open()")
		if ( is.na(remote_dbpath) )
			stop("no remote database; please set $remote_dbpath")
		if ( length(id) != 1L )
			stop("must specify exactly 1 dataset")
		id <- match.arg(id, base::ls(manifest))
		message("syncing dataset: ", sQuote(id))
		if ( !force && id %in% cached() ) {
			message("dataset is already cached; use force=TRUE to sync anyway")
			return(invisible())
		}
		scope <- manifest[[id]]$scope
		group <- manifest[[id]]$group
		scopedir <- file.path(dbpath, scope)
		if ( !dir.exists(scopedir) ) {
			message("creating ", scopedir)
			dir.create(scopedir)
		}
		groupdir <- file.path(dbpath, scope, group)
		if ( !dir.exists(groupdir) ) {
			message("creating ", groupdir)
			dir.create(groupdir)
		}
		src <- file.path(remote_dbpath, scope, group, id)
		src <- paste0(src, "/")
		dest <- file.path(dbpath, scope, group, id)
		dest <- paste0(dest, "/")
		con <- rssh(username,
			destination=remote_dbhost,
			server=server,
			server_username=server_username,
			port=port)
		Sys.sleep(1)
		try(con$download(src, dest, ask))
		con$close()
		message("refreshing local database cache")
		refresh()
	},
	cached = function(full = FALSE) {
		if ( !isopen() ) {
			character(0L)
		} else {
			if ( full ) {
				manifest[[".dbcache"]]
			} else {
				manifest[[".dbcache"]]$id
			}
		}
	},
	refresh = function() {
		close()
		open()
	},
	close = function() {
		if ( isopen() )
			manifest <<- NULL
	})

print.msidata <- function(x, nchar = 60L, ...)
{
	printed <- c("scope", "group", "description",
		"sample processing", "data processing")
	notprinted <- setdiff(names(x), c("title", printed))
	if ( nchar(x$title) > 0L ) {
		cat("##", x$title, "\n")
	} else {
		cat("##", "<Untitled>", "\n")
	}
	for ( name in printed )
	{
		if ( nchar(x[[name]]) > nchar ) {
			desc <- paste0(substr(x[[name]], 1, nchar - 3L), "...")
		} else {
			desc <- x[[name]]
		}
		cat("$", name, ": ", desc, "\n", sep="")
	}
	cat("...additional fields:",
		paste0(sQuote(notprinted), collapse=", "), "\n")
}

msidb <- function(username, dbpath,
	remote_dbpath = NA_character_,
	remote_dbhost = NA_character_,
	server = NA_character_,
	server_username = username,
	port = 8080L,
	open = TRUE)
{
	if ( missing(dbpath) )
		dbpath <- NA_character_
	db <- .msidb(
		username=username,
		dbpath=dbpath,
		remote_dbpath=remote_dbpath,
		remote_dbhost=remote_dbhost,
		server=server,
		server_username=server_username,
		port=port,
		manifest=NULL)
	if ( open )
		db$open()
	db
}
