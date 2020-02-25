#!/bin/bash

for job in $(sacct | grep COMPLETED | awk {'print $1'} | sed 's/\..//') ; do scancel $job; done
