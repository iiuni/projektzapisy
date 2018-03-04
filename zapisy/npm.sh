#!/usr/bin/env bash
set -e

if [ -z "$NO_CREATE_MODULES_DIR" ]; then
    # Ensure the directory exists and has proper perms
    ./webpack_resources/create_modules_dir.sh
fi
./webpack_resources/run_npm_with_copy.sh $@
