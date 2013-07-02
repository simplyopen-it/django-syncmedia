#!/bin/bash

if [ x"$1" = x"" ]; then
	echo "usage: `basename $0` <git branch|tag|commit>"
	exit 1
fi

log_and_eval ()
{
	if [[ x"$@" != x"" ]]; then
		echo "$@" 1>&2
		eval "$@"
	fi
}

GIT_VERSION="$1"
echo "git revision: $GIT_VERSION"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "working dir: $DIR"
cd "$DIR"
NAME=$(grep "Source:" debian/control | awk -F": " '{ print $2 }')
echo "project name: $NAME"
VERSION=$(grep -m1 "version" setup.py | awk -F"=" '{ print $2 }' | tr -d " " | tr -d "'" | tr -d "\"" | tr -d ",")
echo "original version: $VERSION"
TAR_NAME="$NAME""_$VERSION.orig.tar.gz"
echo "archive name: $TAR_NAME"


if [ ! -d ../BUILD ]; then
	log_and_eval mkdir ../BUILD
else
	log_and_eval rm -fr ../BUILD/*
fi

log_and_eval "git archive --format=tar \"$GIT_VERSION\" | gzip > ../\"$TAR_NAME\""

log_and_eval cd ../BUILD
log_and_eval tar zxf ../"$TAR_NAME"
log_and_eval debuild -us -uc -tc
EXIT=$?

exit $EXIT
