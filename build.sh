#!/bin/bash

# Building dir (output package is left here too).
BUILD="../BUILD"
# Wether it must be a release build. If it's NOT a release build,
# branch check is ignored and snapshot name is addedd to changelog
# (Default: not release build).
RELEASE="--ignore-branch -S"
GITRELEASE="--git-ignore-branch"
# Make a tag after successfull build, auto activete in release build
# (Default: no).
RETAG=""
# Weter changelog must bu updated.
CHANGELOG=1
# tag/branch to build
BRANCH=""
# Version format used intag names
VERSION_FORMAT='v%(version)s'

while [[ $# -gt 0 ]]; do
    case "$1" in
	"-b")
	    shift
	    BUILD="$1"
	    ;;
	"-R"|"--release")
	    RELEASE="-R"
	    RETAG="--git-tag --git-retag"
	    GITRELEASE=""
	    ;;
	*) # Commit / tag / branch
	    CHANGELOG=0
	    BRANCH="--git-export=$1"
	    ;;
    esac
    shift
done

if [[ ! -d "$BUILD" ]]; then
    echo "$BUILD does not exist"
    exit 1
fi

if [[ $CHANGELOG -gt 0 ]]; then
    git-dch --git-author --debian-tag=$VERSION_FORMAT -a --spawn-editor=always $RELEASE --commit && \
	git-buildpackage -us -uc --git-ignore-new --git-export-dir=$BUILD --git-debian-tag=$VERSION_FORMAT $GITRELEASE $RETAG
    if [[ x$RETAG != "x" ]]; then
	git push && git push --tags
    fi
else
    git-buildpackage -us -uc --git-ignore-new --git-export-dir=$BUILD $BRANCH --git-debian-tag=$VERSION_FORMAT
fi

exit 0
