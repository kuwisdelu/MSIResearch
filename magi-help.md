
# Magi cluster help

1. [Overview](#Overview)
2. [Accessing the cluster](#Accessing-the-cluster)
3. [Accessing data](#Accessing-data)
4. [File management](#File-management)
5. [Best practices](#Best-practices)
6. [Magi versus Discovery](#Magi-versus-Discovery)


## Overview

The data described in this repository is hosted on the Magi cluster. The Magi cluster is a simple network-of-workstations style Beowulf cluster of commodity Mac hardware maintained by Prof. Kylie Ariel Bemis for the Vitek Lab in the Khoury College of Computer Sciences at Northeastern University. Cluster access requires lab membership, PI authorization, and a Khoury login.


## Accessing the cluster

You can access the Magi cluster from the Khoury login servers:

`ssh viteklab@Magi-02`

To enable X11 forwarding, use either:

`ssh -X viteklab@Magi-02`

or:

`ssh -Y viteklab@Magi-02`

Note that X11 forwarding *must* have been requested when connecting to the Khoury login servers or this will not work.

Currently, the following nodes are available to `viteklab` members:

- `Magi-02` : compute node (M2 Ultra / 16 p-cores / 8 e-cores / 192 GB)

- `Magi-03` : data node (M2 Pro / 6 p-cores / 4 e-cores / 16 GB)

Please contact the Magi cluster maintainer for `viteklab` credentials.


## Accessing data

All Magi nodes have network access to the datasets described in this repository.

Please use the `msirc` functions documented in `README.md` to manage the datasets.

From any R session started on a Magi node, you can do:

```
.msi$attach()
```

This will make all `msirc` functions available without needing to `source()` any files directly.

To remove the functions from your search path, you can do:

```
.msi$detach()
```


## File management

Due to the small number of users, lab members use a shared `viteklab` login to simplify cluster management.

### Shared lab directories

Please use the following directories for data management:

- `~/Datasets/`
	+ Includes `MSIData` repository and dataset manifest
	+ Includes locally cached MSI datasets
	+ Manage using functions from `msirc.R`

- `~/Projects/`
	+ Directory for analysis projects
	+ Create subdirectories for your analyses
	+ Stable storage that will not be removed without notification

- `~/Scratch/`
	+ Directory for temporary files
	+ Create subdirectories for your scratch space
	+ May be deleted without warning

- `~/Documents/`
	+ Directory for lab documents
	+ Use to share documents and reports with other lab members

Please give your subdirectories clear, descriptive names within these directories.

### Copying files

Files and directories can be copied from any Magi node to any host visible to the Khoury network, including the Discovery cluster, using command line programs `scp` or `rsync`.

Copying files and directories to machines not visible to the Northeastern University network requires SSH tunneling.

The files `scripts/magi-download` and `scripts/magi-upload` show an example of using SSH port forwarding to download or upload files to or from a personal computer.

Alternatively, an easier method is to use the `magi_download()` and `magi_upload` functions provided from `msirc.R`. These functions will set up the SSH tunnel for you, copy files or directories using `rsync`, and close the connection automatically after the file transfer is done.

For example, on your personal computer:

```
source("MSIData/msirc.R")
file.create("~/Scratch/test")
magi_upload("Magi-02", "~/Scratch/test", "Scratch/test")
file.remote("~/Scratch/test")
magi_download("Magi-02", "Scratch/test", "~/Scratch/test")
```

This will copy to/from the `viteklab/Scratch/` directory.



## Best practices

Please be mindful of shared system resources.

Please do not upload large datasets without permission. Home directory storage is intended for processed data and analysis results. Contact the Magi cluster maintainer to add datasets to the cluster's storage devices.

In addition, it is recommended to limit parallel analyses to 8 or fewer workers, so that cores are available for other users.

To manage remote sessions, you can either us `tmux` on the Khoury login servers or `screen` on a Magi compute node.

### Using `tmux` on Khoury servers

Each Magi node is connected by ethernet, so disconnection from the Khoury login servers is relatively unlikely, except in the event of power cycling (which would disrupt your session anyway). This means that it should be relatively reliable to use `tmux` from a Khoury login server to manage your session.

For example, you can do:

```
tmux
ssh viteklab@Magi-02
```

You can then do `C-b d` to detach the `tmux` session while still connected to the Magi node with your process running.

To continue the session, do:

```
tmux attach
```

### Using `screen` on Magi nodes

Alternatively, you can use `screen` on a Magi node directly.

Because `screen` sessions will be accessible to other `viteklab` members, it is important to name your sessions.

Please use use the `-S` option to give a descriptive name to your `screen` sessions, e.g., your name:

```
screen -S yourname
```

You can then do `C-a d` to detach the `screen` session with your process running.

To continue the session, do:

```
screen -r yourname
```

You can view existing `screen` sessions with:

```
screen -ls
```

### Installing software

The default software is listed in `magi-info.md`.

If you need additional Python and R packages, but __not__ a specific version, you may install the packages directory using `pip3 install` or `install.packages()`.

If you need *specific versions* of packages, please create a virtual environment using `venv` (for Python packages) or `renv` (for R packages) and install packages into the virtual environment.

If you need additional software or dependencies that require administrator privileges to install, please contact the Magi cluster maintainer.


## Magi versus Discovery

Northeastern University members also have access to the Discovery cluster which includes over 50,000 CPU cores and 525 GPUs.

You should use Magi node if:

- You need faster single-core performance
- You need fast SSD storage for out-of-core computing
- You need less than 192 GB of memory
- You need more memory on a GPU than is available on Discovery
- You need software that is not available on Discovery

You should use Discovery if:

- You need more than 24 CPU cores
- You need more than 192 GB of memory
- You need a more powerful GPU than is available on Magi
- You need multiple CPUs with >40 Gbps interconnect bandwidth
- You need software that is not available on Magi

