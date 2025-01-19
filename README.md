# Mass spectrometry imaging datasets


## Contents

Jump to a section:

- [Overview](#Overview)
- [Scopes](#Scopes)
- [Groups](#Groups)
- [Directory structure](#Directory-structure)
- [Accessing the data](#Accessing-the-data)
- [SSH setup](#SSH-setup)

## Overview

This repository tracks experimental metadata for lab-curated MSI datasets stored on the MSI group's Magi servers.

The metadata is saved in `manifest.toml` in TOML format. Each record in the manifest describes an MSI dataset. The records can be updated by any lab member by editing `manifest.toml` and commiting the changes to this Github repository.

Please consider using an existing field before adding new fields. Some fields including `contact`, `keywords`, and `notes` allow multiple entries and can be extended as necessary.

If you are the contact person for a dataset within the lab, please add yourself to the `contact` field.

If you analyze a dataset, please add to `notes` with your name and your observations.

*Please note that dataset names, scopes, and groups should be ASCII for file system compatibility.*



## Scopes

Datasets are organized into scopes that define their permissions and visibility.

Datasets marked with `Private` scope require authorization from a PI for access even among lab members.

Datasets marked with `Protected` scope should not be shared outside the lab, but are accessible to any lab member.

Datasets marked with `Public` scope are already available on public repositories and can be freely shared.



## Groups

Within each scope, datasets are organized into groups based on their provenance.

For `Private` and `Protected` scope datasets, the groups typically correspond to external labs.

For `Public` scope datasets, the groups are typically public repositories such as GigaDB, MassIVE, METASPACE, and PRIDE.




## Directory structure

Datasets described in this repository can be downloaded and cached locally.

The following directory structure is assumed:

```
/$MAGI_DBPATH
    /MSI
        /MSIResearch
        /Protected
            /...
                /<Dataset>
        /Public
            /...
                /<Dataset>
```

where `...` contain group directories which contain dataset directories.

Recommended usage is to set an environment variable `$MAGI_DBPATH` in your shell to the directory containing the database.

The appropriate directory structure will be created automatically when datasets are downloaded.



## Accessing the data

The `msi` command line utility provides functionality for searching and downloading the data. It assumes you are running in a UNIX-alike environment that includes `ssh` and `rsync` command line programs.

To use the `msi` command, begin by cloning the `MagiSys` git repository, and then running the `install.sh`:

```
git clone git@github.com:kuwisdelu/MagiSys.git
./MagiSys/scripts/install.sh
```

You will then need to update your `.zshrc` or `.bashrc` with the following:

```
export MAGI_DBPATH="/path/to/Datasets"
export MAGI_SYSPATH="/path/to/MagiSys"
source "$MAGI_SYSPATH/scripts/activate.sh"
```

Finally, run the following to clone the database manifest to `$MAGI_DBPATH`:

```
./MagiSys/scripts/install-data.sh
```

You can then see the command help with:

```
msi --help
```

The following subcommands are provided:

- `msi ls`
    + list all datasets
- `msi ls-cache`
    + list cached datasets
- `msi search`
    + search all datasets
- `msi search-cache`
    + search cached datasets
- `msi prune-cache`
    + remove cached datasets
- `msi describe`
    + describe a dataset
- `msi sync`
    + sync a dataset to local cache
- `msi submit`
    + submit a dataset
- `msi status`
    + check cache versus manifest

You can see positional arguments and options for subcommand with the `--help` or `-h` flags.

For example:

```
msi search --help
```



## SSH setup

The Magi servers can be accessed from the Khoury login servers at `login.khoury.northeastern.edu`. You must have a Khoury network account to connect using SSH:

```
ssh <your-khoury-username>@login.khoury.northeastern.edu
```

It is strongly recommended to set up SSH key-based authentication for the intermediate Khoury login servers.

### SSH keys for Khoury servers

If you have not already set up SSH keys, this can be done with the following steps:

#### 1. Generate a private key on your local machine:

`ssh-keygen -t ed25519 -C "<your-email>@northeastern.edu"`

Accepting the defaults is fine, but you can add an optional passphrase.

#### 2. Start the ssh-agent in the background:

`eval "$(ssh-agent -s)"`

#### 3. Edit your configuration file:

`vim ~/.ssh/config`

On macOS, if you want to store the (optional) passphrase in your keychain:

```
Host *
    UseKeychain yes
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_ed25519
```

Otherwise:

```
Host *
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_ed25519
```

You can also list specific hosts instead of `*`.

#### 4. Add your private key to the ssh-agent:

On macOS, if you used a passphrase, you can do:

`ssh-add --apple-use-keychain ~/.ssh/id_ed25519`

Otherwise:

`ssh-add ~/.ssh/id_ed25519`

#### 5. Copy the public key from your local machine to the Khoury servers:

`ssh-copy-id -i ~/.ssh/id_ed25519.pub <your-khoury-username>@login.khoury.northeastern.edu`

You should now be able to access the Khoury servers using key-based authentication rather than using a password:

`ssh <your-khoury-username>@login.khoury.northeastern.edu`

(If you access the servers from multiple machines, you will need to do this on each machine you use.)

#### 6. Access the Magi cluster

You can then access the Magi cluster from the Khoury login servers:

`ssh viteklab@Magi-02`

Please contact the Magi cluster maintainer for `viteklab` credentials.


### SSH keys for Magi servers

By default, you will be asked for password authentication when connecting to any Magi node.

You can use the `magi copy-id` command line utility to set up SSH keys on Magi nodes. See `Magi-README.md` for details.

