
# Example usage:
# 
# db <- msidb("viteklab", "/Volumes/Datasets/")
# db$ls()
# db$search("tumor")
# 

if ( !requireNamespace("jsonlite", quietly=TRUE) )
	install.packages("jsonlite")

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
			file <- file.path(dbpath, "MSIData", "manifest.json")
			file <- normalizePath(file)
			message("parsing ", file)
			db <- jsonlite::fromJSON(file)
			db <- lapply(db, structure, class="msidata")
			manifest <<- list2env(db, parent=emptyenv())
		}
		if ( is.na(dbpath) )
			warning("couldn't find database; please set $dbpath")
	},
	isopen = function() {
		!is.null(manifest)
	},
	ls = function() {
		if ( is.null(manifest) ) {
			character(0L)
		} else {
			base::ls(manifest)
		}
	},
	search = function(pattern) {
		if ( is.null(manifest) || missing(pattern) ) {
			results <- as.list(manifest)
		} else {
			is_hit <- function(x) any(grepl(pattern, unlist(x)))
			hits <- eapply(manifest, is_hit)
			hits <- names(hits)[which(as.logical(unlist(hits)))]
			results <- mget(hits, manifest)
		}
		results
	},
	close = function() {
		if ( !is.null(manifest) )
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
	autoconnect = TRUE)
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
	if ( autoconnect )
		db$open()
	db
}
