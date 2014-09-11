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
RELEASE_BRANCH='release'
BUILD_COMMAND="sbuild -A -s -c wheezy-amd64-sbuild"

usage() {
    echo
    echo $(basename $0) [options] [tag]
    echo "-b <build dir>"
    echo -e "\tbuild directory (default: $BUILD)"
    echo "-R, --release"
    echo -e "\tMake a release build"
    echo "-c <command>"
    echo -e "\tbuild command (default $BUILD_COMMAND)"
    echo "-h, --help"
    echo -e "\tshow this help and exit"
    exit 0
}

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
	"-c")
	    shift
	    BUILD_COMMAND="$1"
	    ;;
	"-h"|"--help")
	    usage
	    ;;
	*) # Commit / tag / branch
	    CHANGELOG=0
	    BRANCH="$1"
	    ;;
    esac
    shift
done

if [[ ! -d "$BUILD" ]]; then
    echo "$BUILD does not exist"
    exit 1
fi

if [[ $CHANGELOG -gt 0 ]]; then
    # Update changelog and, if edit successfully, commit
    git-dch -a \
	--git-author \
	--debian-tag=$VERSION_FORMAT \
	--debian-branch=$RELEASE_BRANCH \
	--spawn-editor=always $RELEASE \
	--commit

    if [[ $? -eq 0 ]]; then
	git-buildpackage \
	    --git-builder="$BUILD_COMMAND" \
	    --git-ignore-new \
	    --git-export-dir=$BUILD \
	    --git-debian-branch=$RELEASE_BRANCH \
	    --git-debian-tag=$VERSION_FORMAT $GITRELEASE $RETAG
    else
	exit $?
    fi

    if [[ x$RETAG != "x" ]]; then
	# This is a release version.
	# New tag present, we can push it
	git push && git push --tags
    fi

else
    # Rebuilding an existing tag
    git-buildpackage \
	--git-builder="$BUILD_COMMAND" \
	--git-ignore-new \
	--git-export-dir=$BUILD \
	--git-export=$BRANCH \
	--git-upstream-tree=$BRANCH \
	--git-debian-tag=$VERSION_FORMAT
fi

exit 0
