
if ( !requireNamespace("jsonlite", quietly=TRUE) )
	install.packages("jsonlite")

.db <- structure(jsonlite::fromJSON("manifest.json"), class="msi_db")

.db <- "manifest.json" |>
	jsonlite::fromJSON() |>
	lapply(structure, class="msi_dataset") |>
	structure(class="msi_db")

.paste_n <- function(x, n = 60L)
{
	if ( nchar(x) > n ) {
		paste0(substr(x, 1, n - 3L), "...")
	} else {
		x
	}
}

print.msi_dataset <- function(x, ...)
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
		cat("$", name, ": ", .paste_n(x[[name]]), "\n", sep="")
	cat("...additional fields:",
		paste0(sQuote(notprinted), collapse=", "), "\n")
}

msi_db <- function(id)
{
	if ( missing(id) ) {
		.db
	} else {
		.db[id]
	}
}

msi_ls <- function() names(.db)

msi_path <- function(id, dir = ".", remote = FALSE)
{
	xs <- .db[id]
	scope <- vapply(xs, function(x) x$scope, character(1L))
	group <- vapply(xs, function(x) x$group, character(1L))
	if ( remote ) {
		file.path("/Volumes", "MagiRAID", scope, group, names(xs))
	} else {
		file.path(dir, scope, group, names(xs))
	}
}

msi_search <- function(pattern)
{
	IS_HIT <- function(x) any(grepl(pattern, unlist(x)))
	hits <- vapply(.db, IS_HIT, logical(1L))
	.db[hits]
}

msi_download <- function(id, username, dir = ".", port = 8080)
{
	if ( length(id) != 1L )
		stop("you must specify exactly one dataset")
	if ( !id %in% msi_ls() )
		stop("dataset", sQuote(id), " not found")
	if ( missing(username) )
		username <- readline("Please enter your Khoury username: ")
	message("connecting to login.khoury.northeastern.edu")
	server <- paste0(username, "@login.khoury.northeastern.edu")
	target <- paste0(port, ":Magi-03:22")
	cmd_ssh <- paste("{", "ssh", "-NL", target, server, "& }")
	cmd_echo <- paste("{", "echo $!", "; }")
	cmd_connect <- paste(cmd_ssh, ";", cmd_echo)
	pid <- system(cmd_connect, intern=TRUE)
	Sys.sleep(1)
	message("forwarding on port ", port)
	Sys.sleep(1)
	path_remote <- msi_path(id, remote=TRUE)
	path_local <- msi_path(id, dir=normalizePath(dir), remote=FALSE)
	src <- paste0("viteklab@localhost:", path_remote)
	dest <- path_local
	message("data will be downloaded from: ", sQuote(src))
	message("data will be downloaded to: ", sQuote(dest))
	if ( isTRUE(askYesNo("continue?")) )
	{
		groupdir <- dirname(dest)
		scopedir <- dirname(groupdir)
		if ( !dir.exists(scopedir) )
			dir.create(scopedir)
		if ( !dir.exists(groupdir) )
			dir.create(groupdir)
		src <- sQuote(src, q=FALSE)
		dest <- sQuote(dest, q=FALSE)
		cmd_copy <- paste("scp", "-rP", port, src, dest)
		system(cmd_copy)
	}
	cmd_close <- paste("kill", pid)
	message("closing connection to server")
	system(cmd_close)
}

message("MSI datasets are parsed and searchable")
message("use msi_search() to search available datasets")
message("use msi_download() to download a dataset")
