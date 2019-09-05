#!/bin/bash

# Set the path to include the standard folders (in case they are not already there)
export PATH="$PATH:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/util/opt/bin"

# Load any modules that we might need
if [ -e /util/opt/lmod/lmod/init/profile ]; then
    . /util/opt/lmod/lmod/init/profile
    export -f module
    GROUPMODPATH=`echo ${HOME} | sed "s/\/${USER}$/\/shared\/modulefiles/g"`
    if [ -d $GROUPMODPATH ]
    then
        MODULEPATH=`/util/opt/lmod/lmod/libexec/addto  --append MODULEPATH $GROUPMODPATH`
        export MODULEPATH
    fi
    MODULEPATH=`/util/opt/lmod/lmod/libexec/addto  --append MODULEPATH /util/opt/hcc-modules/Common`
    export LMOD_AVAIL_STYLE="system:<en_grouped>"
    module load python/3.7
    module list
fi

# Install any missing requirements for python
pip install --user -r requirements.txt
export PATH="$PATH:/home/choueiry/ihowell/.local/bin"

python3 ./sched.py $@
