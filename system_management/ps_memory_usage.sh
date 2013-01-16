#!/bin/bash
###########################################################
# Shows memory usage per process and as a total
#
# Arguments passed to this script are passed to grep which
# filters process list
###########################################################
if [ ! -z "$1" ]
then
	GREP="| grep $*"
else
	GREP=""
fi
eval "ps ax -o pid,rss,command $GREP | awk '{print \$0}{sum+=\$2} END {print \"Total\", sum/1024, \"MB\"}'"
