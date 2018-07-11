#!/usr/bin/env bash
set -e

sudo mkdir -p -m 777 /webpack_modules

if [ "$#" -ne 1 ]; then
	moduleDirOwner=`whoami`
else
	moduleDirOwner=$1
fi
sudo chown $moduleDirOwner: /webpack_modules
