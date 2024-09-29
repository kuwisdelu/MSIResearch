
# Magi data management run commands
# 
# Example usage:
# 
# source("~/Datasets/MSIData/scripts/magirc.R")
# .magi$load()
# .magi$db$ls()
# .magi$db$cached()
# .magi$attach()
# msi_search("tumor")
# msi_search("example")
# msi_sync("Example_Continuous_imzML")
# .magi$detach()
# 

.magi <- new.env()
.magirc <- new.env()

.magi$dbpath <- Sys.getenv("MSI_DBPATH", "/Volumes/Datasets")

.magi$nodes <- c("Magi-01", "Magi-02", "Magi-03")
.magi$nodes <- c(.magi$nodes, paste0(.magi$nodes, ".local"))

.magi$isloaded <- FALSE
.magi$isattached <- FALSE

if ( Sys.info()[["nodename"]] %in% .magi$nodes ) {
	# defaults for Magi nodes
	.magi$defaults <- list(
		username = Sys.info()[["user"]],
		remote_dbhost = "Magi-03.local",
		remote_dbpath = "/Volumes/MagiCache",
		server = NA_character_,
		server_username = NA_character_,
		port = 8080L)
} else {
	# defaults for clients
	.magi$defaults <- list(
		username = "viteklab",
		remote_dbhost = "Magi-03",
		remote_dbpath = "/Volumes/MagiCache",
		server = "login.khoury.northeastern.edu",
		server_username = NA_character_,
		port = 8080L)
}

.magi$load <- function()
{
	with(.magi,
	{
		if ( isloaded )
			return(invisible())
		if ( !exists("msidb") )
		{
			if ( !dir.exists(dbpath) )
				stop("couldn't find database; please set $dbpath")
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

.magi$attach <- function()
{
	if ( !.magi$isloaded )
		.magi$load()
	if ( .magi$isattached )
		return(invisible())
	message("attaching msirc functions:\n",
		paste0(" o ", ls(.magirc), "\n"))
	attach(.magirc, name="msirc")
	.magi$isattached <- TRUE
}

.magi$detach <- function()
{
	if ( !.magi$isloaded || !.magi$isattached )
		return(invisible())
	message("detaching msirc function")
	detach("msirc", character.only=TRUE)
	.magi$isattached <- FALSE
}

.magi$download <- function(node, src, dest, ask = FALSE)
{
	with(.magi,
	{
		if ( !exists("rssh") )
		{
			if ( !dir.exists(dbpath) )
				stop("couldn't find database; please set $dbpath")
			source(file.path(dbpath, "MSIData", "scripts", "rssh.R"),
				local=TRUE)
		}
		con <- rssh(defaults$username, destination=node,
			server=defaults$server,
			server_username=defaults$server_username,
			port=defaults$port)
		try(con$download(src, dest, ask=ask))
		con$close()
	})
}

.magi$upload <- function(node, src, dest, ask = FALSE)
{
	with(.magi,
	{
		if ( !exists("rssh") )
		{
			if ( !dir.exists(dbpath) )
				stop("couldn't find database; please set $dbpath")
			source(file.path(dbpath, "MSIData", "scripts", "rssh.R"),
				local=TRUE)
		}
		con <- rssh(defaults$username, destination=node,
			server=defaults$server,
			server_username=defaults$server_username,
			port=defaults$port)
		try(con$upload(src, dest, ask=ask))
		con$close()
	})
}

with(.magirc,
{
	msi_ls <- function()
	{
		.magi$db$ls()
	}

	msi_search <- function(pattern)
	{
		.magi$db$search(pattern)
	}

	msi_sync <- function(id, force = FALSE, ask = FALSE)
	{
		.magi$db$sync(id, force=force, ask=ask)
	}

	msi_cached <- function(full = FALSE)
	{
		.magi$db$cached(full)
	}

	msi_refresh <- function()
	{
		.magi$db$refresh()
	}

	magi_download <- function(node, src, dest, ask = FALSE)
	{
		.magi$download(node, src=src, dest=dest, ask=ask)
	}

	magi_upload <- function(node, src, dest, ask = FALSE)
	{
		.magi$upload(node, src=src, dest=dest, ask=ask)
	}
})
