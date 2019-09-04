#!/bin/bash

# Set the path to include the standard folders (in case they are not already there)
export PATH="$PATH:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/util/opt/bin"

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
    module load compiler/gcc/8.2
    module load boost/1.67
    module list
fi
