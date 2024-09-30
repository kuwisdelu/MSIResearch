# Magi cluster

Maintainer: Kylie Ariel Bemis <k.bemis@northeastern.edu>
Revised: 30 September 2024

## Nodes

- Magi-01
	+ Private compute node
	+ M2 Ultra Mac Studio
	+ 16 p-cores / 8 e-cores
	+ 192 GB unified memory
	+ 8 TB storage
	+ WGK6THH9JR
	+ a4:fc:14:15:95:cb

- Magi-02
	+ Protected compute node
	+ M2 Ultra Mac Studio
	+ 16 p-cores / 8 e-cores
	+ 192 GB unified memory
	+ 4 TB storage
	+ RCNQ99YFVK
	+ a4:fc:14:18:4b:83

- Magi-03
	+ Private data node
	+ M2 Pro Mac Mini
	+ 6 p-cores / 4 e-cores
	+ 16 GB unified memory
	+ 512 GB storage
	+ HM2CW5L42D
	+ 5c:e9:1e:ea:cc:6a

## Storage

- MagiRAID
	+ 6-bay RAID-5 array
	+ 10 TB slow storage

- MagiBackup
	+ External HDD
	+ 14 TB slow storage

- MagiCache
	+ External SSD
	+ 4 TB fast storage

## Software

- Available on Magi compute nodes

- Command line developer tools
	+ screen
	+ clang
	+ git
	+ python3
	+ pip3

- Python packages (standard installation)
	+ numpy
	+ pandas
	+ scikit-learn
	+ statsmodels
	+ matplotlib
	+ seaborn

- Python packages  (custom installation)
	+ tensorflow
	+ tensorflow-macos
	+ tensorflow-metal
	+ torch
	+ torchvision
	+ torchaudio

- R and CRAN/Bioconductor packages
	+ remotes
	+ renv
	+ rmarkdown
	+ tidyverse
	+ testthat
	+ BiocManager
	+ BiocStyle
	+ Cardinal
	+ CardinalIO
	+ matter

- X11
	+ XQuartz
	+ https://www.xquartz.org

- LaTeX and pandoc
	+ MacTeX
	+ https://tug.org/mactex/
	+ https://pandoc.org
