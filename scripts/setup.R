
# Set up MSI data run commands
# 
# Example usage:
# 
# source("~/Datasets/MSIData/scripts/setup.R")
# .msi$load()
# .msi$db$ls()
# .msi$db$cached()
# .msi$attach()
# msi_search("tumor")
# msi_search("example")
# msi_sync("Example_Continuous_imzML")
# magi_download("Magi-02", "Scratch/test", "~/Scratch/test")
# .msi$detach()
# 

.msi <- new.env()
.msirc <- new.env()

.msi$known_hosts <- c("Magi-01", "Magi-02", "Magi-03")
.msi$dbpath <- Sys.getenv("MSI_DBPATH", "/Volumes/Datasets")
.msi$isloaded <- FALSE

if ( basename(Sys.info()[["nodename"]]) %in% .msi$known_hosts ) {
	# defaults for Magi nodes
	.msi$defaults <- list(
		username = Sys.info()[["user"]],
		remote_dbhost = "Magi-03.local",
		remote_dbpath = "/Volumes/MagiCache",
		server = NA_character_,
		server_username = NA_character_,
		port = 8080L)
} else {
	# defaults for clients
	.msi$defaults <- list(
		username = "viteklab",
		remote_dbhost = "Magi-03",
		remote_dbpath = "/Volumes/MagiCache",
		server = "login.khoury.northeastern.edu",
		server_username = NA_character_,
		port = 8080L)
}

.msi$load <- function()
{
	with(.msi,
	{
		if ( isloaded )
			return(invisible())
		if ( !exists("msidb") )
		{
			if ( !dir.exists(dbpath) )
				stop("couldn't find database; please set $dbpath")
			source(file.path(dbpath, "MSIData", "scripts", "rssh.R"),
				local=TRUE)
			source(file.path(dbpath, "MSIData", "scripts", "msidb.R"),
				local=TRUE)
		}
		db <- msidb(defaults$username, dbpath=dbpath,
			remote_dbpath=defaults$remote_dbpath,
			remote_dbhost=defaults$remote_dbhost,
			server=defaults$server,
			server_username=defaults$server_username,
			port=defaults$port)
		isloaded <- TRUE
	})
}

.msi$attach <- function()
{
	if ( !.msi$isloaded )
		.msi$load()
	message("attaching msirc functions:\n",
		paste0(" + ", ls(.msirc), "\n"))
	attach(.msirc, name="msirc")
}

.msi$detach <- function()
{
	if ( !.msi$isloaded )
		return(invisible())
	message("detaching msirc functions")
	detach("msirc", character.only=TRUE)
}

.msi$magi_download <- function(node, src, dest, username = NULL)
{
	with(.msi,
	{
		if ( !exists("rssh") )
		{
			if ( !dir.exists(dbpath) )
				stop("couldn't find database; please set $dbpath")
			source(file.path(dbpath, "MSIData", "scripts", "rssh.R"),
				local=TRUE)
		}
	})
	if ( is.null(username) )
		username <- .msi$defaults$username
	con <- .msi$rssh(username, destination=node,
		server=.msi$defaults$server,
		server_username=.msi$defaults$server_username,
		port=.msi$defaults$port)
	try(con$download(src, dest))
	con$close()
}

.msi$magi_upload <- function(node, src, dest, username = NULL)
{
	with(.msi,
	{
		if ( !exists("rssh") )
		{
			if ( !dir.exists(dbpath) )
				stop("couldn't find database; please set $dbpath")
			source(file.path(dbpath, "MSIData", "scripts", "rssh.R"),
				local=TRUE)
		}
	})
	if ( is.null(username) )
		username <- .msi$defaults$username
	con <- .msi$rssh(username, destination=node,
		server=.msi$defaults$server,
		server_username=.msi$defaults$server_username,
		port=.msi$defaults$port)
	try(con$upload(src, dest))
	con$close()
}

with(.msirc,
{
	msi_ls <- function()
	{
		.msi$db$ls()
	}

	msi_search <- function(pattern)
	{
		.msi$db$search(pattern)
	}

	msi_sync <- function(id, force = FALSE, ask = FALSE)
	{
		.msi$db$sync(id, force=force, ask=ask)
	}

	msi_cached <- function(full = FALSE)
	{
		.msi$db$cached(full)
	}

	msi_refresh <- function()
	{
		.msi$db$refresh()
	}

	magi_download <- function(node, src, dest, username = NULL)
	{
		.msi$magi_download(node, src=src, dest=dest, username=username)
	}

	magi_upload <- function(node, src, dest, username = NULL)
	{
		.msi$magi_upload(node, src=src, dest=dest, username=username)
	}
})
