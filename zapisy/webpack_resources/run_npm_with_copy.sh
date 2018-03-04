#!/usr/bin/env bash
set -e

# We use yarn because it's much faster than npm

# We'll want the lockfile if it exists
LOCKFILE_NAME="yarn.lock"
if [ -e $LOCKFILE_NAME ]
then
	cp $LOCKFILE_NAME /webpack_modules
fi
cp package.json /webpack_modules

yarn --cwd /webpack_modules $@

cp /webpack_modules/package.json .
cp /webpack_modules/$LOCKFILE_NAME .
