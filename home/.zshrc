
# Developer environment
export CONDA_AUTO_ACTIVATE_BASE=false
alias R="R --no-save"
alias python=python3
alias pydoc=pydoc3
alias pip=pip3

# Magi/MSI environment
export MSI_DBPATH="/Volumes/Datasets"
export BIOCPARALLEL_WORKER_MAX=8
export BIOCPARALLEL_WORKER_NUMBER=4
alias magi="python3 $MSI_DBPATH/MSIResearch/lib/magi.py"
alias msi="python3 $MSI_DBPATH/MSIResearch/lib/msi.py"
