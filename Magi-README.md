# Magi cluster tutorial


## Contents

Jump to a section:

- [Overview](#Overview)
- [Accessing the cluster](#Accessing-the-cluster)
- [Accessing data](#Accessing-data)
- [File management](#File-management)
- [Session management](#Session-management)
- [Software](#Software)
- [Magi versus Discovery](#Magi-versus-Discovery)


## Overview

The data described in this repository is hosted on the Magi cluster. The Magi cluster is a simple network-of-workstations style Beowulf cluster of commodity Mac hardware maintained by Prof. Kylie Ariel Bemis for the Vitek Lab in the Khoury College of Computer Sciences at Northeastern University. Cluster access requires lab membership, PI authorization, and a Khoury login.


## Accessing the cluster

Currently, the following nodes are available to `viteklab` members:

- `Magi-01` : compute node (M2 Ultra / 16 p-cores / 8 e-cores / 192 GB)

- `Magi-02` : compute node (M2 Ultra / 16 p-cores / 8 e-cores / 192 GB)

- `Magi-03` : xfer node (M2 Pro / 6 p-cores / 4 e-cores / 16 GB)

Please contact the Magi cluster maintainer for `viteklab` credentials.

### SSH from Khoury login servers

You can access the Magi cluster from the Khoury login servers:

`ssh viteklab@Magi-02`

To enable X11 forwarding, use either:

`ssh -X viteklab@Magi-02`

or:

`ssh -Y viteklab@Magi-02`

Note that X11 forwarding *must* have been requested when connecting to the Khoury login servers or this will not work.

### SSH from external network

The `magi` command line utility provides functionality for accessing the Magi cluster from an external network. It assumes you are running in a UNIX-alike environment that includes `ssh` and `rsync` command line programs.

Recommended usage is to set an alias `magi` in your shell to the command `python3 $MSI_DBPATH/MSIResearch/lib/magi.py`.

Additionally, environment variables `$MAGI_USER` and `$MAGI_LOGIN` can be used to automatically set your Magi cluster username and Khoury login information.

For example, in your `.zshrc` or `.bashrc`:

```
export MAGI_USER=viteklab
export MAGI_LOGIN=<your-khoury-username>
alias magi="python3 $MSI_DBPATH/MSIResearch/lib/magi.py"
```

You can then see the command help with:

```
magi --help
```

The following subcommands are provided:

- `magi run`
    + run a command (e.g., login shell) on a Magi node
- `magi copy-id`
    + copy SSH key to a Magi node
- `magi download`
    + download file(s) from a Magi node
- `magi upload`
    + upload file(s) to a Magi node

You can see positional arguments and options for subcommand with the `--help` or `-h` flags.

For example:

```
magi run --help
```


## Accessing data

All Magi nodes have network access to the datasets described in this repository.

Please use the `msi` command line utility documented in `README.md` to manage the datasets.

From a shell session on any Magi node, you can do:

```
msi --help
```

This will show available `msi` subcommands.


## File management

Due to the small number of users, lab members use shared `viteklab` credentials to simplify cluster management.

Please do not upload large datasets without permission. Home directory storage is intended for processed data and analysis results. Contact the Magi cluster maintainer to add datasets to the cluster's storage devices.

### Shared lab directories

Please use the following directories for data management:

- `~/Datasets/`
    + Includes `MSIResearch` repository and dataset manifest
    + Includes locally cached MSI datasets
    + Manage using `msi` command line utility

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

Alternatively, an easier method is to use the `magi` command line utility. This program will set up the SSH tunnel for you, copy files or directories using `rsync`, and close the connection automatically after the file transfer is done.

For example, on your personal computer:

```
touch ~/Scratch/test
magi upload -02 ~/Scratch/test Scratch/test
magi download -02 Scratch/test ~/Scratch/test-copy
```

This will copy the `test` file to/from the `viteklab/Scratch/` directory on `Magi-02`.

### Best practices for files

It is recommended to create a subdirectory with your name in `~/Projects` and `~/Scratch` for your own usage.

Additional subdirectories can be created for projects shared between multiple lab members.


## Session management

To manage remote sessions, you can either use `tmux` on the Khoury login servers or `screen` on a Magi compute node.

Please be mindful of shared system resources. When running parallel jobs, please use as few workers as you need so that cores are available for other users.


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

To create a named session, you can do:

```
tmux new -s yourname
```

To attach a named session, do:

```
tmux attach -t yourname
```

You can view existing `tmux` sessions with:

```
tmux ls
```

### Using `screen` on Magi nodes

Alternatively, you can use `screen` on a Magi node directly.

Because `screen` sessions will be accessible to other `viteklab` members, it is important to name your sessions.

Please use the `-S` option to give a descriptive name to your `screen` sessions, e.g., your name:

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

### Best practices for sessions

Please name any `screen` or `tmux` sessions on Magi nodes with your name and/or description.

*Your sessions can be attached by other `viteklab` members.*

This is useful for sharing an ongoing task among lab members, but please be careful not to attach another user's session without permission.



## Software

The default software is listed in `Magi-INFO.md`.

If you need *specific versions* of packages, please create a virtual environment using `conda create` (for multiple dependencies), `venv` (for Python packages), or `renv` (for R packages) and install packages into the virtual environment.

If you need additional software or dependencies that require administrator privileges to install, please contact the Magi cluster maintainer.

### R/Bioconductor

The system R will be kept up-to-date with Bioc-devel, including the Bioc-devel versions of `Cardinal` and `matter`.

The system R is aliased as `R="R --no-save"`.

If you need the release version of Bioconductor or earlier, please use `renv` or `conda create`.

### Python

The system Python will be kept up-to-date with the most recent release that is compatible with both `pytorch-nightly` with `mps` device and `tensorflow-metal`.

The system Python is aliased as `python=python3` and `pip=pip3`.

Additional Python interpreters are available through `conda create`.

### Miniconda

Miniconda 3 is installed to provide package management and environments with `conda`.

While the system R and Python are set up to provide a useful out-of-the-box scientific computing environment, more specific environment needs are best handled using `conda`.

By default, `conda` is not active. Activate the base `conda` environment by using:

```
conda activate
```

Deactivate the current `conda` environment by using:

```
conda deactivate
```

If you have specific environment needs, please create a descriptively-named `conda` environment.

For example:

```
conda create -p ~/Scratch/testenv
conda activate ~/Scratch/testenv
```

You can then install dependencies using `conda` or `pip`.

To get a specific version of Python, you can do:

```
conda create -p ~/Scratch/pythonenv python=3.12
```

To get an environment with `tensorflow-metal`:

```
conda create -p ~/Scratch/tfenv python=3.10
conda activate ~/Scratch/tfenv
pip install tensorflow tensorflow-macos tensorflow-metal
```

To get an environment with `pytorch-nightly`:

```
conda create -p ~/Scratch/torchenv numpy pytorch torchvision torchaudio -c pytorch-nightly
```

For additional details, please see https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html.

To remove unused environments, after deactivating them, use:

```
conda env remove -p ~/Scratch/testenv
conda env remove -p ~/Scratch/pythonenv
conda env remove -p ~/Scratch/tfenv
conda env remove -p ~/Scratch/torchenv
```

### Homebrew

Additional system dependencies are handled via Homebrew.

You can see available Homebrew packages by using:

```
brew list
```

Homebrew packages require administrator permission to install.

Please contact the Magi cluster maintainer if you need additional system dependencies installed.

### Best practices for software

Please use virtual environments as needed to avoid creating conflicts in the system environment.

It should generally be safe to install additional R packages with `install.packages()`.

It is acceptable to install additional Python packages with `pip install` *if they do not conflict with the system `tensorflow-metal` and `pytorch-nightly` installations*. If you are not sure, please install packages to a virtual environment instead.

Environments can become quite large, so please try to re-use your environments as much as possible, and remove unused environments.

For shared projects, it is recommended to create a single `conda` environment to be used by multiple lab members.

Please name your `conda` environments so their owner and purpose are clear to other users.



## Magi versus Discovery

Northeastern University members also have access to the Discovery cluster which includes over 50,000 CPU cores and 525 GPUs.

You should use Magi if:

- You need faster single-core performance
- You need fast SSD storage for out-of-core computing
- You need less than 192 GB of memory
- You need more memory on a GPU than is available on Discovery
- You need software that is not available on Discovery
- Your data is already available on Magi

You should use Discovery if:

- You need more than 24 CPU cores
- You need more than 192 GB of memory
- You need a more powerful GPU than is available on Magi
- You need multiple CPUs with >40 Gbps interconnect bandwidth
- You need software that is not available on Magi
- Your data can be easily transfered to Discovery
