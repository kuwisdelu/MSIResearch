
# Attach MSI data run commands
# 
# Example usage:
# 
# source("~/Datasets/MSIResearch/msirc.R")
# msi_ls()
# msi_cached(full=TRUE)
# msi_search("tumor")
# msi_search("example")
# msi_sync("Example_Continuous_imzML")
# magi_download("Magi-02", "Scratch/test", "~/Scratch/test")
# 

local(
{
	if ( dir.exists("./MSIResearch") ) {
		dbpath <- normalizePath(".")
	} else if ( dir.exists("../MSIResearch") ) {
		dbpath <- normalizePath("..")
	} else {
		dbpath <- Sys.getenv("MSI_DBPATH", "/Volumes/Datasets")
	}
	if ( !dir.exists(file.path(dbpath, "MSIResearch")) )
		stop("can't find database; set $MSI_DBPATH and try again")
	source(file.path(dbpath, "MSIResearch", "scripts", "msisetup.R"))
})

.msi$attach()
