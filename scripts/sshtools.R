
# Example usage:
# 
# con <- ssh("kuwisdelu", "Magi-02", server="login.khoury.northeastern.edu")
# con$isopen()
# file.create("~/Scratch/test")
# con$upload("~/Scratch/test", "Scratch/test")
# file.remove("~/Scratch/test")
# con$download("Scratch/test", "~/Scratch/test")
# con$close()
# 

.ssh <- setRefClass("ssh",
	fields = c(
		username = "character",
		destination = "character",
		server = "character",
		server_username = "character",
		port = "integer",
		destination_port = "integer",
		pid = "character"))

.ssh$methods(
	open = function() {
		if ( !is.na(server) )
		{
			message("connecting to ", server)
			gateway <- paste0(server_username, "@", server)
			target <- paste0(port, ":", destination, ":", destination_port)
			cmd_ssh <- paste("{", "ssh", "-NL", target, gateway, "& }")
			cmd_echo <- paste("{", "echo $!", "; }")
			cmd <- paste(cmd_ssh, ";", cmd_echo)
			pid <<- system(cmd, intern=TRUE)
			reg.finalizer(.self@.xData,
				function(e) e$.self$close(), onexit=TRUE)
			Sys.sleep(1)
			message("forwarding to ", destination, " on port ", port)
		}
	},
	isopen = function() {
		!is.na(pid)
	},
	download = function(src, dest, ask = FALSE) {
		showsrc <- paste0(username, "@", destination, ":", src)
		if ( is.na(server) ) {
			src <- paste0(username, "@", destination, ":", src)
		} else {
			src <- paste0(username, "@localhost:", src)
		}
		message("data will be downloaded from: ", sQuote(showsrc))
		message("data will be downloaded to: ", sQuote(dest))
		if ( isFALSE(ask) || isTRUE(askYesNo("continue?")) )
		{
			rsh <- "ssh -o NoHostAuthenticationForLocalhost=yes"
			rsh <- paste(rsh, "-p", as.character(port))
			rsh <- paste0("--rsh=", sQuote(rsh, FALSE))
			src <- sQuote(src, FALSE)
			dest <- sQuote(path.expand(dest), FALSE)
			cmd_rsync <- paste("rsync", "-aP", rsh, src, dest)
			system(cmd_rsync)
		}
	},
	upload = function(src, dest, ask = FALSE) {
		showdest <- paste0(username, "@", destination, ":", dest)
		if ( is.na(server) ) {
			dest <- paste0(username, "@", destination, ":", dest)
		} else {
			dest <- paste0(username, "@localhost:", dest)
		}
		message("data will be uploaded from: ", sQuote(src))
		message("data will be uploaded to: ", sQuote(showdest))
		if ( isFALSE(ask) || isTRUE(askYesNo("continue?")) )
		{
			rsh <- "ssh -o NoHostAuthenticationForLocalhost=yes"
			rsh <- paste(rsh, "-p", as.character(port))
			rsh <- paste0("--rsh=", sQuote(rsh, FALSE))
			src <- sQuote(path.expand(src), FALSE)
			dest <- sQuote(dest, FALSE)
			cmd_rsync <- paste("rsync", "-aP", rsh, src, dest)
			system(cmd_rsync)
		}
	},
	close = function() {
		if ( !is.na(pid) ) {
			cmd_close <- paste("kill", pid)
			message("closing connection to server")
			pid <<- NA_character_
			system(cmd_close)
		}
	})

ssh <- function(username, destination,
	server = NA_character_,
	server_username = username,
	port = 8080L,
	destination_port = 22L,
	autoconnect = TRUE)
{
	con <- .ssh(
		username=username,
		destination=destination,
		server=server,
		server_username=server_username,
		port=port,
		destination_port=destination_port,
		pid=NA_character_)
	if ( autoconnect )
		con$open()
	con
}
