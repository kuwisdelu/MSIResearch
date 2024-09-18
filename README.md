# Mass spectrometry imaging datasets



## Overview

This repository tracks experimental metadata for lab-curated MSI datasets stored on the imaging group's Magi servers.

The metadata is saved in `manifest.json` in JavaScript Object Notation (JSON) format. Each record in the manifest describes an MSI dataset. The records can be updated by any lab member by editing `manifest.json` and commiting the changes to this Github repository.

Before committing changes, please make sure the manifest can be parsed with `jsonlite::fromJSON` (in R) or `json.load` (in Python).



## Magi servers

The data is currently hosted from the machine `Magi-03` on the Khoury network.

To access the Magi servers, you must first connect to the Khoury login servers:

`ssh <your-khoury-username>@login.khoury.northeastern.edu`

Then you can connect to the Magi servers from any Khoury login server. To access `Magi-03`, you can do:

`ssh viteklab@Magi-03`

Please contact Kylie Bemis at <k.bemis@northeastern.edu> or on Slack for login credentials.

### SSH keys for Khoury servers

It is strongly recommended to set up SSH key-based authentication for the intermediate Khoury login servers:

If you have not already set up SSH keys, this can be done with the following steps:

#### 1. Generate a private key on your local machine:

`ssh-keygen -t ed25519 -C "<your-email>@northeastern.edu"`

Accepting the defaults is fine, but you can add an optional passphrase.

#### 2. Start the ssh-agent in the background:

`eval "$(ssh-agent -s)"`

#### 3. Edit your configuration file:

`vim ~/.ssh/config`

You can list specific hosts instead of `*`, but the following should work in any case:

```
Host *
	UseKeychain yes
	AddKeysToAgent yes
	IdentityFile ~/.ssh/id_ed25519
```

The `UseKeychain` line can be omitted if you are not on macOS or don't want to store the (optional) passphrase in your keychain.

#### 4. Add your private key to the ssh-agent:

On macOS, you can do:

`ssh-add --apple-use-keychain ~/.ssh/id_ed25519`

Otherwise:

`ssh-add ~/.ssh/id_ed25519`

#### 5. Copy the public key from your local machine to the Khoury servers:

`ssh-copy-id -i ~/.ssh/id_ed25519.pub <your-khoury-username>@login.khoury.northeastern.edu`

You should now be able to access the Khoury servers using key-based authentication rather than using a password.

(If you access the servers from multiple machines, you will need to do this on each machine you use.)

### SSH keys for Magi servers

Because we currently rely on shared login credentials for lab members, please do __NOT__ set up SSH keys on Magi servers.

You will be asked for password authentication when connecting to `Magi-03`.



## Scopes

Datasets marked with `Private` scope require authorization from a PI for access even among lab members.

Datasets marked with `Protected` scope should not be shared outside the lab, but are accessible to any lab member.

Datasets marked with `Public` scope are already available on public repositories and can be freely shared.



## Groups

Within each scope, datasets are organized into groups based on their provenance.

For `Private` and `Protected` scope datasets, the groups typically correspond to external labs.

For `Public` scope datasets, the groups are typically public repositories such as GigaGB, MassIVE, METASPACE, and PRIDE.



## Directory structure

The following directory structure is assumed:

```
/<Parent>
    /MSIData
    /Protected
        /...
            /<Dataset>
    /Public
        /...
            /<Dataset>
```

where `...` contain group directories which contain data directories.

Recommended usage is to set your working directory to `<Parent>` when downloading datasets. Then the appropriate directory structure will be created automatically when you download a dataset.



## Accessing the data

The R script `msidata.R` provides convenience functions for searching and downloading the data from R. It assumes you are running in a UNIX environment that includes `ssh` and `scp` command line programs.

Recommended usage is to source the functions with `source("MSIData/msidata.R")`.

The following functions are provided:

- `msi_db()`
    + Return the complete dataset manifest

- `msi_ls()`
    + List all dataset identifiers

- `msi_path(id, dir = ".", remote = FALSE)`
    + Generate the local or remote path for a dataset's storage location (assuming it exists)
    + `id` is a the dataset identifier
    + `dir` is the parent directory used for downloading datasets
    + `remote` indicates whether to return the local or remote storage location 

- `msi_search(pattern)`
    + Search all experimental metadata for `pattern`.
    + `pattern` is a regular expression passed to `grepl()`

- `msi_download(id, username, dir = ".", port = 8080)`
    + Download a single dataset selected by `id`.
    + `id` is a the dataset identifier
    + `username` is your Khoury username for `login.khoury.northeastern.edu`
    + `dir` is the parent directory used for downloading datasets
    + `port` is a port to use for SSH port forwarding

Please be mindful of resources on `Magi-03`.

`Magi-03` is not intended for running analysis. It has limited memory and internal storage. (Data are stored on a connected RAID array.)


